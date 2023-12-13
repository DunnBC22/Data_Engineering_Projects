"""
#################################################################
#
# Project Name: Electric Vehicle Population Project.
#
#####
#
# Author: Brian Dunn
#
#####
#
# Approx. Date of Completion: 11-18-2023
#
#####
#
#  Description: This DAG creates a copy of PostgreSQL table. 
#  Afterwards, it cleans the data. Next, I convert the data 
#  to star schema.
#
#################################################################
"""

#################################################################
#
#  Import Libraries.
#    
#################################################################


from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG

from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.subdag import SubDagOperator
from airflow.utils.edgemodifier import Label


#################################################################
#
#  Import sub-DAGs that were defined in separate files.
#    
#################################################################


import create_star_schema_part_1 as css1
import create_star_schema_part_2 as css2
import clean_up_after_star_schema_creation as cuassc
import sub_dag_remove_samples_with_nulls_in_cols as rswn
import sub_dag_remove_multiple_columns as rmc


#################################################################
#
#  Define default arguments.
#    
#################################################################


default_args = {
    'owner': 'dunnbc22',
    'retries': 5,
    'retry_delay': timedelta(minutes=2)
}

MAIN_DAG_NAME = "Electric_Vehicle_Population-v01"

MAIN_PIPELINE_TABLE = "ev_pop_pipe"

POSTGRES_CONN_NAME = "postgres_conn"


#################################################################
#
#  Create DAG for this pipeline.
#    
#################################################################


with DAG(
    default_args=default_args,
    dag_id=MAIN_DAG_NAME,
    catchup=False,
    description="Pipeline for Electric Vehicle Population",
    start_date=datetime(2023, 12, 1),
    schedule_interval='@once', 
    tags=[
        "Electric", 
        "Vehicle", 
        "Electric Vehicle"
        ],
    owner_links={"airflow": "mailto:DunnBC22@gmail.com"},
    doc_md=__doc__
) as dag:
    
    
    ############################################################
    #
    #  Operators to CREATE copy of TABLE for this pipeline.
    #   
    ############################################################
    
    
    create_copy_of_table = PostgresOperator(
        task_id="create_copy_of_postgres_table",
        postgres_conn_id=POSTGRES_CONN_NAME,
        sql="/sql/create_table_copy.sql",
        params={
            "new_table_name": MAIN_PIPELINE_TABLE,
            "orig_table_name": "ev_population"
        }
    )

    
    ############################################################
    #
    #  Operators to preprocess data.
    #   
    ############################################################
    
    #################################################
    #
    #  Remove columns from table:
    #       - VIN
    #       - CensusTract2020
    #       - DOLVehicleID
    #       - BaseMSRP
    #
    #################################################
    
    
    cols_to_remove = [
        "VIN",
        "CensusTract2020",
        "DOLVehicleID",
        "BaseMSRP"
        ]
    
    remove_unnecessary_columns = SubDagOperator(
        task_id="remove_unnecessary_columns",
        subdag=rmc.sub_dag_remove_multiple_columns(
            table_name=MAIN_PIPELINE_TABLE,
            postgres_conn_name=POSTGRES_CONN_NAME,
            column_names=cols_to_remove,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="remove_unnecessary_columns",
            args=default_args
            ),
    )
    
    
    #################################################
    #
    #  Remove samples that have nulls in any of 
    #  the following columns:
    #   - ElectricUtility
    #   - VehicleLocation
    #   - LegislativeDistrict
    #   - City
    #   - County
    #
    #################################################
    
    
    cols_with_nulls = [
        "ElectricUtility",
        "VehicleLocation",
        "LegislativeDistrict",
        "City",
        "County"
        ]
    
    remove_samples_with_nulls = SubDagOperator(
        task_id="remove_samples_with_nulls",
        subdag=rswn.sub_dag_remove_samples_with_nulls(
            table_name=MAIN_PIPELINE_TABLE,
            postgres_conn_name=POSTGRES_CONN_NAME,
            column_names=cols_with_nulls,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="remove_samples_with_nulls",
            args=default_args
            ),
    )
    
    
    #################################################
    #
    #  Convert each of the following columns into 
    #  dimension tables to convert database to
    #  star schema:
    #       - ElectricUtility
    #       - CAFVEligibility
    #       - ElectricVehicleType
    #       - Model
    #       - Make
    #       - ModelYear
    #       - StateName
    #       - City
    #       - County
    #
    #################################################
    
    
    dim_tables_to_create = [
        {
            "col_name": "ElectricUtility",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "CAFVEligibility",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "ElectricVehicleType",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Model",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Make",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "ModelYear",
            "data_type": "INTEGER"
        },
        {
            "col_name": "StateName",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "City",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "County",
            "data_type": "VARCHAR"
        },
    ]
    
    create_dim_tables = SubDagOperator(
        task_id="create_dim_tables",
        subdag=css1.sub_dag_create_star_schema(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=dim_tables_to_create,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="create_dim_tables",
            postgres_conn_name=POSTGRES_CONN_NAME,
            args=default_args
        )
    )
    
    insert_fk_into_fact_table = SubDagOperator(
        task_id="insert_fk_into_fact_table",
        subdag=css2.sub_dag_create_star_schema(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=dim_tables_to_create,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="insert_fk_into_fact_table",
            postgres_conn_name=POSTGRES_CONN_NAME,
            args=default_args
        )
    )
    
    dim_cols_to_remove = [
        table["col_name"] for table in dim_tables_to_create
        ]
    
    remove_replaced_dim_cols = SubDagOperator(
        task_id="remove_replaced_dim_cols",
        subdag=cuassc.sub_dag_star_schema_clean_up(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=dim_cols_to_remove,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="remove_replaced_dim_cols",
            postgres_conn_name=POSTGRES_CONN_NAME,
            args=default_args
        )
    )

    
    
    #################################################
    #
    #  Create the order of operators for this dag.
    #
    #################################################


    (
        create_copy_of_table 
        >> Label("Transform Data")
        >> remove_unnecessary_columns
        >> remove_samples_with_nulls
        >> Label("Convert to Star Schema")
        >> create_dim_tables
        >> insert_fk_into_fact_table
        >> remove_replaced_dim_cols
    )
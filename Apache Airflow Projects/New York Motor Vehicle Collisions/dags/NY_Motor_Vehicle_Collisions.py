"""
#################################################################
#
# Project Name: New York Motor Vehicle Collisions Project.
#
#####
#
# Author: Brian Dunn
#
#####
#
# Approx. Date of Completion: 12-18-2023
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


import sub_dag_generate_month_dom_year as gen_dmy
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

MAIN_DAG_NAME = "NY_Motor_Vehicle_Collisions-v01"

MAIN_PIPELINE_TABLE = "ny_vehicle_colls_pipe"

POSTGRES_CONN_NAME = "postgres_conn"


#################################################################
#
#  Create DAG for this pipeline.
#    
#################################################################


with DAG(
    default_args=default_args,
    dag_id=MAIN_DAG_NAME,
    description="Pipeline for New York Motor Vehicle Collisions",
    start_date=datetime(2023, 12, 1),
    catchup=False,
    schedule_interval='@once', 
    tags=[
        "NY", 
        "New York", 
        "Motor", 
        "Vehicle", 
        "Collisions", 
        "Motor Vehicle", 
        "Motor Vehicle Collisions"
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
            "orig_table_name": "ny_motor_vehicle"
        }
    )

    
    ############################################################
    #
    #  Operators to preprocess data.
    #   
    ############################################################
    
    #################################################
    #
    #  Remove columns from the table:
    #       - CONTRIBUTING FACTOR VEHICLE 5
    #       - CONTRIBUTING FACTOR VEHICLE 4
    #       - CONTRIBUTING FACTOR VEHICLE 3
    #       - OFF STREET NAME
    #       - CROSS STREET NAME
    #       - ON STREET NAME
    #       - COLLISION_LOCATION
    #       - VEHICLE TYPE CODE 3
    #       - VEHICLE TYPE CODE 4
    #       - VEHICLE TYPE CODE 5
    #       - COLLISION_ID
    #
    #################################################
    
    cols_to_remove = [
        "CONTRIBUTING_FACTOR_VEHICLE_5",
        "CONTRIBUTING_FACTOR_VEHICLE_4",
        "CONTRIBUTING_FACTOR_VEHICLE_3",
        "OFF_STREET_NAME",
        "CROSS_STREET_NAME",
        "ON_STREET_NAME",
        "COLLISION_LOCATION",
        "VEHICLE_TYPE_CODE_3",
        "VEHICLE_TYPE_CODE_4",
        "VEHICLE_TYPE_CODE_5",
        "COLLISION_ID"
        ]
    
    remove_unnecessary_columns = SubDagOperator(
        task_id="remove_unnecessary_columns",
        subdag=rmc.sub_dag_remove_multiple_columns(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=cols_to_remove,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="remove_unnecessary_columns",
            postgres_conn_name=POSTGRES_CONN_NAME,
            args=default_args
            ),
    )
    
    
    #################################################
    #
    #  Generate date parts for the following column:
    #       - CRASH DATE
    #
    #################################################
    
    
    date_col = ["CRASH_DATE"]
    
    generate_date_parts = SubDagOperator(
        task_id=f"generate_date_parts",
        subdag=gen_dmy.sub_dag_generate_month_dom_year_of_date(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=date_col,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="generate_date_parts",
            postgres_conn_name=POSTGRES_CONN_NAME,
            args=default_args
            )
    )
    
    
    #################################################
    #
    #  Add column with the hour of the date 
    #  for the following column(s):
    #       - CRASH TIME
    #
    #################################################
    
    
    time_col = "CRASH_TIME"
    
    hour_from_time_col_params = {
        "table_name": MAIN_PIPELINE_TABLE,
        "input_col_name": time_col,
        "hour_of_day_col_name": f"{time_col}_hour"
        }
    
    crash_time_hour = PostgresOperator(
        task_id="isolate_crash_time_hour_of_day",
        sql="/sql/isolate_hour_of_day.sql",
        postgres_conn_id=POSTGRES_CONN_NAME,
        params=hour_from_time_col_params
    )
    
    
    #################################################
    #
    #  Remove samples that have nulls in any of 
    #  the following columns:
    #       - BOROUGH
    #       - ZIP CODE
    #       - LATITUDE
    #       - LONGITUDE
    #       - NUMBER OF PERSONS INJURED
    #       - NUMBER OF PERSONS KILLED
    #       - VEHICLE TYPE CODE 1
    #       - VEHICLE TYPE CODE 2
    #       - CONTRIBUTING FACTOR VEHICLE 1
    #       - CONTRIBUTING FACTOR VEHICLE 2
    #
    #################################################
    
    
    remove_nulls_in_these_cols = [
        "BOROUGH",
        "ZIP_CODE",
        "LATITUDE",
        "LONGITUDE",
        "NUMBER_OF_PERSONS_INJURED",
        "NUMBER_OF_PERSONS_KILLED",
        "VEHICLE_TYPE_CODE_1",
        "VEHICLE_TYPE_CODE_2",
        "CONTRIBUTING_FACTOR_VEHICLE_1",
        "CONTRIBUTING_FACTOR_VEHICLE_2"
        ]
    
    remove_samples_with_nulls = SubDagOperator(
        task_id="remove_samples_with_nulls",
        subdag=rswn.sub_dag_remove_samples_with_nulls(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=remove_nulls_in_these_cols,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="remove_samples_with_nulls",
            postgres_conn_name=POSTGRES_CONN_NAME,
            args=default_args
            ),
    )
    
    
    #################################################
    #
    #  Convert each of the following columns into 
    #  dimension tables to convert database to
    #  star schema:
    #       - VEHICLE_TYPE_CODE_1
    #       - VEHICLE_TYPE_CODE_2
    #       - CONTRIBUTING_FACTOR_VEHICLE_1
    #       - CONTRIBUTING_FACTOR_VEHICLE_2
    #       - BOROUGH
    #
    #################################################
    
    
    dim_tables_to_create = [
        {
            "col_name": "VEHICLE_TYPE_CODE_1",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "VEHICLE_TYPE_CODE_2",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "CONTRIBUTING_FACTOR_VEHICLE_1",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "CONTRIBUTING_FACTOR_VEHICLE_2",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "BOROUGH",
            "data_type": "VARCHAR"
        }
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
        >> generate_date_parts
        >> crash_time_hour
        >> remove_samples_with_nulls
        >> Label("Convert to Star Schema")
        >> create_dim_tables
        >> insert_fk_into_fact_table
        >> remove_replaced_dim_cols
    )
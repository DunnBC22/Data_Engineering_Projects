"""
#################################################################
#
# Project Name: Analytics Olympiad 2022 Project
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

#################################################################
#
#  Import sub-DAGs that were defined in separate files.
#    
#################################################################

import remove_outliers_1_5_iqr as iqr
import create_star_schema_part_1 as css1
import create_star_schema_part_2 as css2
import clean_up_after_star_schema_creation as cuassc
import sub_dag_remove_multiple_columns as rmc
import sub_dag_change_column_data_type as sdccdt

#################################################################
#
#  Define default arguments & other Basic Values/Constants
#    
#################################################################

default_args = {
    'owner': 'dunnbc22',
    'retries': 5,
    'retry_delay': timedelta(minutes=2)
}

MAIN_DAG_NAME = "analytics_olympiad-v01"
POSTGRES_CONNECTION_STRING = "postgres_conn"
MAIN_PIPELINE_TABLE = "analytics_olympiad_pipeline"
ORIG_TABLE = "ao"

#################################################################
#
#  Create DAG for this pipeline.
#    
#################################################################

with DAG(
    default_args=default_args,
    dag_id=MAIN_DAG_NAME,
    description="Analytics Olympiad 2022 Pipeline",
    start_date=datetime(2023, 12, 1),
    schedule_interval='@once', 
    catchup=False,
    tags=[
        "Analytics", 
        "Olympiad", 
        "2022"
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
        postgres_conn_id=POSTGRES_CONNECTION_STRING,
        sql="/sql/create_table_copy.sql",
        params={
            "new_table_name": MAIN_PIPELINE_TABLE,
            "orig_table_name": ORIG_TABLE
        }
    )

    ############################################################
    #
    #  Operators to preprocess data.
    #   
    ############################################################
    
    #################################################
    #
    #  Remove these columns from table:
    #       - ID
    #
    #################################################
    
    cols_to_remove = [
        "ID"
        ]
    
    remove_unnecessary_columns = SubDagOperator(
        task_id="remove_unnecessary_columns",
        subdag=rmc.sub_dag_remove_multiple_columns(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=cols_to_remove,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="remove_unnecessary_columns",
            postgres_conn_name=POSTGRES_CONNECTION_STRING,
            args=default_args
            ),
    )
    
    #################################################
    #
    #  There are no missing values in this table.
    #
    #################################################
    
    #################################################
    # 
    #  Add ID column to fact table.
    # 
    #################################################
    
    add_id_column = PostgresOperator(
        task_id="add_id_column",
        sql="""
        ALTER TABLE {{ params.table_name }}
        ADD COLUMN {{ params.id_col_name }} SERIAL PRIMARY KEY;
        """,
        postgres_conn_id=POSTGRES_CONNECTION_STRING,
        params={
            "table_name": MAIN_PIPELINE_TABLE,
            "id_col_name": "id_col"
        }
    )
    
    #################################################
    #
    #  Remove samples with outliers (using the 
    #  1.5 * IQR rule) for the following columns:
    #       - ANNUAL_MILEAGE
    #
    #################################################
    
    cols_with_outliers = [
        "annual_mileage"
    ]
    
    remove_outliers_1_5_iqr = SubDagOperator(
        task_id=f"remove_samples_with_outliers",
        subdag=iqr.sub_dag_remove_outliers_1_5_iqr(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=cols_with_outliers,
            id_column_name="id_col",
            parent_dag_name=MAIN_DAG_NAME, 
            postgres_conn_name=POSTGRES_CONNECTION_STRING,
            child_dag_name="remove_samples_with_outliers",
            args=default_args
            ),
        )
    
    #################################################
    # 
    #  Remove ID column to fact table.
    # 
    #################################################
    
    remove_id_column = PostgresOperator(
        task_id="remove_id_column",
        sql="""
        ALTER TABLE {{ params.table_name }}
        DROP COLUMN {{ params.id_col_name }};
        """,
        postgres_conn_id=POSTGRES_CONNECTION_STRING,
        params={
            "table_name": MAIN_PIPELINE_TABLE,
            "id_col_name": "id_col"
        }
    )

    #################################################
    #
    #  Remove outliers using common sense values 
    #  for the following columns:
    #       - PAST_ACCIDENTS 
    #           - Delete samples with more than 5 
    #       - DUIS
    #           - Delete samples with more than 3
    #       - SPEEDING_VIOLATIONS
    #           - Delete samples with more than 5
    #
    #################################################
    
    remove_outliers_past_accidents = PostgresOperator(
        task_id="remove_outliers_past_accidents",
        sql="/sql/common_sense_remove_outliers.sql",
        postgres_conn_id=POSTGRES_CONNECTION_STRING,
        params={
            "table_name": MAIN_PIPELINE_TABLE, 
            "col_name": "PAST_ACCIDENTS", 
            "bool_value_gt": 5
        }
    )
    
    remove_outliers_dui = PostgresOperator(
        task_id="remove_outliers_dui",
        sql="/sql/common_sense_remove_outliers.sql",
        postgres_conn_id=POSTGRES_CONNECTION_STRING,
        params={
            "table_name": MAIN_PIPELINE_TABLE, 
            "col_name": "DUIS", 
            "bool_value_gt": 3
        }
    )
    
    remove_outliers_speeding_violations = PostgresOperator(
        task_id="remove_outliers_speeding_violations",
        sql="/sql/common_sense_remove_outliers.sql",
        postgres_conn_id=POSTGRES_CONNECTION_STRING,
        params={
            "table_name": MAIN_PIPELINE_TABLE, 
            "col_name": "SPEEDING_VIOLATIONS", 
            "bool_value_gt": 5
        }
    )
    
    #################################################
    #
    #  Change data type of column (to new value)
    #       - ANNUAL_MILEAGE (INTEGER)
    #       - CHILDREN (INTEGER)
    #       - MARRIED (INTEGER)
    #       - VEHICLE_OWNERSHIP (INTEGER)
    #
    #################################################
    
    change_cols_data_type = [
        "ANNUAL_MILEAGE",
        "CHILDREN",
        "MARRIED",
        "VEHICLE_OWNERSHIP"
        ]
    
    change_column_data_types = SubDagOperator(
        task_id="change_column_data_types",
        subdag=sdccdt.sub_dag_change_column_data_type(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=change_cols_data_type,
            new_dtype="INTEGER",
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="change_column_data_types",
            postgres_conn_name=POSTGRES_CONNECTION_STRING,
            args=default_args
        )
    )
    
    #################################################
    #
    #  Convert each of the following columns into 
    #  dimension tables to convert database to
    #  star schema:
    #       - TYPE_OF_VEHICLE
    #       - VEHICLE_YEAR
    #       - INCOME
    #       - EDUCATION
    #       - DRIVING_EXPERIENCE
    #       - GENDER
    #       - AGE
    #
    #################################################
    
    dim_tables_to_create = [
        {
            "col_name": "TYPE_OF_VEHICLE",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "VEHICLE_YEAR",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "INCOME",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "EDUCATION",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "DRIVING_EXPERIENCE",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "GENDER",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "AGE",
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
            postgres_conn_name=POSTGRES_CONNECTION_STRING,
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
            postgres_conn_name=POSTGRES_CONNECTION_STRING,
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
            column_names=dim_tables_to_create,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="remove_replaced_dim_cols",
            postgres_conn_name=POSTGRES_CONNECTION_STRING,
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
        >> remove_unnecessary_columns
        >> add_id_column
        >> remove_outliers_1_5_iqr
        >> remove_id_column
        >> remove_outliers_past_accidents
        >> remove_outliers_dui
        >> remove_outliers_speeding_violations
        >> change_column_data_types
        >> create_dim_tables
        >> insert_fk_into_fact_table
        >> remove_replaced_dim_cols
    )
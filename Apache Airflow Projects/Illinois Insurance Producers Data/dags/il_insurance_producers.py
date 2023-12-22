"""
#################################################################
#
# Project Name: Illinois Insurance Producers Pipeline Project
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
#  Description: This DAG creates a copy of PostgreSQL table 
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

import create_star_schema_part_1 as css1
import create_star_schema_part_2 as css2
import clean_up_after_star_schema_creation as cuassc
import sub_dag_remove_samples_with_nulls_in_cols as rswc
import sub_dag_remove_multiple_columns as rmc

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

MAIN_DAG_NAME = "Illinois_Insurance_Producers_Data-v01"
PIPELINE_TABLE_NAME = "iipd_pipeline"
POSTGRES_CONNECTION_STRING = "postgres_conn"

#################################################################
#
#  Create DAG for this pipeline.
#    
#################################################################

with DAG(
    default_args=default_args,
    dag_id=MAIN_DAG_NAME,
    description="Illinois Insurance Producers Data Pipeline",
    start_date=datetime(2023, 12, 1),
    schedule_interval='@once',
    catchup=False,
    tags=[
        "Illinois", 
        "Insurance", 
        "Producers"
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
            "new_table_name": PIPELINE_TABLE_NAME,
            "orig_table_name": "iipd"
        }
    )

    ############################################################
    #
    #  Operators to preprocess data. 
    # 
    #  Note(s):
    #       - No Outliers to worry about since most columns 
    #         are discrete, categorical, or semi-structured 
    #         text.
    #   
    ############################################################
    
    #################################################
    #
    #  Remove these columns from table:
    #       - id
    #       - index_id
    #       - MLG_ADDRESS2
    #       - MLG_ADDRESS1
    #
    #################################################
    
    cols_to_remove = [
        "id",
        "index_id",
        "MLG_ADDRESS2",
        "MLG_ADDRESS1"
        ]
    
    remove_unnecessary_columns = SubDagOperator(
        task_id="remove_unnecessary_columns",
        subdag=rmc.sub_dag_remove_multiple_columns(
            table_name=PIPELINE_TABLE_NAME,
            column_names=cols_to_remove,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="remove_unnecessary_columns",
            postgres_conn_name=POSTGRES_CONNECTION_STRING,
            args=default_args
            ),
        )
    
    #################################################
    #
    #  Remove samples that include null values 
    #  in any of the following columns: 
    #       - LOA_NAME
    #       - FIRST_NAME
    #       - LAST_NAME_OR_BUSINESS_NAME
    #
    #################################################
    
    cols_with_null_sample_values = [
        "LOA_NAME",
        "FIRST_NAME",
        "LAST_NAME_OR_BUSINESS_NAME"
        ]
    
    remove_samples_with_null_values = SubDagOperator(
        task_id="remove_samples_with_null_values",
        subdag=rswc.sub_dag_remove_samples_with_nulls(
            table_name=PIPELINE_TABLE_NAME,
            column_names=cols_with_null_sample_values,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="remove_samples_with_null_values",
            postgres_conn_name=POSTGRES_CONNECTION_STRING,
            args=default_args
            )
        )
    
    #################################################
    #
    #  Convert each of the following columns into 
    #  dimension tables to convert database to
    #  star schema:
    #       - LOA_Name
    #       - ZIP
    #       - MAILING_STATE
    #       - MAILING_CITY
    #       - FIRST_NAME
    #       - LAST_NAME_OR_BUSINESS_NAME
    #
    #################################################
    
    dim_tables_to_create = [
        {
            "col_name": "LOA_Name",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "ZIP",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "MAILING_STATE",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "MAILING_CITY",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "FIRST_NAME",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "LAST_NAME_OR_BUSINESS_NAME",
            "data_type": "VARCHAR"
        }
    ]
    
    create_dim_tables = SubDagOperator(
        task_id="create_dim_tables",
        subdag=css1.sub_dag_create_star_schema(
            table_name=PIPELINE_TABLE_NAME,
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
            table_name=PIPELINE_TABLE_NAME,
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
            table_name=PIPELINE_TABLE_NAME,
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
        >> remove_samples_with_null_values
        >> create_dim_tables
        >> insert_fk_into_fact_table
        >> remove_replaced_dim_cols
    )
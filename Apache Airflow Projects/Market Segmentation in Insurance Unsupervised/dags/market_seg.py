"""
#################################################################
#
# Project Name: Market Segmentation in Insurance Project (Unsupervised)
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

MAIN_DAG_NAME = "market_segmentation-v01"
MAIN_PIPELINE_TABLE = "market_segm_pipe"
POSTGRES_CONNECTION_STRING = "postgres_conn"

#################################################################
#
#  Create DAG for this pipeline.
#    
#################################################################

with DAG(
    default_args=default_args,
    dag_id=MAIN_DAG_NAME,
    description="Market Segmentation in Insurance Pipeline",
    start_date=datetime(2023, 12, 1),
    schedule_interval='@once', 
    catchup=False,
    tags=[
        "market", 
        "segmentation", 
        "market_segmentation",
        "insurance"
        ],
    owner_links={"airflow": "mailto:DunnBC22@gmail.com"},
    doc_md=__doc__
) as dag:
    
    ############################################################
    #
    #  Operators to CREATE copy of TABLE for this pipeline.
    # 
    #  Note(s):
    #       - After viewing some metadata on the dataset, 
    #         there is no reason to remove outliers.
    #       - There are no columns that needs to be 
    #         converted into dimension tables in this table.
    #   
    ############################################################
    
    create_copy_of_table = PostgresOperator(
        task_id="create_copy_of_postgres_table",
        postgres_conn_id=POSTGRES_CONNECTION_STRING,
        sql="/sql/create_table_copy.sql",
        params={
            "new_table_name": MAIN_PIPELINE_TABLE,
            "orig_table_name": "market_seg"
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
    #       - CUST_ID
    #
    #################################################
    
    cols_to_remove = [
        "CUST_ID"
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
            )
    )
    
    #################################################
    #
    #  Remove samples that include null values 
    #  in any of the following columns: 
    #       - MINIMUM_PAYMENTS
    #       - CREDIT_LIMIT
    #
    #################################################
    
    cols_with_null_sample_values = [
        "MINIMUM_PAYMENTS",
        "CREDIT_LIMIT"
    ]
    
    remove_samples_w_nulls = SubDagOperator(
        task_id="remove_samples_with_nulls",
        subdag=rswc.sub_dag_remove_samples_with_nulls(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=cols_with_null_sample_values,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="remove_samples_with_nulls",
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
        >> remove_samples_w_nulls
    )
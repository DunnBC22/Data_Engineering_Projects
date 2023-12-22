"""
#################################################################
#
# Project Name: Caravan Insurance Challenge Project
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


import sub_dag_remove_multiple_columns as rmc
import remove_single_value_columns as rsvc


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

MAIN_DAG_NAME = "Caravan_Insurance_Challenge_Project-v01"
PIPELINE_TABLE_NAME = "pipeline_caravan_insurance"
POSTGRES_CONNECTION_STRING = "postgres_conn"


#################################################################
#
#  Create DAG for this pipeline.
#    
#################################################################


with DAG(
    default_args=default_args,
    dag_id=MAIN_DAG_NAME,
    description="California Housing Data Pipeline",
    start_date=datetime(2023, 12, 1),
    schedule_interval='@once', 
    catchup=False,
    tags=[
        "caravan", 
        "insurance"
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
            "orig_table_name": "caravan_insurance_pred"
        }
    )
    
    ############################################################
    #
    #  Operators to preprocess data.
    # 
    #  Note(s):
    #       - There are no missing values in this dataset
    #       - This dataset is comprised on categorical data, 
    #         so no need to worry about outliers.
    #       - The categorical features are already in a star 
    #         schema compliant format.
    #   
    ############################################################
    
    #################################################
    #
    #  Remove these columns from table:
    #       - ORIGIN
    # 
    #################################################
    
    cols_to_remove = [
        "ORIGIN"
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
    #  Remove columns with only one distinct value.
    #
    #################################################
    
    remove_single_value_columns = SubDagOperator(
        task_id="remove_single_value_columns",
        subdag=rsvc.sub_dag_remove_single_val_cols(
            table_name= PIPELINE_TABLE_NAME,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="remove_single_value_columns",
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
        >> remove_single_value_columns
    )
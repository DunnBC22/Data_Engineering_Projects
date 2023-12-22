"""
#################################################################
#
# Project Name: COVID19 Prediction Binary Classification Project.
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

import create_star_schema_part_1 as css1
import create_star_schema_part_2 as css2
import clean_up_after_star_schema_creation as cuassc
import sub_dag_generate_month_dom_year as gen_dmy

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

MAIN_DAG_NAME = "COVID19_Prediction_Classification-v01"
MAIN_PIPELINE_TABLE = "covid_19_prediction_clf_pipeline"
POSTGRES_CONN_NAME = "postgres_conn"

#################################################################
#
#  Create DAG for this pipeline.
#    
#################################################################

with DAG(
    default_args=default_args,
    dag_id=MAIN_DAG_NAME,
    description="Pipeline for COVID19 Prediction Classification",
    start_date=datetime(2023, 12, 1),
    schedule_interval='@once', 
    catchup=False,
    tags=[
        "COVID19", 
        "COVID", 
        "Prediction", 
        "Binary Classification"
        ],
    owner_links={"airflow": "mailto:DunnBC22@gmail.com"},
    dagrun_timeout=timedelta(minutes=60),
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
            "orig_table_name": "covid19_pred"
        }
    )

    ############################################################
    #
    #  Operators to preprocess data.
    #
    #  Notes: 
    #       - No need to impute missing values (there are 
    #         none).
    #       - Columns are discrete/categorical, so no 
    #         need to worry about outliers.
    #   
    ############################################################
    
    #################################################
    #
    #  Remove columns from table:
    #       - Ind_ID
    #
    #################################################
    
    col_to_remove = "Ind_ID"
    
    remove_col = PostgresOperator(
        task_id=f"remove_{col_to_remove}_column",
        postgres_conn_id=POSTGRES_CONN_NAME,
        sql="/sql/remove_columns.sql",
        params={
            "table_name": MAIN_PIPELINE_TABLE,
            "column_name": col_to_remove
            }
        )
    
    #################################################
    #
    #  Generate date parts for the following 
    #  columns:
    #       - Test_date
    #
    #################################################
    
    date_cols = ["Test_date"]
    
    generate_date_parts = SubDagOperator(
        task_id="generate_date_parts",
        subdag=gen_dmy.sub_dag_generate_month_dom_year_of_date(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=date_cols,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="generate_date_parts",
            postgres_conn_name=POSTGRES_CONN_NAME,
            args=default_args
            ),
    )
    
    #################################################
    #
    #  Convert each of the following columns into 
    #  dimension tables to convert database to
    #  star schema:
    #       - Known_contact
    #       - Sex
    #       - Age_60_above
    #       - Corona
    #       - Headache
    #       - Shortness_of_breath
    #       - Sore_throat
    #       - Fever
    #       - Cough_symptoms
    #
    #################################################
    
    dim_tables_to_create = [
        {
            "col_name": "known_contact",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "sex",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "age_60_above",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "corona",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "headache",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "shortness_of_breath",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "sore_throat",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "fever",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "cough_symptoms",
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
            column_names=dim_tables_to_create,
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
        >> remove_col
        >> generate_date_parts
        >> create_dim_tables
        >> insert_fk_into_fact_table
        >> remove_replaced_dim_cols 
    )
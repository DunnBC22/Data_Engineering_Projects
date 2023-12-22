"""
#################################################################
#
# Project Name: Bank Account and Credit Card Complaints Project
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
##### 
# 
# Data Source: 
# https://www.kaggle.com/datasets/ranadeep/credit-risk-dataset
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

import sub_dag_remove_multiple_columns as sdrmc
import create_star_schema_part_1 as css1
import create_star_schema_part_2 as css2
import clean_up_after_star_schema_creation as cuassc
import sub_dag_remove_samples_with_nulls_in_cols as sdrsn
import sub_dag_clean_vals_and_update_dtypes as cvaud

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

MAIN_DAG_NAME = "bank_and_cc_complaints-v01"
POSTGRES_CONN_NAME = 'postgres_conn'
MAIN_PIPELINE_TABLE = "airflow_complaints"

#################################################################
#
#  Create DAG for this pipeline.
#    
#################################################################

with DAG(
    default_args=default_args,
    dag_id=MAIN_DAG_NAME,
    description="Pipeline for Bank and Credit Card Complaints",
    start_date=datetime(2023, 12, 1),
    schedule_interval='@once', 
    catchup=False,
    tags=[
        "credit_cards", 
        "bank", 
        "complaints"
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
            "orig_table_name": "complaints"
        }
    )

    ############################################################
    #
    #  Operators to preprocess data.
    #   
    ############################################################
    
    #################################################
    #
    #  Remove columns from complaints table:
    #       - tags
    #       - company_public_response
    #       - consumer_complaint_narrative
    #       - sub_issue
    #       - complaint_id
    #
    #################################################
    
    remove_unnecessary_columns = SubDagOperator(
        task_id="remove_unnecessary_columns",
        subdag=sdrmc.sub_dag_remove_multiple_columns(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=[
                "tags", 
                "company_public_response", 
                "consumer_complaint_narrative", 
                "sub_issue",
                "complaint_id"
                ],
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="remove_unnecessary_columns",
            postgres_conn_name=POSTGRES_CONN_NAME,
            args=default_args
            ),
    )
    
    #################################################
    #
    #  For the credit card dataset, fill all NULLS 
    #  with 'credit card' for the sub_product feature.
    #
    #################################################
    
    cc_nulls_params = {
        "table_name": MAIN_PIPELINE_TABLE, 
        "set_col_vals": "Sub_product",
        "other_col_ref": "product", 
        "value_to_set_null_to": "'Credit card'"
        }
    
    fill_sub_product_for_cc_dataset = PostgresOperator(
        task_id=f"fill_sub_product_for_cc_dataset",
        sql="/sql/fill_sub_product_for_cc_ds.sql",
        postgres_conn_id=POSTGRES_CONN_NAME,
        params=cc_nulls_params
        )
    
    #################################################
    #
    #  Fill all NULLS in 'Consumer consent provided'
    #  column with 'Not_yet_60_days'
    #
    #################################################
    
    nulls_in_ccp_params = {
        "table_name": MAIN_PIPELINE_TABLE, 
        "col_to_fill": "Consumer_consent_provided", 
        "value_to_fill_in": "'not_yet_60_days'"
        }
    
    handle_nulls_in_consumer_consent_provided = PostgresOperator(
        task_id=f"handle_nulls_in_consumer_consent_provided",
        sql="/sql/handle_nulls_consumer_consent_provided.sql",
        postgres_conn_id=POSTGRES_CONN_NAME,
        params=nulls_in_ccp_params
        )
    
    #################################################
    #
    #  Fill all NULLS in 'Consumer_disputed'
    #  column with 'N/A'.
    #
    #################################################
    
    nulls_in_cons_disp_params = {
        "table_name": MAIN_PIPELINE_TABLE, 
        "col_name": "Consumer_disputed",
        "default_value": "'NA'"
        }
    
    handle_nulls_in_consumer_disputed = PostgresOperator(
        task_id=f"handle_nulls_in_consumer_disputed",
        sql="/sql/handle_nulls.sql",
        postgres_conn_id=POSTGRES_CONN_NAME,
        params=nulls_in_cons_disp_params
        )
    
    #################################################
    #
    #  Remove samples that have nulls in any of 
    #  the following columns:
    #   - bank_state
    #   - zip_code
    #
    #################################################
    
    remove_samples_with_nulls = SubDagOperator(
        task_id="remove_samples_with_nulls_in_particular_columns",
        subdag=sdrsn.sub_dag_remove_samples_with_nulls(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=[
                "bank_state", 
                "zip_code",
                ],
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="remove_samples_with_nulls_in_particular_columns",
            postgres_conn_name=POSTGRES_CONN_NAME,
            args=default_args
            ),
    )
    
    #################################################
    #
    #  Remove the ``` character whereever it may exist 
    #  in the zip_code column and update the data type 
    #  of that column to INTEGER.
    #
    #################################################
    
    remove_fancy_char_in_zip_codes = SubDagOperator(
        task_id="remove_fancy_char_in_zip_codes",
        subdag=cvaud.sub_dag_clean_vals_and_update_dtypes(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=["bank_state"],
            new_dtype = "INTEGER",
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="remove_fancy_char_in_zip_codes",
            postgres_conn_name=POSTGRES_CONN_NAME,
            args=default_args
            )
        )
    
    #################################################
    #
    #  Convert each of the following columns into 
    #  dimension tables to convert database to
    #  star schema:
    #       - bank_state
    #       - company
    #       - issue
    #       - product
    #       - sub_product
    #       - submitted_via
    #       - consumer_consent_provided
    #
    #################################################
    
    dim_tables_to_create = [
        {
            "col_name": "bank_state",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "company",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "issue",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "product",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "sub_product",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "submitted_via",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "consumer_consent_provided",
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
        >> remove_unnecessary_columns
        >> fill_sub_product_for_cc_dataset
        >> handle_nulls_in_consumer_consent_provided
        >> handle_nulls_in_consumer_disputed
        >> remove_samples_with_nulls
        >> remove_fancy_char_in_zip_codes
        >> create_dim_tables
        >> insert_fk_into_fact_table
        >> remove_replaced_dim_cols
    )
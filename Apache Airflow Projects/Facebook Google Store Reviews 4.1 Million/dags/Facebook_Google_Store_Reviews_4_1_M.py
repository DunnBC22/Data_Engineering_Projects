"""
#################################################################
#
# Project Name: 4.1 Million Facebook Google Store Reviews Project
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

import sub_dag_remove_multiple_columns as rmc
import create_star_schema_part_1 as css1
import create_star_schema_part_2 as css2
import clean_up_after_star_schema_creation as cuassc
import sub_dag_generate_month_dom_year as gen_dmy
import remove_outliers_1_5_iqr as iqr

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

MAIN_DAG_NAME = "facebook_Google_Store_Reviews_4_1_million-v01"
POSTGRES_CONNECTION = "postgres_conn"

PIPELINE_TABLE = "fb_gs_reviews_pipeline"
ORIG_TABLE = "fb_google_reviews"

#################################################################
#
#  Create DAG for this pipeline.
#    
#################################################################

with DAG(
    default_args=default_args,
    dag_id=MAIN_DAG_NAME,
    description="Pipeline for 4.1 Million Facebook Google Store Reviews",
    start_date=datetime(2023, 12, 1),
    schedule_interval='@once', 
    tags=[
        "Facebook", 
        "Google_Store", 
        "Reviews"
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
        postgres_conn_id=POSTGRES_CONNECTION,
        sql="/sql/create_table_copy.sql",
        params={
            "new_table_name": PIPELINE_TABLE,
            "orig_table_name": ORIG_TABLE
        }
    )

    ############################################################
    #
    #  Operators to preprocess data.
    #   
    ############################################################
    
    ######################################################
    # 
    #  Remove the following columns from pipeline table:
    #       - author_app_version
	#	    - index
    #   	- review_id
	#	    - psuedo_author_id
    #
    #################################################
    
    cols_to_remove = [
        "author_app_version",
        "pseudo_author_id",
        "review_id"
    ]
    
    remove_unnecessary_columns = SubDagOperator(
        task_id="remove_unnecessary_columns",
        subdag=rmc.sub_dag_remove_multiple_columns(
            table_name=PIPELINE_TABLE,
            column_names=cols_to_remove,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="remove_unnecessary_columns",
            args=default_args,
            postgres_conn_name=POSTGRES_CONNECTION
            ),
    )
    
    #################################################
    #
    #  Generate Year, Month, & Day of Month for
    #  for the following columns:
    #       - review_timestamp
    #
    #################################################
    
    timestamp_col = ["review_timestamp"]
    
    generate_date_parts = SubDagOperator(
        task_id="generate_date_parts",
        subdag=gen_dmy.sub_dag_generate_month_dom_year_of_date(
            table_name=PIPELINE_TABLE,
            column_names=timestamp_col,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="generate_date_parts",
            postgres_conn_name=POSTGRES_CONNECTION,
            args=default_args
        )
    )
    
    #################################################
    #
    #  Handle samples with missing values in 
    #  following column(s):
    #       - review_text
    #
    #  Because there are only 542 missing values 
    #  of nearly ~4.1 million samples overall, it 
    #  makes the most sense to just drop samples 
    #  with missing values instead of making 
    #  educated guesses.
    #
    #################################################
    
    nulls_params = {
        "table_name": PIPELINE_TABLE, 
        "column_name": "review_text",
        }
    
    handle_columns_with_nulls = PostgresOperator(
        task_id=f"remove_samples_with_any_nulls",
        sql="/sql/remove_samples_with_any_nulls.sql",
        postgres_conn_id=POSTGRES_CONNECTION,
        params=nulls_params
        )
    
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
        postgres_conn_id=POSTGRES_CONNECTION,
        params={
            "table_name": PIPELINE_TABLE,
            "id_col_name": "id_col"
        }
    )
    
    #################################################
    #
    #  Remove samples with outliers (using the 
    #  1.5 * IQR rule) for the following columns:
    #       - review_likes
    #
    #################################################
    
    cols_with_outliers = [
        "review_likes"
    ]
    
    remove_outliers_1_5_iqr = SubDagOperator(
        task_id=f"remove_samples_with_outliers",
        subdag=iqr.sub_dag_remove_outliers_1_5_iqr(
            table_name=PIPELINE_TABLE,
            column_names=cols_with_outliers,
            id_column_name="id_col",
            parent_dag_name=MAIN_DAG_NAME, 
            postgres_conn_name=POSTGRES_CONNECTION,
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
        postgres_conn_id=POSTGRES_CONNECTION,
        params={
            "table_name": PIPELINE_TABLE,
            "id_col_name": "id_col"
        }
    )

    #################################################
    #
    #  Convert each of the following columns into 
    #  dimension tables to convert database to
    #  star schema:
    #       - author_name
    #       - review_text
    #
    #################################################
    
    dim_tables_to_create = [
        {
            "col_name": "review_text",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "author_name",
            "data_type": "VARCHAR"
        }
    ]
    
    create_dim_tables = SubDagOperator(
        task_id="create_dim_tables",
        subdag=css1.sub_dag_create_star_schema(
            table_name=PIPELINE_TABLE,
            column_names=dim_tables_to_create,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="create_dim_tables",
            postgres_conn_name=POSTGRES_CONNECTION,
            args=default_args
        )
    )
    
    insert_fk_into_fact_table = SubDagOperator(
        task_id="insert_fk_into_fact_table",
        subdag=css2.sub_dag_create_star_schema(
            table_name=PIPELINE_TABLE,
            column_names=dim_tables_to_create,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="insert_fk_into_fact_table",
            postgres_conn_name=POSTGRES_CONNECTION,
            args=default_args
        )
    )
	
    dim_cols_to_remove = [
        table["col_name"] for table in dim_tables_to_create
        ]
    
    remove_replaced_dim_cols = SubDagOperator(
        task_id="remove_replaced_dim_cols",
        subdag=cuassc.sub_dag_star_schema_clean_up(
            table_name=PIPELINE_TABLE,
            column_names=dim_tables_to_create,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="remove_replaced_dim_cols",
            postgres_conn_name=POSTGRES_CONNECTION,
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
        >> generate_date_parts
        >> handle_columns_with_nulls
        >> add_id_column
        >> remove_outliers_1_5_iqr
        >> remove_id_column
        >> create_dim_tables
        >> insert_fk_into_fact_table
        >> remove_replaced_dim_cols
    )
"""
#################################################################
#
# Project Name: California Housing Data Project.
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
#  to star schema and run some basic metrics about the data. 
#  If everything completes successfully, I send an email to 
#  notify myself of such.
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
from airflow.utils.edgemodifier import Label

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

MAIN_DAG_NAME = "california_housing_data-v01"

PIPELINE_TABLE_NAME = "pipeline_ca_housing"

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
    tags=[
        "california", 
        "housing", 
        "real_estate"
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
            "orig_table_name": "ca_housing_data"
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
    #       - id
    #       - index_id
    #       - STREET_ADDRESS
    #       - CITY
    #       - NEXT_OPEN_HOUSE_START_TIME
    #       - NEXT_OPEN_HOUSE_END_TIME
    #       - HOA_PER_MONTH
    #       - PRICE_PER_SQUARE_FOOT
    #       - YEAR_BUILT
    #       - SOLD_DATE
    #       - URL_STRING
    #       - MLS
    #       - INTERESTED
    #       - FAVORITE
    #
    #################################################
    
    cols_to_remove = [
        "id",
        "index_id",
        "STREET_ADDRESS",
        "CITY",
        "NEXT_OPEN_HOUSE_START_TIME",
        "NEXT_OPEN_HOUSE_END_TIME",
        "PRICE_PER_SQUARE_FOOT",
        "YEAR_BUILT",
        "SOLD_DATE",
        "URL_STRING",
        "MLS",
        "INTERESTED",
        "FAVORITE",
        "HOA_PER_MONTH"
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
    #       - STATE_OR_PROVINCE
    #       - ZIP_OR_POSTAL_CODE
    #       - PRICE
    #       - BEDS
    #       - PROPERTY_LOCATION
    #       - BATHS
    #       - SQUARE_FEET
    #       - LOT_SIZE
    #       - DAYS_ON_MARKET
    #       - SALES_STATUS
    #       - URL_SOURCE
    #       - LATITUDE
    #       - LONGITUDE
    #
    #################################################
    
    
    cols_with_null_sample_values = [
        "STATE_OR_PROVINCE",
        "ZIP_OR_POSTAL_CODE",
        "PRICE",
        "BEDS",
        "BATHS",
        "SQUARE_FEET",
        "LOT_SIZE",
        "DAYS_ON_MARKET",
        "SALES_STATUS",
        "URL_SOURCE",
        "PROPERTY_LOCATION",
        "LATITUDE",
        "LONGITUDE"
    ]
    
    remove_samples_w_nulls = SubDagOperator(
        task_id="remove_samples_w_nulls",
        subdag=rswc.sub_dag_remove_samples_with_nulls(
            table_name=PIPELINE_TABLE_NAME,
            column_names=cols_with_null_sample_values,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="remove_samples_w_nulls",
            postgres_conn_name=POSTGRES_CONNECTION_STRING,
            args=default_args
            ),
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
        postgres_conn_id=POSTGRES_CONNECTION_STRING,
        params={
            "table_name": PIPELINE_TABLE_NAME,
            "id_col_name": "id_col"
        }
    )
    
    
    #################################################
    #
    #  Remove samples with outliers (using the 
    #  1.5 * IQR rule) for the following columns:
    #       - BEDS
    #       - BATHS
    #       - SQUARE_FEET
    #       - LOT_SIZE
    #       - DAYS_ON_MARKET
    #
    #################################################
    
    cols_with_outliers = [
        "beds",
        "baths",
        "square_feet",
        "lot_size",
        "days_on_market"
    ]
    
    remove_outliers_1_5_iqr = SubDagOperator(
        task_id=f"remove_samples_with_outliers",
        subdag=iqr.sub_dag_remove_outliers_1_5_iqr(
            table_name=PIPELINE_TABLE_NAME,
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
            "table_name": PIPELINE_TABLE_NAME,
            "id_col_name": "id_col"
        }
    )
    
    
    #################################################
    #
    #  Convert each of the following columns into 
    #  dimension tables to convert database to
    #  star schema:
    #       - URL_SOURCE
    #       - SALES_STATUS
    #       - ZIP_OR_POSTAL_CODE
    #       - STATE_OR_PROVINCE
    #       - PROPERTY_TYPE
    #       - SALE_TYPE
    # 
    #  Note(s):
    #       - For the DAYS_ON_MARKET, BEDS & BATHS 
    #         features, I did not include them as 
    #         there would be almost no memory savings 
    #         to do so.
    #
    #################################################
    
    
    dim_tables_to_create = [
        {
            "col_name": "URL_SOURCE",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "SALES_STATUS",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "ZIP_OR_POSTAL_CODE",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "STATE_OR_PROVINCE",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "PROPERTY_TYPE",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "SALE_TYPE",
            "data_type": "VARCHAR"
        },
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
        table["col_name"] 
        for table in dim_tables_to_create
        ]
    
    remove_replaced_dim_cols = SubDagOperator(
        task_id="remove_replaced_dim_cols",
        subdag=cuassc.sub_dag_star_schema_clean_up(
            table_name=PIPELINE_TABLE_NAME,
            column_names=dim_cols_to_remove,
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
        >> Label("Tranform Data")
        >> remove_unnecessary_columns
        >> remove_samples_w_nulls
        >> add_id_column
        >> remove_outliers_1_5_iqr
        >> remove_id_column
        >> Label("Create Star Schema")
        >> create_dim_tables
        >> insert_fk_into_fact_table
        >> remove_replaced_dim_cols
    )
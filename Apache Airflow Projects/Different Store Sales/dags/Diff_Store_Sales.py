"""
#################################################################
#
# Project Name: Different Store Sales Project
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

MAIN_DAG_NAME = "Different_Store_Sales-v01"

MAIN_PIPELINE_TABLE = "dif_store_sales"

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
    description="Pipeline for Different Store Sales",
    start_date=datetime(2023, 12, 1),
    schedule_interval='@once', 
    tags=[
        "Different Store Sales", 
        "Store", 
        "Sales", 
        "Retail", 
        "Store Sales", 
        "Time Series"
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
            "orig_table_name": "diff_store_sales"
        }
    )

    
    ############################################################
    #
    #  Operators to preprocess data.
    # 
    #  Note(s):
    #       - There are no missing values in the entire table.
    #   
    ############################################################
    
    #################################################
    #
    #  Remove columns from this table:
    #       - invoice_no
    #       - customer_id
    #
    #################################################
    
    
    cols_to_remove = [
        "invoice_no",
        "customer_id"
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
    #  Add ID column to fact table.
    # 
    #################################################
    
    
    add_id_column = PostgresOperator(
        task_id="add_id_column",
        sql="""
        ALTER TABLE {{ params.table_name }}
        ADD COLUMN {{ params.id_col_name }} SERIAL PRIMARY KEY;
        """,
        postgres_conn_id=POSTGRES_CONN_NAME,
        params={
            "table_name": MAIN_PIPELINE_TABLE,
            "id_col_name": "id_col"
        }
    )
    
    
    #################################################
    #
    #  Remove samples with outliers (using the 
    #  1.5 * IQR rule) for the following columns:
    #       - cost_price_per_unit
    #       - selling_price_per_unit
    #       - quantity
    #
    #################################################
    
    cols_with_outliers = [
        "cost_price_per_unit",
        "selling_price_per_unit",
        "quantity"
    ]
    
    remove_outliers_1_5_iqr = SubDagOperator(
        task_id=f"remove_samples_with_outliers",
        subdag=iqr.sub_dag_remove_outliers_1_5_iqr(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=cols_with_outliers,
            id_column_name="id_col",
            parent_dag_name=MAIN_DAG_NAME, 
            postgres_conn_name=POSTGRES_CONN_NAME,
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
        postgres_conn_id=POSTGRES_CONN_NAME,
        params={
            "table_name": MAIN_PIPELINE_TABLE,
            "id_col_name": "id_col"
        }
    )
    
    
    #################################################
    #
    #  Generate date parts for the following columns:
    #       - invoice_date
    #
    #################################################
    
    date_cols = ["invoice_date"]
    
    generate_date_parts = SubDagOperator(
        task_id="generate_date_parts",
        subdag=gen_dmy.sub_dag_generate_month_dom_year_of_date(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=date_cols,
            parent_dag_name=MAIN_DAG_NAME, 
            child_dag_name="generate_date_parts",
            postgres_conn_name=POSTGRES_CONN_NAME,
            args=default_args
        )
    )
    
    
    #################################################
    #
    #  Convert each of the following columns into 
    #  dimension tables to convert database to
    #  star schema:
    #       - shopping_mall
    #       - state_name
    #       - region
    #       - payment_method
    #       - category
    #       - gender
    #
    #################################################
    
    
    dim_tables_to_create = [
        {
            "col_name": "shopping_mall",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "state_name",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "region",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "payment_method",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "category",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "gender",
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
        >> Label("Remove Unnecessary Columns")
        >> remove_unnecessary_columns
        >> Label("Remove Outliers Iteratively")
        >> add_id_column
        >> remove_outliers_1_5_iqr
        >> remove_id_column
        >> Label("Generate Date Parts")
        >> generate_date_parts
        >> Label("Convert to Star Schema")
        >> create_dim_tables
        >> insert_fk_into_fact_table
        >> remove_replaced_dim_cols
    )
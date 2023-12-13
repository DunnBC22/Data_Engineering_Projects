"""
#################################################################
#
# Project Name: House Price Prediction Project.
#
#####
#
# Author: Brian Dunn
#
#####
#
# Approx. Date of Completion: 11-18-2023
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

from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.subdag import SubDagOperator
from airflow.utils.edgemodifier import Label


#################################################################
#
#  Import sub-DAGs that were defined in separate files.
#    
#################################################################


import remove_outliers_1_5_iqr as iqr
import sub_dag_generate_month_dom_year as gen_dmy
import create_star_schema_part_1 as css1
import create_star_schema_part_2 as css2
import clean_up_after_star_schema_creation as cuassc
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

MAIN_DAG_NAME = "house_price_prediction-v01"

MAIN_PIPELINE_TABLE = "house_price_pred_pipe"

POSTGRES_CONN_NAME = "postgres_conn"


#################################################################
#
#  Create DAG for this pipeline.
#    
#################################################################

with DAG(
    default_args=default_args,
    dag_id=MAIN_DAG_NAME,
    description="Pipeline for House Price Prediction",
    start_date=datetime(2023, 12, 1),
    schedule_interval='@once', 
    catchup=False,
    tags=[
        "House", 
        "Price", 
        "Prediction", 
        "Regression", 
        "Real Estate"
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
            "orig_table_name": "house_price_pred"
        }
    )
    
    
    ############################################################
    #
    #  Operators to preprocess data.
    #   
    ############################################################
    
    #################################################
    #
    #  Generate Year, Month and Day of Month for 
    #  the following columns:
    #       - Date_Added
    #
    #################################################
    
    
    generate_date_parts = SubDagOperator(
        task_id=f"generate_date_parts",
        subdag=gen_dmy.sub_dag_generate_month_dom_year_of_date(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=["Date_Added"],
            parent_dag_name=MAIN_DAG_NAME, 
            child_dag_name="generate_date_parts",
            postgres_conn_name=POSTGRES_CONN_NAME,
            args=default_args
        )
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
    #       - Area_Size
    #       - bedrooms
    #       - baths
    #
    #################################################
    
    
    cols_with_outliers = [
        "area_size",
        "bedrooms", 
        "baths"
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
    #  Remove ID column from fact table.
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
    #  Remove columns from table:
    #       - Agent
    #       - Agency
    #       - Page_Url
    #       - Location_id
    #       - Property_id
    #
    #################################################
    
    
    cols_to_remove = [
        "Agent",
        "Agency",
        "Page_Url",
        "Location_id",
        "Property_id"
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
    #  Convert each of the following columns into 
    #  dimension tables to convert database to
    #  star schema:
    #       - Area_Category
    #       - Area_Type
    #       - Purpose
    #       - Area
    #       - Province_Name
    #       - City
    #       - Location_Code
    #       - Property_Type
    #
    #################################################
    
    
    dim_tables_to_create = [
        {
            "col_name": "Area_Category",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Area_Type",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Purpose",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Area",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Province_Name",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "City",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Location_Code",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Property_Type",
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
        >> Label("Transform Data")
        >> remove_unnecessary_columns
        >> add_id_column
        >> remove_outliers_1_5_iqr
        >> remove_id_column
        >> generate_date_parts
        >> Label("Convert to Star Schema")
        >> create_dim_tables
        >> insert_fk_into_fact_table
        >> remove_replaced_dim_cols
    )
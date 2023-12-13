"""
#################################################################
#
# Project Name: Travel Insurance Project
#
#####
#
# Author: Brian Dunn
#
#####
#
# Approx. Date of Completion: 12-8-2023
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


import remove_outliers_1_5_iqr as iqr
import create_star_schema_part_1 as css1
import create_star_schema_part_2 as css2
import clean_up_after_star_schema_creation as cuassc
import sub_dag_remove_multiple_columns as rmc
import sub_dag_remove_outliers_fixed_values as rofv


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

MAIN_DAG_NAME = "Travel_Insurance-v01"

PIPELINE_TABLE_NAME = "travel_insurance_pipe"

POSTGRES_CONNECTION_STRING = "postgres_conn"


#################################################################
#
#  Create DAG for this pipeline.
#    
#################################################################


with DAG(
    default_args=default_args,
    dag_id=MAIN_DAG_NAME,
    description="Travel Insurance Pipeline",
    start_date=datetime(2023, 12, 1),
    schedule_interval='@once', 
    catchup=False,
    tags=[
        "travel", 
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
            "orig_table_name": "travel_insurance"
        }
    )

    
    ############################################################
    #
    #  Operators to preprocess data.
    # 
    #  Note(s):
    #       - There are no missing values to impute (after 
    #         removing the Gender column).
    #   
    ############################################################
    
    #################################################
    #
    #  Remove these columns from table:
    #       - Gender (over 70% of values are missing)
    #
    #################################################
    
    
    cols_to_remove = [
        "Gender"
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
    #       - Age
    #
    #################################################
    
    cols_with_outliers = [
        "age"
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
    #  Remove Samples with a Negative Duration value.
    #
    #################################################
    
    cols_with_neg_values = [
        {
            "column_name": "Duration",
            "operator": "<",
            "comparison_value": 0
        }
    ]
    
    remove_samples_w_neg_values = SubDagOperator(
        task_id="remove_samples_w_neg_values",
        subdag=rofv.sub_dag_remove_outliers_fixed_vals(
            table_name=PIPELINE_TABLE_NAME,
            cols_w_fixed_ranges=cols_with_neg_values,
            parent_dag_name=MAIN_DAG_NAME, 
            postgres_conn_name=POSTGRES_CONNECTION_STRING,
            child_dag_name="remove_samples_w_neg_values",
            args=default_args
            )
        )
    
    
    #################################################
    #
    #  Convert each of the following columns into 
    #  dimension tables to convert database to
    #  star schema:
    #       - Destination
    #       - Claim
    #       - Distribution_Channel
    #       - Agency_Type
    #       - Agency
    #
    #################################################
    
    
    dim_tables_to_create = [
        {
            "col_name": "Destination",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Claim",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Distribution_Channel",
            "data_type": "VARCHAR"
        },{
            "col_name": "Agency_Type",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Agency",
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
        >> Label("Transform Data")
        >> remove_unnecessary_columns
        >> remove_samples_w_neg_values
        >> add_id_column
        >> remove_outliers_1_5_iqr
        >> remove_id_column
        >> Label("Convert to Star Schema")
        >> create_dim_tables
        >> insert_fk_into_fact_table
        >> remove_replaced_dim_cols
    )
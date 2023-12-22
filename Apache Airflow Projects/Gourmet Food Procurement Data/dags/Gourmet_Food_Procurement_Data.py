"""
#################################################################
#
# Project Name: Gourmet Food Procurement Data Project.
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

import impute_with_median as imputer
import remove_outliers_1_5_iqr as iqr
import create_star_schema_part_1 as css1
import create_star_schema_part_2 as css2
import clean_up_after_star_schema_creation as cuassc
import sub_dag_remove_samples_with_nulls_in_cols as rswn
import sub_dag_remove_multiple_columns as rmc
import sub_dag_remove_samples_with_neg_vals as rswnv

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

MAIN_DAG_NAME = "Gourmet_Food_Procurement_Data-v01"
MAIN_PIPELINE_TABLE = "gourmet_food_procurement_data_pipeline"
POSTGRES_CONN_NAME = "postgres_conn"

#################################################################
#
#  Create DAG for this pipeline.
#    
#################################################################

with DAG(
    default_args=default_args,
    dag_id=MAIN_DAG_NAME,
    description="Pipeline for Gourmet Food Procurement Data",
    start_date=datetime(2023, 12, 1),
    schedule_interval='@once', 
    tags=[
        "Gourmet Food Procurement", 
        "Gourmet", 
        "Food", 
        "Procurement"
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
            "orig_table_name": "gourmet_food_procurement"
        }
    )

    ############################################################
    #
    #  Operators to preprocess data.
    #   
    ############################################################
    
    #################################################
    #
    #  Remove columns from the table:
    #       - Product_Type
    #       - Product_Name
    #
    #################################################
    
    cols_to_remove = [
        "Product_Type",
        "Product_Name"
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
    #       - Total_Weight_in_lbs
    #       - Num_Of_Units
    #
    #################################################
    
    cols_with_outliers = [
        "total_weight_in_lbs",
        "num_of_units"
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
    #  Remove samples that have values that do 
    #  not make sense (i.e.- negative values) in 
    #  the following column(s):
    #       - Total_Weight_in_lbs
    #       - Num_of_Units
    #
    #################################################
    
    remove_negative_values_cols = [
        "Total_Weight_in_lbs",
        "Num_of_Units"
    ]
    
    remove_negative_values = SubDagOperator(
        task_id="remove_samples_with_neg_vals",
        subdag=rswnv.sub_dag_remove_samples_with_neg_values(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=remove_negative_values_cols,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="remove_samples_with_neg_vals",
            postgres_conn_name=POSTGRES_CONN_NAME,
            args=default_args
            )
    )
    
    #################################################
    #
    #  Impute missing values with an Iterative 
    #  Imputer.
    #
    #################################################
    
    cols_to_impute = [
        "Total_Cost"
    ]
    impute_missing_values = SubDagOperator(
        task_id="impute_missing_values",
        subdag=imputer.sub_dag_impute_with_median(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=cols_to_impute,
            parent_dag_name=MAIN_DAG_NAME, 
            child_dag_name="impute_missing_values",
            postgres_conn_name=POSTGRES_CONN_NAME,
            args=default_args
            ),
        )
    
    #################################################
    #
    #  Remove samples that have nulls in any of 
    #  the following columns:
    #       - Total_Weight_in_lbs
    #       - Num_Of_Units
    #       - Vendor
    #       - Distributor
    #       - OriginDetail
    #
    #################################################
    
    cols_with_nulls = [
        "Total_Weight_in_lbs",
        "Num_Of_Units",
        "Vendor",
        "Distributor",
        "OriginDetail"
        ]
    
    remove_samples_with_nulls = SubDagOperator(
        task_id="remove_samples_with_nulls",
        subdag=rswn.sub_dag_remove_samples_with_nulls(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=cols_with_nulls,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="remove_samples_with_nulls",
            postgres_conn_name=POSTGRES_CONN_NAME,
            args=default_args
            ),
    )
    
    #################################################
    #
    #  Convert each of the following columns into 
    #  dimension tables to convert database to
    #  star schema:
    #       - Vendor
    #       - Distributor
    #       - Food_Product_Category
    #       - Food_Product_Group
    #       - TimePeriod
    #       - Agency
    #
    #################################################
    
    
    dim_tables_to_create = [
        {
            "col_name": "Vendor",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Distributor",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Food_Product_Category",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Food_Product_Group",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "TimePeriod",
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
        >> impute_missing_values
        >> add_id_column
        >> remove_outliers_1_5_iqr
        >> remove_id_column
        >> remove_negative_values
        >> remove_samples_with_nulls
        >> create_dim_tables
        >> insert_fk_into_fact_table
        >> remove_replaced_dim_cols
    )
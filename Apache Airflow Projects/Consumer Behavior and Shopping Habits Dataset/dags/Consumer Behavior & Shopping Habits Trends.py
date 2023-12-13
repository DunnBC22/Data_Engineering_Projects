"""
###################################################################
#
# Project Name: Consumer Behavior & Shopping Habits Trends Project.
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
#  Description: This DAG creates a copy of PostgreSQL table. 
#  Afterwards, it cleans the data. Next, I convert the data 
#  to star schema and run some basic metrics about the data. 
#  If everything completes successfully, I send an email to 
#  notify myself of such.
#
###################################################################
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


import remove_outliers_1_5_iqr as iqr
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

MAIN_DAG_NAME = "consumer_behavior_and_shopping_habits_trends-v01"

MAIN_PIPELINE_TABLE = "consumer_behavior_shop_habits_trends"

POSTGRES_CONN_NAME = "postgres_conn"


#################################################################
#
#  Create DAG for this pipeline.
#    
#################################################################


with DAG(
    default_args=default_args,
    dag_id=MAIN_DAG_NAME,
    description="Pipeline for Consumer Behavior and Shopping Habits Trends",
    start_date=datetime(2023, 11, 9),
    schedule_interval='@once', 
    tags=[
        "consumer", 
        "behavior", 
        "shopping", 
        "habits", 
        "trends"
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
            "orig_table_name": "consumer_behavior"
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
    #       - customerid
    #
    #################################################
    
    
    remove_unnecessary_columns = SubDagOperator(
        task_id="remove_unnecessary_columns",
        subdag=rmc.sub_dag_remove_multiple_columns(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=[
                "CustomerID"
                ],
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
    #  Remove outliers using the 1.5 * IQR rule 
    #  for the following columns:
    #       - ReviewRating
    #       - PurchaseAmount
    #       - Age
    #
    #################################################
    
    cols_to_include = [
        "ReviewRating",
        "PurchaseAmount", 
        "Age"]

    remove_outliers = SubDagOperator(
        task_id="remove_outliers",
        subdag=iqr.sub_dag_remove_outliers_1_5_iqr(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=cols_to_include,
            id_column_name="id_col",
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="remove_outliers",
            postgres_conn_name=POSTGRES_CONN_NAME,
            args=default_args
        )
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
    #  No samples have any nulls.
    #
    #################################################
    
    
    #################################################
    #
    #  Convert each of the following columns into 
    #  dimension tables to convert database to
    #  star schema:
    #       - FrequencyOfPurchases
    #       - PaymentMethod
    #       - PromoCodeUsed
    #       - DiscountApplied
    #       - ShippingType
    #       - SubscriptionStatus
    #       - Season
    #       - Color
    #       - ItemSize
    #       - PurchaseLocation
    #       - Category
    #       - ItemPurchased
    #       - Gender
    #
    #################################################
    
    
    dim_tables_to_create = [
        {
            "col_name": "FrequencyofPurchases",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "PaymentMethod",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Promo_Code_Used",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "DiscountApplied",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "ShippingType",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "SubscriptionStatus",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Season",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Color",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "ItemSize",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "PurchaseLocation",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Category",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "ItemPurchased",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Gender",
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
        table["col_name"] 
        for table in dim_tables_to_create
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
        >> remove_unnecessary_columns
        >> add_id_column
        >> remove_outliers
        >> remove_id_column
        >> create_dim_tables
        >> insert_fk_into_fact_table
        >> remove_replaced_dim_cols
    )
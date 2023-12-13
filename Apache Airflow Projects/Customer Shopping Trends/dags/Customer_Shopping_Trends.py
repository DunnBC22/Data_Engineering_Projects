"""
#################################################################
#
# Project Name: Customer Shopping Trends Project
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

MAIN_DAG_NAME = "Customer_Shopping_Trends-v01"

MAIN_PIPELINE_TABLE = "cust_shop_trends_pipe"

POSTGRES_CONN_NAME = "postgres_conn"


#################################################################
#
#  Create DAG for this pipeline.
#    
#################################################################


with DAG(
    default_args=default_args,
    dag_id=MAIN_DAG_NAME,
    description="Pipeline for Customer Shopping Trends",
    start_date=datetime(2023, 10, 9),
    schedule_interval='@once', 
    tags=[
        "Customer", 
        "Shopping", 
        "Trends"
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
            "orig_table_name": "customer_shopping_trends"
        }
    )

    
    ############################################################
    #
    #  Operators to preprocess data.
    #   
    #  Note(s):
    #       - None of the continuous numerical fields have
    #         outliers about which to worry.
    #       - There are no missing values in the entire table.
    # 
    ############################################################
    
    #################################################
    #
    #  Remove columns from complaints table:
    #       - CustomerID
    #
    #################################################
    
    
    remove_unnecessary_columns = SubDagOperator(
        task_id="remove_unnecessary_columns",
        subdag=rmc.sub_dag_remove_multiple_columns(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=["CustomerID"],
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
    #       - Frequency of Purchases
    #       - Preferred Payment Method
    #       - Promo Code Used
    #       - Discount Applied
    #       - Shipping Type
    #       - Payment Method
    #       - Subscription Status
    #       - Season
    #       - Color
    #       - Size
    #       - Location
    #       - Category
    #       - Item Purchased
    #       - Gender
    #
    #################################################
    
    
    dim_tables_to_create = [
        {
            "col_name": "FrequencyOfPurchases",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "PreferredPaymentMethod",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "PromoCodeUsed",
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
            "col_name": "PaymentMethod",
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
            "col_name": "Size",
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
        >> create_dim_tables
        >> insert_fk_into_fact_table
        >> remove_replaced_dim_cols
    )
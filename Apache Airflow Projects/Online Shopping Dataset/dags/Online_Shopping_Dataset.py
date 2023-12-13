"""
#################################################################
#
# Project Name: Online Shopping Dataset Project.
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
import sub_dag_remove_samples_with_nulls_in_cols as rswn
import create_star_schema_part_1 as css1
import create_star_schema_part_2 as css2
import clean_up_after_star_schema_creation as cuassc
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

MAIN_DAG_NAME = "Online_Shopping_Dataset-v01"

MAIN_PIPELINE_TABLE = "online_shopping_dataset_pipe"

POSTGRES_CONN_NAME = "postgres_conn"


#################################################################
#
#  Create DAG for this pipeline.
#    
#################################################################


with DAG(
    default_args=default_args,
    dag_id=MAIN_DAG_NAME,
    description="Pipeline for Online Shopping Dataset",
    start_date=datetime(2023, 12, 1),
    catchup=False,
    schedule_interval='@once', 
    tags=[
        "Online", 
        "Shopping", 
        "Online Shopping"
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
            "orig_table_name": "online_shopping"
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
    #       - record_id
    #       - Transaction_ID
    #
    #################################################
    
    cols_to_remove = [
        "record_id",
        "Transaction_ID"
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
    #       - Avg_Price
    #       - Delivery_Charges
    #       - Quantity
    #
    #################################################
    
    cols_with_outliers = [
        "avg_price",
        "delivery_charges",
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
    #  Remove samples that have nulls in any of 
    #  the following columns:
    #   - Discount_pct
    #   - Coupon_Code
    #   - Online_Spend
    #   - Offline_Spend
    #   - GST
    #   - Coupon_Status
    #   - Delivery_Charges
    #   - Avg_Price
    #   - Quantity
    #   - Product_Category
    #   - Product_Description
    #   - Product_SKU
    #   - Tenure_Months
    #   - Customer_Location
    #   - Gender
    #   - CustomerID
    #
    #################################################
    
    
    samples_with_nulls = [
        "Discount_pct",
        "Coupon_Code",
        "Online_Spend",
        "Offline_Spend",
        "GST",
        "Coupon_Status",
        "Delivery_Charges",
        "Avg_Price",
        "Quantity",
        "Product_Category",
        "Product_Description",
        "Product_SKU",
        "Tenure_Months",
        "Customer_Location",
        "Gender",
        "CustomerID"
        ]
    
    remove_samples_with_nulls = SubDagOperator(
        task_id="remove_samples_with_nulls",
        subdag=rswn.sub_dag_remove_samples_with_nulls(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=samples_with_nulls,
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
    #       - Gender
    #       - Customer_Location
    #       - Product_SKU
    #       - Product_Description
    #       - Product_Category
    #       - Coupon_Status
    #       - Coupon_Code
    #       - Discount_pct
    #
    #################################################
    
    
    dim_tables_to_create = [
        {
            "col_name": "Gender",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Customer_Location",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Product_SKU",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Product_Description",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Product_Category",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Coupon_Status",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Coupon_Code",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Discount_pct",
            "data_type": "FLOAT"
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
        >> Label("Transform Data")
        >> remove_unnecessary_columns
        >> add_id_column
        >> remove_outliers_1_5_iqr
        >> remove_id_column
        >> remove_samples_with_nulls
        >> Label("Convert to Star Schema")
        >> create_dim_tables
        >> insert_fk_into_fact_table
        >> remove_replaced_dim_cols
    )
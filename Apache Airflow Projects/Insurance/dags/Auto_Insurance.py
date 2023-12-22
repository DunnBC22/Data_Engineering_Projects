"""
#################################################################
#
# Project Name: Automotive Insurance Project
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

import create_star_schema_part_1 as css1
import create_star_schema_part_2 as css2
import clean_up_after_star_schema_creation as cuassc
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

MAIN_DAG_NAME = "Auto_Insurance-v01"
MAIN_PIPELINE_TABLE = "auto_insurance_pipe"
POSTGRES_CONNECTION_STRING = "postgres_conn"

#################################################################
#
#  Create DAG for this pipeline.
#    
#################################################################

with DAG(
    default_args=default_args,
    dag_id=MAIN_DAG_NAME,
    description="Automotive Insurance Pipeline",
    start_date=datetime(2023, 12, 1),
    schedule_interval='@once', 
    catchup=False,
    tags=[
        "Automotive", 
        "Insurance"
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
            "new_table_name": MAIN_PIPELINE_TABLE,
            "orig_table_name": "auto_insurance"
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
    #       - Customer
    #
    #################################################
    
    cols_to_remove = [
        "Customer"
        ]
    
    remove_unnecessary_columns = SubDagOperator(
        task_id="remove_unnecessary_columns",
        subdag=rmc.sub_dag_remove_multiple_columns(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=cols_to_remove,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="remove_unnecessary_columns",
            postgres_conn_name=POSTGRES_CONNECTION_STRING,
            args=default_args
            ),
    )
    
    #################################################
    #
    #  There are no missing values in this table.
    #
    #################################################
    
    #################################################
    #
    #  Generate date parts with the 
    #  'Effective_To_Date' column.
    #
    #################################################
    
    gen_date_parts = PostgresOperator(
        task_id="generate_date_parts",
        postgres_conn_id=POSTGRES_CONNECTION_STRING,
        sql="/sql/generate_month_dom_year.sql",
        params={
            "table_name": MAIN_PIPELINE_TABLE,
            "col_name": "Effective_To_Date",
            "month_col_name": f"Month_of_Effective_To_Date",
            "year_col_name": f"Year_of_Effective_To_Date",
            "dom_col_name": f"D_o_M_of_Effective_To_Date"
        }
    )
    
    #################################################
    #
    #  Remove samples with outliers (using the 
    #  a common sense limit) for the following 
    #  columns:
    #       - Customer Lifetime Value
    #       - Total Claim Amount
    #       - Monthly Premium Auto
    #
    #################################################
    
    # Remove outliers in Customer_Lifetime_Value column 
    # that are more than 35,000
    remove_cust_lifetime_val_outliers = PostgresOperator(
        task_id="remove_cust_lifetime_val_outliers",
        postgres_conn_id=POSTGRES_CONNECTION_STRING,
        sql="/sql/common_sense_remove_outliers.sql",
        params={
            "table_name": MAIN_PIPELINE_TABLE, 
            "col_name": "Customer_Lifetime_Value", 
            "bool_value_gt": 35000
            }
    )
    
    # Remove outliers in Total_Claim_Amount
    # that are more than 1,450
    remove_total_claim_amt_outliers = PostgresOperator(
        task_id="remove_total_claim_amt_outliers",
        postgres_conn_id=POSTGRES_CONNECTION_STRING,
        sql="/sql/common_sense_remove_outliers.sql",
        params={
            "table_name": MAIN_PIPELINE_TABLE, 
            "col_name": "Total_Claim_Amount", 
            "bool_value_gt": 1450
        }
    )
    
    # Remove outliers in Monthly_Premium_Auto
    # that are more than 230
    remove_monthly_auto_prem_outliers = PostgresOperator(
        task_id="remove_monthly_auto_prem_outliers",
        postgres_conn_id=POSTGRES_CONNECTION_STRING,
        sql="/sql/common_sense_remove_outliers.sql",
        params={
            "table_name": MAIN_PIPELINE_TABLE, 
            "col_name": "Monthly_Premium_Auto", 
            "bool_value_gt": 230
        }
    )    
    
    #################################################
    #
    #  Convert each of the following columns into 
    #  dimension tables to convert database to
    #  star schema:
    #       - Vehicle_Size
    #       - Vehicle_Class
    #       - Sales_Channel
    #       - Renew_Offer_type
    #       - Policy_Name
    #       - Policy_Type
    #       - Marital_Status
    #       - Location_Code
    #       - Gender
    #       - EmploymentStatus
    #       - Education
    #       - Coverage
    #       - Customer_State
    #
    #################################################
    
    dim_tables_to_create = [
        {
            "col_name": "Vehicle_Size",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Vehicle_Class",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Sales_Channel",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Renew_Offer_type",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Policy_Name",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Policy_Type",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Marital_Status",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Location_Code",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Gender",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "EmploymentStatus",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Education",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Coverage",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Customer_State",
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
            postgres_conn_name=POSTGRES_CONNECTION_STRING,
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
            table_name=MAIN_PIPELINE_TABLE,
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
        >> remove_unnecessary_columns
        >> gen_date_parts
        >> remove_cust_lifetime_val_outliers
        >> remove_total_claim_amt_outliers
        >> remove_monthly_auto_prem_outliers
        >> create_dim_tables
        >> insert_fk_into_fact_table
        >> remove_replaced_dim_cols
    )
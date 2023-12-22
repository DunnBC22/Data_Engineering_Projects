"""
#################################################################
#
# Project Name: Insurance Fraud Project
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

import remove_outliers_1_5_iqr as iqr
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

MAIN_DAG_NAME = "Insurance_Fraud-v01"
MAIN_PIPELINE_TABLE = "insurance_fraud_pipeline"
POSTGRES_CONNECTION_STRING = "postgres_conn"

#################################################################
#
#  Create DAG for this pipeline
#    
#################################################################

with DAG(
    default_args=default_args,
    dag_id=MAIN_DAG_NAME,
    description="Insurance Fraud Pipeline",
    start_date=datetime(2023, 12, 1),
    schedule_interval='@once', 
    tags=[
        "insurance",
        "fraud"
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
            "orig_table_name": "insurance_fraud"
        }
    )

    ############################################################
    #
    #  Operators to preprocess data.
    # 
    #  Note(s):
    #       - There are no missing values in this table.
    #   
    ############################################################
    
    #################################################
    #
    #  Remove these columns from table:
    #       - PolicyNumber
    #
    #################################################
    
    cols_to_remove = [
        "PolicyNumber"
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
            "table_name": MAIN_PIPELINE_TABLE,
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
            table_name=MAIN_PIPELINE_TABLE,
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
            "table_name": MAIN_PIPELINE_TABLE,
            "id_col_name": "id_col"
        }
    )
    
    #################################################
    #
    #  Convert each of the following columns into 
    #  dimension tables to convert database to
    #  star schema:
    #       - BasePolicy
    #       - Year_accident
    #       - NumberOfCars
    #       - AddressChange_Claim
    #       - NumberOfSuppliments
    #       - AgentType
    #       - WitnessPresent
    #       - PoliceReportFiled
    #       - AgeOfPolicyHolder
    #       - AgeOfVehicle
    #       - PastNumberOfClaims
    #       - Days_Policy_Claim
    #       - Days_Policy_Accident
    #       - Deductible
    #       - VehiclePrice
    #       - VehicleCategory
    #       - PolicyType
    #       - Fault
    #       - MaritalStatus
    #       - Sex
    #       - MonthClaimed
    #       - DayOfWeekClaimed
    #       - AccidentArea
    #       - Make
    #       - DayOfWeek
    #       - Month_accident
    #
    #################################################
    
    dim_tables_to_create = [
        {
            "col_name": "BasePolicy",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Year_accident",
            "data_type": "INTEGER"
        },
        {
            "col_name": "NumberOfCars",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "AddressChange_Claim",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "NumberOfSuppliments",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "AgentType",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "WitnessPresent",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "PoliceReportFiled",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "AgeOfPolicyHolder",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "AgeOfVehicle",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "PastNumberOfClaims",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Days_Policy_Claim",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Days_Policy_Accident",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Deductible",
            "data_type": "INTEGER"
        },
        {
            "col_name": "VehiclePrice",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "VehicleCategory",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "PolicyType",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Fault",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "MaritalStatus",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Sex",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "MonthClaimed",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "DayOfWeekClaimed",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "AccidentArea",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Make",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "DayOfWeek",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Month_accident",
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
        >> add_id_column
        >> remove_outliers_1_5_iqr
        >> remove_id_column
        >> create_dim_tables
        >> insert_fk_into_fact_table
        >> remove_replaced_dim_cols
    )
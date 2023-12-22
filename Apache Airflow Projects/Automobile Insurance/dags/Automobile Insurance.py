"""
#################################################################
#
# Project Name: Automobile Insurance Project
#
#####
#
# Author: Brian Dunn
#
#####
#
# Approx. Date of Completion: 12-5-2023
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

#################################################################
#
#  Import sub-DAGs that were defined in separate files.
#    
#################################################################


import create_star_schema_part_1 as css1
import create_star_schema_part_2 as css2
import clean_up_after_star_schema_creation as cuassc
import sub_dag_remove_multiple_columns as rmc
import sub_dag_generate_month_dom_year as gen_dmy


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

MAIN_DAG_NAME = "Automobile_Insurance-v01"

PIPELINE_TABLE_NAME = "automobile_insurance"

POSTGRES_CONNECTION_STRING = "postgres_conn"


#################################################################
#
#  Create DAG for this pipeline.
#    
#################################################################

with DAG(
    default_args=default_args,
    dag_id=MAIN_DAG_NAME,
    description="Automobile Insurance Pipeline",
    start_date=datetime(2023, 12, 1),
    schedule_interval='@once', 
    catchup=False,
    tags=[
        "Automobile", 
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
            "new_table_name": PIPELINE_TABLE_NAME,
            "orig_table_name": "insur_claims"
        }
    )

    
    ############################################################
    #
    #  Operators to preprocess data.
    # 
    #  Note(s):
    #       - There are no missing values in the dataset.
    #   
    ############################################################
    
    #################################################
    #
    #  Remove the following columns:
    #       - incident_location
    #       - policy_number
    #       - insured_zip
    #
    #################################################
    
    cols_to_remove = [
        "incident_location",
        "policy_number",
        "insured_zip"
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
            )
    )
    
    #################################################
    #
    #  Generate Date parts for the following columns:
    #       - incident_date
    #       - policy_bind_date
    #
    #################################################
    
    date_cols = [
        "incident_date",
        "policy_bind_date"
    ]
    
    generate_date_parts = SubDagOperator(
        task_id=f"generate_date_parts",
        subdag=gen_dmy.sub_dag_generate_month_dom_year_of_date(
            table_name=PIPELINE_TABLE_NAME,
            column_names=date_cols,
            parent_dag_name=MAIN_DAG_NAME, 
            postgres_conn_name=POSTGRES_CONNECTION_STRING,
            child_dag_name="generate_date_parts",
            args=default_args
            ),
        )
    
    #################################################
    #
    #  Convert each of the following columns into 
    #  dimension tables to convert database to
    #  star schema:
    #       - policy_state
    #       - policy_csl
    #       - policy_deductable
    #       - insured_sex
    #       - insured_education_level
    #       - insured_occupation
    #       - insured_hobbies
    #       - insured_relationship
    #       - incident_type
    #       - collision_type
    #       - incident_severity
    #       - authorities_contacted
    #       - incident_state
    #       - incident_city
    #       - property_damage
    #       - police_report_available
    #       - auto_make
    #       - auto_model
    #       - auto_year
    #       - fraud_reported
    #
    #################################################
    
    dim_tables_to_create = [
        {
            "col_name": "policy_state",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "policy_csl",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "policy_deductable",
            "data_type": "INTEGER"
        },
        {
            "col_name": "insured_sex",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "insured_education_level",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "insured_occupation",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "insured_hobbies",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "insured_relationship",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "incident_type",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "collision_type",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "incident_severity",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "authorities_contacted",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "incident_state",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "incident_city",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "property_damage",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "police_report_available",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "auto_make",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "auto_model",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "auto_year",
            "data_type": "INTEGER"
        },
        {
            "col_name": "fraud_reported",
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
        >> remove_unnecessary_columns
        >> generate_date_parts
        >> create_dim_tables
        >> insert_fk_into_fact_table
        >> remove_replaced_dim_cols
    )
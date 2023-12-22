"""
#################################################################
#
# Project Name: Hospital Insurance Claim Fraud Project
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
import sub_dag_remove_samples_with_nulls_in_cols as rswc
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

MAIN_DAG_NAME = "hosp_insur_claim_fraud-v01"
MAIN_PIPELINE_TABLE = "hosp_insur_claim_fraud_pipeline"
POSTGRES_CONNECTION_STRING = "postgres_conn"

#################################################################
#
#  Create DAG for this pipeline.
#    
#################################################################

with DAG(
    default_args=default_args,
    dag_id=MAIN_DAG_NAME,
    description="Hospital Insurance Claim Fraud Pipeline",
    start_date=datetime(2023, 12, 1),
    schedule_interval='@once', 
    tags=[
        "hospital", 
        "insurance", 
        "claim", 
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
            "orig_table_name": "hosp_insur_claim_fraud"
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
    #       - Hospital_Id
    #
    #################################################
    
    cols_to_remove = [
        "Hospital_Id"
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
    #  Remove samples that include null values 
    #  in any of the following columns: 
    #       - Mortality_risk
    #       - Days_spend_hsptl
    #       - Hospital_County
    #       - Area_Service
    #
    #################################################
    
    cols_with_null_sample_values = [
        "Mortality_risk",
        "Days_spend_hsptl",
        "Hospital_County",
        "Area_Service"
        ]
    
    remove_samples_w_nulls = SubDagOperator(
        task_id="remove_samples_with_nulls",
        subdag=rswc.sub_dag_remove_samples_with_nulls(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=cols_with_null_sample_values,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="remove_samples_with_nulls",
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
    #       - ratio_of_total_costs_to_total_charges
    #       - Tot_cost
    #       - Tot_charg
    #       - Weight_baby
    #       - Days_spend_hsptl
    #
    #################################################
    
    cols_with_outliers = [
        "ratio_of_total_costs_to_total_charges",
        "tot_cost",
        "tot_charg",
        "weight_baby",
        "days_spend_hsptl"
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
    #       - area_Service
    #       - hospital_County
    #       - age
    #       - gender
    #       - cultural_group
    #       - ethnicity
    #       - admission_type
    #       - home_or_self_care
    #       - apr_drg_description
    #       - surg_Description
    #       - abortion
    #       - emergency_dept_yes_no
    #
    #################################################
    
    dim_tables_to_create = [
        {
            "col_name": "area_Service",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "hospital_County",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "age",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Gender",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "cultural_Group",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "ethnicity",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "admission_type",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "home_or_self_care",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "apr_drg_description",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "surg_Description",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "abortion",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "emergency_dept_yes_no",
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
        >> remove_samples_w_nulls
        >> add_id_column
        >> remove_outliers_1_5_iqr
        >> remove_id_column
        >> create_dim_tables
        >> insert_fk_into_fact_table
        >> remove_replaced_dim_cols
    )
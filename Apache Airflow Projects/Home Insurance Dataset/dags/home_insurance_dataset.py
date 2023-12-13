"""
#################################################################
#
# Project Name: Home Insurance Dataset Project
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


import remove_outliers_1_5_iqr as iqr
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

MAIN_DAG_NAME = "home_insurance_ds-v01"

MAIN_PIPELINE_TABLE = "home_insurance_ds_pipeline"

POSTGRES_CONNECTION_STRING = "postgres_conn"


#################################################################
#
#  Create DAG for this pipeline.
#    
#################################################################

with DAG(
    default_args=default_args,
    dag_id=MAIN_DAG_NAME,
    description="Home Insurance Dataset Pipeline",
    start_date=datetime(2023, 12, 1),
    schedule_interval='@once', 
    catchup=False,
    tags=[
        "home", 
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
            "new_table_name": MAIN_PIPELINE_TABLE,
            "orig_table_name": "home_insurance_ds"
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
    #       - id
    #       - Police
    #
    #################################################
    
    
    cols_to_remove = [
        "id",
        "Police"
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
    #  There are no missing values in this dataset.
    #
    #################################################
    
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
    #       - LAST_ANN_PREM_GROSS
    #       - MAX_DAYS_UNOCC
    #
    #################################################
    
    cols_with_outliers = [
        "last_ann_prem_gross",
        "max_days_unocc"
    ] # inputs values can only be lowercase letters & underscores
    
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
    #  Generate the date parts (month, year, day of 
    #  month) for the following columns:
    #       - COVER_START
    #       - P1_DOB
    #
    #################################################
    
    date_columns = [
        "COVER_START",
        "P1_DOB"
    ]
    
    generate_date_parts = SubDagOperator(
        task_id=f"generate_date_parts",
        subdag=gen_dmy.sub_dag_generate_month_dom_year_of_date(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=date_columns,
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
    #       - CLAIM3YEARS
    #       - P1_EMP_STATUS
    #       - BUS_USE
    #       - AD_BUILDINGS
    #       - AD_CONTENTS
    #       - CONTENTS_COVER
    #       - BUILDINGS_COVER
    #       - P1_MAR_STATUS
    #       - P1_POLICY_REFUSED
    #       - P1_SEX
    #       - APPR_ALARM
    #       - APPR_LOCKS
    #       - FLOODING
    #       - NEIGH_WATCH
    #       - OCC_STATUS
    #       - SAFE_INSTALLED
    #       - SEC_DISC_REQ  
    #       - SUBSIDENCE
    #       - YEARBUILT
    #       - PAYMENT_METHOD
    #       - LEGAL_ADDON_PRE_REN
    #       - LEGAL_ADDON_POST_REN
    #       - HOME_EM_ADDON_PRE_REN
    #       - HOME_EM_ADDON_POST_REN
    #       - GARDEN_ADDON_PRE_REN
    #       - GARDEN_ADDON_POST_REN
    #       - KEYCARE_ADDON_PRE_REN
    #       - KEYCARE_ADDON_POST_REN
    #       - HP1_ADDON_PRE_REN
    #       - HP1_ADDON_POST_REN
    #       - HP2_ADDON_PRE_REN
    #       - HP2_ADDON_POST_REN
    #       - HP3_ADDON_PRE_REN
    #       - HP3_ADDON_POST_REN
    #       - MTA_FLAG
    #       - POL_STATUS
    #
    #################################################
    
    
    dim_tables_to_create = [
        {
            "col_name": "CLAIM3YEARS",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "P1_EMP_STATUS",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "BUS_USE",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "AD_BUILDINGS",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "AD_CONTENTS",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "CONTENTS_COVER",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "BUILDINGS_COVER",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "P1_MAR_STATUS",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "P1_POLICY_REFUSED",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "P1_SEX",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "APPR_ALARM",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "APPR_LOCKS",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "FLOODING",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "NEIGH_WATCH",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "OCC_STATUS",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "SAFE_INSTALLED",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "SEC_DISC_REQ",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "SUBSIDENCE",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "YEARBUILT",
            "data_type": "INTEGER"
        },
        {
            "col_name": "PAYMENT_METHOD",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "LEGAL_ADDON_PRE_REN",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "LEGAL_ADDON_POST_REN",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "HOME_EM_ADDON_PRE_REN",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "HOME_EM_ADDON_POST_REN",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "GARDEN_ADDON_PRE_REN",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "GARDEN_ADDON_POST_REN",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "KEYCARE_ADDON_PRE_REN",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "KEYCARE_ADDON_POST_REN",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "HP1_ADDON_PRE_REN",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "HP1_ADDON_POST_REN",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "HP2_ADDON_PRE_REN",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "HP2_ADDON_POST_REN",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "HP3_ADDON_PRE_REN",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "HP3_ADDON_POST_REN",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "MTA_FLAG",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "POL_STATUS",
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
            column_names=dim_cols_to_remove,
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
        >> add_id_column
        >> remove_outliers_1_5_iqr
        >> remove_id_column
        >> generate_date_parts
        >> Label("Convert to Star Schema")
        >> create_dim_tables
        >> insert_fk_into_fact_table
        >> remove_replaced_dim_cols
    )
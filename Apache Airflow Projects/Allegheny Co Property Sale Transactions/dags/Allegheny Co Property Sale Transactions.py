"""
#################################################################
#
# Project Name: Allegheny Co Property Sale Transactions Project
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


import sub_dag_generate_month_dom_year as gen_dmy
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

MAIN_DAG_NAME = "Allegheny_Co_Property_Sale_Transactions-v01"

PIPELINE_TABLE_NAME = "allegheny_co_property_sale_transactions"

POSTGRES_CONNECTION_STRING = "postgres_conn"


#################################################################
#
#  Create DAG for this pipeline.
#
#################################################################


with DAG(
    default_args=default_args,
    dag_id=MAIN_DAG_NAME,
    description="Allegheny Co Property Sale Transactions Pipeline",
    start_date=datetime(2023, 12, 1),
    schedule_interval='@once', 
    tags=[
        "Allegheny", 
        "County", 
        "property_sales"
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
            "orig_table_name": "allegheny"
        }
    )

    
    ############################################################
    #
    #  Operators to preprocess data.
    # 
    #  Note(s):
    #       - There are no outliers for which to worry as 
    #         most columns are discrete/categorical.
    # 
    #   
    ############################################################
    
    
    #################################################
    #
    #  Remove these columns from table:
    #       - PARID
    #       - PROPERTYHOUSENUM
    #       - PROPERTYADDRESSDIR
    #       - PROPERTYADDRESSSTREET
    #       - PROPERTYADDRESSUNITDESC
    #       - PROPERTYUNITNO
    #       - PROPERTYSTATE
    #       - INSTRTYPDESC
    #
    #################################################
    
    cols_to_remove = [
        "PARID",
        "PROPERTYHOUSENUM",
        "PROPERTYADDRESSDIR",
        "PROPERTYADDRESSSTREET",
        "PROPERTYADDRESSUNITDESC",
        "PROPERTYUNITNO",
        "PROPERTYSTATE",
        "INSTRTYPDESC"
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
    #  Remove samples that include null values in 
    #  any of the following columns: 
    #       - DEEDPAGE
    #       - DEEDBOOK
    #       - PRICE
    #       - RECORDDATE
    #       - PROPERTYZIP
    #       - PROPERTYCITY
    #       - PROPERTYADDRESSSUF
    #
    #################################################
    
    
    cols_with_null_sample_values = [
        "DEEDPAGE",
        "DEEDBOOK",
        "PRICE",
        "RECORDDATE",
        "PROPERTYZIP",
        "PROPERTYCITY",
        "PROPERTYADDRESSSUF"
    ]
    
    remove_samples_w_nulls = SubDagOperator(
        task_id="remove_samples_with_nulls",
        subdag=rswc.sub_dag_remove_samples_with_nulls(
            table_name=PIPELINE_TABLE_NAME,
            column_names=cols_with_null_sample_values,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="remove_samples_with_nulls",
            postgres_conn_name=POSTGRES_CONNECTION_STRING,
            args=default_args
            ),
        )
    
    
    #################################################
    #
    #  Remove samples where the RECORDDATE is 
    #  an invalid date.
    #
    #################################################
    
    
    remove_samples_w_invalid_dates = PostgresOperator(
        task_id="remove_samples_w_invalid_dates",
        sql="/sql/remove_samples_w_invalid_date.sql",
        params={
            "table_name": PIPELINE_TABLE_NAME,
            "column_name": "RECORDDATE"
            },
        postgres_conn_id=POSTGRES_CONNECTION_STRING
    )
    
    
    #################################################
    #
    #  Generate date parts for the following columns:
    #       - SALEDATE
    #       - RECORDDATE
    #
    #################################################
    
    
    date_columns = [
        "SALEDATE",
        "RECORDDATE"
    ]
    
    generate_date_parts = SubDagOperator(
        task_id="generate_date_parts",
        subdag=gen_dmy.sub_dag_generate_month_dom_year_of_date(
            table_name=PIPELINE_TABLE_NAME,
            column_names=date_columns,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="generate_date_parts",
            postgres_conn_name=POSTGRES_CONNECTION_STRING,
            args=default_args
            )
    )
    
    
    #################################################
    #
    #  Convert each of the following columns into 
    #  dimension tables to convert database to
    #  star schema:
    #       - INSTRTYP
    #       - SALEDESC
    #       - DEEDBOOK
    #       - DEEDPAGE
    #       - MUNIDESC
    #       - MUNICODE
    #       - SCHOOLDESC
    #       - PROPERTYZIP
    #       - PROPERTYCITY
    #       - PROPERTYADDRESSSUF
    #       - PROPERTYFRACTION
    #
    #################################################
    
    
    dim_tables_to_create = [
        {
            "col_name": "INSTRTYP",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "SALEDESC",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "DEEDBOOK",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "DEEDPAGE",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "MUNIDESC",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "MUNICODE",
            "data_type": "INTEGER"
        },
        {
            "col_name": "SCHOOLDESC",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "PROPERTYZIP",
            "data_type": "INTEGER"
        },
        {
            "col_name": "PROPERTYCITY",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "PROPERTYADDRESSSUF",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "PROPERTYFRACTION",
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
        >> remove_samples_w_nulls
        >> remove_samples_w_invalid_dates
        >> generate_date_parts
        >> Label("Create Star Schema")
        >> create_dim_tables
        >> insert_fk_into_fact_table
        >> remove_replaced_dim_cols
    )
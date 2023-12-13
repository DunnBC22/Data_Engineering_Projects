"""
#################################################################
#
# Project Name: Cyclistic Summary Data Project
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
import sub_dag_generate_month_dom_year as gen_dmy
import remove_outliers_1_5_iqr as iqr


#################################################################
#
#  Define default arguments.
#    
#################################################################


default_args = {
    'owner': 'dunnbc22',
    'retries': 5,
    'retry_delay': timedelta(minutes=2),
    'depends_on_past': True
}

MAIN_DAG_NAME = "Cyclistic_Summary_Data-v01"

MAIN_PIPELINE_TABLE = "cyclistic_summary_data_pipe"

POSTGRES_CONN_NAME = "postgres_conn"


#################################################################
#
#  Create DAG for this pipeline.
#    
#################################################################


with DAG(
    default_args=default_args,
    dag_id=MAIN_DAG_NAME,
    description="Pipeline for Cyclistic Summary Data",
    start_date=datetime(2023, 12, 1),
    schedule_interval='@once', 
    catchup=False,
    tags=["All Season", "Cyclistic", "Summary"],
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
            "orig_table_name": "cyclistic_summary"
        }
    )

    
    ############################################################
    #
    #  Operators to preprocess data.
    # 
    #  Note(s):
    #       - No missing values in the entire table
    #       - No columns to remove.
    #   
    ############################################################
    
    #################################################
    #
    #  Generate date parts for the following columns:
    #       - start_day
    #       - stop_day
    #
    #################################################
    
    
    date_cols = [
        "start_day",
        "stop_day"
    ]
    
    generate_date_parts = SubDagOperator(
        task_id=f"generate_date_parts",
        subdag=gen_dmy.sub_dag_generate_month_dom_year_of_date(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=date_cols,
            parent_dag_name=MAIN_DAG_NAME, 
            child_dag_name="generate_date_parts",
            postgres_conn_name=POSTGRES_CONN_NAME,
            args=default_args
            )
        )
    
    
    #################################################
    #
    #  Calculate the number of days between the 
    #  start and stop days for each sample.
    #
    #################################################
    
    
    date_range_calc_params = {
        "table_name": MAIN_PIPELINE_TABLE,
        "start_date_col": "start_day",
        "stop_date_col": "stop_day",
        "date_range_col_name": "cyclic_days_length"
        }
    
    calculate_date_range = PostgresOperator(
        task_id=f"calculate_date_range",
        sql="/sql/calculate_date_range.sql",
        postgres_conn_id=POSTGRES_CONN_NAME,
        params=date_range_calc_params
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
    #       - day_mean_wind_speed
    #
    #################################################
    
    cols_with_outliers = [
        "day_mean_wind_speed"
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
    #  Convert each of the following columns into 
    #  dimension tables to convert database to
    #  star schema:
    #       - usertype
    #       - borough_start
    #       - neighborhood_start
    #       - borough_end
    #       - neighborhood_end
    #
    #################################################
    
    
    dim_tables_to_create = [
        {
            "col_name": "usertype",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "borough_start",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "neighborhood_start",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "borough_end",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "neighborhood_end",
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
        >> generate_date_parts
        >> calculate_date_range
        >> add_id_column
        >> remove_outliers_1_5_iqr
        >> remove_id_column
        >> create_dim_tables
        >> insert_fk_into_fact_table
        >> remove_replaced_dim_cols
    )
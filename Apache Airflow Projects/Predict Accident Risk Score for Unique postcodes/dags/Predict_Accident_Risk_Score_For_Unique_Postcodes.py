"""
#########################################################################
#
# Project Name: Predict Accident Risk Score For Unique Postcodes Project
#               Postcodes Project
#
#####
#
# Author: Brian Dunn
#
#####
#
# Approx. Date of Completion: 12-12-2023
#
#####
#
#  Description: This DAG creates a copy of PostgreSQL table 
#  Afterwards, it cleans the data. Next, I convert the data 
#  to star schema.
#
#########################################################################
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

MAIN_DAG_NAME = "pred_accident_risk_score_unique_postcodes-v01"

MAIN_PIPELINE_TABLE = "predict_accident_risk_pipe"

POSTGRES_CONNECTION_STRING = "postgres_conn"


#################################################################
#
#  Create DAG for this pipeline.
#    
#################################################################


with DAG(
    default_args=default_args,
    dag_id=MAIN_DAG_NAME,
    description="Predict Accident Risk Score For Unique Postcodes Pipeline",
    start_date=datetime(2023, 12, 1),
    catchup=False,
    schedule_interval='@once', 
    tags=[
        "Predict", 
        "Accident",
        "Risk", 
        "Score",
        "Accident_Risk_Score",
        "Postcodes"
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
            "orig_table_name": "postcode_acc_risk_pred"
        }
    )

    
    ############################################################
    #
    #  Operators to preprocess data.
    # 
    #  Note(s):
    #       - No columns need to have analysis for outliers 
    #         removed.
    #
    ############################################################
    
    #################################################
    #
    #  Remove these columns from table:
    #       - Accident_ID
    #       - Country_Name
    #       - second_Road_Number
    #
    #################################################
    
    
    cols_to_remove = [
        "Accident_ID",
        "Country_Name",
        "second_Road_Number"
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
    #  Generate date parts for the Event_Date column.
    #
    #################################################
    
    
    date_col = "Event_Date"
    
    generate_date_parts = PostgresOperator(
        task_id="generate_date_parts",
        postgres_conn_id=POSTGRES_CONNECTION_STRING,
        sql="/sql/generate_month_dom_year.sql",
        params={
            "table_name": MAIN_PIPELINE_TABLE,
            "col_name": date_col,
            "month_col_name": f"{date_col}_month",
            "year_col_name": f"{date_col}year",
            "dom_col_name": f"{date_col}_day_of_month"
        }
    )
    
    
    #################################################
    #
    #  Isolate the hour part of the Event_Time column.
    #
    #################################################
    
    
    time_col = "Event_Time"
    
    isolate_hour_from_event_time = PostgresOperator(
        task_id="isolate_hour_from_event_time",
        postgres_conn_id=POSTGRES_CONNECTION_STRING,
        sql="/sql/isolate_hour_of_day.sql",
        params={
            "table_name": MAIN_PIPELINE_TABLE,
            "col_name": time_col,
            "hour_of_day_col_name": f"{time_col}_hour_of_day"
        }
    )
    
    
    #################################################
    #
    #  Remove samples that include null values 
    #  in any of the following columns: 
    #       - Event_Time
    #       - Road_Surface_Conditions
    #       - Special_Conditions_at_Site
    #
    #################################################
    
    
    cols_with_null_sample_values = [
        "Event_Time",
        "Road_Surface_Conditions",
        "Special_Conditions_at_Site"
    ]
    
    remove_samples_w_nulls = SubDagOperator(
        task_id="remove_samples_w_nulls",
        subdag=rswc.sub_dag_remove_samples_with_nulls(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=cols_with_null_sample_values,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="remove_samples_w_nulls",
            postgres_conn_name=POSTGRES_CONNECTION_STRING,
            args=default_args
            ),
        )
    
    
    #######################################################
    #
    #  Convert each of the following columns into 
    #  dimension tables to convert database to
    #  star schema:
    #       - State_Name
    #       - Did_Police_Officer_Attend_Scene_of_Accident
    #       - Carriageway_Hazards
    #       - Special_Conditions_at_Site
    #       - Road_Surface_Conditions
    #       - Weather_Conditions
    #       - Light_Conditions
    #       - Pedestrian_Crossing_Physical_Facilities
    #       - Pedestrian_Crossing_Human_Control
    #       - Speed_limit
    #       - Road_Type
    #       - Local_Authority_District
    #       - Local_Authority_Highway
    # 
    #######################################################
    
    
    dim_tables_to_create = [
        {
            "col_name": "State_Name",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Did_Police_Officer_Attend_Scene_of_Accident",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Carriageway_Hazards",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Special_Conditions_at_Site",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Road_Surface_Conditions",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Weather_Conditions",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Light_Conditions",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Pedestrian_Crossing_Physical_Facilities",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Pedestrian_Crossing_Human_Control",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Speed_Limit",
            "data_type": "INTEGER"
        },
        {
            "col_name": "Road_Type",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Local_Authority_District",
            "data_type": "INTEGER"
        },
        {
            "col_name": "Local_Authority_Highway",
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
        >> generate_date_parts
        >> isolate_hour_from_event_time
        >> remove_samples_w_nulls
        >> Label("Convert to Star Schema")
        >> create_dim_tables
        >> insert_fk_into_fact_table
        >> remove_replaced_dim_cols
    )
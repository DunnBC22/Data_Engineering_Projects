"""
##################################################################
#
# Project Name: Transfer Flight Data From Postgres to MySQL
#
#####
#
# Author: Brian Dunn
#
#####
#
# Date of Completion: 01-28-2024
#
#####
#
#  Description: This DAG creates a copy of PostgreSQL table, make
#  any necessary updates, & then inserts it into a table in MySQL.
#
#####
#
#  Data Source: 
#  https://www.kaggle.com/datasets/robikscube/flight-delay-dataset-20182022
#
##################################################################
"""

#################################################################
#
#  Import Libraries.
#    
#################################################################

from __future__ import annotations
import os

from datetime import datetime, timedelta

from airflow import DAG

from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.mysql.operators.mysql import MySqlOperator
from airflow.operators.subdag import SubDagOperator

#################################################################
#
#  Import sub-DAGs that were defined in separate files.
#    
#################################################################

import drop_cols_w_all_nulls as dcwan
import retrieve_joined_tables as rjt
import drop_single_value_columns as dsvc
import sub_dag_remove_samples_with_nulls_in_cols as rswnic
import fill_nulls_with_fixed_value as fnwfv
import postgres_bulk_dump as pbd
import mysql_bulk_load as mbl
import remove_multiple_columns as rmc

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

MAIN_DAG_NAME = "flight_data_postgres_to_mysql"
MAIN_PIPELINE_TABLE = "flight_data_pipe"
NEW_MYSQL_TABLE_NAME = "flight_data"
MYSQL_SCHEMA_NAME = "flight_files_mysql_db"

POSTGRES_CONN_NAME = "postgres_conn"
MYSQL_CONN_NAME = "mysql_conn"

TEMP_FOLDER_PATH = "tmp_files"
TEMP_FILE_PATH = os.path.join(
    TEMP_FOLDER_PATH, 
    'pg_to_mysql_tmp_file.tsv'
    )

#################################################################
#
#  Create DAG for this pipeline.
#    
#################################################################

with DAG(
    default_args=default_args,
    dag_id=MAIN_DAG_NAME,
    description="Transfer Flight Data From Postgres Table to MySQL Table",
    start_date=datetime(2024, 1, 1),
    schedule_interval='@once', 
    catchup=False,
    tags=[
        "Flight",
        "Airport",
        "Airline",
        "PostgreSQL",
        "MySQL"
        ],
    owner_links={"airflow": "mailto:DunnBC22@gmail.com"},
    dagrun_timeout=timedelta(minutes=90),
    doc_md=__doc__
    ) as dag:
    
    ############################################################
    #
    #  Lists used in multiple operators/tasks.
    #   
    ############################################################
    
    input_names = [
        "Flights_2022_2",
        "Flights_2022_3"
    ]
    
    ############################################################
    #
    #  Operator to create pipeline table.
    #   
    ############################################################
    
    create_pipeline_table = PostgresOperator(
        task_id="create_pipeline_table",
        sql="/sql/create_table.sql",
        params= {
            "table_name": MAIN_PIPELINE_TABLE
        },
        postgres_conn_id=POSTGRES_CONN_NAME
    )
    
    ############################################################
    #
    #  Operator to grant permissions.
    #   
    ############################################################
    
    grant_perms_to_pipeline_table = PostgresOperator(
        task_id="grant_permissions_to_pipeline_table",
        sql="""
        GRANT 
            SELECT, 
            INSERT, 
            UPDATE, 
            DELETE 
        ON {{ params.table_name }} TO airflow;
        """,
        params= {
            "table_name": MAIN_PIPELINE_TABLE
        },
        postgres_conn_id=POSTGRES_CONN_NAME
    )
    
    ############################################################
    #
    #  Operator to INSERT copy of multiple tables for pipeline
    #   
    ############################################################
    
    create_joined_db_table = SubDagOperator(
        task_id="create_joined_pg_tables",
        subdag=rjt.retrieve_concatenated_pipeline_table(
            new_table_name=MAIN_PIPELINE_TABLE,
            input_table_names=input_names,
            parent_dag_name=MAIN_DAG_NAME, 
            child_dag_name="create_joined_pg_tables",
            db_conn_name=POSTGRES_CONN_NAME,
            args=default_args
            )
    )
    
    ############################################################
    #
    #  Operator to add a primary key that is auto-incremented.
    #   
    ############################################################
    
    add_primary_key = PostgresOperator(
        task_id="create_auto_incremented_primary_key",
        sql="""
        ALTER TABLE {{ params.table_name }}
        ADD COLUMN {{ params.new_column_name }} SERIAL PRIMARY KEY;
        """,
        params= {
            "table_name": MAIN_PIPELINE_TABLE, 
            "new_column_name": "flight_id"
        },
        postgres_conn_id=POSTGRES_CONN_NAME
    )

    ############################################################
    #
    #  Operators to update data.
    #
    ############################################################
    
    #################################################################
    #
    #  Drop these column(s):
    #       - FlightDate
    #       - Duplicate
    #
    #################################################################
    
    cols_2_remove = [
        "FlightDate",
        "duplicate_value"
    ]
    
    remove_unneeded_cols = SubDagOperator(
        task_id="remove_unneeded_cols",
        subdag=rmc.sub_dag_remove_multiple_columns(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=cols_2_remove,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="remove_unneeded_cols",
            postgres_conn_name=POSTGRES_CONN_NAME,
            args=default_args
        ),
    )
    
    #################################################################
    #
    #  Remove Columns if all samples are null.
    #
    #################################################################
    
    remove_cols_w_all_null_values = SubDagOperator(
        task_id="drop_cols_w_only_null_values",
        subdag=dcwan.subdag_drop_cols_of_all_nulls(
            table_name=NEW_MYSQL_TABLE_NAME,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="drop_cols_w_only_null_values",
            mysql_conn_name=MYSQL_CONN_NAME,
            args=default_args
        )
    )
    
    #################################################################
    #
    #  Remove Columns if all values in that column are the same.
    #
    #################################################################
    
    remove_single_value_cols = SubDagOperator(
        task_id='remove_single_value_cols',
        subdag=dsvc.sub_dag_remove_single_value_columns(
            table_name=NEW_MYSQL_TABLE_NAME,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="remove_single_value_cols",
            mysql_conn_name=MYSQL_CONN_NAME,
            args=default_args
        )
    )
    
    #################################################################
    #
    #  Remove samples with null values in the following columns (if 
    #  the columns have not been removed yet):
    #       - flight_year 
    #       - flight_quarter
    #       - flight_month
    #       - DayofMonth
    #       - DayOfWeek
    #       - Marketing_Airline_Network
    #       - Operated_or_Branded_Code_Share_Partners
    #       - DOT_ID_Marketing_Airline
    #       - IATA_Code_Marketing_Airline
    #       - Flight_Number_M
    #       - Operating_Airline
    #       - DOT_ID_Operating_Airline
    #       - IATA_Code_Operating_Airline
    #       - Tail_Number
    #       - Flight_Number_Operating_Airline
    #       - OriginAirportID
    #       - OriginAirportSeqID
    #       - OriginCityMarketID
    #       - Origin
    #       - OriginCityName
    #       - OriginState
    #       - OriginStateFips
    #       - OriginStateName
    #       - OriginWac
    #       - DestAirportID
    #       - DestAirportSeqID
    #       - DestCityMarketID
    #       - Dest
    #       - DestCityName
    #       - DestState
    #       - DestStateFips
    #       - DestStateName
    #       - DestWac
    #       - CRSDepTime
    #       - DepTime
    #       - DepDelay
    #       - DepDelayMinutes
    #       - DepDel15
    #       - DepartureDelayGroups
    #       - DepTimeBlk
    #       - TaxiOut
    #       - WheelsOff
    #       - WheelsOn
    #       - TaxiIn
    #       - CRSArrTime
    #       - ArrTime
    #       - ArrDelay
    #       - ArrDelayMinutes
    #       - ArrDel15
    #       - ArrivalDelayGroups
    #       - ArrTimeBlk
    #       - Cancelled
    #       - CancellationCode
    #       - Diverted
    #       - CRSElapsedTime
    #       - ActualElapsedTime
    #       - AirTime
    #       - Flights
    #       - Distance
    #       - DistanceGroup   
    #       - DivAirportLandings
    #
    #################################################################

    remove_samples_w_nulls = [
        "flight_year",
        "flight_quarter",
        "flight_month",
        "DayofMonth",
        "DayOfWeek",
        "Marketing_Airline_Network",
        "Operated_or_Branded_Code_Share_Partners",
        "DOT_ID_Marketing_Airline",
        "IATA_Code_Marketing_Airline",
        "Flight_Number_M",
        "Operating_Airline",
        "DOT_ID_Operating_Airline",
        "IATA_Code_Operating_Airline",
        "Tail_Number",
        "Flight_Number_Operating_Airline",
        "OriginAirportID",
        "OriginAirportSeqID",
        "OriginCityMarketID",
        "Origin",
        "OriginCityName",
        "OriginState",
        "OriginStateFips",
        "OriginStateName",
        "OriginWac",
        "DestAirportID",
        "DestAirportSeqID",
        "DestCityMarketID",
        "Dest",
        "DestCityName",
        "DestState",
        "DestStateFips",
        "DestStateName",
        "DestWac",
        "CRSDepTime",
        "DepTime",
        "DepDelay",
        "DepDelayMinutes",
        "DepDel15",
        "DepartureDelayGroups",
        "DepTimeBlk",
        "TaxiOut",
        "WheelsOff",
        "WheelsOn",
        "TaxiIn",
        "CRSArrTime",
        "ArrTime",
        "ArrDelay",
        "ArrDelayMinutes",
        "ArrDel15",
        "ArrivalDelayGroups",
        "ArrTimeBlk",
        "Cancelled",
        "CancellationCode",
        "Diverted",
        "CRSElapsedTime",
        "ActualElapsedTime",
        "AirTime",
        "Flights",
        "Distance",
        "DistanceGroup",
        "DivAirportLandings"
        ]

    remove_samples_with_null_values = SubDagOperator(
        task_id="remove_samples_with_null_values",
        subdag=rswnic.sub_dag_remove_samples_with_nulls(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=remove_samples_w_nulls,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="remove_samples_with_null_values",
            postgres_conn_name=POSTGRES_CONN_NAME,
            args=default_args
            )
        )
    
    ############################################################
    #
    #  Operator to drop a primary key that is auto-incremented 
    #  as it is no longer required.
    #   
    ############################################################
    
    drop_primary_key = PostgresOperator(
        task_id="drop_primary_key",
        sql="""
        ALTER TABLE {{ params.table_name }}
        DROP COLUMN {{ params.id_column_name }};
        """,
        params= {
            "table_name": MAIN_PIPELINE_TABLE, 
            "id_column_name": "flight_id"
        },
        postgres_conn_id=POSTGRES_CONN_NAME
    )
    
    ############################################################
    #
    #  Operator to create new table in MySQL to place dataset.
    #   
    ############################################################
    
    create_mysql_table = MySqlOperator(
        task_id="create_mysql_table",
        sql="/sql/create_table.sql",
        params= {
            "table_name": NEW_MYSQL_TABLE_NAME
        },
        mysql_conn_id=MYSQL_CONN_NAME
    )
    
    ############################################################
    #
    #  Grant necessary permissions to MySQL table.
    #   
    ############################################################
    
    grant_mysql_table_permissions = MySqlOperator(
        task_id="grant_mysql_table_permissions",
        sql="""
        GRANT 
            SELECT, 
            INSERT, 
            UPDATE, 
            DELETE 
        ON 
            {{ params.database_name }}.{{ params.table_name }}
        TO 
            'airflow'@'localhost';
        GRANT FILE ON *.* TO 'airflow'@'localhost';
        """,
        params= {
            "table_name": NEW_MYSQL_TABLE_NAME,
            "database_name": MYSQL_SCHEMA_NAME
        },
        mysql_conn_id=MYSQL_CONN_NAME
    )
    
    #################################################################
    #
    #  Save Postgres table to a tsv file in a temporary 
    #  folder/sub-drectory.
    #
    #################################################################

    postgres_bulk_dump = SubDagOperator(
        task_id="postgres_bulk_dump",
        subdag=pbd.sub_postgres_bulk_dump(
            postgres_table_name=MAIN_PIPELINE_TABLE,
            postgres_conn_name=POSTGRES_CONN_NAME,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="postgres_bulk_dump",
            temp_folder_path= TEMP_FOLDER_PATH,
            temp_file_path= TEMP_FILE_PATH,
            args=default_args
        )
    )

    #################################################################
    #
    #  Retrieve dataset from temporary file and load into MySQL table.
    #
    #################################################################

    mysql_bulk_load = SubDagOperator(
        task_id="mysql_bulk_load",
        subdag=mbl.subdag_mysql_bulk_load(
            mysql_table_name=NEW_MYSQL_TABLE_NAME,
            mysql_conn_name=MYSQL_CONN_NAME,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="mysql_bulk_load",
            temp_file_path=TEMP_FILE_PATH,
            args=default_args
        )
    )

    #################################################
    #
    #  Create the order of operators for this dag.
    #
    #################################################
    
    (
        create_pipeline_table
        >> grant_perms_to_pipeline_table
        >> create_joined_db_table
        >> add_primary_key
        >> remove_unneeded_cols
        >> remove_samples_with_null_values
        >> drop_primary_key
        >> create_mysql_table
        >> grant_mysql_table_permissions
        >> postgres_bulk_dump
        >> mysql_bulk_load
        >> remove_single_value_cols
        >> remove_cols_w_all_null_values
    )
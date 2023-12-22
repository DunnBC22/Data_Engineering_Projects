"""
#################################################################
#
# Project Name: Indicators of Heart Disease 2022 Project
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
import impute_with_mode as imputer_str
import impute_with_median as imputer_num
import create_star_schema_part_1 as css1
import create_star_schema_part_2 as css2
import clean_up_after_star_schema_creation as cuassc
import sub_dag_remove_samples_with_nulls_in_cols as rswnc
import sub_dag_remove_multiple_columns as rmc

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

MAIN_DAG_NAME = "Indicators_of_Heart_Disease_2022-v01"
MAIN_PIPELINE_TABLE = "indicators_of_heart_disease_2022_pipe"
POSTGRES_CONN_NAME = "postgres_conn"

#################################################################
#
#  Create DAG for this pipeline.
#    
#################################################################

with DAG(
    default_args=default_args,
    dag_id=MAIN_DAG_NAME,
    description="Pipeline for Indicators of Heart Disease 2022",
    start_date=datetime(2023, 12, 1),
    schedule_interval='@once', 
    catchup=False,
    tags=[
        "Indicators", 
        "Medical", 
        "Heart", 
        "Disease", 
        "Heart Disease", 
        "2022"
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
            "orig_table_name": "heart_disease_indicators"
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
    #       - TetanusLast10Tdap
    #       - BMI
    #       - CovidPos
    #
    #################################################
    
    cols_to_remove = [
        "TetanusLast10Tdap",
        "CovidPos",
        "BMI"
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
    #  Remove samples that have nulls in any of 
    #  the following columns:
    #   - HadDiabetes
    #   - HadArthritis
    #   - HadKidneyDisease
    #   - HadDepressiveDisorder
    #   - HadCOPD
    #   - HadSkinCancer
    #   - HadAsthma
    #   - HadStroke
    #   - HadAngina
    #   - HadHeartAttack
    #   - SleepHours
    #   - PhysicalActivities
    #   - GeneralHealth
    # 
    #  Note(s):
    #       - I removed samples with missing 
    #         values in columns with less than 
    #         about 1 percent missing values 
    #         (~4,500).
    #       - I also removed samples with a missing 
    #         target value.
    #
    #################################################
    
    cols_with_null_samples_to_drop = [
        "HadDiabetes",
        "HadArthritis",
        "HadKidneyDisease",
        "HadDepressiveDisorder",
        "HadCOPD",
        "HadSkinCancer",
        "HadAsthma",
        "HadStroke",
        "HadAngina",
        "HadHeartAttack",
        "SleepHours",
        "PhysicalActivities",
        "GeneralHealth"
        ]
    
    remove_samples_w_nulls = SubDagOperator(
        task_id="remove_samples_with_nulls",
        subdag=rswnc.sub_dag_remove_samples_with_nulls(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=cols_with_null_samples_to_drop,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="remove_samples_with_nulls",
            postgres_conn_name=POSTGRES_CONN_NAME,
            args=default_args
        )
    )
    
    #################################################
    #
    #  Impute missing values for columns that have 
    #  more than 1 percent missing values, including 
    #  the following columns: 
    #       - HighRiskLastYear
    #       - PneumoVaxEver
    #       - FluVaxLast12
    #       - HIVTesting
    #       - AlcoholDrinkers
    #       - WeightInKilograms
    #       - HeightInMeters
    #       - AgeCategory
    #       - RaceEthnicityCategory
    #       - ChestScan
    #       - ECigaretteUsage
    #       - SmokerStatus
    #       - DifficultyErrands
    #       - DifficultyDressingBathing
    #       - DifficultyWalking
    #       - DifficultyConcentrating
    #       - BlindOrVisionDifficulty
    #       - DeafOrHardOfHearing
    #       - RemovedTeeth
    #       - LastCheckupTime 
    #       - MentalHealthDays
    #       - PhysicalHealthDays
    #
    #  Note(s):
    #       - Impute missing string/VARCHAR values 
    #         with the column's mode.
    #       - Impute missing numerical values with 
    #         the column's median.
    # 
    #################################################
    
    cols_with_nulls_str = [
        "HighRiskLastYear",
        "PneumoVaxEver",
        "FluVaxLast12",
        "HIVTesting",
        "AlcoholDrinkers",
        "AgeCategory",
        "RaceEthnicityCategory",
        "ChestScan",
        "ECigaretteUsage",
        "SmokerStatus",
        "DifficultyErrands",
        "DifficultyDressingBathing",
        "DifficultyWalking",
        "DifficultyConcentrating",
        "BlindOrVisionDifficulty",
        "DeafOrHardOfHearing",
        "RemovedTeeth",
        "LastCheckupTime",
        "HadDiabetes",
        "HadArthritis",
        "HadKidneyDisease",
        "HadDepressiveDisorder",
        "HadCOPD",
        "HadSkinCancer",
        "HadAsthma",
        "HadStroke",
        "HadAngina",
        "HadHeartAttack",
        "PhysicalActivities",
        "GeneralHealth"
        ]
    
    impute_missing_values_str = SubDagOperator(
        task_id=f"impute_missing_values_strings",
        subdag=imputer_str.sub_dag_impute_with_mode(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=cols_with_nulls_str,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="impute_missing_values_strings",
            postgres_conn_name=POSTGRES_CONN_NAME,
            args=default_args
        )
    )
    
    cols_with_nulls_num = [
        "WeightInKilograms",
        "HeightInMeters",
        "MentalHealthDays",
        "PhysicalHealthDays"
        ]
    
    impute_missing_values_num = SubDagOperator(
        task_id="impute_missing_values_numbers",
        subdag=imputer_num.sub_dag_impute_with_median(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=cols_with_nulls_num,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="impute_missing_values_numbers",
            postgres_conn_name=POSTGRES_CONN_NAME,
            args=default_args
        )
    )
    
    #################################################
    #
    #  Calculate BMI from HeightInMetters & 
    #  WeightInKilograms
    #
    #################################################
    
    bmi_calc_params = {
        "table_name": MAIN_PIPELINE_TABLE,
        "column_name": "BMI",
        "height_value": "HeightInMeters",
        "weight_value": "WeightInKilograms"
        }
    
    calculate_bmi = PostgresOperator(
        task_id=f"calculate_bmi",
        sql="/sql/calculate_bmi.sql",
        postgres_conn_id=POSTGRES_CONN_NAME,
        params=bmi_calc_params
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
    #       - WeightInKilograms
    #       - HeightInMeters
    #       - BMI (the new BMI calculated column)
    #
    #################################################
    
    cols_with_outliers = [
        "weightinkilograms",
        "heightinmeters",
        "bmi"
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
    #       - RaceEthnicityCategory
    #       - AgeCategory
    #       - SmokerStatus
    #       - ECigaretteUsage
    #       - RemovedTeeth
    #       - LastCheckupTime
    #       - GeneralHealth
    #       - Sex
    #       - StateName
    #       - HighRiskLastYear
    #       - PneumoVaxEver
    #       - FluVaxLast12
    #       - HIVTesting
    #       - AlcoholDrinkers
    #       - ChestScan	
    #       - DifficultyErrands
    #       - DifficultyDressingBathing
    #       - DifficultyWalking
    #       - DifficultyConcentrating
    #       - BlindOrVisionDifficulty
    #       - DeafOrHardOfHearing
    #       - HadDiabetes
    #       - HadArthritis
    #       - HadKidneyDisease
    #       - HadDepressiveDisorder
    #       - HadCOPD
    #       - HadSkinCancer
    #       - HadAsthma
    #       - HadStroke
    #       - HadAngina
    #       - HadHeartAttack
    #       - PhysicalActivities
    #
    #################################################

    dim_tables_to_create = [
        {
            "col_name": "RaceEthnicityCategory",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "AgeCategory",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "SmokerStatus",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "ECigaretteUsage",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "RemovedTeeth",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "LastCheckupTime",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "GeneralHealth",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Sex",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "StateName",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "HighRiskLastYear",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "PneumoVaxEver",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "FluVaxLast12",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "HIVTesting",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "AlcoholDrinkers",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "ChestScan",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "DifficultyErrands",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "DifficultyDressingBathing",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "DifficultyWalking",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "DifficultyConcentrating",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "BlindOrVisionDifficulty",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "DeafOrHardOfHearing",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "HadDiabetes",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "HadArthritis",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "HadKidneyDisease",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "HadDepressiveDisorder",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "HadCOPD",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "HadSkinCancer",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "HadAsthma",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "HadStroke",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "HadAngina",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "HadHeartAttack",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "PhysicalActivities",
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
        >> remove_unnecessary_columns
        >> remove_samples_w_nulls
        >> impute_missing_values_str
        >> impute_missing_values_num
        >> calculate_bmi
        >> add_id_column
        >> remove_outliers_1_5_iqr
        >> remove_id_column
        >> create_dim_tables
        >> insert_fk_into_fact_table
        >> remove_replaced_dim_cols
    )
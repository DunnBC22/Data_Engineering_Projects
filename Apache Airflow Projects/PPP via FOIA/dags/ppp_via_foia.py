"""
#################################################################
#
# Project Name: Paycheck Protection Program via FOIA Project
#
#####
#
# Author: Brian Dunn
#
#####
#
# Approx. Date of Completion: 12-15-2023
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


import create_star_schema_part_1 as css1
import create_star_schema_part_2 as css2
import clean_up_after_star_schema_creation as cuassc
import sub_dag_remove_samples_with_nulls_in_cols as rswc
import sub_dag_remove_multiple_columns as rmc
import fill_nulls_in_these_cols_with_fixed_value as fnwfv
import sub_dag_remove_outliers_fixed_values as rofv
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

MAIN_DAG_NAME = "ppp_via_foia-v01"

MAIN_PIPELINE_TABLE = "ppp_via_foia_pipe"

POSTGRES_CONNECTION_STRING = "postgres_conn"


#################################################################
#
#  Create DAG for this pipeline.
#    
#################################################################


with DAG(
    default_args=default_args,
    dag_id=MAIN_DAG_NAME,
    description="Paycheck Protection Program via FOIA Pipeline",
    start_date=datetime(2023, 12, 1),
    catchup=False,
    schedule_interval='@once', 
    tags=[
        "Paycheck", 
        "Protection", 
        "PPP",
        "Program",
        "FOIA"
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
            "orig_table_name": "ppp_via_foia"
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
    #       - DEBT_INTEREST_PROCEED
    #       - HEALTH_CARE_PROCEED
    #       - REFINANCE_EIDL_PROCEED
    #       - RENT_PROCEED
    #       - MORTGAGE_INTEREST_PROCEED
    #       - UTILITIES_PROCEED
    #       - LoanNumber
    #       - OriginatingLenderState (OriginatingLenderID)
    #       - OriginatingLenderCity (OriginatingLenderID)
    #       - OriginatingLender (OriginatingLenderID)
    #       - ProjectZip
    #       - ProjectState
    #       - ProjectCountyName
    #       - ProjectCity
    #       - BusinessAgeDescription
    #       - LMIIndicator
    #       - HubzoneIndicator
    #       - RuralUrbanIndicator
    #       - ServicingLenderZip
    #       - ServicingLenderState
    #       - ServicingLenderCity
    #       - ServicingLenderAddress
    #       - SBAGuarantyPercentage (only one distinct value)
    #       - BorrowerAddress
    #       - FranchiseName
    #
    #################################################
    
    
    cols_to_remove = [
        "DEBT_INTEREST_PROCEED",
        "HEALTH_CARE_PROCEED",
        "REFINANCE_EIDL_PROCEED",
        "RENT_PROCEED",
        "MORTGAGE_INTEREST_PROCEED",
        "UTILITIES_PROCEED",
        "LoanNumber",
        "OriginatingLenderState",
        "OriginatingLenderCity",
        "OriginatingLender",
        "ProjectZip",
        "ProjectState",
        "ProjectCountyName",
        "ProjectCity",
        "BusinessAgeDescription",
        "LMIIndicator",
        "HubzoneIndicator",
        "RuralUrbanIndicator",
        "ServicingLenderZip",
        "ServicingLenderState",
        "ServicingLenderCity",
        "ServicingLenderAddress",
        "SBAGuarantyPercentage",
        "BorrowerAddress",
        "FranchiseName"
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
    #       - ForgivenessDate
    #       - ForgivenessAmount
    #       - BusinessType
    #       - PAYROLL_PROCEED
    #       - NAICSCode
    #       - JobsReported
    #       - CD
    #       - UndisbursedAmount
    #       - LoanStatusDate
    #       - BorrowerZip
    #       - BorrowerState
    #
    #################################################
    
    
    cols_with_null_sample_values = [
        "ForgivenessDate",
        "ForgivenessAmount",
        "BusinessType",
        "PAYROLL_PROCEED",
        "NAICSCode",
        "JobsReported",
        "CD",
        "UndisbursedAmount",
        "LoanStatusDate",
        "BorrowerZip",
        "BorrowerState"
        ]
    
    remove_samples_with_nulls = SubDagOperator(
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
    #  Fill in missing values in the following 
    #  columns with common sense values:
    #       - NonProfit (N)
    #
    #################################################
    
    
    cols_for_fixed_val_impute = [
        {
            "col_name": "NonProfit",
            "fill_value": "'N'"
        }
    ]
    
    impute_w_fixed_values = SubDagOperator(
        task_id="impute_with_fixed_values",
        subdag=fnwfv.sub_dag_fill_nulls_w_fixed_value(
            table_name=MAIN_PIPELINE_TABLE,
            cols_to_impute=cols_for_fixed_val_impute,
            parent_dag_name=MAIN_DAG_NAME,
            child_dag_name="impute_with_fixed_values",
            postgres_conn_name=POSTGRES_CONNECTION_STRING,
            args=default_args
        )
    )
    
    
    #################################################
    #
    #  Remove samples with outliers (using a common 
    #  sense limit) for the following columns:
    #       - JobsReported (under 300)
    #
    #################################################
    
    
    cols_w_outliers = [
        {
            "column_name": "JobsReported",
            "operator": ">",
            "comparison_value": 300
        }
    ]
    
    remove_outliers_w_fixed_vals = SubDagOperator(
        task_id="remove_outliers_with_fixed_vals",
        subdag=rofv.sub_dag_remove_outliers_fixed_vals(
            table_name=MAIN_PIPELINE_TABLE,
            cols_w_fixed_ranges=cols_w_outliers,
            parent_dag_name=MAIN_DAG_NAME,
            postgres_conn_name=POSTGRES_CONNECTION_STRING,
            child_dag_name="remove_outliers_with_fixed_vals",
            args=default_args
            )
        )
    
    #################################################
    #
    #  Generate date parts for the following columns:
    #       - ForgivenessDate
    #       - LoanStatusDate
    #       - DateApproved
    #
    #################################################
    
    
    cols_to_gen_date_parts = [
        "ForgivenessDate",
        "LoanStatusDate",
        "DateApproved"
        ]
    
    generate_date_parts = SubDagOperator(
        task_id="generate_date_parts",
        subdag=gen_dmy.sub_dag_generate_month_dom_year_of_date(
            table_name=MAIN_PIPELINE_TABLE,
            column_names=cols_to_gen_date_parts,
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
    #       - NonProfit
    #       - Veteran
    #       - Gender
    #       - BusinessType
    #       - Ethnicity
    #       - Race
    #       - NAICSCode
    #       - CD
    #       - ServicingLenderName
    #       - ServicingLenderLocationID
    #       - Term
    #       - LoanStatus
    #       - BorrowerName
    #       - BorrowerCity
    #       - BorrowerState
    #       - BorrowerZip
    #       - ProcessingMethod
    #
    #################################################
    
    
    dim_tables_to_create = [
        {
            "col_name": "NonProfit",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Veteran",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Gender",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "BusinessType",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Ethnicity",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "Race",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "NAICSCode",
            "data_type": "INTEGER"
        },
        {
            "col_name": "CD",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "ServicingLenderName",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "ServicingLenderLocationID",
            "data_type": "INTEGER"
        },
        {
            "col_name": "Term",
            "data_type": "INTEGER"
        },
        {
            "col_name": "LoanStatus",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "BorrowerName",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "BorrowerCity",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "BorrowerState",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "BorrowerZip",
            "data_type": "VARCHAR"
        },
        {
            "col_name": "ProcessingMethod",
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
        >> Label("Transform Data")
        >> remove_unnecessary_columns
        >> remove_samples_with_nulls
        >> impute_w_fixed_values
        >> remove_outliers_w_fixed_vals
        >> generate_date_parts
        >> Label("Convert to Star Schema")
        >> create_dim_tables
        >> insert_fk_into_fact_table
        >> remove_replaced_dim_cols
    )
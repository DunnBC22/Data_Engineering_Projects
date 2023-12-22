"""
#################################################################
#
#  Author: Brian Dunn
#
#  Approx. Date Completed: 11-25-2023
#
#  Create sub-DAG to include the following columns for each
#  column that is a date:
#       - month
#       - day of month, & 
#       - year.
#    
#################################################################
"""

#################################################################
#
#  Import Necessary Libraries.
#
#################################################################

from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

from dag_config_class import DAGConfig

#################################################################
#
#  Creates the sub-DAG that includes the following  
#  columns for each column that is a date:
#       - month
#       - day of month, & 
#       - year.
#
#################################################################

def sub_dag_generate_month_dom_year_of_date(table_name: str,
                                            column_names: list[str],
                                            parent_dag_name: str, 
                                            child_dag_name: str,
                                            postgres_conn_name: str,
                                            args: DAGConfig
                                            ) -> DAG:
    """
    Summary:
        This subdag creates columns that include the
        month, year, and day of the month of the date 
        columns inputted.

    Args:
        table_name (str): This is the name of the main 
            DAG for the entire pipeline.
        column_names (list[str]): These are the columns from 
            which to extract/generate month, year and day of 
            month values.
        parent_dag_name (str): This is the parent DAG for 
            this pipeline.
        child_dag_name (str): This is the child DAG name for 
            this subdag of task(s).
        postgres_conn_name (str): This is the Connection ID to 
            the PostgreSQL database used for this pipeline.
        args (dict[str, str]): These are the default arguments. 
            They are the same exact default arguments as the 
            arguments used in the main DAG.

    Returns:
        generate_date_parts_subdag (DAG): This function 
            returns the subDAG that was created in this file.
    """
    
    
    generate_date_parts_subdag = DAG(
        dag_id=f"{parent_dag_name}.{child_dag_name}",
        default_args=args,
        start_date=datetime(2023, 12, 1),
        catchup=False,
        schedule_interval='@once',
    )
    
    for col in column_names:
        parameters={
            "table_name": table_name, 
            "col_name": col,
            "month_col_name": f"{col}_month",
            "year_col_name": f"{col}_year",
            "dom_col_name": f"{col}_day_of_month",
            }
        PostgresOperator(
            task_id=f"generate-date-parts-of-{col}",
            sql="/sql/generate_month_dom_year.sql",
            postgres_conn_id=postgres_conn_name,
            params=parameters,
            dag=generate_date_parts_subdag)
    
    return generate_date_parts_subdag
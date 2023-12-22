"""
#################################################################
#
#  Author: Brian Dunn
#
#  Approx. Date Completed: 12-20-2023
#
#  This sub-DAG imputes missing values with the median value 
#  from the same column.
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
#  Create sub-DAG for imputing missing values with median value.
#
#################################################################


def sub_dag_impute_with_median(table_name: str,
                                  column_names: list[str],
                                  parent_dag_name: str, 
                                  child_dag_name: str,
                                  postgres_conn_name: str,
                                  args: DAGConfig
                                  ) -> DAG:
    """
    Summary: 
       This subdag imputes missing values with median for 
       respective column.

    Args:
        table_name (str): This is the name of the main 
            DAG for the entire pipeline.
        column_names (list[str]): These are the columns that 
            have missing values to impute with the median for 
            that column.
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
        DAG: This function 
            returns the subDAG that was created in this file.
    """
    
    
    impute_missing_values_median = DAG(
        dag_id=f"{parent_dag_name}.{child_dag_name}",
        default_args=args,
        start_date=datetime(2023, 12, 1),
        catchup=False,
        schedule_interval='@once',
    )
    
    for col in column_names:
        parameters={
            "table_name": table_name, 
            "column_name": col
            }
        
        PostgresOperator(
            task_id=f"impute_missing_values_in_{col}_with_median",
            sql="/sql/impute_with_median.sql",
            params=parameters,
            postgres_conn_id=postgres_conn_name,
            dag=impute_missing_values_median)
    
    return impute_missing_values_median
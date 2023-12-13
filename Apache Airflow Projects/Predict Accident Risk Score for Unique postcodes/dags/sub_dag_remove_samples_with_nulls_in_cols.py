"""
#################################################################
#
#  Author: Brian Dunn
#
#  Approx. Date Completed: 11-25-2023
#
#  Create sub-DAG to remove samples with null values.
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
#  Create the sub-DAG for removing samples in a table.
#
#################################################################


def sub_dag_remove_samples_with_nulls(table_name: str,
                                      column_names: list[str],
                                      parent_dag_name: str,
                                      child_dag_name: str,
                                      postgres_conn_name: str,
                                      args: DAGConfig
                                      ):
    """
    Summary: 
       This is a subdag that handles removing samlples with 
       nulls in particular columns from a postgres table.

    Args:
        table_name (str): This is the name of the main 
            DAG for the entire pipeline.
        column_names (list[str]): These are the columns to 
            check for nulls when deleting samples.
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
    
    
    sub_dag_remove_null_samples = DAG(
        dag_id=f"{parent_dag_name}.{child_dag_name}",
        default_args=args,
        start_date=datetime(2023, 12, 1),
        catchup=False,
        schedule_interval='@once',
        )
        
    for col in column_names:
        PostgresOperator(
            task_id=f"{child_dag_name}.remove_samples_with_null_{col}_values",
            postgres_conn_id=postgres_conn_name,
            sql="/sql/remove_samples_with_any_nulls.sql",
            params={
                "table_name": table_name,
                "column_name": col
                },
            dag=sub_dag_remove_null_samples
        )
    
    return sub_dag_remove_null_samples
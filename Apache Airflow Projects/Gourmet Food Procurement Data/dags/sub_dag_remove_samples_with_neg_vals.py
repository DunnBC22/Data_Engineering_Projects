"""
#################################################################
#
#  Author: Brian Dunn
#
#  Approx. Date Completed: 11-25-2023
#
#  Create sub-DAG to remove samples with negative value in 
#  at least one of many columns.
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
#  Create sub-DAG to remove samples with negative value in 
#  at least one of many columns.
#
#################################################################


def sub_dag_remove_samples_with_neg_values(table_name: str,
                                           column_names: list[str],
                                           parent_dag_name: str,
                                           child_dag_name: str,
                                           postgres_conn_name: str,
                                           args: DAGConfig
                                           ):
    """
    Summary: 
       This subdag will remove samples with negative value in 
       at least one column.

    Args:
        table_name (str): This is the name of the main 
            DAG for the entire pipeline.
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
        sub_dag_remove_samples_with_neg_values (DAG [or SubDAG]): This 
        function returns the subDAG that was created in this file.
    """
    
    
    sub_dag_remove_columns = DAG(
        dag_id=f"{parent_dag_name}.{child_dag_name}",
        default_args=args,
        start_date=datetime(2023, 12, 1),
        catchup=False,
        schedule_interval='@once',
        )
        
    for col in column_names:
        PostgresOperator(
            task_id=f"{child_dag_name}.remove_samples_with_neg_{col}_val",
            postgres_conn_id=postgres_conn_name,
            sql="/sql/remove_samples_negative_values.sql",
            params={
                "table_name": table_name,
                "col_for_bool": col
                },
            dag=sub_dag_remove_columns
        )
    
    return sub_dag_remove_columns
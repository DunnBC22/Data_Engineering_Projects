"""
#################################################################
#
#  Author: Brian Dunn
#
#  Approx. Date Completed: 11-25-2023
#
#  Create the sub-DAG to change the data type of multiple 
#  columns.
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
#  Create the sub-DAG to change the data type of multiple 
#  columns.
#
#################################################################


def sub_dag_change_column_data_type(table_name: str,
                                    column_names: list[str],
                                    new_dtype: str,
                                    parent_dag_name: str, 
                                    child_dag_name: str,
                                    postgres_conn_name: str,
                                    args: DAGConfig
                                    ) -> DAG:
    """
    Summary: 
       This subdag changes the data type of table columns.

    Args:
        table_name (str): This is the name of the main 
            DAG for the entire pipeline.
        column_names (list[str]): These are the columns that 
            will have their data type updated.
        parent_dag_name (str): This is the parent DAG for 
            this pipeline.
        new_dtype (Union[int, float, str]): This is the data 
            type to which you want to modify the column.
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
    
    
    change_col_dtype = DAG(
        dag_id=f"{parent_dag_name}.{child_dag_name}",
        default_args=args,
        start_date=datetime(2023, 12, 1),
        catchup=False,
        schedule_interval='@once',
    )
    
    for col in column_names:
        parameters={
            "table_name": table_name,
            "col_name_to_update": col,
            "new_data_type": new_dtype
            }
        PostgresOperator(
            task_id=f"change_{col}_data_type",
            sql="/sql/convert_data_type_of_column.sql",
            params=parameters,
            postgres_conn_id=postgres_conn_name,
            dag=change_col_dtype)
    
    return change_col_dtype
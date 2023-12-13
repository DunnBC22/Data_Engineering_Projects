"""
#################################################################
#
#  Author: Brian Dunn
#
#  Approx. Date Completed: 11-25-2023
#
#  Create sub-DAG to fill null values with fixed values.
#    
#################################################################
"""


#################################################################
#
#  Import Necessary Libraries.
#
#################################################################


from __future__ import annotations
from typing import Union
from datetime import datetime

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

from dag_config_class import DAGConfig


#################################################################
#
#  Create the sub-DAG for filling null values with a fixed value
#
#################################################################


def sub_dag_fill_nulls_w_fixed_value(table_name: str,
                                     cols_to_impute: list[dict[str, Union[str, int, float]]],
                                     parent_dag_name: str,
                                     child_dag_name: str,
                                     postgres_conn_name: str,
                                     args: DAGConfig
                                     ):
    """
    Summary: 
       This is a subdag that fills null values with a 
            fixed value

    Args:
        table_name (str): This is the name of the main 
            DAG for the entire pipeline.
        cols_to_impute list[dict[str, Union[str, int, float]]]:
            This is a list of dictionaries that have the 
            column_names and values to impute into null values 
            in the column_name.
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
    
    
    fill_nuls_w_fixed_values = DAG(
        dag_id=f"{parent_dag_name}.{child_dag_name}",
        default_args=args,
        start_date=datetime(2023, 12, 1),
        catchup=False,
        schedule_interval='@once',
        )
        
    for col in cols_to_impute:
        column_name = col['col_name']
        
        PostgresOperator(
            task_id=f"{child_dag_name}.impute_{column_name}_w_fixed_val",
            postgres_conn_id=postgres_conn_name,
            sql="/sql/fill_nulls_in_these_cols_with_fixed_value.sql",
            params={
                "table_name": table_name,
                "col_to_fill": col['col_name'],
                "value_to_fill_in": col['fill_value']
                },
            dag=fill_nuls_w_fixed_values
        )
    
    return fill_nuls_w_fixed_values
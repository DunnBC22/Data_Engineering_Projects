"""
#################################################################
#
#  Author: Brian Dunn
#
#  Approx. Date Completed: 12-15-2023
#
#  This sub-DAG removes the original columns that are no longer 
#  needed as there are foreign keys that will be used instead.
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


##################################################################
#
#  This sub-DAG creates dimension tables from categorical values.
#
##################################################################


def sub_dag_star_schema_clean_up(table_name: str,
                               column_names: list[str],
                               parent_dag_name: str, 
                               child_dag_name: str,
                               postgres_conn_name: str,
                               args: DAGConfig
                               ):
    """
    Summary:
        This subdag removes the original columns in the fact 
        table that were replaced (without being overwritten) 
        in the fact table.

    Args:
        table_name (str): This is the name of the main fact table.
        column_names list[str]: This is the list of columns that 
            need to be addressed to convert table to star schema.
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
        sub_dag_create_star_schema (DAG [or SubDAG]): This 
        function returns the subDAG that was created in this file.
    """
    
    #################################################################
    #
    #  Define the DAG (that will be referenced later).
    #    
    #################################################################
    
    sub_dag_clean_up_fact_table = DAG(
        dag_id=f"{parent_dag_name}.{child_dag_name}",
        default_args=args,
        start_date=datetime(2023, 12, 1),
        catchup=False,
        schedule_interval='@once',
        description=__doc__
        )
    

    #################################################################
    #
    #  Loop through all of the columns (pre-defined) that will be 
    #  converted to dimension tables. Each iteration through the 
    #  loop aligns with a single column from the original table.
    #    
    #################################################################
    
    
    dim_tables_to_create = column_names
        
    for col in dim_tables_to_create:
        dim_table_params = {
            "table_name": table_name,
            "column_name": col['col_name']
        }
        
        column_name = col['col_name']
                
        remove_orig_column = PostgresOperator(
            task_id=f'remove_original_{column_name}_in_fact_table',
            sql="/sql/remove_columns.sql",
            postgres_conn_id=postgres_conn_name,
            dag=sub_dag_clean_up_fact_table,
            params=dim_table_params
        )
        
    return sub_dag_clean_up_fact_table
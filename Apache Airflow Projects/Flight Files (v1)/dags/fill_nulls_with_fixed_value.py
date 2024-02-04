"""
#################################################################
#
#  Author: Brian Dunn
#
#  Approx. Date Completed: 12-28-2023
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
from typing import Union

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.postgres_hook import PostgresHook

from dag_config_class import DAGConfig

#################################################################
#
#  Create the sub-DAG for removing samples in a table.
#
#################################################################

def sub_dag_fill_nulls_w_fixed_value(
    table_name,
    column_names,
    parent_dag_name,
    child_dag_name,
    postgres_conn_name,
    val_to_fill_in,
    primary_key,
    args: DAGConfig
    ):
    
    """
    Summary: 
       This is a subdag that handles removing samples with 
       nulls in particular columns from a postgres table.

    Args:
        table_name (str): This is the name of the main 
            DAG for the entire pipeline.
        column_names (list[str]): These are the columns to replace 
            nulls with a fixed value.
        parent_dag_name (str): This is the parent DAG for 
            this pipeline.
        child_dag_name (str): This is the child DAG name for 
            this subdag of task(s).
        postgres_conn_name (str): This is the Connection ID to 
            the PostgreSQL database used for this pipeline.
        val_to_fill_in (Union[float, int, str]): This is the value 
            that will replace null values.
        args (dict[str, str]): These are the default arguments. 
            They are the same exact default arguments as the 
            arguments used in the main DAG.

    Returns:
        DAG: This function 
            returns the subDAG that was created in this file.
    """
    
    fill_nulls_subdag = DAG(
        dag_id=f"{parent_dag_name}.{child_dag_name}",
        default_args=args,
        start_date=datetime(2024, 1, 1),
        catchup=False,
        schedule_interval='@once',
        )
    
    def fill_nulls_main(
        col_names: list[str],
        val_to_fill_in: Union[float, int, str, object],
        postgres_conn_name: str,
        table_name: str
    ):
        
        # PostgreSQL hook
        pg_hook = PostgresHook(postgres_conn_id=postgres_conn_name)
        
        # Wrap the blocks in a with block
        with pg_hook.get_conn() as conn:
            with conn.cursor() as cursor:
                for col in col_names:
                    fill_null_values_query = f"""
                    WITH cte AS (
                        SELECT *
                        FROM {table_name}
                        WHERE {col} IS NULL
                        ORDER BY {primary_key}
                        FOR UPDATE
                    )
                    -- Update the selected rows
                    UPDATE {table_name}
                    SET {col} = {val_to_fill_in}
                    FROM cte
                    WHERE {table_name}.{primary_key} = cte.{primary_key};"""
                    #fill_null_values_query = f"UPDATE {table_name} SET {col} = %s WHERE {col} IS NULL;"
                    cursor.execute(fill_null_values_query)
    
    
    fill_null_values_with_preset_value = PythonOperator(
        task_id=f"fill_null_values_with_preset_value",
        python_callable=fill_nulls_main,
        op_kwargs={
            'col_names': column_names, 
            'val_to_fill_in': val_to_fill_in,
            'postgres_conn_name': postgres_conn_name,
            'table_name': table_name
            },
        provide_context=True,
        dag=fill_nulls_subdag
    )
    
    return fill_nulls_subdag
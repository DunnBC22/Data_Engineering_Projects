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
import logging
from datetime import datetime

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.postgres_hook import PostgresHook

from dag_config_class import DAGConfig

import psycopg2

#################################################################
#
#  Create the sub-DAG for removing samples in a table.
#
#################################################################

def sub_dag_remove_samples_with_nulls(
    table_name: str,
    column_names: list[str],
    parent_dag_name: str,
    child_dag_name: str,
    postgres_conn_name: str,
    args: DAGConfig
    ) -> DAG:
    
    """
    Summary: 
       This is a subdag that handles removing samlples with 
       nulls in particular columns from a postgres table.

    Args:
        table_name (str): This is the name of the PostgreSQL table.
        column_names (list[str]): These are the columns to look for 
            the null values to remove.
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
        start_date=datetime(2024, 1, 1),
        catchup=False,
        schedule_interval='@once',
        )
    
    # this function returns a list of the columns currently in this table
    def get_column_names(
        table_name, 
        postgres_conn_name
        ):
        
        column_names = []

        conn = None
        cursor = None
        
        try:
            # Create PostgreSQL Connection
            pg_hook = PostgresHook(
                postgres_conn_id=postgres_conn_name
                )
            pg_conn = pg_hook.get_conn()
            pg_cursor = pg_conn.cursor()
            
            # Execute a query to get the column names
            query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'"
            
            # Execute query to retrieve column names & their data types
            pg_cursor.execute(query)
            
            # Fetch all the results as a list of tuples and extract column names
            column_names = [column[0] for column in pg_cursor.fetchall()]
            col_names = [col.lower() for col in column_names]
            return col_names
        except Exception as e:
            print(f"Exception: {e}")
        finally:
            # Close the cursor and connection
            if pg_cursor:
                pg_cursor.close()
            if pg_conn:
                pg_conn.close()
    
    # This is the function that the PythonOperator will call
    def remove_samples_w_nulls(
        table_name,
        postgres_conn_name,
        column_names
        ):
        
        # update the list of columns to iterate through
        col_list_passed_in = set(column_names)
        cols_still_in_table = set(get_column_names(table_name, postgres_conn_name))
        
        cols_to_iterate_through = list(col_list_passed_in.intersection(cols_still_in_table))
        
        column_names_to_iter_thru = [item.lower() for item in cols_to_iterate_through]
        
        for col in column_names_to_iter_thru:
            column_names = []

            conn = None
            cursor = None
            
            try:
                # Create PostgreSQL Connection
                pg_hook = PostgresHook(postgres_conn_id=postgres_conn_name)
                pg_conn = pg_hook.get_conn()
                pg_cursor = pg_conn.cursor()
                
                # Execute a query to get the column names
                query = f'DELETE FROM {table_name} WHERE {col} is NULL;'
                
                # Execute query to retrieve column names & their data types
                pg_cursor.execute(query)
                
                pg_conn.commit()
            except Exception as e:
                print(f"Error: {e}")
            finally:
                # Close the cursor and connection
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()

    remove_samples_with_nulls = PythonOperator(
        task_id=f'{parent_dag_name}.{child_dag_name}',
        python_callable=remove_samples_w_nulls,
        provide_context=True,
        op_kwargs={
            "table_name": table_name,
            "postgres_conn_name": postgres_conn_name,
            "column_names": column_names
        },
        dag=sub_dag_remove_null_samples,
    )
    
    return sub_dag_remove_null_samples
"""
#################################################################
#
#  Author: Brian Dunn
#
#  Approx. Date Completed: 11-25-2023
#
#  This sub-DAG removes all columns that only have one distinct 
#  value in them.
#
#  Note: Remember to install Pandas & psycopg2 in the Dockerfile.
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
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.postgres_hook import PostgresHook

from dag_config_class import DAGConfig
from airflow import DAG
from airflow.operators.python_operator import PythonOperator


#################################################################
#
#  This sub-DAG converts the fact table into a Pandas DataFrame 
#  & saves it to file.
#
#################################################################


def sub_dag_remove_single_val_cols(table_name: str,
                                   parent_dag_name: str, 
                                   child_dag_name: str,
                                   postgres_conn_name: str,
                                   args: DAGConfig
                                   ) -> DAG:
   
    """
    Summary:
        This sub-DAG converts the fact table into a Pandas DataFrame 
        & saves it to file.

    Args:
        table_name (str): This is the name of the main 
            DAG for the entire pipeline.
        parent_dag_name (str): This is the parent DAG for 
            this pipeline.
        child_dag_name (str): This is the child DAG name for 
            this pipeline.
        postgres_conn_name (str): This is the Connection ID to 
            the PostgreSQL database used for this pipeline.
        args (dict[str, str]): These are the default arguments. 
            They are the same exact default arguments as the 
            arguments used in the main DAG.

    Returns:
        sub_dag_remove_single_val_cols (DAG): This function 
            returns the subDAG that was created in this file.
    """
    
    #################################################################
    #
    #  Import necessary libraries.
    #
    #################################################################

    import pandas as pd
    import psycopg2
    
    #################################################################
    #
    #  Define the DAG that will be referenced later.
    #
    #################################################################
    
    sub_dag_remove_single_value_columns = DAG(
        dag_id=f"{parent_dag_name}.{child_dag_name}",
        default_args=args,
        start_date=datetime(2023, 12, 1),
        catchup=False,
        schedule_interval='@once',
    )
    
    #################################################################
    #
    #  Define the function that will:
    #       - Define thePostgresHook, 
    #       - Connect to the database, 
    #       - retreive Fact Table,
    #       - Convert it to Pandas DataFrame, &
    #       - Save it as a CSV file.
    #
    #################################################################
    
    dag = DAG(
        'remove_single_value_columns_dag',
        default_args=args,
        schedule_interval=None,
    )

    def remove_single_value_columns(table_name,
                                    postgres_conn_name
                                    ):
        # Create the PostgresHook
        postgres_hook = PostgresHook(postgres_conn_id=postgres_conn_name)
        
        # Get connection to the database
        conn = postgres_hook.get_conn()
        cursor = conn.cursor()

        try:
            # Loop through all columns in the table
            cursor.execute(
                f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                """
                )
            columns = cursor.fetchall()
            print("columns", columns)

            for column in columns:
                column_name = column[0]

                # Count the number of distinct values in the column
                cursor.execute(f"SELECT COUNT(DISTINCT {column_name}) FROM {table_name}")
                distinct_count = cursor.fetchone()[0]

                # If there is only one distinct value, drop the column
                if distinct_count == 1:
                    cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN {column_name}")
                    conn.commit()
                    print(f"Dropped column {column_name} from table {table_name}")

        finally:
            cursor.close()
            conn.close()

    # Define the PythonOperator for the sub-DAG
    remove_single_value_columns_task = PythonOperator(
        task_id='remove_single_value_columns',
        python_callable=remove_single_value_columns,
        op_args=[table_name, postgres_conn_name], 
        dag=sub_dag_remove_single_value_columns
    )
    
    # Return the sub-dag
    return sub_dag_remove_single_value_columns
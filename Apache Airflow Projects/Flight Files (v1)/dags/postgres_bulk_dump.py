"""
##################################################################
#
#  Author: Brian Dunn
#
#  Approx. Date Completed: 1-28-2024
#
#  This subdag pulls the data from the Postgres table and inserts 
#  it into a MySQL table.
#    
##################################################################
"""

#################################################################
#
#  Import Necessary Libraries.
#
#################################################################

from __future__ import annotations

import os

from airflow import DAG
from datetime import datetime

from airflow.operators.python_operator import PythonOperator
from airflow.hooks.postgres_hook import PostgresHook

from dag_config_class import DAGConfig

###################################################################
#
#  Create the sub-DAG for removing multiple columns within a table.
#
###################################################################

def sub_postgres_bulk_dump(
    postgres_table_name: str,
    postgres_conn_name: str,
    parent_dag_name: str,
    child_dag_name: str,
    temp_folder_path: str,
    temp_file_path: str,
    args: DAGConfig
    ):
    
    """
    Summary: 
       This subdag pulls the data from the Postgres table and
       inserts it into a MySQL table.

    Args:
        postgres_table_name (str): This is name of the Postgres 
            Table.
        postgres_conn_name (str): This is the Connection ID to 
            the PostgreSQL database used for this pipeline.
        parent_dag_name (str): This is the parent DAG for 
            this pipeline.
        child_dag_name (str): This is the child DAG name for 
            this subdag of task(s).
        temp_folder_path (str): This is path to the temporary 
            subdirectory/folder used to store the dataset in between 
            transfer between PostgreSQL and MySQL.
        temp_file_path (str): This is path to the temporary 
            file where the dataset is stored in between transfer 
            from PostgreSQL to MySQL.
        args (dict[str, str]): These are the default arguments. 
            They are the same exact default arguments as the 
            arguments used in the main DAG.

    Returns:
        sub_dag_remove_multiple_columns (DAG [or SubDAG]): This 
        function returns the subDAG that was created in this file.
    """
    
    #################################################################
    #
    #  Define DAG to use for this subdag.
    #
    #################################################################
    
    transfer_postgres_to_mysql_subdag = DAG(
        dag_id=f"{parent_dag_name}.{child_dag_name}",
        default_args=args,
        start_date=datetime(2024, 1, 1),
        catchup=False,
        schedule_interval='@once'
    )
    
    def main_postgres_to_mysql_subdag(
        postgres_conn_name: str,
        pg_table_name: str,
        temp_folder_path: str,
        temp_file_path: str
        ):
        
        # create the file
        if not os.path.exists(temp_folder_path):
            os.mkdir(temp_folder_path)
        
        pg_hook = PostgresHook(
            postgres_conn_id=postgres_conn_name
            )
        
        pg_hook.bulk_dump(
            table=pg_table_name, 
            tmp_file=temp_file_path
            )
    
    PythonOperator(
        task_id=f"transfer_postgres_to_mysql",
        python_callable=main_postgres_to_mysql_subdag,
        op_kwargs={
            "postgres_conn_name": postgres_conn_name,
            "temp_folder_path": temp_folder_path,
            "temp_file_path": temp_file_path,
            "pg_table_name": postgres_table_name,
            },
        dag=transfer_postgres_to_mysql_subdag
    )
    
    return transfer_postgres_to_mysql_subdag
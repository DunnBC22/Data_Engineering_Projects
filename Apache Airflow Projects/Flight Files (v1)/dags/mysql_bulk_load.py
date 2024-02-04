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

from airflow import DAG
from datetime import datetime

from airflow.operators.python_operator import PythonOperator
from airflow.hooks.mysql_hook import MySqlHook

from dag_config_class import DAGConfig

###################################################################
#
#  Create the sub-DAG for removing multiple columns within a table.
#
###################################################################

def subdag_mysql_bulk_load(
    mysql_table_name: str,
    mysql_conn_name: str,
    parent_dag_name: str,
    child_dag_name: str,
    temp_file_path: str,
    args: DAGConfig
    ):
    
    """
    Summary: 
       This subdag pulls the data from the Postgres table and
       inserts it into a MySQL table.

    Args:
        mysql_table_name (str): This is name of the Postgres 
            Table.
        mysql_conn_name (str): This is the Connection ID to 
            the MySQL database used for the transfer in this 
            pipeline.
        parent_dag_name (str): This is the parent DAG for 
            this pipeline.
        child_dag_name (str): This is the child DAG name for 
            this subdag of task(s).
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
    
    mysql_bulk_load = DAG(
        dag_id=f"{parent_dag_name}.{child_dag_name}",
        default_args=args,
        start_date=datetime(2024, 1, 1),
        catchup=False,
        schedule_interval='@once'
    )
    
    def mysql_load_subdag(
        mysql_table_name: str,
        mysql_conn_name: str,
        temp_file_path: str
        ):
        
        # Define MySQL Hook
        mysql_hook = MySqlHook(
            mysql_conn_id=mysql_conn_name, 
            local_infile=True
        )
        
        # use Bulk Load function to load data from tsv file to table
        mysql_hook.bulk_load(
            table=mysql_table_name,
            tmp_file=temp_file_path
        )
    
    PythonOperator(
        task_id=f"mysql_bulk_import",
        python_callable=mysql_load_subdag,
        op_kwargs={
            "mysql_conn_name": mysql_conn_name,
            "temp_file_path": temp_file_path,
            "mysql_table_name": mysql_table_name
            },
        dag=mysql_bulk_load
    )
    
    return mysql_bulk_load
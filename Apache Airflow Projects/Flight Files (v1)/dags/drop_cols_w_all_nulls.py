"""
#################################################################
#
#  Author: Brian Dunn
#
#  Approx. Date Completed: 01-04-2024
#
#  This subdag will remove columns that are all null values.
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
from airflow.hooks.mysql_hook import MySqlHook

from dag_config_class import DAGConfig

#################################################################
#
#  This subdag will remove columns that are all null values.
#
#################################################################

def subdag_drop_cols_of_all_nulls(
    table_name: str,
    parent_dag_name: str,
    child_dag_name: str,
    mysql_conn_name: str,
    args: DAGConfig
    ):
    
    """
    Summary: 
       This subdag will remove columns that are all null values.

    Args:
        table_name (str): This is the table name.
        parent_dag_name (str): This is the parent DAG for 
            this pipeline.
        child_dag_name (str): This is the child DAG name for 
            this subdag of task(s).
        mysql_conn_name (str): This is the Connection ID to 
            the MySQL database used for this pipeline.
        args (dict[str, str]): These are the default arguments. 
            They are the same exact default arguments as the 
            arguments used in the main DAG.

    Returns:
        sub_dag_remove_multiple_columns (DAG [or SubDAG]): This 
        function returns the subDAG that was created in this file.
    """
    
    subdag_remove_cols_w_all_nulls = DAG(
        dag_id=f"{parent_dag_name}.{child_dag_name}",
        default_args=args,
        start_date=datetime(2024, 1, 1),
        catchup=False,
        schedule_interval='@once',
        )

    def remove_cols_w_all_null_values(
        table_name: str, 
        mysql_conn_name: str
        ):
        
        # Connect to MySQL
        hook = MySqlHook(mysql_conn_id=mysql_conn_name)
        conn = hook.get_conn()
        cursor = conn.cursor()

        # Get the list of columns in the table
        query_columns = f"SELECT * FROM {table_name} LIMIT 1"
        cursor.execute(query_columns)
        columns = [desc[0] for desc in cursor.description]
        
        # Remove columns with all null values
        for column in columns:
            query_null_check = f"SELECT COUNT(*) FROM {table_name} WHERE {column} IS NOT NULL"
            cursor.execute(query_null_check)
            count_non_null = cursor.fetchone()[0]
            
            if count_non_null == 0:
                query_remove_column = f"ALTER TABLE {table_name} DROP COLUMN {column}"
                cursor.execute(query_remove_column)

        # Commit and close the connection
        conn.commit()
        cursor.close()
        conn.close()

    remove_cols_w_all_nulls = PythonOperator(
        task_id='remove_cols_w_all_nulls',
        python_callable=remove_cols_w_all_null_values,
        op_kwargs={
            'table_name': table_name,
            'mysql_conn_name': mysql_conn_name
        },
        provide_context=True,
        dag=subdag_remove_cols_w_all_nulls
    )
    
    return subdag_remove_cols_w_all_nulls
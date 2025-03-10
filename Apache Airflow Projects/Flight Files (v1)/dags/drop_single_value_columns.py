"""
#################################################################
#
#  Author: Brian Dunn
#
#  Approx. Date Completed: 12-28-2023
#
#  Create subdag to drop columns with only one distinct values.
#    
#################################################################
"""

#################################################################
#
#  Import Necessary Libraries.
#
#################################################################

from __future__ import annotations
from airflow import DAG

from airflow.operators.python_operator import PythonOperator
from airflow.hooks.mysql_hook import MySqlHook

from datetime import datetime
from dag_config_class import DAGConfig

#################################################################
#
#  Create subdag to drop columns with only one distinct values.
#
#################################################################

def sub_dag_remove_single_value_columns(
    table_name: str,
    parent_dag_name: str,
    child_dag_name: str,
    mysql_conn_name: str,
    args: DAGConfig
    ):
    """
    Summary: 
       Create subdag to drop columns with only one distinct values.

    Args:
        table_name (str): This is the name of the pipeline table.
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
        subdag_remove_single_value_columns (DAG [or SubDAG]): This 
        function returns the subDAG that was created in this file.
    """

    subdag_remove_single_value_columns = DAG(
        dag_id=f"{parent_dag_name}.{child_dag_name}",
        default_args=args,
        start_date=datetime(2024, 1, 1),
        catchup=False,
        schedule_interval='@once',
        )
    
    def remove_single_value_columns( 
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

        # Remove columns if all values in that column are the same
        for column in columns:
            query_distinct_values = f"SELECT COUNT(DISTINCT {column}) FROM {table_name}"
            cursor.execute(query_distinct_values)
            count_distinct_values = cursor.fetchone()[0]

            if count_distinct_values == 1:
                query_remove_column = f"ALTER TABLE {table_name} DROP COLUMN {column}"
                cursor.execute(query_remove_column)

        # Commit and close the connection
        conn.commit()
        cursor.close()
        conn.close()
    
    remove_single_value_cols = PythonOperator(
        task_id='remove_single_value_cols',
        python_callable=remove_single_value_columns,
        provide_context=True,
        dag=subdag_remove_single_value_columns,
        op_kwargs={
            'table_name': table_name,
            'mysql_conn_name': mysql_conn_name
        }
    )
    
    remove_single_value_cols

    return subdag_remove_single_value_columns

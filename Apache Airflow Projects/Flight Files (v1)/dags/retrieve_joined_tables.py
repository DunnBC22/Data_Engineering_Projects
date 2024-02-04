"""
#################################################################
#
#  Author: Brian Dunn
#
#  Approx. Date Completed: 01-10-2024
#
#  This subdag returns a single pipeline table that is the result 
#  of concatenating two or more tables.
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

#################################################################
#
#  This subdag returns a single pipeline table that is the  
#  result of concatenating two or more tables.
#
#################################################################

def retrieve_concatenated_pipeline_table(
    new_table_name: str,
    input_table_names: list[str],
    parent_dag_name: str, 
    child_dag_name: str,
    db_conn_name: str,
    args: DAGConfig
    ) -> DAG:

    """
    Summary:
        This subdag returns a single pipeline table that is the 
        result of concatenating two or more tables.

    Args:
        new_table_name (str): This is the name of the main 
            pipeline for the entire pipeline (once created via 
            UNION operator of multiple tables).
        input_table_names (list[str]): This is the list of table 
            names that will be added to the main pipeline table.
        parent_dag_name (str): This is the parent DAG for 
            this pipeline.
        child_dag_name (str): This is the child DAG name for 
            this subdag of task(s).
        db_conn_name (str): This is the Connection ID to 
            the PostgreSQL database used for this pipeline.
        args (dict[str, str]): These are the default arguments. 
            They are the same exact default arguments as the 
            arguments used in the main DAG.

    Returns:
        
    """

    #################################################################
    #
    #  This is the definition of the DAG, which will be referenced 
    #  later in the PythonOperator.
    #
    #################################################################

    retrieve_concat_pipeline_table_subdag = DAG(
        dag_id=f"{parent_dag_name}.{child_dag_name}",
        default_args=args,
        start_date=datetime(2024, 1, 1),
        catchup=False,
        schedule_interval="@once"
    )
    
    #################################################################
    #
    #  This function is the function that the PythonOperator will 
    #  call to complete this task.
    #
    #################################################################

    def concatenate_tables(
        target_table: str, 
        source_tables: list[str],
        db_conn_name: str
        ):
        
        # Create the SQL query
        sql_query = f'INSERT INTO {target_table} SELECT * FROM '

        # Add UNIONS for each additional table (dynamically) 
        for source_table in source_tables:
            sql_query += f'"{source_table}" UNION ALL SELECT * FROM '

        # Remove the trailing " UNION ALL SELECT * FROM "
        sql_query = sql_query[:-25]
        
        postgres_hook = PostgresHook(postgres_conn_id=db_conn_name)
        
        pg_conn = None
        pg_cursor = None
        
        try:
            pg_conn = postgres_hook.get_conn()
            pg_cursor = pg_conn.cursor()
            
            pg_cursor.execute(sql_query)
            
            pg_cursor.commit()
        except:
            pass
        finally:
            if pg_cursor:
                pg_cursor.close()
            if pg_conn:
                pg_conn.close()
            
        postgres_hook.run(sql_query)
    
    #################################################################
    #
    #  Define PythonOperator that executes the concatenate_tables 
    #  function & insert this operator/task into the (sub)dag.
    #
    #################################################################
    
    concatenate_task = PythonOperator(
        task_id='return_main_pipeline_table',
        python_callable=concatenate_tables,
        op_kwargs={
            'target_table': new_table_name, 
            'source_tables': input_table_names,
            'db_conn_name': db_conn_name
            },
        provide_context=True,
        dag=retrieve_concat_pipeline_table_subdag,
    )
    
    #################################################################
    #
    #  Return the subdag.
    #
    #################################################################
    
    return retrieve_concat_pipeline_table_subdag
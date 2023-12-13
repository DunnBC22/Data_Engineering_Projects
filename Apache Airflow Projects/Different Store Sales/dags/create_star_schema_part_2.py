"""
#################################################################
#
#  Author: Brian Dunn
#
#  Approx. Date Completed: 12-15-2023
#
#  This sub-DAG converts a single table into a star schema.
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
from airflow.operators.dummy_operator import DummyOperator

from dag_config_class import DAGConfig


##################################################################
#
#  This sub-DAG creates dimension tables from categorical values.
#
##################################################################


def sub_dag_create_star_schema(table_name: str,
                               column_names: list[dict[str, str]],
                               parent_dag_name: str, 
                               child_dag_name: str,
                               postgres_conn_name: str,
                               args: DAGConfig
                               ):
    """
    Summary:
        This subdag adds a new column in the fact table that will
        be the foreign key that is associated with the primary key 
        (id) of the dimension table. Then, it uses the dimension 
        tables that were created in part 1 to fill the foreign key 
        column in the fact table with the correct id number.

    Args:
        table_name (str): This is the name of the main fact table.
        column_names list[dict[str, str]]: This is a list of 
            dictionaries. Each dictionary contains the column name 
            and data type of a column (from the original table) that 
            needs to be addressed (when converting a table to 
            star schema).
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
    
    sub_dag_create_dim = DAG(
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
            "dimension_col": col['col_name']
        }
        
        column_name = col['col_name']
        
        start_task = DummyOperator(
            task_id=f'start_of_insert_fk_in_fact_table_for_{column_name}',
            dag=sub_dag_create_dim,
        )
        
        insert_fk_in_fact_table = PostgresOperator(
            task_id=f'insert_fk_col_in_fact_table_{column_name}',
            sql="/sql/insert_fk_col_in_fact_table.sql",
            postgres_conn_id=postgres_conn_name,
            dag=sub_dag_create_dim,
            params=dim_table_params
        )
        
        end_task = DummyOperator(
            task_id=f'end_of_insert_fk_in_fact_table_for_{column_name}',
            dag=sub_dag_create_dim,
        )

        (
            start_task
            >> insert_fk_in_fact_table 
            >> end_task
        )

    return sub_dag_create_dim
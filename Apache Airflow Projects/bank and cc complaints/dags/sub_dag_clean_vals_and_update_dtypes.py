"""
#################################################################
#
#  Author: Brian Dunn
#
#  Approx. Date Completed: 11-25-2023
#
#  Create sub-DAG to both remove letters from columns that 
#  should be numerical and then update data type.
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

#################################################################
#
#  Create the sub-DAG to remove letters from decimals & 
#  change column's data type.
#
#################################################################

def sub_dag_clean_vals_and_update_dtypes(table_name: str,
                                         column_names: list[str],
                                         new_dtype: str,
                                         parent_dag_name: str,
                                         child_dag_name: str,
                                         postgres_conn_name: str,
                                         args: DAGConfig
                                         ):
    """
    Summary: 
       This subdag will remove letters (and whitespace) from
       what should be numerical values.

    Args:
        table_name (str): This is the name of the main 
            DAG for the entire pipeline.
        column_names (list[str]): These are the columns from 
            which to remove erroneous values and of which to 
            change data types.
        new_dtype (str): This is the data type to convert 
            the columns to after removing erroneous character 
            in them.
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
        sub_dag_clean_vals_and_update_dtypes (DAG [or SubDAG]): 
            This function returns the subDAG that was created 
            in this file.
    """
    
    
    sub_dag_clean_vals_update_dtypes = DAG(
        dag_id=f"{parent_dag_name}.{child_dag_name}",
        default_args=args,
        start_date=datetime(2023, 12, 1),
        catchup=False,
        schedule_interval='@once',
        )
        
    for col in column_names:
        PostgresOperator(
            task_id=f"{child_dag_name}.clean_letters_from_{col}",
            postgres_conn_id=postgres_conn_name,
            sql="/sql/remove_chars_from_decimals.sql",
            params={
                "table_name": table_name,
                "col_name": col
                },
            dag=sub_dag_clean_vals_update_dtypes
        )
        
        # params: table_name, col_name_to_update, new_data_type
        PostgresOperator(
            task_id=f"{child_dag_name}.make_{col}_decimal",
            postgres_conn_id=postgres_conn_name,
            sql="/sql/convert_data_type_of_column.sql",
            params={
                "table_name": table_name,
                "col_name_to_update": col,
                "new_data_type": new_dtype
                },
            dag=sub_dag_clean_vals_update_dtypes
        )
    
    return sub_dag_clean_vals_update_dtypes
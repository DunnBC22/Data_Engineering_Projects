"""
#################################################################
#
#  Author: Brian Dunn
#
#  Approx. Date Completed: 11-25-2023
#
#  Create sub-DAG to remove outliers from multiple columns 
#  using predetermined/fixed values that are included in the 
#  input parameters.
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


##################################################################
#
#  Create the sub-DAG remove outliers using a predefined common 
#  sense limit.
#
##################################################################


def sub_dag_remove_outliers_fixed_vals(table_name: str,
                                       cols_w_fixed_ranges: list[dict(str, str)],
                                       parent_dag_name: str, 
                                       postgres_conn_name: str,
                                       child_dag_name: str,
                                       args: DAGConfig
                                       ) -> DAG:
    """ 
    Summary: 
        This subdag remove outliers using a predetermined/fixed 
        value.

    Args:
        table_name (str): This is the name of the main 
            DAG for the entire pipeline.
        cols_w_fixed_ranges (list[dict(str, str)]): This is
            the column names, operators and comparison values 
            for creating the Postgres Statements to remove
            outliers based on predetermined ranges/values.
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
        sub_dag_remove_outliers_fixed_vals (DAG): This function 
            returns the subDAG that was created in this file.
    """
    
        
    #################################################################
    #
    #  Define the DAG (that will be referenced later).
    #    
    #################################################################
    
    
    remove_outliers_predetermined_values = DAG(
        dag_id=f"{parent_dag_name}.{child_dag_name}",
        default_args=args,
        start_date=datetime(2023, 12, 1),
        catchup=False,
        schedule_interval='@once',
    )
    
    
    #################################################################
    #
    #  Iterate through each column in the inputted list of 
    #  dictionaries and remove samples that are outliers.
    #    
    ################################################################# 
    
    
    for col in cols_w_fixed_ranges:
        column_name = col['column_name']
        
        PostgresOperator(
            task_id=f"{column_name}-remove_outliers_common_sense",
            postgres_conn_id=postgres_conn_name,
            sql="sql/remove_outliers_common_sense.sql",
            params={
                "table_name": table_name, 
                "col_name": col["column_name"], 
                "operator": col["operator"], 
                "comparison_value": col["comparison_value"]
                },
            dag=remove_outliers_predetermined_values)
    
    
    #################################################################
    #
    #  Return the subdag.
    #    
    ################################################################# 
    
    
    return remove_outliers_predetermined_values
    
    
    
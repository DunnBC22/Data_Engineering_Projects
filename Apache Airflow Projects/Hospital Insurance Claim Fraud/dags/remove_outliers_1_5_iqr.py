"""
#################################################################
#
#  Author: Brian Dunn
#
#  Approx. Date Completed: 11-25-2023
#
#  Create sub-DAG to remove outliers from multiple columns 
#  using the IQR * 1.5 method.
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

from sqlalchemy import create_engine

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

from dag_config_class import DAGConfig


##################################################################
#
#  Create the sub-DAG remove outliers using the IQR * 1.5 method.
#
##################################################################


def sub_dag_remove_outliers_1_5_iqr(table_name: str,
                                    column_names: list[str],
                                    id_column_name: str,
                                    parent_dag_name: str, 
                                    postgres_conn_name: str,
                                    child_dag_name: str,
                                    args: DAGConfig
                                    ) -> DAG:
    """ 
    Summary: 
        This subdag remove outliers using the 
        IQR * 1.5 method.

    Args:
        table_name (str): This is the name of the main 
            DAG for the entire pipeline.
        column_names (list[str]): This is a list of column 
            names that need to be iterated through for 
            finding and removing outliers.
        id_column_name (str): The id column name
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
        remove_outliers_1_5_iqr_sub_dag (DAG): This function 
            returns the subDAG that was created in this file.
    """
    
    #################################################################
    #
    #  Import Pandas library
    #    
    #################################################################
    
    import pandas as pd
    
    #################################################################
    #
    #  Create DAG (which will be referenced later)
    #    
    #################################################################
    
    remove_outliers_1_5_iqr_sub_dag = DAG(
        dag_id=f"{parent_dag_name}.{child_dag_name}",
        default_args=args,
        start_date=datetime(2023, 12, 1),
        catchup=False,
        schedule_interval='@once',
        )
    
    #################################################################
    #
    #  Create function that collects & compiles the table of outlier 
    #  records across all of the columns that were input to this 
    #  subdag.
    #    
    #################################################################
    
    def detect_outliers(
        df: pd.DataFrame, 
        column_names: list[str],
        id_col_name: str
        ) -> pd.DataFrame:
        """
        Identify outliers using the 1.5 * IQR method for a specific column.
        Returns a DataFrame with outlier records for.
        """
        
        outliers_df = pd.DataFrame()
        
        for column in column_names:
            df[column] = pd.to_numeric(df[column], errors='coerce')
            
            q1 = df[column].quantile(0.25)
            q3 = df[column].quantile(0.75)
            
            iqr = q3 - q1
            
            lower_bound = q1 - (1.5 * iqr)
            upper_bound = q3 + (1.5 * iqr)
            
            column_outliers = df[
                (df[column] < lower_bound) | (df[column] > upper_bound)
                ]
            
            outliers_df = pd.concat(
                [outliers_df, column_outliers], 
                ignore_index=True
                )
        
        #################################################################
        #
        #  Filter out duplicate index column values (to avoid potential 
        #  errors later)
        #    
        #################################################################    
        
        distinct_outliers_df = outliers_df.drop_duplicates(
            subset=[id_col_name]
            )

        return distinct_outliers_df

    
    #################################################################
    #
    #  Main function to remove outliers using the 1.5 * IQR method.
    #    
    #################################################################
    
    def process_fact_table(
        postgres_conn_name: str,
        table_name: str,
        column_names: list[str],
        id_col_name: str
        ):
        
        """
        Retrieve records from the specified table, 
        identify outliers, create outliers table, and
        delete outliers from the specified table.
        """
        
        #################################################################
        #
        #  Define Postgresql Hook & create SQLAlchemy engine
        #    
        #################################################################
        
        postgres_hook = PostgresHook(postgres_conn_name)
        engine = postgres_hook.get_sqlalchemy_engine()
        
        #################################################################
        #
        #  Retrieve records from specified table 
        #    
        #################################################################
        
        fact_query = f"SELECT * FROM {table_name};"
        
        df = pd.read_sql(
            fact_query, 
            engine
            )

        #################################################################
        #
        #  Create outliers table with outliers inserted
        #    
        #################################################################
        
        outliers_df = detect_outliers(
            df, 
            column_names,
            id_col_name
            )
        
        #################################################################
        #
        #  Convert the dataframe of outliers to SQL
        #    
        #################################################################
        
        outliers_df.to_sql(
            'outliers_table', 
            engine, 
            if_exists='replace', 
            index=False
            )
        
        #################################################################
        #
        #  Delete the outliers that were previously collected
        #    
        #################################################################
        
        # Delete outliers from the specified table
        for index, row in outliers_df.iterrows():
            delete_query = f"DELETE FROM {table_name} WHERE {id_col_name} = {row[id_col_name]};"
            engine.execute(delete_query)

        print("Outliers processed and deleted.")
    
    #################################################################
    #
    #  Run the code that was created above in a PythonOperator
    #    
    #################################################################    
    
    process_outlier_removal = PythonOperator(
        task_id='process_fact_table',
        python_callable=process_fact_table,
        op_kwargs={
            "postgres_conn_name": postgres_conn_name,
            "table_name": table_name,
            "column_names": column_names,
            "id_col_name": id_column_name
            },
        provide_context=True,
        dag = remove_outliers_1_5_iqr_sub_dag
    )
    
    #################################################################
    #
    #  Return subdag.
    #    
    #################################################################

    return remove_outliers_1_5_iqr_sub_dag
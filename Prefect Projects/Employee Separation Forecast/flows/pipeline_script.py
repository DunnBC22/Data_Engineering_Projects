###################################################################
#
#       Prefect Pipeline for Employee Separation Forecast
#
###################################################################

import os, re, string
from typing import List

from prefect import task, flow
from prefect_sqlalchemy import (
    SqlAlchemyConnector, 
    ConnectionComponents, 
    SyncDriver
    )
from prefect.context import get_run_context
from sqlalchemy import create_engine, text

import polars as pl

from pymongo import MongoClient

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

###################################################################
#                              Tasks
###################################################################

@task
def create_pg_connector():
    # Postgres Source Block
    pg_connector = SqlAlchemyConnector(
        connection_info=ConnectionComponents(
            driver=SyncDriver.POSTGRESQL_PSYCOPG2,
            username="pg",
            password="pg",
            host="postgres",
            port=5432,
            database="employee_separation_forecast_pg_db"
        )
    )

    # Save connector
    pg_connector.save("pg-connector", overwrite=True)
    return pg_connector

@task
def fetch_data(
    table_name: str,
    connector_name: str = "pg-connector"
    ) -> pl.DataFrame:
    """
    This function/task retrieves data from a Postgres table (as passed in
    via the function/task argument) and puts it into a Polars DataFrame.
    
    Args:
        table_name (str): The name of the table for which to look for the data.
        connector_name (str): The name of the connector for connecting to 
            the database to retrieve data.

    Returns:
        pl.DataFrame: DataFrame with the data from the database table.
    """
    # Load the saved connector block
    connector = SqlAlchemyConnector.load(connector_name)

    # Get the SQLAlchemy engine
    engine = connector.get_engine()

    # Define the query
    query = f"SELECT * FROM {table_name}"

    # Use engine to execute query & read with Polars
    with engine.connect() as conn:
        df = pl.read_database(query=query, connection=conn)
    
    return df

@task
def join_dataframes(
    df1: pl.DataFrame, 
    df2: pl.DataFrame, 
    on: str, 
    how: str = "inner"
    ) -> pl.DataFrame:
    """
    This function/task joins the two Polars DataFrames that are 
    passed into this function/task via the df1 and df2 parameters.
    
    This function/task is comparable to a SQL JOIN operation.
    
    Args:
        df1 (pl.DataFrame): Input Polars DataFrame
        df2 (pl.DataFrame): Input Polars DataFrame
        on (str): Column name on which to join DataFrames
        how (str): strategy for joining DataFrames

    Returns:
        pl.DataFrame: The joined DataFrame (df1 + df2 based on the passed in column name)
    """
    return df1.join(df2, on=on, how=how)

@task
def concat_dataframes(
    df1: pl.DataFrame, 
    df2: pl.DataFrame,
    how_to_concat: str = "vertical_relaxed"
    ) -> pl.DataFrame:
    """
    
    This function/task concatenates two Polars DataFrames that are 
    passed into this function/task via the df1 and df2 parameters.
    
    This function/task is comparable to a SQL JOIN operation.
    
    Args:
        df1 (pl.DataFrame): Input Polars DataFrame
        df2 (pl.DataFrame): Input Polars DataFrame
        how_to_concat (str): strategy for concatenating DataFrames

    Returns:
        pl.DataFrame: The concatenated DataFrame
    """
    return pl.concat([df1, df2], how=how_to_concat)

@task
def rename_columns(
    df: pl.DataFrame, 
    rename_map: dict[str, str]
    ) -> pl.DataFrame:
    """
    This function/task renames columns/features according to the 
    rename_map (a dictionary) that is passed into this 
    function/task.
    
    Args:
        df (pl.DataFrame): Input Polars DataFrame
        columns_to_drop (Dict[str, str]): Dictionary of values to rename where:
            - the key is the original column name
            - the values is the string value to which to change the column name.

    Returns:
        pl.DataFrame: DataFrame with the renamed columns.
    """
    return df.rename(rename_map)

@task
def drop_columns(
    df: pl.DataFrame, 
    columns_to_drop: list[str]
    ) -> pl.DataFrame:
    """
    This function/task drop columns/features that are passed in 
    via the columns_to_drop parameter. 
    
    Args:
        df (pl.DataFrame): Input Polars DataFrame
        columns_to_drop (List[str]): List of column names to 
            remove/drop/delete from the DataFrame

    Returns:
        pl.DataFrame: DataFrame with the columns (that were passed in) removed.
    """
    return df.drop(columns_to_drop)

@task
def clean_string_columns_remove_all_underscores_and_dashes(
    df: pl.DataFrame, 
    string_columns: list[str]
    ) -> pl.DataFrame:
    """
    This function/task removes all underscores and dashes for the 
    columns/features that are passed into this function/task.
    
    Args:
        df: Input Polars DataFrame
        string_columns: List of column names (strings) that need to have 
            this string cleaning function applied to it.
    
    Returns:
        A Polars DataFrame with the string columns cleaned.
    """
    # Apply cleanup operations on string columns
    for col in string_columns:
        df = df.with_columns([
            pl.col(col)
            .str.replace_all(r"[-_]", "")
            .alias(col)
        ])
    return df

@task
def clean_string_columns_replace_all_amp_with_and(
    df: pl.DataFrame, 
    string_columns: list[str]
    ) -> pl.DataFrame:
    """
    This function/task replaces all instances of '&' with 'And' for the 
    columns/features that are passed into this function/task.
    
    Args:
        df: Input Polars DataFrame
        string_columns: List of column names (strings) that need to have 
            this string cleaning function applied to it.
    
    Returns:
        A Polars DataFrame with the string columns cleaned.
    """
    # Apply cleanup operations on string columns
    for col in string_columns:
        df = df.with_columns([
            pl.col(col)
            .str.replace_all("&", "And", literal=True)
            .alias(col)
        ])
    return df

@task
def clean_string_columns_remove_all_ws(
    df: pl.DataFrame,
    string_columns: list[str]
    ) -> pl.DataFrame:
    """
    This function/task removes all whitespace for the 
    columns/features that are passed into this function/task.
    
    Args:
        df: Input Polars DataFrame
        string_columns: List of column names (strings) that need to have 
            this string cleaning function applied to it.
    
    Returns:
        A Polars DataFrame with the string columns cleaned.
    """
    # Apply cleanup operations on string columns
    for col in string_columns:
        df = df.with_columns([
            pl.col(col)
            .str.replace_all(r"\s+", "")
            .alias(col)
        ])
    return df

@task
def clean_values_using_dict(
    df: pl.DataFrame, 
    replacements_dict: dict
    ) -> pl.DataFrame:
    """
    Cleans a Polars DataFrame by applying column-specific 
    value replacements and transformations.

    Parameters:
    ----------
    df : pl.DataFrame
        - The Polars DataFrame to clean.
    replacements_dict : dict
        - A dictionary where:
            - Keys are column names (features) in the DataFrame.
            - Values are dictionaries mapping old values to new 
                values for replacement.

    Returns:
    -------
    pl.DataFrame
        - The updated Polars DataFrame with all specified 
            replacements and transformations applied.
    """
    return df.with_columns([
        pl.col(col).replace(replacement_dict).alias(col)
        for col, replacement_dict in replacements_dict.items()
        if col in df.columns
    ])

@task
def compute_statistics_with_histograms(
    df: pl.DataFrame,
    pdf_path: str = "transformed_data_report.pdf"
) -> tuple[dict, str]:
    """
    Returns descriptive statistics, histograms for numeric columns,
    bar charts for string columns, and a paginated PDF report.

    Args:
        df (pl.DataFrame): Polars DataFrame to analyze.
        pdf_path (str): Path to output PDF report.

    Returns:
        Tuple containing:
            - Dictionary with metadata and summary statistics
            - Path to the saved PDF report
    """
    num_rows = df.height
    num_cols = df.width
    column_names = df.columns
    null_counts_full = {col: df.select(pl.col(col).is_null().sum()).item() for col in df.columns}
    null_counts = {k: v for k, v in null_counts_full.items() if v > 0}
    dtype_counts = df.dtypes

    # Determine numeric and string columns
    numeric_types = {
        pl.Int8, pl.Int16, pl.Int32, pl.Int64,
        pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
        pl.Float32, pl.Float64
    }
    string_types = {pl.Utf8}
    
    numeric_cols = [col for col, dtype in zip(df.columns, df.dtypes) if dtype in numeric_types]
    string_cols = [col for col, dtype in zip(df.columns, df.dtypes) if dtype in string_types]

    # Numeric stats
    numeric_stats = df.select([
        pl.col(col).mean().alias(f"{col}_mean") for col in numeric_cols
    ] + [
        pl.col(col).std().alias(f"{col}_std") for col in numeric_cols
    ])

    histograms = {}
    bar_charts = {}

    with PdfPages(pdf_path) as pdf:
        # Histograms for numeric columns
        for col in numeric_cols:
            values = df[col].drop_nulls().to_numpy()
            plt.figure()
            plt.hist(values, bins=10, edgecolor='black')
            plt.title(f"Histogram of {col}")
            plt.xlabel(col)
            plt.ylabel("Frequency")
            pdf.savefig()
            plt.close()
            histograms[col] = values.tolist()

        # Bar charts for string columns
        for col in string_cols:
            counts = df[col].drop_nulls().value_counts().sort("count", descending=True).head(10)

            categories = counts[col].to_list()
            frequencies = counts["count"].to_list()
            plt.figure(figsize=(10, 6))
            plt.barh(categories, frequencies, color='skyblue')
            plt.title(f"Top 10 {col} Categories")
            plt.xlabel("Frequency")
            plt.ylabel(col)
            plt.gca().invert_yaxis()
            pdf.savefig()
            plt.close()
            bar_charts[col] = dict(zip(categories, frequencies))

        # Summary pages
        summary_lines = []
        summary_lines.append("Data Summary Report")
        summary_lines.append(f"Rows: {num_rows}, Columns: {num_cols}")
        summary_lines.append("")

        if null_counts:
            summary_lines.append("Null Counts (only columns with ≥ 1 null):")
            for k, v in null_counts.items():
                summary_lines.append(f"  {k}: {v}")
            summary_lines.append("")

        summary_lines.append("Data Types:")
        for col, dtype in zip(column_names, dtype_counts):
            summary_lines.append(f"  {col}: {dtype}")
        summary_lines.append("")

        if numeric_cols:
            summary_lines.append("Numeric Summary (mean and std):")
            for col in numeric_cols:
                mean_value = numeric_stats.select(f"{col}_mean").item()
                std_value = numeric_stats.select(f"{col}_std").item()
                summary_lines.append(f"  {col}: mean = {mean_value:.2f}, std = {std_value:.2f}")

        # Pagination
        lines_per_page = 40  # Adjust as needed
        for i in range(0, len(summary_lines), lines_per_page):
            fig, ax = plt.subplots(figsize=(8.5, 11))  # Letter size
            ax.axis('off')
            page_text = "\n".join(summary_lines[i:i+lines_per_page])
            ax.text(0, 1, page_text, verticalalignment='top', horizontalalignment='left', fontsize=10, wrap=True)
            pdf.savefig(fig)
            plt.close(fig)

    return {
        "num_rows": num_rows,
        "num_columns": num_cols,
        "column_names": column_names,
        "null_counts": null_counts,
        "dtypes": [str(dt) for dt in dtype_counts],
        "numeric_summary": numeric_stats.to_dict(as_series=False),
        # "histograms": histograms,
        # "bar_charts": bar_charts
    }, pdf_path

@task
def load_data_to_mongodb(
    df: pl.DataFrame, 
    mongo_uri: str, 
    db_name: str, 
    collection_name: str):
    """
    Inserts data from a Polars DataFrame into a MongoDB collection.

    Parameters:
        - df: Polars DataFrame containing the data to insert.
        - mongo_uri: MongoDB connection URI.
        - db_name: Name of the MongoDB database.
        - collection_name: Name of the collection to insert data into.
    """
    # Convert Polars DataFrame to list of dictionaries
    records = df.to_dicts()
    if not records:
        return

    # Connect to MongoDB and insert records
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]
    collection.insert_many(records)

###################################################################
#                              Flow
###################################################################

@flow(
    name="Employee Separation Forecast Dataset", 
    description="This pipeline transfers Employee Separation Forecast dataset from Postgres to MongoDB.",
    log_prints=True)
def pg_to_mongodb_flow(
    name: str = "default_run_name"
    ) -> list:
    """
    This defines the Prefect pipeline that 
        - Retrieves data from Postgres
        - Transforms the data
        - Sends the transformed data to MongoDB
    """
    
    context = get_run_context()
    flow_run = context.flow_run

    flow_run.name = f"Run-{name}"
    
    create_pg_connector()
    
    # Retrieve data
    df_start_train = fetch_data(
        table_name="train_ee_sep_forecast_pg_table",
        connector_name="pg-connector"
    )
    
    df_start_test_wo_results = fetch_data(
        table_name="test_wo_results_ee_sep_forecast_pg_table",
        connector_name="pg-connector"
    )
    
    df_start_test_results = fetch_data(
        table_name="test_results_ee_sep_forecast_pg_table",
        connector_name="pg-connector"
    )
    
    df_start_test = join_dataframes(
        df_start_test_wo_results, 
        df_start_test_results, 
        on="ID", 
        how="inner"
    )
    
    # Combine Training & Testing Datasets
    df_start = concat_dataframes(
        df_start_train, 
        df_start_test,
        how_to_concat="vertical_relaxed"
    )
    
    # Define rename mapping
    rename_map = {
        "ID": "Id",
        "Age": "EmpAge",
        "Department": "DepartmentName",
        "Education": "EducationLevel",
        "Gender": "EmpGender",
        "MaritalStatus": "EmpMaritalStatus",
        "PerformanceRating": "EmpPerformanceRating",
        "YearsWithCurrManager": "YearsWithCurrentManager"
    } 
    
    # Rename columns
    df_renamed = rename_columns(
        df_start, 
        rename_map
        )
    
    # Remove unnecessary Features
    columns_to_remove_private = [
        "StandardHours",
	    "Over18",
	    "EmployeeNumber"
    ]
    
    df_w_fewer_features = drop_columns(
        df_renamed, 
        columns_to_remove_private
        )
    
    df_all_amps_replaced_with_and = clean_string_columns_replace_all_amp_with_and(
        df_w_fewer_features,
        ["DepartmentName"]
    )
    
    df_underscores_dashes_removed = clean_string_columns_remove_all_underscores_and_dashes(
        df_all_amps_replaced_with_and,
        ["BusinessTravel"]
    )
    
    # Remove all whitespace
    cols_to_remove_ws = [
        "JobRole",
        "EducationField",
        "DepartmentName"
    ]
    
    df_w_o_ws = clean_string_columns_remove_all_ws(
        df_underscores_dashes_removed, 
        cols_to_remove_ws
    )
	
    dict_of_values_to_update = {
        "EmpGender": 
            {
                "Male": "M",
                "Female": "F"
            }
    }
    
    df_completed = clean_values_using_dict(
        df_w_o_ws,
        dict_of_values_to_update
    )
    
    # Return some metrics about the data in the pipeline
    stats, pdf_path = compute_statistics_with_histograms(df_completed)
    print("Stats Summary:", stats)
    print("PDF Report saved to:", pdf_path)
    
    # Send transformed data to MongoDB
    mongo_uri = "mongodb://mongodb_user:mongodb_password@mongodb:27017"
    mongodb_name = "employee_separation_forecast_mongo_db"
    mongodb_collection_name = "employee_separation_forecast_mongo_coll"

    load_data_to_mongodb(
        df_completed, 
        mongo_uri, 
        mongodb_name, 
        mongodb_collection_name
        )

###################################################################
#                           Run This Script
###################################################################

if __name__ == "__main__":
    pg_to_mongodb_flow()

###################################################################
#                   Additional Helpful Instructions
###################################################################

# Steps to run this pipeline:

# >> docker exec -it prefect-cli bash
# >> cd /root/flows
# >> prefect deploy pipeline_script.py:pg_to_mongodb_flow --name "Employee-Separation-Forecast-Deployment"
# >> python pipeline_script.py

# To view the Prefect dashboard:
#       http://localhost:4200
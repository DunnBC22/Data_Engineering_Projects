###################################################################
#
#          Prefect Pipeline for Airbnb Global Listings
#
###################################################################

import re
from typing import Dict, Any

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
def create_mariadb_connector():
    # MariaDB Target Block
    mariadb_connector = SqlAlchemyConnector(
        connection_info=ConnectionComponents(
            driver=SyncDriver.MYSQL_PYMYSQL,
            username="mariadb_user",
            password="mariadb_pass",
            host="mariadb",
            port=3306,
            database="most_watched_movies_and_tv_shows_mariadb_db"
        )
    )

    # Save connector
    mariadb_connector.save("mariadb-connector", overwrite=True)
    return mariadb_connector

@task
def fetch_data(
    table_name: str, 
    batch_size: int, 
    connector_name: str
    ) -> pl.DataFrame:
    """
    This function/task retrieves data from a database table in batches & 
    puts it into a Polars DataFrame.
    
    Args:
        table_name (str): The name of the table for which to look 
            for the data.
        batch_size (int): Size of each batch when retrieving data from 
            database table
        connector_name (str): Connector name (block name) to use for
            connecting to database.

    Returns:
        pl.DataFrame: DataFrame with the data from the database table.
    """
    # Load the Prefect block/connector
    connector = SqlAlchemyConnector.load(connector_name)
    
    # Initialize an empty list to hold the rows
    rows = []
    
    with connector.get_connection(begin=False) as conn:
        offset = 0
        while True:
            # Fetch a batch of rows
            query = text(f"SELECT * FROM {table_name} LIMIT {batch_size} OFFSET {offset}")
            batch = conn.execute(query).mappings().fetchall()
            if not batch:
                break
            # Convert each row to a dictionary and append to the rows list
            rows.extend([dict(row) for row in batch])
            offset += batch_size

    # Convert the list of rows to a Polars DataFrame
    df = pl.DataFrame(rows, infer_schema_length=None)

    return df

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
def remove_suffix(
    df: pl.DataFrame, 
    columns: list[str],
    suffix_to_remove: str
) -> pl.DataFrame:
    """
    Removes suffix from string values in specified columns.

    Args:
        df (pl.DataFrame): Input Polars DataFrame.
        columns (list): List of column names where suffix should be removed.
        suffix_to_remove (str): String suffix to remove from column values.

    Returns:
        pl.DataFrame: Updated DataFrame with suffixes removed.
    """
    # Escape any regex special characters in the suffix
    escaped_suffix = re.escape(suffix_to_remove)
    # Build a regex pattern to match the suffix at the end of the string
    pattern = rf'{escaped_suffix}$'

    for col in columns:
        df = df.with_columns(
            pl.col(col).cast(str).str.replace(pattern, '', literal=False).alias(col)
        )
    return df

@task
def clean_string_columns_remove_all_commas(
    df: pl.DataFrame,
    string_columns: list[str]
    ) -> pl.DataFrame:
    """
    This function/task removes all commas for the 
    columns/features that are passed into this function/task.
    
    Args:
        df: Input Polars DataFrame
        string_columns: List of column names (strings) from which to
            remove all commas.
    
    Returns:
        A Polars DataFrame with the string columns cleaned.
    """
    # Apply cleanup operations on string columns
    for col in string_columns:
        df = df.with_columns([
            pl.col(col)
            .str.replace_all(r",", "", literal=True)
            .alias(col)
        ])
    return df

@task
def impute_missing_values(
    df: pl.DataFrame, 
    imputations: Dict[str, Any]
    ) -> pl.DataFrame:
    """
    Imputes missing values for specified columns in the input Polars DataFrame.

    Parameters:
    ----------
    df : pl.DataFrame
        The input Polars DataFrame.
    imputations : dict
        A dictionary where keys are column names and values are the value to impute for missing data.

    Returns:
    -------
    pl.DataFrame
        The DataFrame with missing values imputed.
    """
    for col, value in imputations.items():
        if col in df.columns:
            df = df.with_columns(
                pl.col(col).fill_null(value).alias(col)
            )

    return df

@task
def cast_columns(
    df: pl.DataFrame, 
    column_casts: dict
    ) -> pl.DataFrame:
    """
    This function/task updates the column/feature data types according
    to the columns_casts dictionary that is passed into this function/task.
    
    Args:
        df (pl.DataFrame): Polars DataFrame to analyze.
        column_casts (dict): Dictionary where:
            - The keys are the column names to convert
            - The values are the data type in which to convert the column name (the key).

    Returns:
        A Polars DataFrame with column data types casted. 
    """
    # Cast selected columns
    for col, dtype in column_casts.items():
        df = df.with_columns(pl.col(col).cast(dtype).alias(col))
    return df

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

    numeric_types = {
        pl.Int8, pl.Int16, pl.Int32, pl.Int64,
        pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
        pl.Float32, pl.Float64
    }
    string_types = {pl.Utf8}

    numeric_cols = [col for col, dtype in zip(df.columns, df.dtypes) if dtype in numeric_types]
    string_cols = [col for col, dtype in zip(df.columns, df.dtypes) if dtype in string_types]

    numeric_stats = df.select([
        pl.col(col).mean().alias(f"{col}_mean") for col in numeric_cols
    ] + [
        pl.col(col).std().alias(f"{col}_std") for col in numeric_cols
    ])

    histograms = {}
    bar_charts = {}

    with PdfPages(pdf_path) as pdf:
        # Histograms
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

        # Bar charts
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

        # Summary
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
                mean_value = next(iter(numeric_stats.select(f"{col}_mean").to_series()), None)
                std_value = next(iter(numeric_stats.select(f"{col}_std").to_series()), None)
                mean_str = f"{mean_value:.2f}" if mean_value is not None else "N/A"
                std_str = f"{std_value:.2f}" if std_value is not None else "N/A"
                summary_lines.append(f"  {col}: mean = {mean_str}, std = {std_str}")

        # Pagination
        lines_per_page = 40
        for i in range(0, len(summary_lines), lines_per_page):
            fig, ax = plt.subplots(figsize=(8.5, 11))  # US Letter
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
        df: Polars DataFrame containing the data to insert.
        mongo_uri: MongoDB connection URI.
        db_name: Name of the MongoDB database.
        collection_name: Name of the collection to insert data into.
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
    name="Most Watched Movies and TV Shows Dataset", 
    description="""
    This pipeline transfers Most Watched Movies and 
    TV Shows dataset from MariaDB to MongoDB.""",
    log_prints=True)
def mariadb_to_mongodb_flow(
    name: str = "default_run_name"
    ) -> list:
    """
    This defines the Prefect pipeline that 
        - Retrieves data from MariaDB,
        - Transforms the data,
        - Sends the transformed data to MongoDB
    """
    
    context = get_run_context()
    flow_run = context.flow_run

    flow_run.name = f"Run-{name}"
    
    create_mariadb_connector()
    
    # Retrieve data
    df_start = fetch_data(
        table_name="most_watched_movies_and_tv_shows_mariadb_table", 
        batch_size=50_000, 
        connector_name="mariadb-connector"
    )
    
    rename_map = {
        "Rank": "MovieRank",
        "Title": "MovieTitle",
        "Type": "MovieType",
        "Premiere": "MoviePremiere",
        "Genre": "MovieGenre",
        "Watchtime": "MovieWatchtime",
        "Watchtime in Million": "MovieWatchtimeInMillions"
    } 
    
    # Rename columns
    df_renamed = rename_columns(
        df_start, 
        rename_map
        )
    
    col_cast_map = {
        "MovieRank": pl.Int32,
        "MovieTitle": pl.String,
        "MovieType": pl.String,
        "MoviePremiere": pl.Int32,
        "MovieGenre": pl.String,
        "MovieWatchtime": pl.String,
        "MovieWatchtimeInMillions": pl.String
    }
    
    df_casted = cast_columns(
        df_renamed,
        col_cast_map
    )
    
    df_movie_premiere_imputed = impute_missing_values(
        df_casted,
        {"MoviePremiere": 9999}
    )
    
    df_movie_genre_imputed = impute_missing_values(
        df_movie_premiere_imputed,
        {"MovieGenre": "NotListed"}
    )
    
    df_movie_watch_time_cleaned = clean_string_columns_remove_all_commas(
        df_movie_genre_imputed,
        ["MovieWatchtime"]
    )
    
    df_cleaned_suffix = remove_suffix(
        df_movie_watch_time_cleaned,
        columns=["MovieWatchtimeInMillions"],
        suffix_to_remove="M"
    )
	
    # Update Feature data types
    column_casts = {
        "MovieWatchtime": pl.Int64,
        "MovieWatchtimeInMillions": pl.Float32
    }
        
    df_completed = cast_columns(
        df_cleaned_suffix,
        column_casts
    )
    
    # Return some metrics about the data in the pipeline
    stats, pdf_path = compute_statistics_with_histograms(df_completed)
    print("Stats Summary:", stats)
    print("PDF Report saved to:", pdf_path)
    
    # Send transformed data to MongoDB
    mongo_uri = "mongodb://mongodb_user:mongodb_password@mongodb:27017/?authSource=admin"
    mongodb_name = "most_watched_movies_and_tv_shows_mongo_db"
    mongodb_collection_name = "most_watched_movies_and_tv_shows_mongo_coll"

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
    mariadb_to_mongodb_flow()

###################################################################
#                   Additional Helpful Instructions
###################################################################

# Steps to run this pipeline:

# >> docker exec -it prefect-cli bash
# >> cd /root/flows
# >> prefect deploy pipeline_script.py:mariadb_to_mongodb_flow --name "Most-Watched-Movies-TV-Shows-Deployment"
# >> python pipeline_script.py

# To view the Prefect dashboard:
#       http://localhost:4200
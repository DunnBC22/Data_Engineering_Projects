###################################################################
#
#    Prefect Pipeline for Insurance Disposition Classification
#
###################################################################

import os
from typing import List

from prefect import task, flow
from prefect_sqlalchemy import (
    SqlAlchemyConnector, 
    ConnectionComponents, 
    SyncDriver
)

from prefect.context import get_run_context

import polars as pl

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from elasticsearch import Elasticsearch, helpers

###################################################################
#                              Tasks
###################################################################

@task
def create_postgres_connector():
    """
    This function/task creates & saves the Postgres connector that is used
    when retrieving data from the source database table (in Postgres).
    """
    postgres_connector = SqlAlchemyConnector(
        connection_info=ConnectionComponents(
            driver=SyncDriver.POSTGRESQL_PSYCOPG2,
            username="pg",
            password="pg",
            host="postgres",
            port=5432,
            database="insurance_dispostion_clf_pg_db",
        )
    )
    
    # Save connector
    postgres_connector.save("pg-connector", overwrite=True)
    return postgres_connector

@task
def fetch_data(
    table_name: str
    ) -> pl.DataFrame:
    """
    This function/task retrieves data from a Postgres table (as passed in
    via the function/task argument) and puts it into a Polars DataFrame.
    
    Args:
        table_name (str): The name of the table for which to look for the data.

    Returns:
        pl.DataFrame: DataFrame with the data from the Postgres table.
    """
    # Load the saved connector block
    connector = SqlAlchemyConnector.load("pg-connector")

    # Get the SQLAlchemy engine
    engine = connector.get_engine()

    # Define the query
    query = f"SELECT * FROM {table_name}"

    # Use engine to execute query & read with Polars
    with engine.connect() as conn:
        df = pl.read_database(query=query, connection=conn)
    
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
        pl.DataFrame: DataFrame with the columns (that were passed in) renamed.
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
def convert_strings_to_dates(
    df: pl.DataFrame, 
    timestamp_cols: List[str] = ["timestamp"], 
    default_date: str = "01-01-1900"
) -> pl.DataFrame:
    """
    This function/task converts one or more timestamp columns in the DataFrame to datetime format (date and time).
    
    Parameters:
        - df: Polars DataFrame
        - timestamp_cols: List of column names to convert from string to datetime
        - default_date: The default value to impute for invalid or missing date values (default is '1900-01-01 00:00')

    Returns:
        - DataFrame with new columns replacing the original columns'
    """
    for col in timestamp_cols:
        # Attempt to convert to datetime
        df = df.with_columns(
            pl.when(pl.col(col).str.strptime(pl.Datetime, "%d-%m-%Y", strict=False).is_null())
            .then(pl.lit(default_date).str.strptime(pl.Date, "%d-%m-%Y"))
            .otherwise(pl.col(col).str.strptime(pl.Datetime, "%d-%m-%Y", strict=False))
            .alias(f"{col}")
        )
    return df

@task
def extract_date_parts(
    df: pl.DataFrame, 
    date_col: str = "date"
    ) -> pl.DataFrame:
    """
    Extracts date parts for each date column in the list `date_cols`.
    For each date column, it will add:
        - DayOfWeek
        - DayOfMonth
        - DayOfYear
        - Month
        - Quarter
        - Year
    
    Args:
        df: Input Polars DataFrame
        date_col: column name (strings) that this function/task
        will append columns and return elements of the date.
        
    Returns:
        A Polars DataFrame with the added columns for the following 
        elements of the date column that was passed into this function:
            - DayOfWeek
            - DayOfMonth
            - DayOfYear
            - Month
            - Quarter
            - Year
    """
    df = df.with_columns([
        pl.col(date_col).dt.weekday().alias(f"{date_col}_DayOfWeek"),
        pl.col(date_col).dt.day().alias(f"{date_col}_DayOfMonth"),
        pl.col(date_col).dt.ordinal_day().alias(f"{date_col}_DayOfYear"),
        pl.col(date_col).dt.month().alias(f"{date_col}_Month"),
        pl.col(date_col).dt.quarter().alias(f"{date_col}_Quarter"),
        pl.col(date_col).dt.year().alias(f"{date_col}_Year"),
    ])
    return df

@task
def clean_string_columns_remove_ltw(
    df: pl.DataFrame, 
    string_columns: list[str]
    ) -> pl.DataFrame:
    """
    This function/task cleans string values in the columns/features that 
    are passed into this function/task via the string_columns parameter.
    
    Cleans string values in specified columns by:
        1. Removing all whitespace
    
    Args:
        df: Input Polars DataFrame
        string_columns: List of column names (strings) that need to have 
            the string cleaning function applied to it.
    
    Returns:
        A Polars DataFrame with the string columns (that were passed in) cleaned.
    """
    # Apply cleanup operations on string columns
    for col in string_columns:
        df = df.with_columns([
            pl.col(col)
            .str.strip_chars()     # Remove leading/trailing spaces
            .alias(col)
        ])
    return df

@task
def clean_string_columns_remove_weird_chars(
    df: pl.DataFrame, 
    string_columns: list[str]
    ) -> pl.DataFrame:
    """
    This function/task cleans string values in the columns/features that 
    are passed into this function/task via the string_columns parameter.
    
    Cleans string values in specified columns by:
        1. Removing all leading and trailing non-alphanumerical characters
        2. Removing all leading and trailing whitespace 
        3. Converting to title case
    
    Args:
        df: Input Polars DataFrame
        string_columns: List of column names (strings) that need to have 
            the string cleaning function applied to it.
    
    Returns:
        A Polars DataFrame with the string columns (that were passed in) cleaned.
    """
    # Apply cleanup operations on string columns
    for col in string_columns:
        df = df.with_columns([
            pl.col(col)
            .str.replace(r"^[^a-zA-Z0-9]+", "") # Remove leading non-alphanumeric characters
            .str.replace(r"[^a-zA-Z0-9]+$", "") # Remove trailing non-alphanumeric characters
            .str.strip_chars()     # Remove leading/trailing spaces
            .str.to_titlecase()    # Convert to lowercase
            .alias(col)
        ])
    return df

@task
def clean_string_columns_remove_all_whitespace(
    df: pl.DataFrame, 
    string_columns: list[str]
    ) -> pl.DataFrame:
    """
    This function/task cleans string values in the columns/features that 
    are passed into this function/task via the string_columns parameter.
    
    Cleans string values in specified columns by:
        1. Removing all whitespace
    
    Args:
        df: Input Polars DataFrame
        string_columns: List of column names (strings) that need to have 
            the string cleaning function applied to it.
    
    Returns:
        A Polars DataFrame with the string columns (that were passed in) cleaned.
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
def calculate_days_between(
    df: pl.DataFrame, 
    start_date_col: str, 
    end_date_col: str, 
    output_col: str = "duration_days"
) -> pl.DataFrame:
    """
    Calculates the number of days between two date columns.

    Args:
        df: Input Polars DataFrame
        start_date_col: Column name representing the start date
        end_date_col: Column name representing the end date
        output_col: Name of the new column to store duration (in days)

    Returns:
        A Polars DataFrame with a new column containing the date differences
    """
    return df.with_columns([
        (pl.col(end_date_col) - pl.col(start_date_col)).dt.total_days().alias(output_col)
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
        "numeric_summary": numeric_stats.to_dict(as_series=False)
    }, pdf_path

@task
def send_data_to_elasticsearch(
    df: pl.DataFrame, 
    index_name: str, 
    es_host: str = "http://localhost:9200", 
    es_user: str = "elastic",
    es_password: str = "es_prefect_pass",
    batch_size: int = 5000
) -> None:
    """
    This function/task sends the transformed data (in Polars) to the
    Elasticsearch and places the data in the index that is passed 
    into this task/function it batches.
    
    Args:
        df (pl.DataFrame): Polars DataFrame of data to send to Elasticsearch.
        index_name (str): The name of the index in which to insert the data.
        es_host (str): host name and port number for the Elasticsearch target.
        es_user (str): Elasticsearch username to use to insert data.
        es_password (str): Elasticsearch password to use to insert data.
        batch_size (int): number of records per batch to insert.
    """
    es = Elasticsearch(
        es_host,
        basic_auth=(es_user, es_password),
        verify_certs=False  # Disable SSL verification for local/dev use
    )

    # Convert Polars DataFrame to list of dictionaries
    records = df.to_dicts()

    # Helper to yield chunks
    def chunked(iterable, size):
        for i in range(0, len(iterable), size):
            yield iterable[i:i + size]

    # Bulk insert in batches
    for chunk in chunked(records, batch_size):
        actions = [
            {
                "_index": index_name,
                "_source": record
            }
            for record in chunk
        ]
        helpers.bulk(es, actions)

###################################################################
#                              Flow
###################################################################

@flow(
    name="Insurance Disposition Classification Dataset", 
    description="This pipeline transfers Insurance Disposition Classification data from Postgres to Elasticsearch.", 
    log_prints=True)
def postgres_to_es_flow(
    name: str = "default_run_name"
    ) -> list:
    """
    This defines the Prefect pipeline that 
        - Retrieves data from Postgres
        - Transforms the data
        - Sends the transformed data to Elasticsearch
    """
    context = get_run_context()
    flow_run = context.flow_run

    flow_run.name = f"Run-{name}"  # Set name dynamically at runtime
    
    postgres_connector = create_postgres_connector()
    
    # Retrieve data
    df_claims = fetch_data("insur_claim_info_pg_table")
    
    df_dates = fetch_data("insur_date_data_pg_table")
    
    df_results = fetch_data("insur_result_data_pg_table")
    
    # Individual dataset Transformations
        # Rename columns
    claims_rename_mapping = {
        "Claim Number": "ClaimNumber",
        "City Code": "CityCode",
        "City": "CityName",
        "Enterprise Type": "EnterpriseType",
        "Claim Type": "ClaimType",
        "Claim Site": "ClaimSite",
        "Product Insured": "ProductInsured"
    }
    
    df_claims_renamed = rename_columns(
        df_claims, 
        claims_rename_mapping
        )
    
    dates_rename_mapping =  {
        "Claim Number": "ClaimNumber",
        "Incident Date": "IncidentDate",
        "Date Received"	: "DateReceived"
    }
    
    df_dates_renamed = rename_columns(
        df_dates, 
        dates_rename_mapping
        )
    
    results_rename_mapping = {
        "Claim Number": "ClaimNumber",
        "Claim Amount": "ClaimAmount",
        "Close Amount": "CloseAmount"
    }
    
    df_results_renamed = rename_columns(
        df_results, 
        results_rename_mapping
        )
    
    # Join DataFrames
    joined_df_part_a = join_dataframes(
        df_claims_renamed, 
        df_dates_renamed, 
        on="ClaimNumber", 
        how="inner"
        )
    
    joined_df = join_dataframes(
        joined_df_part_a, 
        df_results_renamed, 
        on="ClaimNumber", 
        how="inner"
    )
    
    # Remove Leading & Trailing Whitespace
    string_columns_remove_ltw = [
        "ClaimNumber",
        "CityCode",
        "CityName",
        "EnterpriseType",
        "ClaimType",
        "ClaimSite",
        "ProductInsured",
        "Disposition"
        ]
    
    df_w_o_lead_trail_ws = clean_string_columns_remove_ltw(
        df=joined_df, 
        string_columns=string_columns_remove_ltw
    )
    
    string_cols_to_remove_weird_chars = [
        "EnterpriseType",
        "ProductInsured"
    ]

    df_no_weird_chars = clean_string_columns_remove_weird_chars(
        df_w_o_lead_trail_ws,
        string_cols_to_remove_weird_chars
    )

    string_cols_remove_all_ws = [
        "ClaimType",
        "ClaimSite",
        "EnterpriseType",
        "ProductInsured"
    ]
    
    df_w_clean_strings = clean_string_columns_remove_all_whitespace(
        df_no_weird_chars,
        string_cols_remove_all_ws
    )
    
    # Convert String Features to Dates
    timestamp_cols_to_handle = [
        "IncidentDate",
        "DateReceived"
    ]
    
    df_dates_converted = convert_strings_to_dates(
        df_w_clean_strings, 
        timestamp_cols_to_handle
    )
    
    # Extract Date Parts
    df_w_extract_dates_IncidentDate_only = extract_date_parts(
        df_dates_converted,
        "IncidentDate"
    )
    
    df_w_extract_dates = extract_date_parts(
        df_w_extract_dates_IncidentDate_only,
        "DateReceived"
    )
    
    # Calculate Duration
    df_all_cleaned = calculate_days_between(
        df_w_extract_dates,
        start_date_col="DateReceived",
        end_date_col="IncidentDate",
        output_col="DaysToReport"
    )
    
    # Return some metrics about the data in the pipeline
    stats, pdf_path = compute_statistics_with_histograms(df_all_cleaned)
    print("Stats Summary:", stats)
    print("PDF Report saved to:", pdf_path)
    
    # Send transformed data to Elasticsearch
    send_data_to_elasticsearch(
        df_all_cleaned, 
        index_name="insurance_disposition_clf",
        es_host="http://elasticsearch:9200"
        )

###################################################################
#                           Run This Script
###################################################################

if __name__ == "__main__":
    postgres_to_es_flow()

###################################################################
#                   Additional Helpful Instructions
###################################################################

# Steps to run this pipeline:

# >> docker exec -it prefect-cli bash
# >> cd /root/flows
# >> prefect deploy pipeline_script.py:postgres_to_es_flow --name "Insurance-Disposition-Classification-Deployment"
# >> python pipeline_script.py

# To view the Prefect dashboard:
#       http://localhost:4200
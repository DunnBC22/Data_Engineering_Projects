###################################################################
#
#     Prefect Pipeline for Comprehensive Supply Chain Analysis
#
###################################################################

import os, re
from datetime import datetime
from typing import Optional, List

from prefect import task, flow
from prefect_sqlalchemy import SqlAlchemyConnector, ConnectionComponents, SyncDriver
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
def create_mariadb_connector():
    """
    This function/task creates & saves the mariadb connector that is used
    when sending the transformed data to the target database table (in MariaDB).
    """
    mariadb_connector = SqlAlchemyConnector(
        connection_info=ConnectionComponents(
            driver=SyncDriver.MYSQL_PYMYSQL,
            username="mariadb_user",
            password="mariadb_password",
            host="mariadb",
            port=3306,
            database="csca_mariadb_db"
        )
    )

    # Save connector
    mariadb_connector.save("mariadb-connector", overwrite=True)
    return mariadb_connector

@task
def fetch_data_from_elasticsearch(
    index_name: str, 
    es_host: str = "http://elasticsearch:9200"
    ) -> pl.DataFrame:
    """
    This function/task that retrieves data from the Elasticsearch 
    Index as provided as the input.
    
    Args:
        index_name (str): The name of the index for which to look for the data.
        es_host (str): The data source (host name & port number).

    Returns:
        pl.DataFrame: DataFrame with the data from the Elasticsearch Index.
    """
    es = Elasticsearch(es_host, basic_auth=("elastic", "es_prefect_pass"))

    # Use a scroll to retrieve all documents
    results = []
    scroll = es.search(index=index_name, scroll='2m', size=1000, body={"query": {"match_all": {}}})

    sid = scroll['_scroll_id']
    hits = scroll['hits']['hits']
    
    while hits:
        for doc in hits:
            results.append(doc['_source'])
        
        scroll = es.scroll(scroll_id=sid, scroll='2m') 
        sid = scroll['_scroll_id']
        hits = scroll['hits']['hits']

    # Convert to Polars DataFrame
    return pl.DataFrame(results)

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
def clean_and_convert_date_strings(
    df: pl.DataFrame,
    timestamp_cols: List[str] = ["timestamp"],
    default_date: str = "1900-01-01"
) -> pl.DataFrame:
    """
    Cleans and converts inconsistent date strings to 'YYYY-MM-DD' format.

    Handles:
        - 1 or 2 digit day/month
        - 2 or 4 digit years
        - Ignores time component if present
        - Invalid or missing values are replaced with `default_date`

    Args:
        df (pl.DataFrame): Input Polars DataFrame
        timestamp_cols (List[str]): List of column names to clean
        default_date (str): Default fallback date

    Returns:
        pl.DataFrame: DataFrame with cleaned date columns
    """
    def clean_and_parse_date(
        value: Optional[str]
        ) -> Optional[str]:
        if not value or not isinstance(value, str):
            return default_date
        try:
            # Match date at start (ignore time if present)
            match = re.match(r"(\d{1,2})/(\d{1,2})/(\d{2,4})", value.strip())
            if not match:
                return default_date

            day, month, year = match.groups()

            # Normalize 2-digit years
            if len(year) == 2:
                year = "20" + year if int(year) < 50 else "19" + year

            # Pad day/month and convert to proper date format
            date_str = f"{int(day):02}-{int(month):02}-{year}"

            # Convert to datetime and return as 'YYYY-MM-DD'
            return datetime.strptime(date_str, "%d-%m-%Y").strftime("%Y-%m-%d")
        except Exception:
            return default_date

    for col in timestamp_cols:
        df = df.with_columns([
            df[col]
              .map_elements(clean_and_parse_date, return_dtype=pl.Utf8)
              .str.to_datetime("%Y-%m-%d", strict=False)
              .alias(col)
        ])

    return df

@task
def extract_date_parts(
    df: pl.DataFrame, 
    date_cols: List[str]
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
        date_cols: List of column names (strings) that this function/task
        will append columns and return elements of the dates.
        
    Returns:
        A Polars DataFrame with the added columns for the following 
        elements of the date columns that were passed into this function:
            - DayOfWeek
            - DayOfMonth
            - DayOfYear
            - Month
            - Quarter
            - Year
    """
    new_columns = []

    for date_col in date_cols:
        if date_col not in df.columns:
            continue  # Skip if the column isn't present

        new_columns.extend([
            pl.col(date_col).dt.weekday().alias(f"{date_col}_DayOfWeek"),
            pl.col(date_col).dt.day().alias(f"{date_col}_DayOfMonth"),
            pl.col(date_col).dt.ordinal_day().alias(f"{date_col}_DayOfYear"),
            pl.col(date_col).dt.month().alias(f"{date_col}_Month"),
            pl.col(date_col).dt.quarter().alias(f"{date_col}_Quarter"),
            pl.col(date_col).dt.year().alias(f"{date_col}_Year"),
        ])

    return df.with_columns(new_columns)

@task
def clean_string_columns(
    df: pl.DataFrame, 
    string_columns: list[str]
    ) -> pl.DataFrame:
    """
    This function/task cleans string values in the columns/features that 
    are passed into this function/task via the string_columns parameter.
    
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
            .str.replace_all(r"[\$,]", "") # remove $ and ,
            .str.strip_chars()
            .alias(col)
        ])
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
        A Polars DataFrame with a new column containing the date differences (in days).
    """
    df = df.with_columns([
        (pl.col(end_date_col).cast(pl.Date) - pl.col(start_date_col).cast(pl.Date))
        .alias(output_col)
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
def write_to_mariadb(
    df: pl.DataFrame, 
    table_name: str, 
    if_exists: str = "replace"
    ) -> None:
    """
    This function/task sends the transformed data (in Polars) to the MariaDB
    table that is named in the arguments passed into this function.
    
    Args:
        df (pl.DataFrame): Polars DataFrame to analyze.
        table_name (str): The name of the table in which to insert the data.
        if_exists (str): What to do if the table already exists.
    """
    # Load the saved MariaDB connector block
    connector = SqlAlchemyConnector.load("mariadb-connector")
    
    # Retrieve the SQLAlchemy engine
    engine = connector.get_engine()

    # Write the DataFrame to the specified table in MariaDB
    df.write_database(
        table_name=table_name, 
        connection=engine, 
        engine="sqlalchemy",
        if_table_exists=if_exists
    )

###################################################################
#                              Flow
###################################################################

@flow(
    name="Comprehensive Supply Chain Analysis Dataset", 
    description="This pipeline transfers Comprehensive Supply Chain Analysis from Elasticsearch to MariaDB.", 
    log_prints=True)
def es_to_mariadb_flow(
    name: str = "default_run_name"
    ) -> list:
    """
    This defines the Prefect pipeline that 
        - Retrieves data from Elasticsearch
        - Transforms the data
        - Sends transformed data to MariaDB
    """
    context = get_run_context()
    flow_run = context.flow_run

    flow_run.name = f"Run-{name}"  # Set name dynamically at runtime
    
    mariadb_connector = create_mariadb_connector()
    
    # Retrieve data
    df_start = fetch_data_from_elasticsearch(
        index_name="csca_data", 
        es_host = "http://elasticsearch:9200"
        )
    
    # Remove Unnecessary Features
    columns_to_remove = [
        "CurrencyCode"
        ]
    
    df_w_o_svf = drop_columns(
        df_start, 
        columns_to_remove
        )
    
    # Clean String-Valued Features
    string_feature_to_clean = [
        "UnitPrice",
        "UnitCost"
    ]

    # Clean the string columns
    df_strings_cleaned = clean_string_columns(
        df_w_o_svf, 
        string_feature_to_clean
        )
    
    # Convert UnitPrice from string to float
    features_cast = {
        "UnitPrice": pl.Float64,
        "UnitCost": pl.Float64
    }
    
    df_casted_features = cast_columns(
        df_strings_cleaned, 
        column_casts=features_cast
    )
    
    # convert string values to date data types after cleaning them
    string_date_features = [
        "ProcuredDate",
        "OrderDate",
        "ShipDate",
        "DeliveryDate"
    ]
    
    df_dates_as_dates = clean_and_convert_date_strings(
        df_casted_features, 
        string_date_features,
        default_date = "1900-01-01"
    )
    
    df_w_date_parts = extract_date_parts(
        df_dates_as_dates,
        date_cols=string_date_features
    )
    
    df_procured_to_delivery = calculate_days_between(
        df_w_date_parts, 
        start_date_col="ProcuredDate",
        end_date_col="DeliveryDate", 
        output_col = "ProcuredToDeliveryDays"
    )
    
    df_ordered_to_delivery = calculate_days_between(
        df_procured_to_delivery, 
        start_date_col="OrderDate", 
        end_date_col="DeliveryDate", 
        output_col = "OrderToDeliveryDays"
    )
    
    df_procured_to_ship = calculate_days_between(
        df_ordered_to_delivery, 
        start_date_col="ProcuredDate", 
        end_date_col="ShipDate",
        output_col = "ProcuredToShipDays"
    )
    
    # Return some metrics about the data in the pipeline
    stats, pdf_path = compute_statistics_with_histograms(df_procured_to_ship)
    print("Stats Summary:", stats)
    print("PDF Report saved to:", pdf_path)
    
    # Send transformed data to DuckDB
    write_to_mariadb(
        df_procured_to_ship, 
        table_name="csca_mariadb_table"
    )

###################################################################
#                           Run This Script
###################################################################

if __name__ == "__main__":
    es_to_mariadb_flow()

###################################################################
#                   Additional Helpful Instructions
###################################################################

# Steps to run this pipeline:

# >> docker exec -it prefect-cli bash
# >> cd /root/flows
# >> prefect deploy pipeline_script.py:es_to_mariadb_flow --name "Comprehensive-Supply-Chain-Analysis-Data-Deployment"
# >> python pipeline_script.py

# To view the Prefect dashboard:
#       http://localhost:4200
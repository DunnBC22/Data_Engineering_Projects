###################################################################
#
#          Prefect Pipeline for E-Commerce Website Logs
#
###################################################################

import os, re
from typing import List, Dict

from prefect import task, flow
from prefect.context import get_run_context

from pymongo import MongoClient

import polars as pl

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from cassandra.cluster import Cluster

###################################################################
#                              Tasks
###################################################################

@task
def fetch_data_from_mongodb(
    host: str = "localhost",
    port: int = 27017,
    username: str = "mongodb_user",
    password: str = "mongodb_password",
    database_name: str = "your_database",
    collection_name: str = "your_collection",
    query: dict = {},
    projection: dict = None
) -> pl.DataFrame:
    """
    This function/task retrieves data from a MongoDB collection (as 
    passed in via the function/task argument) and inserts it into a 
    Polars DataFrame.
    
    Args:
        host (str): Host name for the connection to the MongoDB Database
        port (int): Port for the connection to the MongoDB Database
        username (str): Username used for authentication
        password (str): Password used for authentication
        database_name (str): MongoDB database from which to retrieve data.
        collection_name (str): MongoDB collection from which to retrieve data.
        query: (dict): A custom query that you can use to specify 
            criteria for selecting documents from a collection.
        projection (dict): The set of fields to include or exclude when 
            retrieving documents using a query

    Returns:
        pl.DataFrame: DataFrame with the data from the MongoDB Collection.
    """
    client = MongoClient(
        host=host,
        port=port,
        username=username,
        password=password,
        authSource="admin"  # default auth DB for root user
    )

    db = client[database_name]
    collection = db[collection_name]

    documents = list(collection.find(query, projection))

    # Clean and normalize
    for doc in documents:
        doc.pop("_id", None)  # Remove MongoDB's internal ID
        for key, value in doc.items():
            if value == "--":
                doc[key] = None  # Replace placeholder values

    # Clean and normalize
    all_keys = set()
    for doc in documents:
        doc.pop("_id", None)
        for k, v in doc.items():
            if v in ("--", ""):
                doc[k] = None
        all_keys.update(doc.keys())

    normalized_docs = []
    for doc in documents:
        normalized_doc = {key: doc.get(key, None) for key in all_keys}
        normalized_docs.append(normalized_doc)

    # Create DataFrame with extended schema inference
    df = pl.DataFrame(normalized_docs, infer_schema_length=1000)
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
        df1 (pl.DataFrame): Input Polars DataFrame (left DataFrame)
        df1 (pl.DataFrame): Input Polars DataFrame (right DataFrame)
        on (str): Feature/column name which is used to join DataFrames
        how(str): strategy for how to join DataFrames

    Returns:
        pl.DataFrame: Resulting DataFrame after joining two DataFrames.
    """
    return df1.join(df2, on=on, how=how)

@task
def clean_nan_values(
    df: pl.DataFrame, 
    column_names: list
    ) -> pl.DataFrame:
    """
    This function cleans nan values in for the columns that are passed into this function.
    
    Cleans a Polars DataFrame by replacing null and NaN values for specified columns:
        - Float columns: fill null and NaN with -1.0
        - Integer columns: fill null with -1
        - Boolean columns: fill null with False
        - String columns: fill null with "-1"
        - Other types: fill null with "N/A"
    
    Args:
        df (pl.DataFrame): Input Polars DataFrame
        column_names (List): List of column names to apply the cleaning
        functionality of this function.

    Returns:
        pl.DataFrame: DataFrame where nan's in selected columns are cleaned.
    """
    for col in column_names:
        if col in df.columns:
            dtype = df.schema[col]
            
            if dtype in [pl.Float64, pl.Float32]:
                df = df.with_columns(
                    pl.col(col)
                    .fill_null(-1.0)
                    .fill_nan(-1.0)
                )
            elif dtype in [pl.Int64, pl.Int32, pl.Int16, pl.Int8, pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64]:
                df = df.with_columns(pl.col(col).fill_null(-1))
            elif dtype == pl.Boolean:
                df = df.with_columns(pl.col(col).fill_null(False))
            elif dtype == pl.Utf8:
                df = df.with_columns(pl.col(col).fill_null("-1"))
            else:
                # Fallback for unsupported or custom types
                df = df.with_columns(pl.col(col).fill_null("N/A"))
    
    return df

@task
def convert_timestamps_to_dates(
    df: pl.DataFrame, 
    timestamp_cols: List[str] = ["timestamp"], 
    default_date: str = "1900-01-01 00:00:00.000"
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
            pl.when(pl.col(col).str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S%.3f", strict=False).is_null())
            .then(pl.lit(default_date).str.strptime(pl.Date, "%Y-%m-%d %H:%M:%S%.3f"))
            .otherwise(pl.col(col).str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S%.3f", strict=False))
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
def clean_values_using_dict(
    df: pl.DataFrame, 
    values_dict: Dict[str, Dict[str, str]]
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
    for column, value_map in values_dict.items():
        if column in df.columns:
            # Apply the value mapping for the column
            for old_value, new_value in value_map.items():
                df = df.with_columns(
                    pl.col(column)
                    .map_elements(lambda x: new_value if x == old_value else x, return_dtype=pl.Utf8)
                    .alias(column)
                )
    return df

@task
def titlecase_string_values(
    df: pl.DataFrame, 
    string_columns: list[str]
    ) -> pl.DataFrame:
    """
    This function/task titlecases the string values in the columns/features 
    that are passed into this function/task via the string_columns parameter.
    
    Args:
        df: Input Polars DataFrame
        string_columns: List of column names (strings) that will have titlecased values.
    
    Returns:
        A Polars DataFrame with the string columns (that were passed in) titlecased.
    """
    for col in string_columns:
        df = df.with_columns([
            pl.col(col)
            .str.to_titlecase()
            .alias(col)
        ])
    return df

@task
def remove_leading_trailing_whitespace(
    df: pl.DataFrame, 
    string_columns: list[str]
    ) -> pl.DataFrame:
    """
    This function/task removes the leading & trailing whitespace from the 
    string values in the columns/features that are passed into this 
    function/task via the string_columns parameter.
    
    Args:
        df: Input Polars DataFrame
        string_columns: List of column names (strings) that have the leading & trailing whitespace removed.
    
    Returns:
        A Polars DataFrame with the string columns (that were passed in) that have the leading & trailing whitespace removed.
    """
    for col in string_columns:
        df = df.with_columns([
            pl.col(col)
            .str.strip_chars() # Remove leading/trailing spaces
            .alias(col)
        ])
    return df

@task
def remove_all_whitespace(
    df: pl.DataFrame, 
    string_columns: list[str]
    ) -> pl.DataFrame:
    """
    This function/task removes ALL whitespace from the string values
    in the columns/features that are passed into this function/task
    via the string_columns parameter.
    
    Args:
        df: Input Polars DataFrame
        string_columns: List of column names (strings) that have ALL 
            of the whitespace removed.
    
    Returns:
        A Polars DataFrame with the string columns (that were passed 
            in) that have ALL of the whitespace removed.
    """
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
def add_unique_id(
    df: pl.DataFrame, 
    id_column_name: str = "unique_id"
    ) -> pl.DataFrame:
    """
    Adds a unique ID column to the DataFrame.

    Parameters:
    ----------
    df : pl.DataFrame
        The input Polars DataFrame.
    id_column_name : str, optional
        Name of the ID column to create (default is 'unique_id').

    Returns:
    -------
    pl.DataFrame
        A DataFrame with a new unique ID column.
    """
    n_rows = df.height
    unique_ids = pl.Series(id_column_name, range(1, n_rows + 1))

    df = df.with_columns(unique_ids)
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
        lines_per_page = 45  # Adjust as needed
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

@task(retries=3, retry_delay_seconds=5)
def write_to_cassandra(
    keyspace: str, 
    table: str, 
    data: pl.DataFrame
    ):
    """
    This function/task sends the transformed data (from Polars) to the 
    Apache Cassandra table that is named in the arguments passed into 
    this function.
    
    Args:
        keyspace (str): The name of the Apache Cassandra keyspace to which 
            to send this data.
        table (str): The name of the Apache Cassandra table in which to 
            insert the data.
        data (pl.DataFrame): Polars DataFrame of data to send to Apache Cassandra.
    """
    # Connect to Cassandra cluster
    cluster = Cluster(['cassandra'])  # Replace with your Cassandra host
    session = cluster.connect(keyspace)

    # Get column names
    columns = data.columns
    columns_str = ', '.join(columns)
    placeholders = ', '.join(['%s'] * len(columns))
    query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders});"

    # Iterate over rows and insert into Cassandra
    for row in data.iter_rows():
        session.execute(query, row)

###################################################################
#                              Flow
###################################################################

@flow(
    name="E-Commerce Website Logs Dataset", 
    description="This pipeline transfers E-Commerce Website Logs Dataset from MongoDB to Apache Cassandra.", 
    log_prints=True)
def mongodb_to_cassandra_flow(
    name: str = "default_run_name"
    ) -> list:
    """
    This defines the Prefect pipeline that 
        - Retrieves data from a MongoDB Collection
        - Transforms the data
        - Sends transformed data to Apache Cassandra
    """
    
    context = get_run_context()
    flow_run = context.flow_run

    flow_run.name = f"Run-{name}"  # Set name dynamically at runtime
    
    # Retrieve data
    df_start = fetch_data_from_mongodb(
        host="mongodb",
        port=27017,
        username = "mongodb_user",
        password = "mongodb_password",
        database_name="ecomm_web_logs_mongo_db",
        collection_name="ecomm_web_logs_mongo_coll",
        query={},
        projection=None
    )
    
    # Define rename mapping
    rename_map = {
        "accessed_date": "AccessedDate",
        "duration_(secs)": "DurationInSeconds",
        "network_protocol": "NetworkProtocol",
        "ip": "IpAddress",
        "bytes": "BytesUsed",
        "accessed_Ffom": "BrowserAccessedFrom",
        "age": "UserAge",
        "gender": "UserGender",
        "country": "UserCountry",
        "membership": "UserMembershipLevel",
        "language": "UserLanguage",
        "sales": "SalesAmount",
        "returned": "ProductReturned",
        "returned_amount": "ReturnedAmount",
        "pay_method": "PaymentMethod"
    }
    
    df_renamed = rename_columns(
        df_start, 
        rename_map
        )
    
    # Handle nan in features
    nan_cols_to_correct = [
        "UserAge"
    ]
    
    df_no_nans = clean_nan_values(
        df=df_renamed,
        column_names=nan_cols_to_correct
        )
    
    # Clean up String spelling(s):
    string_values_to_clean = {
        "BrowserAccessedFrom": {
            "SafFRi": "Safari"
            },
        "ProductReturned": {
            "No": "0",
            "Yes": "1"
        }
    }
    
    df_clean_spelling = clean_values_using_dict(
        df_no_nans, 
        string_values_to_clean
    )
    
    # Remove all leading & trailing whitespace
    cols_to_remove_ltw = [
        "NetworkProtocol",
        "IpAddress",
        "UserMembershipLevel",
        "UserLanguage"
    ]
    
    df_w_o_ltw = remove_leading_trailing_whitespace(
        df_clean_spelling,
        cols_to_remove_ltw
    )
    
    # Titlecase
    cols_to_titlecase = [
        "UserLanguage",
        "BrowserAccessedFrom",
        "PaymentMethod"
    ]
    
    df_titlecased = titlecase_string_values(
        df_w_o_ltw,
        cols_to_titlecase
    )
    
    #  Remove ALL Whitespace
    cols_to_remove_all_ws = [
        "BrowserAccessedFrom",
        "PaymentMethod"
    ]
    
    df_strings_w_o_ws = remove_all_whitespace(
        df_titlecased,
        cols_to_remove_all_ws
    )
    
    # Update Feature data types
    column_casts = {
        "UserAge": pl.Int32,
        "ProductReturned": pl.Int32
    }

    # Apply the casting function
    casted_df = cast_columns(
        df_strings_w_o_ws, 
        column_casts
        )
    
    # Add a unique identifier feature named LogId
    df_w_unique_id = add_unique_id(
        casted_df,
        id_column_name = "LogId"
        )
    
    # Handle timestamps (convert to date data type & extract parts)
    datetime_col_name = ["AccessedDate"]
    
    df_date_time_converted = convert_timestamps_to_dates(
        df_w_unique_id,
        datetime_col_name
    )

    df_prepared = extract_date_parts(
        df_date_time_converted,
        "AccessedDate"
    )
    
    # Return some metrics about the data in the pipeline
    stats, pdf_path = compute_statistics_with_histograms(df_prepared)
    print("Stats Summary:", stats)
    print("PDF Report saved to:", pdf_path)
    
    # Send transformed data to Apache Cassandra
    write_to_cassandra(
        keyspace="ecomm_website_logs_keyspace_cassie",
        table="ecomm_website_logs_table_cassie", 
        data=df_prepared)

###################################################################
#                           Run This Script
###################################################################

if __name__ == "__main__":
    mongodb_to_cassandra_flow()

###################################################################
#                   Additional Helpful Instructions
###################################################################

# Steps to run this pipeline:

# >> docker exec -it prefect-cli bash
# >> cd /root/flows
# >> prefect deploy pipeline_script.py:mongodb_to_cassandra_flow --name "E-Commerce-Website-Logs-Data-Deployment"
# >> python pipeline_script.py

# To view the Prefect dashboard:
#       http://localhost:4200
###################################################################
#
#         Prefect Pipeline for Top Scientist & Researcher
#
###################################################################

import os
from typing import List, Dict

from prefect import task, flow
from prefect.context import get_run_context

import polars as pl

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from pymongo import MongoClient
from elasticsearch import Elasticsearch, helpers

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
        authSource="admin",
        serverSelectionTimeoutMS=5000
    )
    
    db = client[database_name]
    collection = db[collection_name]

    documents = list(collection.find(query, projection))
    print(f"Fetched {len(documents)} documents from MongoDB")

    all_keys = set()
    for doc in documents:
        doc.pop("_id", None)
        for k, v in doc.items():
            if v in ("--", ""):
                doc[k] = None
        all_keys.update(doc.keys())

    normalized_docs = [
        {key: doc.get(key, None) for key in all_keys}
        for doc in documents
    ]

    if not normalized_docs:
        raise ValueError("No documents to convert after normalization.")

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
    default_date: str = "1900-01-01"
) -> pl.DataFrame:
    """
    This function/task converts one or more timestamp columns in the DataFrame to date format.
    
    Parameters:
        - df: Polars DataFrame
        - timestamp_cols: List of column names to convert from string to date
        - default_date: The default value to impute for invalid or missing date values (default is '1900-01-01')

    Returns:
        - DataFrame with new columns appended, named '<original_col>'
    """
    for col in timestamp_cols:
        # Attempt to convert to datetime
        df = df.with_columns(
            pl.when(pl.col(col).str.strptime(pl.Datetime, "%Y/%m/%d %H:%M:%S", strict=False).is_null())
            .then(pl.lit(default_date).str.strptime(pl.Date, "%Y-%m-%d"))
            .otherwise(pl.col(col).str.strptime(pl.Datetime, "%Y/%m/%d %H:%M:%S", strict=False))
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
def remove_all_periods(
    df: pl.DataFrame, 
    string_columns: list[str]
    ) -> pl.DataFrame:
    """
    This function/task removes all of the periods from the string values in the 
    columns/features that are passed into this function/task via the 
    string_columns parameter.
    
    Args:
        df: Input Polars DataFrame
        string_columns: List of column names (strings) that will have all periods removed.
    
    Returns:
        A Polars DataFrame with the string columns (that were passed in) with NO periods.
    """
    # Apply cleanup operations on string columns
    for col in string_columns:
        df = df.with_columns([
            pl.col(col)
            .str.replace_all(r"\.", "")   # replace all periods
            .alias(col)
        ])
    return df

@task
def remove_lt_ws_and_titlecase(
    df: pl.DataFrame, 
    string_columns: list[str]
    ) -> pl.DataFrame:
    """
    This function/task removes the leading & trailing whitespace then 
    titlecases the string values from the columns/features that are 
    passed into this function/task via the string_columns parameter.
    
    Args:
        df: Input Polars DataFrame
        string_columns: List of column names (strings) that have the 
            leading & trailing whitespace removed then are titlecased
    
    Returns:
        A Polars DataFrame with the string columns (that were passed in) that have the leading & trailing whitespace removed.
    """
    
    for col in string_columns:
        df = df.with_columns([
            pl.col(col)
            .str.strip_chars()
            .str.to_titlecase()
            .alias(col)
        ])
    return df

@task
def remove_repetitive_whitespace(
    df: pl.DataFrame, 
    string_columns: list[str]
    ) -> pl.DataFrame:
    """
    This function/task removes all repetitive whitespace from the string 
    values in the columns/features that are passed into this function/task
    via the string_columns parameter.
    
    Args:
        df: Input Polars DataFrame
        string_columns: List of column names (strings) that have repetitive 
            whitespace removed.
    
    Returns:
        A Polars DataFrame with the string columns (that were passed 
            in) that have all repetitive whitespace removed.
    """
    
    for col in string_columns:
        df = df.with_columns([
            pl.col(col)
            .str.replace_all(r"\s+", " ")  # Replace repetitive of whitespace
            .alias(col)
        ])
    return df

@task
def clean_values_using_dict(
    df: pl.DataFrame, 
    values_dict: Dict[str, Dict[str, str]]
    ) -> pl.DataFrame:
    """
    Cleans the values in the dataframe based on a dictionary that maps
    old values to new values for specific columns.

    Args:
    - df (pl.DataFrame): The Polars DataFrame to clean.
    - values_dict (dict): Dictionary containing columns as keys and nested
                          dictionaries with old values as keys and new values as values.

    Returns:
    - pl.DataFrame: The cleaned Polars DataFrame.
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
        # "histograms": histograms,
        # "bar_charts": bar_charts
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
    name="Top Scientists And Researchers Dataset", 
    description="This pipeline transfers Top Scientists And Researchers Dataset from MongoDB to Elasticsearch.", 
    log_prints=True)
def mongodb_to_es_flow(
    name: str = "default_run_name"
    ) -> list:
    """
    This defines the Prefect pipeline that 
        - Retrieves data from a CSV File via SFTP,
        - Transforms the data,
        - Sends the transformed data to Elasticsearch
    """
    context = get_run_context()
    flow_run = context.flow_run

    flow_run.name = f"Run-{name}"  # Set name dynamically at runtime
    
    # Retrieve  data
    df_start = fetch_data_from_mongodb(
        host="mongodb",
        port=27017,
        username = "mongodb_user",
        password = "mongodb_password",
        database_name="tsr_mongo_db",
        collection_name="tsr_mongo_coll",
        query={},
        projection=None
    )
    
    # Remove unnecessary Features in dataset
    columns_to_remove = [
        "Years of Experience"
    ]
    
    df_w_fewer_features = drop_columns(
        df_start, 
        columns_to_remove
        )
    
    # Define rename mapping
    rename_map = {
        "id": "Id",
        "Name": "ResearcherName",
        "Department": "DepartmentName",
        "University": "UniversityName",
        "Location": "WorkLocation",
        "Profile URL": "PersonalProfileLink", 
        "Qualification": "Qualifications",
        "Honours and Awards": "HonorsAndAwards",
        "Highest Qualification": "HighestQualification",
        "Has Awards": "HasAwards",
        "Start Year": "StartYear"
    } 
    
    df_renamed = rename_columns(
        df_w_fewer_features, 
        rename_map
        )
    
    str_cols_to_impute  = {
        "HonorsAndAwards": {
            None: "NoneListed"
            },
        "WorkLocation": {
            None : "NotListed"
            }
        }
    
    df_imputed = clean_values_using_dict(
        df_renamed, 
        str_cols_to_impute
    )
    
    # Replace repeated WHITESPACE with a single space
    replace_repeated_whitespace_w_one_space = [
        "HonorsAndAwards",
        "HighestQualification"
    ]
    
    df_no_repeated_ws = remove_repetitive_whitespace(
        df_imputed,
        replace_repeated_whitespace_w_one_space
    )
    
    # Remove leading and trailing whitespace
    remove_all_lead_trail_whitespace = [
        "ResearcherName",
        "Position",
        "DepartmentName",
        "UniversityName",
        "WorkLocation",
        "PersonalProfileLink",
        "HonorsAndAwards",
        "HighestQualification"
    ]
    
    df_w_o_lt_ws = remove_lt_ws_and_titlecase(
        df_no_repeated_ws,
        remove_all_lead_trail_whitespace
    )
    
    # Remove all periods
    remove_all_periods_cols = [    
        "HighestQualification"
    ]
    
    df_w_o_periods = remove_all_periods(
        df_w_o_lt_ws,
        remove_all_periods_cols
    )
    
    # Clean WorkLocation values
    str_values_to_clean = {
        "WorkLocation": {
            "None": "NotListed",
            "Haryana?": "Haryana",
            "Chhattishgarh": "Chhattisgarh",
            "Gujarat State": "Gujarat",
            "Jammu & Kashmir": "Jammu And Kashmir",
            "Maharasthra": "Maharashtra",
            "Maharshtra": "Maharashtra",
            "Orissa": "Odisha",
            "TamilNadu": "Tamil Nadu",
            "Tamilnadu": "Tamil Nadu",
            "TN": "Tamil Nadu",
            "Telagana": "Telangana",
            "Utter Pradesh": "Uttar Pradesh"
        },
        "Position": {
            "Assistant Professor (Grade-I)": "Assistant Professor",
            "Assistant Professor (Grade-II)": "Assistant Professor",
            "Assistant Professor (Grade-III)": "Assistant Professor",
            "Assistant Professor (Senior Grade)": "Assistant Professor",
            "Assistant Professor - Selection Grade": "Assistant Professor",
            "Assistant Professor - Senior Scale": "Assistant Professor",
            "Assistant professor": "Assistant Professor",
            "Associate Professor (Senior Grade)": "Associate Professor",
            "Associate Professor": "Associate Professor",
            "Associate Professor G": "Associate Professor",
            "Associate Professor": "Associate Professor",
            "Associate Research Professor": "Associate Professor", 
            "Associate Teaching Professor": "Associate Professor",
            "Infosys Chair Professor": "Chair Professor",
            "Chairman": "Chairperson",
            "Directorate of Research": "Directorate",
            "Head Of the Department": "Head of Department",
            "Librarian (Associate Professor Scale)": "Librarian",
            "Pro Vice-Chancellor": "Pro Vice Chancellor",
            "Pro-Chancellor": "Pro Chancellor",
            "Professor (HAG)": "Professor",
            "Professor of Practice": "Professor", 
            "professor": "Professor",
            "Prof. Agharkar Chair": "Professor", 
            "Institute Professor": "Professor",
            "Scientific Officer D": "Scientific Officer",
            "Scientific Officer E": "Scientific Officer",
            "Scientific Officer F": "Scientific Officer",
            "Scientific Officer G": "Scientific Officer",
            "Scientific Officer H": "Scientific Officer",
            "Scientist B": "Scientist",
            "Scientist C": "Scientist",
            "Scientist D": "Scientist",
            "Scientist E": "Scientist",
            "Scientist E1": "Scientist",
            "Scientist E2": "Scientist",
            "Scientist F": "Scientist",
            "Scientist G": "Scientist",
            "Scientist SG": "Scientist",
            "Scientist V": "Scientist",
            "Scientist VII": "Scientist"
        }
    }
    
    df_cleaned_string_values = clean_values_using_dict(
        df_w_o_periods, 
        str_values_to_clean
    )
    
    # Update Feature data types
    column_casts = {
        "StartYear": pl.Int64
    }

    # Apply the casting function
    df_completed = cast_columns(
        df_cleaned_string_values, 
        column_casts
        )
    
    # Return some metrics about the data in the pipeline
    stats, pdf_path = compute_statistics_with_histograms(df_completed)
    print("Stats Summary:", stats)
    print("PDF Report saved to:", pdf_path)
    
    # Send transformed data to Elasticsearch
    send_data_to_elasticsearch(
        df=df_completed, 
        index_name="top_scientists_researchers", 
        es_host="http://elasticsearch:9200"
        )

###################################################################
#                           Run This Script
###################################################################

if __name__ == "__main__":
    mongodb_to_es_flow()

###################################################################
#                   Additional Helpful Instructions
###################################################################

# Steps to run this pipeline:

# >> docker exec -it prefect-cli bash
# >> cd /root/flows
# >> prefect deploy pipeline_script.py:mongodb_to_es_flow --name "Top-Scientists-Researchers-Data-Deployment"
# >> python pipeline_script.py

# To view the Prefect dashboard:
#       http://localhost:4200
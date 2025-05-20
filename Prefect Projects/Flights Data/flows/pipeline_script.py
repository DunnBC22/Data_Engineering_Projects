###################################################################
#
#               Prefect Pipeline for Flights Data
#
###################################################################

import os
from typing import List, Dict, Any

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
def create_postgres_connector():
    # Postgres Target Block
    postgres_connector = SqlAlchemyConnector(
        connection_info=ConnectionComponents(
            driver=SyncDriver.POSTGRESQL_PSYCOPG2,
            username="pg",
            password="pg",
            host="postgres",
            port=5432,
            database="flights_db_pg",
        )
    )
    
    # Save connector
    postgres_connector.save("pg-connector", overwrite=True)
    return postgres_connector

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
def remove_none_and_null_rows(
    df: pl.DataFrame, 
    features: list[str]
    ) -> pl.DataFrame:
    """
    Removes rows from the DataFrame where any specified feature column contains either
    the string "None" or a null value.

    Parameters:
    ----------
    df : pl.DataFrame
        The input Polars DataFrame.
    features : list of str
        The column names to check.

    Returns:
    -------
    pl.DataFrame
        A filtered DataFrame excluding rows with "None" (string) or null values in any given column.
    """
    for feature in features:
        if feature in df.columns:
            df = df.filter((pl.col(feature) != "None") & (pl.col(feature).is_not_null()))
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
            pl.when(pl.col(col).str.strptime(pl.Datetime, "%Y%m%d", strict=False).is_null())
            .then(pl.lit(default_date).str.strptime(pl.Date, "%Y-%m-%d"))
            .otherwise(pl.col(col).str.strptime(pl.Datetime, "%Y%m%d", strict=False))
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
            .str.strip_chars()
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
def remove_miles_suffix(
    df: pl.DataFrame, 
    columns: list
    ) -> pl.DataFrame:
    """
    Removes the ' miles' suffix from string values in specified columns.

    Args:
        df (pl.DataFrame): Input Polars DataFrame.
        columns (list): List of column names where ' miles' suffix should be removed.

    Returns:
        pl.DataFrame: Updated DataFrame with suffixes removed.
    """
    for col in columns:
        df = df.with_columns(
            pl.col(col).cast(str).str.strip_chars().str.replace(r'\s*miles$', '', literal=False).alias(col)
        )
    return df

@task
def normalize_boolean_columns(
    df: pl.DataFrame, 
    columns: List[str] = None
    ) -> pl.DataFrame:
    """
    Converts various representations of boolean values in specified columns to proper True/False.
    
    Args:
        df (pl.DataFrame): Input DataFrame.
        columns (list): List of column names to apply normalization on.

    Returns:
        pl.DataFrame: DataFrame with standardized boolean columns.
    """
    # Default mappings
    true_values = ["1", 1, "true", "True", "TRUE", True]
    false_values = ["0", 0, "false", "False", "FALSE", False]
    
    # If columns not specified, apply to all columns
    columns = columns or df.columns

    for col in columns:
        df = df.with_columns(
            pl.col(col).cast(str).map_elements(
                lambda val: True if val in map(str, true_values)
                else False if val in map(str, false_values)
                else None,  # Optional: handle unexpected values
                return_dtype=pl.Boolean
            ).alias(col)
        )
    return df

@task
def create_dimension_table(
    df: pl.DataFrame, 
    columns: list[str]
    ) -> pl.DataFrame:
    """
    Selects only the specified columns and returns distinct records based on them.

    Parameters:
    ----------
    df : pl.DataFrame
        The input Polars DataFrame.
    columns : list of str
        Column names to include and use for identifying distinct rows.

    Returns:
    -------
    pl.DataFrame
        A DataFrame with distinct records from the selected columns.
    """
    if not all(col in df.columns for col in columns):
        missing = [col for col in columns if col not in df.columns]
        raise ValueError(f"The following columns are missing from the DataFrame: {missing}")
    
    return df.select(columns).unique()

@task
def concatenate_dataframes(
    df1: pl.DataFrame, 
    df2: pl.DataFrame
    ) -> pl.DataFrame:
    """
    Concatenates two Polars DataFrames vertically.

    Parameters:
    ----------
    df1 : pl.DataFrame
        The first DataFrame.
    df2 : pl.DataFrame
        The second DataFrame.

    Returns:
    -------
    pl.DataFrame
        A single DataFrame resulting from concatenating df1 and df2.
    """
    concatenated_df = pl.concat([df1, df2], how="vertical")
    return concatenated_df

@task
def get_distinct_records(
    df: pl.DataFrame
    ) -> pl.DataFrame:
    """
    Returns only the distinct (unique) records from the input Polars DataFrame,
    considering all columns for uniqueness.

    Parameters:
    ----------
    df : pl.DataFrame
        The input Polars DataFrame.

    Returns:
    -------
    pl.DataFrame
        A DataFrame with only distinct rows based on all columns.
    """
    distinct_df = df.unique()
    return distinct_df

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
def write_to_postgres(
    df: pl.DataFrame, 
    table_name: str, 
    if_exists: str = "replace"
    ):
    """
    This function/task sends the transformed data (in Polars) to the database
    table that is named in the arguments passed into this function.
    
    Args:
        df (pl.DataFrame): Polars DataFrame to analyze.
        table_name (str): The name of the table in which to insert the data.
        if_exists (str): What to do if the table already exists.
    """
    # Load the saved database connector block
    connector = SqlAlchemyConnector.load("pg-connector")
    
    # Retrieve the SQLAlchemy engine
    engine = connector.get_engine()

    # Write the DataFrame to the specified table in Postgres
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
    name="Flights Data Dataset"
    )
def es_to_pg_flow(
    name: str = "default_run_name"
    ) -> list:
    """
        This defines the Prefect pipeline that:
            - Retrieves data from Elasticsearch
            - Transforms the data
            - Sends transformed data to Postgres
    """
    context = get_run_context()
    flow_run = context.flow_run

    flow_run.name = f"Run-{name}"  # Set name dynamically at runtime
    
    postgres_connector = create_postgres_connector()
    
    # Retrieve data
    df_start = fetch_data_from_elasticsearch(
        index_name="flights_data", 
        es_host = "http://elasticsearch:9200"
        )
    
    # Data Transformations
    # Define rename mapping
    rename_map = {
        "TRANSACTIONID": "TransactionId",
        "FLIGHTDATE": "FlightDate",
        "AIRLINECODE": "AirlineCode",
        "TAILNUM": "TailNumber",
        "FLIGHTNUM": "FlightNumber",
        "ORIGINAIRPORTCODE": "OriginAirportCode",
        "ORIGINCITYNAME": "OriginCityName",
        "ORIGINSTATE": "OriginState",
        "DESTAIRPORTCODE": "DestinationAirportCode",
        "DESTCITYNAME": "DestinationCityName",
        "DESTSTATE": "DestinationState",
        "CRSDEPTIME": "CrsDepartureTime",
        "DEPTIME": "DepartureTime",
        "DEPDELAY": "DepartureDelay",
        "TAXIOUT": "TaxiOut",
        "WHEELSOFF": "WheelsOff",
        "WHEELSON": "WheelsOn",
        "TAXIIN": "TaxiIn",
        "CRSARRTIME": "CrsArrivalTime",
        "ARRTIME": "ArrivalTime",
        "ARRDELAY": "ArrivalDelay",
        "CRSELAPSEDTIME": "CrsElapsedTime",
        "ACTUALELAPSEDTIME": "ActualElapsedTime",
        "CANCELLED": "FlightCancelled",
        "DIVERTED": "FlightDiverted",
        "DISTANCE": "FlightDistance",
        "ORIGAIRPORTNAME": "OriginAirportName",
        "ORIGINSTATENAME": "OriginStateName",
        "DESTAIRPORTNAME": "DestinationAirportName",
        "DESTSTATENAME": "DestinationStateName"
    } 
    
    # Rename columns
    df_renamed = rename_columns(
        df_start, 
        rename_map
        )
    
    # Remove unnecessary Features
    columns_to_remove = [
        "AIRLINENAME"
    ]
    
    df_w_fewer_features = drop_columns(
        df_renamed, 
        columns_to_remove
        )
    
    # Remove records with nulls in select features
    nulls_to_filter = [
        "OriginState",
        "DestinationState",
        "DepartureTime",
        "DepartureDelay",
        "ArrivalTime",
        "ArrivalDelay",
        "CrsElapsedTime",
        "ActualElapsedTime"
    ]
    
    df_filtered_null_records = remove_none_and_null_rows(
        df_w_fewer_features,
        nulls_to_filter
    )
    
    fixed_value_imputations = {
        "TailNumber": "UNKNOWN",
        "TaxiOut": -1000,
        "WheelsOff": -1000,
        "WheelsOn": -1000,
        "TaxiIn": -1000
    }
    
    df_w_fixed_value_imputations = impute_missing_values(
        df_filtered_null_records,
        fixed_value_imputations
    )
    
    bool_cols_to_normalize = [
        "FlightCancelled",
        "FlightDiverted"
    ]

    df_normalized_bools = normalize_boolean_columns(
        df_w_fixed_value_imputations, 
        bool_cols_to_normalize
    )
    
    # Remove appended ' miles' from each value in FlightDistance
    df_strings_cleaned = remove_miles_suffix(
        df_normalized_bools, 
        ["FlightDistance"]
        )

    # Handle dates (both convert to date data type & extract date parts)
    date_features = ["FlightDate"]
    
    df_date_converted = convert_timestamps_to_dates(
        df_strings_cleaned,
        date_features
    )
    
    df_w_date_parts_extracted = extract_date_parts(
        df_date_converted,
        "FlightDate"
    )
    
    # Remove leading & trailing whitespace from the following features:
    cols_to_remove_lt_ws = [
        "AirlineCode",
        "TailNumber",
        "OriginAirportCode",
        "OriginCityName",
        "OriginState",
        "DestinationAirportCode",
        "DestinationCityName",
        "DestinationState"
    ]
    
    df_strings_cleaned = clean_string_columns(
        df_w_date_parts_extracted, 
        cols_to_remove_lt_ws
    )
    
    # Update Feature data types
    # Specify the columns and their target data types
    column_casts = {
        "FlightCancelled": bool,
        "FlightDiverted": bool,
        "FlightDistance": pl.Int32
    }

    # Apply the casting function
    df_casted = cast_columns(
        df_strings_cleaned, 
        column_casts
        )
    
    # Return some metrics about the data in the pipeline
    stats, pdf_path = compute_statistics_with_histograms(df_casted)
    print("Stats Summary:", stats)
    print("PDF Report saved to:", pdf_path)
    
    
    ### Create nodes (airports) table
    # Retrieve only Origin Airport data (distinct values only)
    origin_airport_features = [
        "OriginAirportCode",
        "OriginCityName",
        "OriginState",
        "OriginAirportName",
        "OriginStateName"
    ]
    
    origin_airports = create_dimension_table(
        df_casted,
        origin_airport_features
        )
    
    # Retrieve only Destination Airport data (distinct values only)
    dest_airport_features = [
        "DestinationAirportCode",
        "DestinationCityName",
        "DestinationState",
        "DestinationAirportName",
        "DestinationStateName"
    ]
    
    dest_airports = create_dimension_table(
        df_casted,
        dest_airport_features
        )
    
    # Rename columns in Origin Airport (sub-)dataset
    origin_to_airport_rename_map = {
        "OriginAirportCode": "AirportCode",
        "OriginCityName": "AirportCityName",
        "OriginState": "AirportState",
        "OriginAirportName": "AirportName",
        "OriginStateName": "AirportStateName"
    }
    
    origin_airports_renamed = rename_columns(
        origin_airports,
        origin_to_airport_rename_map
    )
    
    # Rename columns in Destination Airport (sub-)dataset
    dest_to_airport_rename_map = {
        "DestinationAirportCode": "AirportCode",
        "DestinationCityName": "AirportCityName",
        "DestinationState": "AirportState",
        "DestinationAirportName": "AirportName",
        "DestinationStateName": "AirportStateName"
    }
    
    dest_airports_renamed = rename_columns(
        dest_airports,
        dest_to_airport_rename_map
    )
    
    # Concatenate both Airport Dataframes 
    df_all_airports = concatenate_dataframes(
        origin_airports_renamed,
        dest_airports_renamed
    )
    
    # Return the distinct values after joining the data
    df_airport_nodes = get_distinct_records(
        df_all_airports
        )
    
    # Send transformed data to Postgres
    write_to_postgres(
        df_airport_nodes, 
        "airports_table_pg"
        )
    
    
    ### create relationships (flights) table
    
    rel_cols_to_remove = [
        "OriginCityName",
        "OriginState",
        "OriginAirportName",
        "OriginStateName",
        "DestinationCityName",
        "DestinationState",
        "DestinationAirportName",
        "DestinationStateName"
    ]
    
    relationships_df = drop_columns(
        df_casted, 
        rel_cols_to_remove
        )
    
    # Send transformed data to Postgres
    write_to_postgres(
        relationships_df, 
        "flights_table_pg")

###################################################################
#                           Run This Script
###################################################################

if __name__ == "__main__":
    es_to_pg_flow()

###################################################################
#                   Additional Helpful Instructions
###################################################################

# Steps to run this pipeline:

# >> docker exec -it prefect-cli bash
# >> cd /root/flows
# >> prefect deploy pipeline_script.py:es_to_pg_flow --name "Flights-Data-Deployment"
# >> python pipeline_script.py

# To view the Prefect dashboard:
#       http://localhost:4200
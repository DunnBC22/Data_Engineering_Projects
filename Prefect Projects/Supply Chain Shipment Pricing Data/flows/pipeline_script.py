###################################################################
#
#         Prefect Pipeline for Supply Chain Pricing Data
#
###################################################################

import os
from typing import List

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
def create_mysql_connector():
    # MySQL Source Block
    mysql_connector = SqlAlchemyConnector(
        connection_info=ConnectionComponents(
            driver=SyncDriver.MYSQL_PYMYSQL,
            username="mysql",
            password="mysql",
            host="mysql",
            port=3306,
            database="supply_chain_shipment_pricing_data_db_mysql"
        )
    )
    
    # Save connector
    mysql_connector.save("mysql-connector", overwrite=True)
    return mysql_connector

@task
def fetch_data(
    table_name: str
    ):
    """
    This function/task retrieves data from a database table (as passed in
    via the function/task argument) and puts it into a Polars DataFrame.
    
    Args:
        table_name (str): The name of the table for which to look for the data.

    Returns:
        pl.DataFrame: DataFrame with the data from the Postgres table.
    """
    # Load the saved connector block
    source_connector = SqlAlchemyConnector.load("mysql-connector")

    # Get the SQLAlchemy engine
    engine = source_connector.get_engine()

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
def clean_nan_values(
    df: pl.DataFrame, 
    column_names: list
    ) -> pl.DataFrame:
    """
    This function/task cleans nan values in the columns/features that 
    are passed into this function/task via the column_names parameter.
    
    Cleans a Polars DataFrame by replacing null and NaN values for specified columns:
    - Float columns: fill null and NaN with -1.0
    - Integer columns: fill null with -1
    - Boolean columns: fill null with False
    - String columns: fill null with "-1"
    - Other types: fill null with "N/A"
    
    Args:
        df (pl.DataFrame): The input Polars DataFrame
        column_names (list): column names to which to apply this function.
    
    Returns:
        A Polars DataFrame with nans handled for the columns that were passed in.
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
def convert_string_to_datetime(
    df: pl.DataFrame, 
    timestamp_cols: List[str] = ["timestamp"], 
    default_date: str = "01-Jan-1900"
) -> pl.DataFrame:
    """
    This function/task converts one or more timestamp columns in the DataFrame to date format.
    
    Parameters:
        - df: Polars DataFrame
        - timestamp_cols: List of column names to convert from string to date
        - default_date: The default value to impute for invalid or missing date values (default is '01-Jan-1900')

    Returns:
        - DataFrame with new columns appended, named '<original_col>'
    """
    for col in timestamp_cols:
        # Attempt to convert to datetime
        df = df.with_columns(
            pl.when(pl.col(col).str.strptime(pl.Datetime, "%d-%b-%y", strict=False).is_null())
            .then(pl.lit(default_date).str.strptime(pl.Date, "%d-%b-%Y"))
            .otherwise(pl.col(col).str.strptime(pl.Datetime, "%d-%b-%Y", strict=False))
            .alias(f"{col}")
        )
    return df

@task
def extract_date_parts(
    df: pl.DataFrame,
    date_cols: list[str] = ["date"]
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
    new_columns = []

    for col in date_cols:
        new_columns.extend([
            pl.col(col).dt.weekday().alias(f"{col}_DayOfWeek"),
            pl.col(col).dt.day().alias(f"{col}_DayOfMonth"),
            pl.col(col).dt.ordinal_day().alias(f"{col}_DayOfYear"),
            pl.col(col).dt.month().alias(f"{col}_Month"),
            pl.col(col).dt.quarter().alias(f"{col}_Quarter"),
            pl.col(col).dt.year().alias(f"{col}_Year"),
        ])

    df = df.with_columns(new_columns)
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
        A Polars DataFrame with a new column containing the date differences in days
    """
    df = df.with_columns([
        (pl.col(end_date_col) - pl.col(start_date_col))
        .dt.total_days()
        .alias(output_col)
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
    
    Cleans string values in specified columns by:
        1. Replace '&' with 'And'
        2. Remove commas, periods, dashes, & division signs
        3. Removing leading and trailing whitespace
        4. Titlecase string values
    
    Args:
        df: Input Polars DataFrame
        string_columns: List of column names (strings) that need to have 
            the string cleaning function applied to it.
    
    Returns:
        A Polars DataFrame with the string columns (that were passed in) cleaned.
    """
    for col in string_columns:
        df = df.with_columns([
            pl.col(col)
            .str.replace_all("&", "And")        # Replace "&" with "And"
            .str.replace_all(r"[,\.\-/]", "")   # Remove commas, periods, dashes, & division signs
            .str.strip_chars()                  # Remove leading/trailing spaces
            .str.to_titlecase()                 # Convert to titlecase
            .alias(col)         
        ])
    return df

@task
def impute_static_values(
    df: pl.DataFrame, 
    impute_map: dict
    ) -> pl.DataFrame:
    """
    Imputes missing (null) values in according to the impute_map dictionary
    that is passed into this task/function.

    Parameters:
    ----------
    df : pl.DataFrame
        The input Polars DataFrame.
    impute_map : dict
        The dictionary with column names and values to impute into those 
            respective columns as such:
                - key: column names to impute values
                - value: fix value to impute into missing values in 
                    respective column name

    Returns:
    -------
    pl.DataFrame
        The DataFrame with imputed values.
    """
    return df.with_columns([
        pl.col(col).fill_null(val) for col, val in impute_map.items()
    ])

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
        lines_per_page = 52  # Adjust as needed
        for i in range(0, len(summary_lines), lines_per_page):
            fig, ax = plt.subplots(figsize=(8, 10))
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
def send_data_to_elasticsearch(
    df: pl.DataFrame, 
    index_name: str, 
    es_host: str = "http://localhost:9200", 
    es_user: str = "elastic",
    es_password: str = "es_prefect_pass",
    batch_size: int = 5000
):
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

# define flow
@flow(
    name="Supply Chain Shipping Pricing Data", 
    description="This pipeline transfers Supply Chain Shipping Pricing Data from MySQL to Elasticsearch.", 
    log_prints=True)
def mysql_to_es_flow(
    name: str = "default_run_name"
    ) -> list:
    """
    This defines the Prefect pipeline that 
        - Retrieves data from MySQL,
        - Transforms the data,
        - Sends transformed data to Elasticsearch
    """
    context = get_run_context()
    flow_run = context.flow_run

    flow_run.name = f"Run-{name}"
    
    # Retrieve data
    mysql_connector = create_mysql_connector()
    
    df_start = fetch_data(
        table_name="supply_chain_shipment_pricing_data_table_mysql"
    )
    
    # Data Transformations
    rename_map = {
        "id": "Id",
        "project_code": "ProjectCode",
        "pq_number": "PqNumber",
        "po_or_so_num": "PoOrSoNumber",
        "asn_or_dn_num": "AsnOrDnNumber",
        "country_name": "CountryName",
        "managed_by": "ManagedBy",
        "fulfilled_via": "FulfilledVia",
        "vendor_inco_term": "VendorIncoTerm",
        "shipment_mode": "ShipmentMode",
        "pq_first_sent_to_client_date": "PqFirstSentToClientDate",
        "po_sent_to_vendor_date": "PoSentToVendorDate",
        "scheduled_delivery_date": "ScheduledDeliveryDate",
        "delivered_to_client_date": "DeliveredToClientDate",
        "delivery_recorded_date": "DeliveryRecordedDate",
        "product_group": "ProductGroup",
        "sub_classification": "SubClassification",
        "vendor": "VendorName",
        "item_desc": "ItemDescription",
        "molecule_or_test_type": "MoleculeOrTestType",
        "brand": "BrandName",
        "dosage": "Dosage",
        "dosage_form": "DosageForm",
        "unit_of_measure_per_pack": "UnitOfMeasurePerPack",
        "line_item_quantity": "LineItemQuantity",
        "line_item_value": "LineItemValue",
        "pack_price": "PackPrice",
        "unit_price": "UnitPrice",
        "manufacturing_site": "ManufacturingSite",
        "first_line_designation": "FirstLineDesignation",
        "weight_in_kg": "WeightInKG",
        "freight_cost_in_usd": "FreightCostInUSD",
        "line_item_insurance_in_usd": "LineItemInsuranceInUSD"
    }
    
    # Rename Features
    df_renamed = rename_columns(
        df_start, 
        rename_map
        )
    
    # Clean String-Valued Features
    string_cols_to_clean = [
        "CountryName",
        "SubClassification",
        "ManagedBy",
        "VendorName",
        "ShipmentMode",
        "FulfilledVia",
        "DosageForm",
        "VendorIncoTerm"
        ]

    df_cleaned_strings = clean_string_columns(
        df_renamed,
        string_columns=string_cols_to_clean
    )
    
    # Handle/Impute nulls
    null_and_nan_cols_to_clean = ['LineItemInsuranceInUSD']
    
    df_nans_cleaned = clean_nan_values(
        df_cleaned_strings, 
        null_and_nan_cols_to_clean
        )
    
    # handling dates:
    dates_to_convert_and_extract = [
        "PoSentToVendorDate",
        "ScheduledDeliveryDate",
        "DeliveredToClientDate",
        "DeliveryRecordedDate"
    ]
    
    df_dates_dtype_converted = convert_string_to_datetime(
        df_nans_cleaned,
        dates_to_convert_and_extract
    )
    
    # Extract Date Parts
    df_date_parts_extracted = extract_date_parts(
        df_dates_dtype_converted,
        dates_to_convert_and_extract
    )
    
    # Durations (Date Calculations)
    # Retrieve the number of days between:
        # - DeliveredToClientDate - ScheduledDeliveryDate AS DaysLateOrEarly
        # - PoSentToVendorDate - DeliveredToClientDate AS DaysPoSentUntilDelivery
    
    df_DaysLateOrEarly = calculate_days_between(
        df_date_parts_extracted, 
        start_date_col="DeliveredToClientDate", 
        end_date_col="ScheduledDeliveryDate", 
        output_col="DaysLateOrEarly"
    )
    
    df_prepared = calculate_days_between(
        df_DaysLateOrEarly,
        start_date_col="PoSentToVendorDate",
        end_date_col="DeliveredToClientDate",
        output_col="DaysPoSentUntilDelivery"
    )
    
    # Return some metrics about the data in the pipeline
    stats, pdf_path = compute_statistics_with_histograms(df_prepared)
    print("Stats Summary:", stats)
    print("PDF Report saved to:", pdf_path)
    
    # Send transformed data to Elasticsearch
    send_data_to_elasticsearch(
        df_prepared,
        index_name = "supply_chain_shipment_pricing_data", 
        es_host = "http://elasticsearch:9200", 
        es_user = "elastic",
        es_password = "es_prefect_pass",
        batch_size = 5000
    )

###################################################################
#                           Run This Script
###################################################################

if __name__ == "__main__":
    mysql_to_es_flow()

###################################################################
#                   Additional Helpful Instructions
###################################################################

# Steps to run this pipeline:

# >> docker exec -it prefect-cli bash
# >> cd /root/flows
# >> prefect deploy pipeline_script.py:mysql_to_es_flow --name "Supply-Chain_Shipment-Pricing-Data-Deployment"
# >> python pipeline_script.py

# To view the Prefect dashboard:
#       http://localhost:4200
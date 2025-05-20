###################################################################
#
#     Prefect Pipeline for Brazilian E-Commerce Public Dataset
#
###################################################################

import os, gc
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

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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
            database="brazilian_ecomm_public_dataset_mysql_db"
        )
    )
    
    # Save connector
    mysql_connector.save("mysql-connector", overwrite=True)
    return mysql_connector

@task
def create_pg_connector():
    # PostGIS Target Block
    pg_connector = SqlAlchemyConnector(
        connection_info=ConnectionComponents(
            driver=SyncDriver.POSTGRESQL_PSYCOPG2,
            username="pg",
            password="pg",
            host="postgres",
            port=5432,
            database="brazilian_ecomm_public_dataset_pg_db"
        )
    )
    
    # Save connector
    pg_connector.save("pg-connector", overwrite=True)
    return pg_connector

@task
def fetch_data(
    table_name: str
    ):
    """
    This function/task that retrieves data from the table name
    that was provided as the input.
    
    Args:
        table_name (str): The table name for which to look in for the data.

    Returns:
        pl.DataFrame: DataFrame with the data from the database table.
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
def convert_strings_to_timestamps(
    df: pl.DataFrame, 
    timestamp_cols: List[str] = ["timestamp"], 
    default_date: str = "1900-01-01 01:01:01"
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
            .then(pl.lit(default_date).str.strptime(pl.Date, "%Y-%m-%d  %H:%M:%S"))
            .otherwise(pl.col(col).str.strptime(pl.Datetime, "%Y/%m/%d %H:%M:%S", strict=False))
            .alias(f"{col}")
        )
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
def calculate_minutes_between(
    df: pl.DataFrame, 
    start_date_col: str, 
    end_date_col: str, 
    output_col: str = "duration_minutes"
) -> pl.DataFrame:
    """
    Calculates the number of minutes between two datetime columns.

    Args:
        df: Input Polars DataFrame
        start_date_col: Column name representing the start datetime
        end_date_col: Column name representing the end datetime
        output_col: Name of the new column to store duration (in minutes)

    Returns:
        A Polars DataFrame with a new column containing the datetime differences in minutes
    """
    df = df.with_columns([
        (
            (pl.col(end_date_col).cast(pl.Datetime("ns")) - pl.col(start_date_col).cast(pl.Datetime("ns")))
            .cast(pl.Duration("ns"))
            .cast(pl.Int64) / 60_000_000_000
        ).alias(output_col)
    ])
    return df

@task
def cast_from_timestamp_to_date(df: pl.DataFrame, column_name: str) -> pl.DataFrame:
    """
    Casts a timestamp column to a date column in a Polars DataFrame.

    Parameters:
    - df: The input Polars DataFrame
    - column_name: The name of the column to cast to date

    Returns:
    - A new DataFrame with the specified column cast to pl.Date
    """
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in DataFrame.")

    return df.with_columns(
        pl.col(column_name).dt.date().alias(column_name)
    )

@task
def clean_string_columns_remove_all_lt_ws_only(
    df: pl.DataFrame, 
    string_columns: list[str]
    ) -> pl.DataFrame:
    """
    This function/task cleans string values in the columns/features that 
    are passed into this function/task via the string_columns parameter.
    
    Cleans string values in specified columns by:
        1. Titlecases string values
    
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
            .alias(col)  # Update the column with the cleaned version
        ])
    return df

@task
def clean_string_columns_remove_duplicative_ws(
    df: pl.DataFrame,
    string_columns: list[str]
    ) -> pl.DataFrame:
    """
    This function/task cleans string values in the columns/features that 
    are passed into this function/task via the string_columns parameter.
    
    Cleans string values in specified columns by:
        1. Replaceall duplicate whitespace with a single space.
    
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
            .str.replace_all(r"\s+", " ") # Replace all duplicative whitespace with single space
            .alias(col)  # Update feature with cleaned version
        ])
    return df

@task
def clean_string_columns_convert_underscores_titlecase(
    df: pl.DataFrame,
    string_columns: list[str]
    ) -> pl.DataFrame:
    """
    This function/task cleans string values in the columns/features that 
    are passed into this function/task via the string_columns parameter.
    
    Cleans string values in specified columns by:
        1. Replaces underscores (_) with a single space
        2. Titlecases string values
    
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
            .str.replace_all(r"_", " ") # Replace all underscores with single space
            .str.to_titlecase()         # titlecase values after converting underscores to single spaces
            .alias(col)  # Update feature with cleaned version
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

@task()
def join_dataframes_dif_col_names(
    df1: pl.DataFrame, 
    df2: pl.DataFrame, 
    how: str = "inner",
    suffix: str = "_right",
    left_on: str = None,
    right_on: str = None
    ) -> pl.DataFrame:
    """
    This function/task joins the two Polars DataFrames that are 
    passed into this function/task via the df1 and df2 parameters.
    
    This function/task is comparable to a SQL JOIN operation.
    
    Args:
        df1 (pl.DataFrame): Input Polars DataFrame
        df2 (pl.DataFrame): Input Polars DataFrame
        how (str): strategy for joining DataFrames
        suffix (str): Suffix string value to append to to columns 
            with a duplicate name
        left_on (str): Name in left (df1) dataframe to join on
        right_on (str): Name in right (df2) dataframe to join on

    Returns:
        pl.DataFrame: The joined DataFrame (df1 + df2 based on the passed in column name)
    """
    return df1.join(
        df2,
        how=how,
        left_on=left_on,
        right_on=right_on,
        suffix=suffix
        )

@task
def titlecase_and_remove_lt_ws(
    df: pl.DataFrame, 
    string_columns: list[str]
    ) -> pl.DataFrame:
    """
    This function/task cleans string values in the columns/features that 
    are passed into this function/task via the string_columns parameter.
    
    Cleans string values in specified columns by:
        1. Titlecases string values
        2. Removes all leading and trailing whitespace
    
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
            .str.strip_chars()     # Remove leading & trailing whitespace
            .str.to_titlecase()    # Convert to titlecase
            .alias(col)  # Update column with cleaned version
        ])
    return df

@task
def impute_static_values(
    df: pl.DataFrame, 
    impute_map: dict
    ) -> pl.DataFrame:
    """
    This task imputes missing values with a fixed value according to the 
    impute_map values passed into this task.
    
    Args:
        df (pl.DataFrame): The input DataFrame
        impute_map (dict): Dictionary of fixed values to impute in specified columns:
            key: the column name to impute missing values
            value: the fixed value to impute into missing values
        
    Returns:
        pl.DataFrame: The DataFrame with fixed values imputed in missing values 
            according to the impute_map dictionary.
    """
    return df.with_columns([
        pl.col(col).fill_null(val) for col, val in impute_map.items()
    ])

@task
def fill_none_with_prefixed_col_name(
    df: pl.DataFrame, 
    columns: list[str], 
    prefix: str
    ) -> pl.DataFrame:
    """
    This task imputes missing values in specified features 
        with: <prefix><column name>
    
    Args:
        df (pl.DataFrame): Input Polars DataFrame 
        columns (list[str]): list of columns that will be used to both determine 
            which columns to apply this task to and as the second part of the 
            value that gets imputed in the missing values.
        prefix (str): The string prefix value to prepend to imputed values
    
    Returns:
        pl.DataFrame: The DataFrame with specified columns imputed with: <prefix><column name>
    """
    for col in columns:
        if col not in df.columns:
            continue

        replacement_value = f"{prefix}{col}"

        df = df.with_columns(
            pl.when((pl.col(col).is_null()) | (pl.col(col) == "None"))
            .then(pl.lit(replacement_value))
            .otherwise(pl.col(col))
            .alias(col)
        )

    return df

@task
def clean_none_values(
    df: pl.DataFrame, 
    column_names: list
    ) -> pl.DataFrame:
    """
    Cleans a Polars DataFrame by replacing null and NaN values for specified columns:
        - Float columns: fill null and NaN with -1.0
        - Integer columns: fill null with -1
        - Boolean columns: fill null with False
        - String columns: fill null with "-1"
        - Other types: fill null with "N/A"
    
    Args:
        df (pl.DataFrame): Input Polars DataFrame 
        column_names (list): List of features to apply this task to.
    
    Returns:
        pl.DataFrame: The DataFrame with nans in specified features imputed.
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
def add_point_column(
    df: pl.DataFrame, 
    lat_col: str, 
    lon_col: str, 
    point_col: str = "geo_point"
    ) -> pl.DataFrame:
    """
    This function/task creates the Geographical POINT using the 
    latitudinal (lat_col) & longitudinal (lon_col) features.
    
    Args:
        df (pl.DataFrame): Polars DataFrame to analyze.
        lat_col: str, 
    lon_col: str, 
    point_col

    Returns:
        A Polars DataFrame with the point_col feature/column that has a POINT(<longitude coord> <latitude coord>)
    """
    df = df.with_columns([
        pl.format(
            "POINT({} {})", 
            pl.col(lon_col), 
            pl.col(lat_col)).alias(point_col)
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
        # "column_names": column_names,
        "null_counts": null_counts,
        "dtypes": [str(dt) for dt in dtype_counts],
        "numeric_summary": numeric_stats.to_dict(as_series=False),
        # "histograms": histograms,
        # "bar_charts": bar_charts
    }, pdf_path

@task
def write_to_db(
    df: pl.DataFrame, 
    table_name: str, 
    if_exists: str = "replace"
    ):
    """
    This function/task sends the transformed data (in Polars) to the MariaDB
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

    # Write the DataFrame to the specified table in database
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
    name="Brazilian E-Commerce Public Dataset", 
    description="This pipeline transfers the Brazilian E-Commerce Public Dataset from MySQL to PostGIS.",
    log_prints=True)
def mysql_to_pg_flow(
    name: str = "default_run_name"
    ) -> list:
    """
    This defines the Prefect pipeline that:
        - Retrieves data from MySQL
        - Transforms the data
        - Sends the transformed data to PostGIS
    """
    
    context = get_run_context()
    flow_run = context.flow_run

    flow_run.name = f"Run-{name}"
    
    create_mysql_connector()
    create_pg_connector()
    
    
    """
    Customers Dataset
    """
    df_customers_start = fetch_data("customers_bepd_mysql_table")
    
    # Remove unnecessary Features
    columns_to_remove_customers = [
        "customer_unique_id"
    ]
    
    df_w_fewer_features_customers = drop_columns(
        df_customers_start, 
        columns_to_remove_customers
        )
    
    customers_rename_map = {
        "customer_id": "CustomerId",
        "customer_zip_code_prefix": "CustomerZipCodePrefix",
        "customer_city": "CustomerCity",
        "customer_state": "CustomerState"
    }
    
    df_renamed_customers = rename_columns(
        df_w_fewer_features_customers, 
        customers_rename_map
        )
    
    customer_cols_to_drop = [
        "CustomerCity",
        "CustomerState"
    ]
    
    df_customers_prepped = drop_columns(
        df_renamed_customers,
        customer_cols_to_drop
    )
    
    
    """
    Geolocation Dataset
    """
    df_geo_start = fetch_data("geolocation_bepd_mysql_table")
    
    geo_rename_map = {
        "geolocation_zip_code_prefix": "GeoZipCodePrefix",
        "geolocation_lat": "GeoLatitude",
        "geolocation_lng": "GeoLongitude",
        "geolocation_city": "GeoCity",
        "geolocation_state": "GeoState"
    }
    
    df_renamed_geo = rename_columns(
        df_geo_start, 
        geo_rename_map
        )
    
    geo_string_cols_to_clean = [
        "GeoCity"
    ]
    
    df_geo_string_cleaned = titlecase_and_remove_lt_ws(
        df_renamed_geo,
        geo_string_cols_to_clean
    )
    
    df_geo_coord_set = add_point_column(
        df_geo_string_cleaned,
        lat_col="GeoLatitude", 
        lon_col="GeoLongitude", 
        point_col="GeometryPoint"
    )
    
    geo_to_remove_customers = [
        "GeoLatitude",
		"GeoLongitude"
    ]
    
    df_geo_minus_geo_points = drop_columns(
        df_geo_coord_set, 
        geo_to_remove_customers
        )
    
    geo_cols_to_cast = {
        "GeoState": pl.Categorical,
        "GeoCity": pl.Categorical
    }
    
    df_geo_prepped = cast_columns(
        df_geo_minus_geo_points, 
        geo_cols_to_cast
    )
    
    
    """
    Order Items Dataset
    """
    df_order_items_start = fetch_data("order_items_bepd_mysql_table")
    
    order_item_rename_map = {
        "order_id": "OrderId",
        "order_item_id": "OrderItemId",
        "product_id": "ProductId",
        "seller_id": "SellerId",
        "shipping_limit_date": "ShippingLimitDate",
        "price": "OrderItemPrice",
        "freight_value": "FreightValue"
    }
    
    df_renamed_order_items = rename_columns(
        df_order_items_start, 
        order_item_rename_map
        )
    
    order_item_timestamp_cols = [
        "ShippingLimitDate"
    ]
    
    df_timestamps_converted = convert_strings_to_timestamps(
        df_renamed_order_items, 
        order_item_timestamp_cols, 
        default_date="1900-01-01 01:01:01"
    )
    
    df_order_items_prepped = extract_date_parts(
        df_timestamps_converted, 
        order_item_timestamp_cols
    )
    

    """
    Order Payments Dataset
    """
    df_order_payments_start = fetch_data("order_payments_bepd_mysql_table")
    
    order_payments_rename_map = {
        "order_id": "OrderId",
        "payment_sequential": "PaymentSequential",
        "payment_type": "PaymentType",
        "payment_installments": "PaymentInstallments",
        "payment_value": "PaymentValue"
    }
    
    df_renamed_order_payments = rename_columns(
        df_order_payments_start, 
        order_payments_rename_map
        )
    
    order_payments_replacement = {
        "PaymentType": {
            "boleto": "Ticket",
			"credit_card": "CreditCard",
			"debit_card": "DebitCard",
			"not_defined": "NotDefined",
			"voucher": "Voucher" 
        }
    }
    
    df_order_payments_clean_strings = clean_values_using_dict(
        df_renamed_order_payments, 
        order_payments_replacement
    )

    order_payment_cols_to_cast = {
        "PaymentType": pl.Categorical
    }
    
    
    df_order_payments_prepped = cast_columns(
        df_order_payments_clean_strings,
        order_payment_cols_to_cast
    )
    
    
    """
    Order Reviews Dataset
    """
    df_order_reviews_start = fetch_data("order_reviews_bepd_mysql_table")
    
    cols_to_drop_reviews = [
        "review_id"
    ]
    
    df_w_fewer_features_reviews = drop_columns(
        df_order_reviews_start, 
        cols_to_drop_reviews
        )
    
    order_reviews_rename_map = {
        "order_id": "OrderId",
        "review_score": "ReviewScore",
        "review_comment_title": "ReviewCommentTitle",
        "review_comment_message": "ReviewCommentMessage",
        "review_creation_date": "ReviewCreationDate",
        "review_answer_timestamp": "ReviewAnswerTimestamp"
    }
    
    df_renamed_order_reviews = rename_columns(
        df_w_fewer_features_reviews, 
        order_reviews_rename_map
        )
    
    order_reviews_replacement = [
        "ReviewCommentTitle",
        "ReviewCommentMessage"
    ]
    
    df_order_reviews_strings_imputed = fill_none_with_prefixed_col_name(
        df_renamed_order_reviews,
        order_reviews_replacement,
        "No")
    
    order_review_cols_to_clean = [
        "ReviewCommentTitle",
        "ReviewCommentMessage"
    ]
    
    df_order_reviews_no_lt_ws = clean_string_columns_remove_all_lt_ws_only(
        df_order_reviews_strings_imputed, 
        order_review_cols_to_clean
    )

    df_order_reviews_strings_cleaned = clean_string_columns_remove_duplicative_ws(
        df_order_reviews_no_lt_ws,
        order_review_cols_to_clean
    )
    
    order_reviews_timestamp_cols = [
        "ReviewCreationDate",
        "ReviewAnswerTimestamp"
    ]
    
    df_timestamps_converted = convert_strings_to_timestamps(
        df_order_reviews_strings_cleaned, 
        order_reviews_timestamp_cols, 
        default_date="1900-01-01 01:01:01"
    )
    
    df_order_reviews_prepped = extract_date_parts(
        df_timestamps_converted, 
        order_reviews_timestamp_cols
    )
    
    
    """
    Orders Dataset
    """
    df_orders_start = fetch_data("orders_bepd_mysql_table")
    
    orders_rename_map = {
        "order_id": "OrderId",
        "customer_id": "CustomerId",
        "order_status": "OrderStatus",
        "order_purchase_timestamp": "OrderPurchaseTimestamp",
        "order_approved_at": "OrderApprovedAt",
        "order_delivered_carrier_date": "OrderDeliveredCarrierDate",
        "order_delivered_customer_date": "OrderDeliveredCustomerDate",
        "order_estimated_delivery_date": "OrderEstimatedDeliveryDate"
    }
    
    df_renamed_orders = rename_columns(
        df_orders_start, 
        orders_rename_map
        )
    
    df_orders_titlecased_no_lt_ws = titlecase_and_remove_lt_ws(
        df_renamed_orders,
        ["OrderStatus"]
    )
    
    timestamp_cols_to_handle = [
        "OrderApprovedAt",
        "OrderDeliveredCarrierDate",
        "OrderDeliveredCustomerDate",
        "OrderEstimatedDeliveryDate"
    ]
    
    df_timestamps_converted_orders = convert_strings_to_timestamps(
        df_orders_titlecased_no_lt_ws, 
        timestamp_cols_to_handle, 
        default_date="1900-01-01 01:01:01"
    )

    df_orders_date_parts_extracted = extract_date_parts(
        df_timestamps_converted_orders,
        timestamp_cols_to_handle
    )
    
    df_minutes_calculated = calculate_minutes_between(
        df_orders_date_parts_extracted, 
        start_date_col="OrderDeliveredCustomerDate", 
        end_date_col="OrderDeliveredCarrierDate", 
        output_col="CarrierDeliveryTurnaroundInMinutes"
    )
    
    df_timestamp_to_date = cast_from_timestamp_to_date(
        df_minutes_calculated, 
        "OrderEstimatedDeliveryDate"
        )
    
    orders_cols_to_cast = {
        "OrderStatus": pl.Categorical
    }
    
    df_orders_prepped = cast_columns(
        df_timestamp_to_date,
        orders_cols_to_cast
    )
    
    
    """
    Product Category Dataset
    """
    df_prod_category_start = fetch_data("product_category_bepd_mysql_table")
    
    prod_category_rename_map = {
        "product_category_name": "ProductCategoryName",
        "product_category_name_english": "ProductCategoryNameInEnglish"
    }
    
    df_renamed_prod_category = rename_columns(
        df_prod_category_start, 
        prod_category_rename_map
        )
    
    df_prod_category_strings_cleaned = clean_string_columns_convert_underscores_titlecase(
        df_renamed_prod_category,
        ["ProductCategoryNameInEnglish"]
    )
    
    prod_category_cols_to_cast = {
        "ProductCategoryNameInEnglish": pl.Categorical
    }
    
    df_prod_category_prepped = cast_columns(
        df_prod_category_strings_cleaned,
        prod_category_cols_to_cast
    )
    
    
    """
    Products Dataset
    """
    df_prods_start = fetch_data("products_bepd_mysql_table")
    
    prods_rename_map = {
        "product_id": "ProductId",
        "product_category_name": "ProductCategoryName",
        "product_name_lenght": "ProductNameLength",
        "product_description_lenght": "ProductDescriptionLength",
        "product_photos_qty": "ProductPhotosQty",
        "product_weight_g": "ProductWeightG",
        "product_length_cm": "ProductLengthCm",
        "product_height_cm": "ProductHeightCm",
        "product_width_cm": "ProductWidthCm"
    }
    
    df_renamed_prods = rename_columns(
        df_prods_start, 
        prods_rename_map
        )
    
    prods_cols_to_drop = [
        "ProductNameLength",
        "ProductDescriptionLength",
    ]
    df_prods_fewer_cols = drop_columns(
        df_renamed_prods,
        prods_cols_to_drop
    )
    
    products_replacements_list = {
        "ProductPhotosQty",
        "ProductWeightG",
        "ProductLengthCm",
        "ProductHeightCm",
        "ProductWidthCm"
    }
    
    df_prods_nones_handled = clean_none_values(
        df_prods_fewer_cols,
        products_replacements_list
    )
    
    products_imputation_map = {
        "ProductPhotosQty": -1,
        "ProductWeightG": -1,
        "ProductLengthCm": -1,
        "ProductHeightCm": -1,
        "ProductWidthCm": -1
    }
    
    df_prods_imputed = impute_static_values(
        df_prods_nones_handled, 
        products_imputation_map
    )
    
    df_products_in_english = join_dataframes(
        df_prods_imputed,
        df_prod_category_prepped,
        on="ProductCategoryName", 
        how="left"
    )
    
    products_in_english_cols_to_cast = {
        "ProductPhotosQty": pl.Int16,
        "ProductLengthCm": pl.Int16,
        "ProductHeightCm": pl.Int16,
        "ProductWidthCm": pl.Int16
    }
    
    df_products_casted = cast_columns(
        df_products_in_english,
        products_in_english_cols_to_cast
    )
    
    df_products_in_english_prepped = drop_columns(
        df_products_casted,
        "ProductCategoryName"
    )
        
    
    """
    Sellers Dataset
    """
    df_sellers_start = fetch_data("sellers_bepd_mysql_table")
    
    sellers_rename_map = {
        "seller_id": "SellerId",
        "seller_zip_code_prefix": "SellerZipCodePrefix",
        "seller_city": "SellerCity",
        "seller_state": "SellerState"
    }
    
    df_renamed_sellers = rename_columns(
        df_sellers_start, 
        sellers_rename_map
        )
    
    sellers_cols_to_remove = [
        "SellerCity",
        "SellerState"
    ]
    
    df_sellers_prepped = drop_columns(
        df_renamed_sellers,
        sellers_cols_to_remove
    )
    
    
    """
    Join Tables Into One
    """
    df_main_start = join_dataframes(
        df_orders_prepped, 
        df_customers_prepped,
        on="CustomerId", 
        how="left"
    )
    
    df_main_a = join_dataframes(
        df_main_start, 
        df_order_items_prepped,
        on="OrderId", 
        how="left"
    )
    
    df_main_b = join_dataframes(
        df_main_a, 
        df_order_payments_prepped,
        on="OrderId", 
        how="left"
    )
    
    df_main_c = join_dataframes(
        df_main_b, 
        df_order_reviews_prepped,
        on="OrderId", 
        how="left"
    )
    
    df_main_d = join_dataframes(
        df_main_c, 
        df_products_in_english_prepped,
        on="ProductId", 
        how="left"
    )
    
    df_main_e = join_dataframes(
        df_main_d, 
        df_sellers_prepped,
        on="SellerId", 
        how="left"
    )
    
    cols_to_drop_from_joined_df = [
        'OrderId', 
        'CustomerId', 
        'RecordId', 
        'OrderItemId', 
        'ProductId', 
        'SellerId'
    ]
    
    df_completed = drop_columns(
        df_main_e, 
        cols_to_drop_from_joined_df
    )
    
    # Return some metrics about data in pipeline
    stats, pdf_path = compute_statistics_with_histograms(df_completed)
    print("Stats Summary:", stats)
    print("PDF Report saved to:", pdf_path)
    
    # Send df_geo_prepped to Apache Spark table
    write_to_db(
        df_geo_prepped,
        "geo_bepd_pg_table"
    )
    
    # Send Transformed data (main DataFrame) to PostGIS
    write_to_db(
        df_completed, 
        "main_bepd_pg_table"
    )

###################################################################
#                           Run This Script
###################################################################

if __name__ == "__main__":
    mysql_to_pg_flow()

###################################################################
#                   Additional Helpful Instructions
###################################################################

# Steps to run this pipeline:

# >> docker exec -it prefect-cli bash
# >> cd /root/flows
# >> prefect deploy pipeline_script.py:mysql_to_pg_flow --name "Brazilian-E-Commerce-Public-Dataset-Deployment"
# >> python pipeline_script.py

# To view the Prefect dashboard:
#       http://localhost:4200
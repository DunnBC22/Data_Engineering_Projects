###################################################################
#
#         Prefect Pipeline for German City Rainfall Data
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


###################################################################
#                              Tasks
###################################################################

@task
def create_mariadb_connector():
    """
    This function/task creates & saves the mariadb connector that is used
    to retrieve data from the source database table (in MariaDB).
    """
    mariadb_connector = SqlAlchemyConnector(
        connection_info=ConnectionComponents(
            driver=SyncDriver.MYSQL_PYMYSQL,
            username="mariadb_user",
            password="mariadb_pass",
            host="mariadb",
            port=3306,
            database="gcrd_mariadb_db"
        )
    )

    # Save connector
    mariadb_connector.save("mariadb-connector", overwrite=True)
    return mariadb_connector

@task
def create_postgis_connector():
    """
    This function/task creates & saves the PostGIS connector that is used
    when sending the transformed data to the target database table (in PostGIS).
    """
    postgis_connector = SqlAlchemyConnector(
        connection_info=ConnectionComponents(
            driver=SyncDriver.POSTGRESQL_PSYCOPG2,
            username="pg",
            password="pg",
            host="postgis",
            port=5432,
            database="gcrd_db_pg",
        )
    )
    
    # Save connector
    postgis_connector.save("postgis-connector", overwrite=True)
    return postgis_connector

@task
def fetch_data(
    table_name: str
    ) -> pl.DataFrame:
    """
    This function/task retrieves data from a MariaDB table (as passed in
    via the function/task argument) and puts it into a Polars DataFrame.
    
    Args:
        table_name (str): The table name in the source database for 
            which to look for the data.

    Returns:
        pl.DataFrame: DataFrame with the data from the MariaDB table.
    """
    # Load the saved connector block
    source_connector = SqlAlchemyConnector.load("mariadb-connector")

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
def convert_timestamps_to_dates(
    df: pl.DataFrame, 
    timestamp_cols: List[str] = ["timestamp"], 
    default_date: str = "1900-01-01"
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
            pl.when(pl.col(col).str.strptime(pl.Datetime, "%Y/%m/%d %H:%M:%S", strict=False).is_null())
            .then(pl.lit(default_date).str.strptime(pl.Date, "%Y-%m-%d"))
            .otherwise(pl.col(col).str.strptime(pl.Datetime, "%Y/%m/%d %H:%M:%S", strict=False))
            .alias(f"{col}_date")
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
def clean_string_columns(
    df: pl.DataFrame, 
    string_columns: list[str]
    ) -> pl.DataFrame:
    """
    This function/task cleans string values in the columns/features that 
    are passed into this function/task via the string_columns parameter.
    
    Cleans string values in specified columns by:
        1. Converting to title case
        2. Removing all leading & trailing whitespace
    
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
            .str.to_titlecase()    # Convert to titlecase
            .alias(col)  # Update the column with the cleaned version
        ])
    return df

# Create Geo Point from the latitude and longitude columns
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
def compute_statistics_with_histograms(
    df: pl.DataFrame,
    pdf_path: str = "transformed_data_report.pdf"
) -> tuple[dict, str]:
    """
    Returns descriptive statistics and a histogram PDF for numeric columns in the dataframe.

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
    null_counts = {col: df.select(pl.col(col).is_null().sum()).item() for col in df.columns}
    dtype_counts = df.dtypes

    # Determine numeric columns manually
    numeric_types = {
        pl.Int8, pl.Int16, pl.Int32, pl.Int64,
        pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
        pl.Float32, pl.Float64
    }
    numeric_cols = [col for col, dtype in zip(df.columns, df.dtypes) if dtype in numeric_types]

    numeric_stats = df.select([
        pl.col(col).mean().alias(f"{col}_mean") for col in numeric_cols
    ] + [
        pl.col(col).std().alias(f"{col}_std") for col in numeric_cols
    ])

    histograms = {}

    # Create histograms and add them to the PDF
    with PdfPages(pdf_path) as pdf:
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

    # Append summary page with ReportLab
    c = canvas.Canvas(pdf_path, pagesize=letter)
    text = c.beginText(40, 750)
    text.setFont("Helvetica", 10)
    text.textLine("Data Summary Report")
    text.textLine(f"Rows: {num_rows}, Columns: {num_cols}")
    text.textLine("")

    for k, v in null_counts.items():
        text.textLine(f"Nulls in {k}: {v}")

    text.textLine("")
    for col, dtype in zip(column_names, dtype_counts):
        text.textLine(f"{col}: {dtype}")

    c.drawText(text)
    c.showPage()
    c.save()

    return {
        "num_rows": num_rows,
        "num_columns": num_cols,
        "column_names": column_names,
        "null_counts": null_counts,
        "dtypes": [str(dt) for dt in dtype_counts],
        "numeric_summary": numeric_stats.to_dict(as_series=False),
        "histograms": histograms
    }, pdf_path

@task
def write_to_postgis(
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
    # Load the saved PostGIS connector block
    connector = SqlAlchemyConnector.load("postgis-connector")
    
    # Retrieve the SQLAlchemy engine
    engine = connector.get_engine()
    
    # Write the DataFrame to the specified table in PostGIS
    df.write_database(
        table_name=table_name, 
        connection=engine, 
        if_table_exists=if_exists)

###################################################################
#                              Flow
###################################################################

@flow(
    name="German City Rainfall Data", 
    description="This pipeline transfers German City Rainfall Data from MariaDB to PostGIS.", 
    log_prints=True)
def mariadb_to_postgis_flow(
    name: str = "default_run_name"
    ) -> list:
    """
    This defines the Prefect pipeline that 
        - Retrieves data from MariaDB table
        - Transforms the data
        - Sends transformed data to PostGIS
    """
    context = get_run_context()
    flow_run = context.flow_run

    flow_run.name = f"Run-{name}"  # Set name dynamically at runtime
    
    mariadb_connector = create_mariadb_connector()
    postgis_connector = create_postgis_connector()
    
    # Retrieve data
    df_start = fetch_data("gcrd_mariadb_table")
    
    # Data Transformations
    # Define rename mapping for private schools dataset
    rename_map = {
        "City": "RecordedCity",
        "Latitude": "RecordedLatitude",
        "Longitude": "RecordedLongitude",
        "Month": "RecordedMonth",
        "Year": "RecordedYear",
        "Rainfall (mm)": "RainfallInMillimeters",
        "Elevation (m)": "ElevationInMeters",
        "Climate_Type": "ClimateType",
        "Temperature (Â°C)": "TemperatureInCelsius",
        "Humidity (%)": "HumidityPercent"
    } 
    
    # Rename columns
    df_renamed = rename_columns(
        df_start, 
        rename_map
        )
    
    # Clean String-Valued Features
    string_columns_to_clean = [
        "RecordedCity",
        "ClimateType"
        ]

    df_strings_cleaned = clean_string_columns(
        df_renamed,
        string_columns_to_clean
    )
    
    # Handle Geo Coordinates
    df_with_point = add_point_column(
        df_strings_cleaned, 
        lat_col="RecordedLatitude", 
        lon_col="RecordedLongitude",
        point_col="GeographicalPoint"
        )
    
    # Remove old longitude & latitude coordinate features
    columns_to_remove = [
        "RecordedLongitude",
        "RecordedLatitude"
    ]
    
    df_with_point_cleaned = drop_columns(
        df_with_point, 
        columns_to_remove
        )
    
    # Return some metrics about the data in the pipeline
    stats, pdf_path = compute_statistics_with_histograms(df_with_point_cleaned)
    print("Stats Summary:", stats)
    print("PDF Report saved to:", pdf_path)
    
    # Send transformed data to PostGIS
    write_to_postgis(
        df=df_with_point_cleaned,
        table_name="gcrd_table_pg"
    )

###################################################################
#                           Run This Script
###################################################################

if __name__ == "__main__":
    mariadb_to_postgis_flow()

###################################################################
#                   Additional Helpful Instructions
###################################################################

# Steps to run this pipeline:

# >> docker exec -it prefect-cli bash
# >> cd /root/flows
# >> prefect deploy pipeline_script.py:mariadb_to_postgis_flow --name "German-City-Rainfall-Data-Deployment"
# >> python pipeline_script.py

# To view the Prefect dashboard:
#       http://localhost:4200
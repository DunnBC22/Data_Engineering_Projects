###################################################################
#
#           Prefect Pipeline for US Schools Dataset
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
def create_mysql_connector():
    # MySQL Source Block
    mysql_connector = SqlAlchemyConnector(
        connection_info=ConnectionComponents(
            driver=SyncDriver.MYSQL_PYMYSQL,
            username="mysql",
            password="mysql",
            host="mysql",
            port=3306,
            database="us_schools_geo_mysql_db"
        )
    )
    
    # Save connector
    mysql_connector.save("mysql-connector", overwrite=True)
    return mysql_connector

@task
def create_postgis_connector():
    # PostGIS Target Block
    postgis_connector = SqlAlchemyConnector(
        connection_info=ConnectionComponents(
            driver=SyncDriver.POSTGRESQL_PSYCOPG2,
            username="pg",
            password="pg",
            host="postgis",
            port=5432,
            database="us_schools_geo_db_pg",
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
    This function/task retrieves data from a MySQL table (as passed in
    via the function/task argument) and puts it into a Polars DataFrame.
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
    """
    return df.drop(columns_to_drop)

@task
def concatenate_dataframes(df1: pl.DataFrame, df2: pl.DataFrame) -> pl.DataFrame:
    """
    Concatenates two Polars DataFrames vertically (row-wise).

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
def cast_columns(
    df: pl.DataFrame, 
    column_casts: dict
    ) -> pl.DataFrame:
    """
    This function/task updates the column/feature data types according
    to the columns_casts dictionary that is passed into this function/task.
    """
    # Cast selected columns
    for col, dtype in column_casts.items():
        df = df.with_columns(pl.col(col).cast(dtype).alias(col))
    return df

@task
def clean_nan_values(df: pl.DataFrame, column_names: list) -> pl.DataFrame:
    """
    Cleans a Polars DataFrame by replacing null and NaN values for specified columns:
    - Float columns: fill null and NaN with 0.0
    - Integer columns: fill null with 0
    - Boolean columns: fill null with False
    - String columns: fill null with "Unknown"
    - Other types: fill null with "N/A"
    """
    for col in column_names:
        if col in df.columns:
            dtype = df.schema[col]
            
            if dtype in [pl.Float64, pl.Float32]:
                df = df.with_columns(
                    pl.col(col)
                    .fill_null(0.0)
                    .fill_nan(0.0)
                )
            elif dtype in [pl.Int64, pl.Int32, pl.Int16, pl.Int8, pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64]:
                df = df.with_columns(pl.col(col).fill_null(0))
            elif dtype == pl.Boolean:
                df = df.with_columns(pl.col(col).fill_null(False))
            elif dtype == pl.Utf8:
                df = df.with_columns(pl.col(col).fill_null("Unknown"))
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
    This function/task extracts the following from the date column
    passed into this function/task via the date_col parameter.
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
    This function/task cleans string values in the columns/features
    that are passed into this function/task via the 
    string_columns parameter.
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

@task
def clean_string_columns_custom(
    df: pl.DataFrame,
    string_columns: list[str]
    ) -> pl.DataFrame:
    """
    This is a custom function/task that cleans string values in the
    columns/features that are passed into this function/task via the 
    string_columns parameter.
    """
    # Apply cleanup operations on string columns
    for col in string_columns:
        df = df.with_columns([
            pl.col(col)
            .str.replace("/", " ", literal=True)    # replace "/" with a space
            .str.to_titlecase()                     # Convert to titlecase
            .str.replace_all(r"\s+", "")            # Remove all whitespace
            .alias(col)  # Update feature with cleaned version
        ])
    return df

@task
def impute_static_values(
    df: pl.DataFrame, 
    impute_map: dict
    ) -> pl.DataFrame:
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
    """
    # Cast selected columns
    for col, dtype in column_casts.items():
        df = df.with_columns(pl.col(col).cast(dtype).alias(col))
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
def write_to_db(
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
    name="US School Locations Dataset", 
    description="This pipeline transfers US school location data from MySQL to PostGIS.",
    log_prints=True)
def mysql_to_postgis_flow(
    name: str = "default_run_name"
    ) -> list:
    """
    This defines the Prefect pipeline that 
        - Retrieves data from two MySQL tables,
        - Transforms the data
        - Sends the transformed (single) dataframe to PostGIS
    """
    context = get_run_context()
    flow_run = context.flow_run

    flow_run.name = f"Run-{name}"  # Set name dynamically at runtime
    
    mysql_connector = create_mysql_connector()
    postgis_connector = create_postgis_connector()
    
    # Retrieve public school data
    df_public = fetch_data("us_schools_geo_mysql_table_public")
    
    # Retrieve private school data
    df_private = fetch_data("us_schools_geo_mysql_table_private")
    
    # Data Transformations
    # Define rename mapping for private schools dataset
    private_rename_map = {
        "X": "XCoord",
        "Y": "YCoord",
        "FID": "fid",
        "OBJECTID": "ObjectId",
        "NCESID": "NcesId",
        "NAME": "SchoolName",
        "ADDRESS": "SchoolAddress",
        "CITY": "SchoolCity",
        "STATE": "SchoolState",
        "ZIP": "SchoolZipCode",
        "ZIP4": "SchoolZipFour",
        "TELEPHONE": "SchoolTelephone",
        "TYPE": "SchoolType",
        "STATUS": "SchoolStatus",
        "POPULATION": "DistrictPopulation",
        "COUNTY": "SchoolCounty",
        "COUNTYFIPS": "CountyFips",
        "COUNTRY": "CountryName",
        "LATITUDE": "LatitudeCoord",
        "LONGITUDE": "LongitudeCoord",
        "NAICS_CODE": "naics_code",
        "NAICS_DESC": "naics_description",
        "SOURCE": "Source",
        "SOURCEDATE": "SourceDate",
        "VAL_METHOD": "ValidationMethod",
        "VAL_DATE": "ValidationDate",
        "WEBSITE": "WebsiteLink",
        "LEVEL_": "SchoolLevel",
        "ENROLLMENT": "SchoolEnrollment",
        "START_GRAD": "StartGrade",
        "END_GRADE": "EndGrade",
        "FT_TEACHER": "NumOfFullTimeTeachers",
        "SHELTER_ID": "ShelterId"
    } 
    
    # Define rename mapping for public schools dataset
    public_rename_map = {
        "X": "XCoord",
        "Y": "YCoord",
        "OBJECTID": "ObjectId",
        "NCESID": "NcesId",
        "NAME": "SchoolName",
        "ADDRESS": "SchoolAddress",
        "CITY": "SchoolCity",
        "STATE": "SchoolState",
        "ZIP": "SchoolZipCode",
        "ZIP4": "SchoolZipFour",
        "TELEPHONE": "SchoolTelephone",
        "TYPE": "SchoolType",
        "STATUS": "SchoolStatus",
        "POPULATION": "DistrictPopulation",
        "COUNTY": "SchoolCounty",
        "COUNTYFIPS": "CountyFips",
        "COUNTRY": "CountryName",
        "LATITUDE": "LatitudeCoord",
        "LONGITUDE": "LongitudeCoord",
        "NAICS_CODE": "naics_code",
        "NAICS_DESC": "naics_description",
        "SOURCE": "Source",
        "SOURCEDATE": "SourceDate",
        "VAL_METHOD": "ValidationMethod",
        "VAL_DATE": "ValidationDate",
        "WEBSITE": "WebsiteLink",
        "LEVEL_": "SchoolLevel",
        "ENROLLMENT": "SchoolEnrollment",
        "ST_GRADE": "StartGrade",
        "END_GRADE": "EndGrade",
        "DISTRICTID": "district_id",
        "FT_TEACHER": "NumOfFullTimeTeachers",
        "SHELTER_ID": "ShelterId"
    }
    
    # Rename columns
    df_private_renamed = rename_columns(
        df_private, 
        private_rename_map
        )
    
    df_public_renamed = rename_columns(
        df_public, 
        public_rename_map
        )
    
    # Remove unnecessary Features in df_private
    columns_to_remove_private = [
        "XCoord",
        "YCoord",
        "fid",
        "ObjectId",
        "naics_code",
        "naics_description"
    ]
    
    condensed_df_private = drop_columns(
        df_private_renamed, 
        columns_to_remove_private
        )
    
    # Remove unnecessary Features in df_public
    columns_to_remove_public = [
        "XCoord",
        "YCoord",
        "ObjectId",
        "district_id",
        "naics_code",
        "naics_description"
        ]
    
    condensed_df_public = drop_columns(
        df_public_renamed, 
        columns_to_remove_public
        )
    
    # concatenate DataFrames
    df_concatenated = concatenate_dataframes(
        condensed_df_private, 
        condensed_df_public, 
        )
    
    # Handle nan in features
    nan_cols_to_correct = [
        "StartGrade",
        "EndGrade",
        "NumOfFullTimeTeachers"
    ]
    
    df_w_o_nans = clean_nan_values(
        df_concatenated, 
        column_names=nan_cols_to_correct
        )
    
    # convert_timestamp_to_date
    timestamp_feature = [
        "SourceDate", 
        "ValidationDate"
        ]
    
    df_w_timestamps = convert_timestamps_to_dates(
        df_w_o_nans, 
        timestamp_cols=timestamp_feature,
        default_date = "1900-01-01"
        )
    
    # handle erroneous values
    # ValidationMethod update
    clean_string_columns_custom(
        df_w_o_nans,
        string_columns=["ValidationMethod"]
    )
    
    # handle string features
    imputation_map = {
        "NcesId": "999999999999",
        "SchoolName": "SchoolNameUnknown",
        "SchoolAddress": "SchoolAddressUnknown",
        "SchoolCity": "SchoolCityUnknown",
        "StartGrade": "-1"
    }
    
    df_imputed = impute_static_values(
        df_w_timestamps, 
        impute_map = imputation_map
    )
    
    # Clean String-Valued Features
    string_columns = [
        "SchoolName",
        "SchoolAddress",
        "SchoolCity",
        "SchoolCounty",
        "CountyFips",
        "Source",
        "WebsiteLink",
        "SchoolLevel",
        "ShelterId"
        ]
    
    # Clean the string columns
    df_strings_cleaned = clean_string_columns(
        df_imputed, 
        string_columns
        )
    
    # Update Feature data types
    # Specify the columns and their target data types
    column_casts = {
        # "StartGrade": pl.Int32,
        # "DistrictPopulation": pl.Int32,
        # "SchoolEnrollment": pl.Int32,
        "NumOfFullTimeTeachers": pl.Int32
    }

    # Apply the casting function
    casted_df = cast_columns(
        df_strings_cleaned, 
        column_casts
        )
    
    # Handle Geo Coordinates
    df_with_point = add_point_column(
        casted_df, 
        lat_col="LatitudeCoord", 
        lon_col="LongitudeCoord",
        point_col="SchoolLocation"
        )
    
    # Remove old longitude & latitude coordinate features
    columns_to_remove = [
        "LatitudeCoord",
        "LongitudeCoord"
    ]
    
    df_completed = drop_columns(
        df_with_point, 
        columns_to_remove
        )
    
    # Return some metrics about the data in the pipeline
    stats, pdf_path = compute_statistics_with_histograms(df_completed)
    print("Stats Summary:", stats)
    print("PDF Report saved to:", pdf_path)
    
    # Send transformed data to PostGIS
    write_to_db(
        df_completed, 
        table_name="us_schools_geo_table_pg",
        if_exists="replace"
    )

###################################################################
#                           Run This Script
###################################################################

if __name__ == "__main__":
    mysql_to_postgis_flow()

###################################################################
#                   Additional Helpful Instructions
###################################################################

# Steps to run this pipeline:

# >> docker exec -it prefect-cli bash
# >> cd /root/flows
# >> prefect deploy pipeline_script.py:mysql_to_postgis_flow --name "US-Schools-Dataset-Deployment"
# >> python pipeline_script.py

# To view the Prefect dashboard:
#       http://localhost:4200
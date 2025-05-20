###################################################################
#
#           Prefect Pipeline for Heart Attack Risk
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
            database="ha_risk_pg_db",
        )
    )
    
    # Save connector
    postgres_connector.save("postgres-connector", overwrite=True)
    return postgres_connector

@task
def create_mysql_connector():
    """
    This function/task creates & saves the MySQL connector that is used
    when sending the transformed data to the target database table (in MySQL).
    """
    mysql_connector = SqlAlchemyConnector(
        connection_info=ConnectionComponents(
            driver=SyncDriver.MYSQL_PYMYSQL,
            username="mysql",
            password="mysql",
            host="mysql",
            port=3306,
            database="ha_risk_mysql_db"
        )
    )
    
    # Save connector
    mysql_connector.save("mysql-connector", overwrite=True)
    return mysql_connector

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
    connector = SqlAlchemyConnector.load("postgres-connector")

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
def remove_leading_and_trailing_whitespace(
    df: pl.DataFrame, 
    string_columns: list[str]
    ) -> pl.DataFrame:
    """
    This function/task cleans string values in the columns/features that 
    are passed into this function/task via the string_columns parameter.
    
    Cleans string values in specified columns by applying the following of transformations:
        1. Strip leading/trailing spaces
    
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
            .str.strip_chars()
            .alias(col)
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
        1. Replacing the '&' character with 'And'
        2. Removing commas, periods, division signs, and dashes
        3. Removing all leading & trailing whitespace
        4. Converting all values to title case
    
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
            .str.replace_all("&", "And")
            .str.replace_all(r"[,\.\-/]", "")   # remove commas, periods, division signs, & dashes
            .str.strip_chars()
            .str.to_titlecase()
            .alias(col)
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
        "null_counts": null_counts,
        "dtypes": [str(dt) for dt in dtype_counts],
        "numeric_summary": numeric_stats.to_dict(as_series=False),
        "bar_charts": bar_charts
    }, pdf_path

@task
def write_to_mysql(
    df: pl.DataFrame, 
    table_name: str,
    if_table_exists: str = "append"
    ):
    """
    This function/task sends the transformed data (in Polars) to the database
    table that is named in the arguments passed into this function.
    
    Args:
        df (pl.DataFrame): Polars DataFrame of data to insert into db table.
        table_name (str): The name of the table in which to insert the data.
        if_exists (str): What to do if the table already exists.
    """
    # Load the saved MySQL connector block
    connector = SqlAlchemyConnector.load("mysql-connector")
    
    # Retrieve the SQLAlchemy engine
    engine = connector.get_engine()
    
    # Write the DataFrame to the specified table in MySQL
    df.write_database(
        table_name=table_name, 
        connection=engine,
        if_table_exists=if_table_exists
        )

###################################################################
#                              Flow
###################################################################

@flow(
    name="Heart Attack Risk Data", 
    description="This pipeline transfers Heart Attack Risk Data from Postgres to MySQL.",
    log_prints=True)
def postgres_to_mysql_flow(
    name: str = "default_run_name"
    ) -> list:
    """
    This defines the Prefect pipeline that 
        - Retrieves data from Postgres,
        - Transforms the data,
        - Sends the transformed data to MySQL
    """
    context = get_run_context()
    flow_run = context.flow_run

    flow_run.name = f"Run-{name}"  # Set name dynamically at runtime
    
    postgres_connector = create_postgres_connector()
    mysql_connector = create_mysql_connector()
    
    # Retrieve data
    df_start = fetch_data("ha_risk_pg_table")
    
    # Data Transformations
    rename_map = {
        "Age": "PatientAge",
        "Gender": "PatientGender",
        "Smoking": "SmokingStatus",
        "Alcohol_Consumption": "AlcoholConsumption",
        "Physical_Activity_Level": "PhysicalActivityLevel",
        "BMI": "PatientBodyMassIndex",
        "Cholesterol_Level": "CholesterolLevel",
        "Resting_BP": "RestingBloodPressure",
        "Heart_Rate": "HeartRate",
        "Family_History": "FamilyHistory",
        "Stress_Level": "StressLevel",
        "Chest_Pain_Type": "ChestPainType",
        "Fasting_Blood_Sugar": "FastingBloodSugar",
        "ECG_Results": "EcgResults",
        "Exercise_Induced_Angina": "ExerciseInducedAngina",
        "Max_Heart_Rate_Achieved": "MaxHeartRateAchieved",
        "Heart_Attack_Risk": "HeartAttackRisk"
    } 
    
    # Rename columns
    df_renamed = rename_columns(
        df_start, 
        rename_map
        )
    
    # Remove leading and trailing whitespace
    remove_lt_cols = {
        "PatientGender",
        "PhysicalActivityLevel",
        "StressLevel",
        "ChestPainType",
        "Thalassemia",
        "EcgResults",
        "HeartAttackRisk"
    }
    
    df_w_o_lt_whitespace = remove_leading_and_trailing_whitespace(
        df_renamed,
        remove_lt_cols 
    )
    
    string_columns_to_close = {
        "EcgResults",
        "Thalassemia",
        "ChestPainType"
    }
    
    # Clean the string columns
    df_strings_cleaned = clean_string_columns(
        df_w_o_lt_whitespace, 
        string_columns_to_close
        )
    
    # Return some metrics about the data in the pipeline
    stats, pdf_path = compute_statistics_with_histograms(df_strings_cleaned)
    print("Stats Summary:", stats)
    print("PDF Report saved to:", pdf_path)
    
    # Send transformed data to MySQL
    write_to_mysql(
        df_strings_cleaned,
        table_name="ha_risk_mysql_table")

###################################################################
#                           Run This Script
###################################################################

if __name__ == "__main__":
    postgres_to_mysql_flow()

###################################################################
#                   Additional Helpful Instructions
###################################################################

# Steps to run this pipeline:

# >> docker exec -it prefect-cli bash
# >> cd /root/flows
# >> prefect deploy pipeline_script.py:postgres_to_mysql_flow --name "Heart-Attack-Risk-Data-Deployment"
# >> python pipeline_script.py

# To view the Prefect dashboard:
#       http://localhost:4200
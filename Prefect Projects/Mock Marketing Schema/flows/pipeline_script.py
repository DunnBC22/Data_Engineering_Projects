###################################################################
#
#          Prefect Pipeline for Mock Marketing Schema
#
###################################################################

from typing import List

from prefect import task, flow
from prefect_sqlalchemy import (
    SqlAlchemyConnector, 
    ConnectionComponents, 
    SyncDriver
    )
from prefect.context import get_run_context

from cassandra.cluster import Cluster

import polars as pl

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

###################################################################
#                              Tasks
###################################################################

@task
def create_pg_connector():
    # Postgres Source Block
    pg_connector = SqlAlchemyConnector(
        connection_info=ConnectionComponents(
            driver=SyncDriver.POSTGRESQL_PSYCOPG2,
            username="pg",
            password="pg",
            host="postgres",
            port=5432,
            database="mock_marketing_pg_db"
        )
    )

    # Save connector
    pg_connector.save("pg-connector", overwrite=True)
    return pg_connector

@task
def fetch_data(
    table_name: str,
    connector_name: str = "pg-connector"
    ) -> pl.DataFrame:
    """
    This function/task retrieves data from a Postgres table (as passed in
    via the function/task argument) and puts it into a Polars DataFrame.
    
    Args:
        table_name (str): The name of the table for which to look for the data.
        connector_name (str): The name of the connector for connecting to 
            the database to retrieve data.

    Returns:
        pl.DataFrame: DataFrame with the data from the database table.
    """
    # Load the saved connector block
    connector = SqlAlchemyConnector.load(connector_name)

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
        pl.DataFrame: DataFrame with the renamed columns.
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
    default_date: str = "2999-01-01"
) -> pl.DataFrame:
    """
    This function/task converts one or more timestamp columns in the DataFrame to date format.
    
    Parameters:
        - df: Polars DataFrame
        - timestamp_cols: List of column names to convert from string to date
        - default_date: The default value to impute for invalid or missing date values (default is '9999-01-01')

    Returns:
        - DataFrame with new columns appended, named '<original_col>'
    """
    for col in timestamp_cols:
        # Attempt to convert to datetime
        df = df.with_columns(
            pl.when(pl.col(col).str.strptime(pl.Datetime, "%Y-%m-%d", strict=False).is_null())
            .then(pl.lit(default_date).str.strptime(pl.Date, "%Y-%m-%d"))
            .otherwise(pl.col(col).str.strptime(pl.Datetime, "%Y-%m-%d", strict=False))
            .alias(f"{col}")
        )
    return df

@task
def clean_string_columns_remove_all_lt_ws_and_titlecase(
    df: pl.DataFrame, 
    string_columns: list[str]
    ) -> pl.DataFrame:
    """
    This function/task removes all leading & trailing whitespace
    then titlecases the string values in the columns/features
    that are passed into this function/task.
    
    Args:
        df: Input Polars DataFrame
        string_columns: List of column names (strings) that need 
            to have leading and trailing whitespace removed then
            have string values titlecased.
    
    Returns:
        A Polars DataFrame with the string columns cleaned.
    """
    # Apply cleanup operations on string columns
    for col in string_columns:
        df = df.with_columns([
            pl.col(col)
            .str.strip_chars()
            .str.to_titlecase()
            .alias(col)  # Update the column with the cleaned version
        ])
    return df

@task
def clean_string_columns_remove_all_ws(
    df: pl.DataFrame,
    string_columns: list[str]
    ) -> pl.DataFrame:
    """
    This function/task removes all whitespace for the 
    columns/features that are passed into this function/task.
    
    Args:
        df: Input Polars DataFrame
        string_columns: List of column names (strings) that need to have 
            all whitespace removed.
    
    Returns:
        A Polars DataFrame with the string columns cleaned.
    """
    # Apply cleanup operations on string columns
    for col in string_columns:
        df = df.with_columns([
            pl.col(col)
            .str.replace_all(r"\s", "")
            .str.strip_chars()
            .alias(col)
        ])
    return df

@task
def clean_currency_columns(
    df: pl.DataFrame,
    currency_columns: list[str]
    ) -> pl.DataFrame:
    """
    This function/task removes all commas and dollar signs ('$') for 
    the columns/features that are passed into this function/task. Then,
    the values are converted to the floating point data type.
    
    Args:
        df: Input Polars DataFrame
        string_columns: List of column names (strings) to clean & 
            convert to currency (floating point data type).
    
    Returns:
        A Polars DataFrame with the string columns cleaned.
    """
    # Apply cleanup operations on string columns
    for col in currency_columns:
        df = df.with_columns([
            pl.col(col)
            .cast(str)
            .str.replace_all(r"[$,]", "")
            .cast(pl.Float64)
            .alias(col)
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

def remove_prefix(
    df: pl.DataFrame,
    column: str,
    prefix_to_remove: str
) -> pl.DataFrame:
    """
    Removes a fixed prefix string from the beginning of each value 
        in the specified column.

    Args:
        df (pl.DataFrame): The input Polars DataFrame.
        column (str): The name of the column to process.
        prefix_to_remove (str): The prefix string to remove.

    Returns:
        pl.DataFrame: The DataFrame with the prefix removed from the specified column.
    """
    pattern = f'^{prefix_to_remove}'  # regex pattern to match prefix at start
    df = df.with_columns(
        pl.col(column).cast(str).str.replace(pattern, '', literal=False).alias(column)
    )
    return df

@task
def titlecase_string_values(
    df: pl.DataFrame, 
    string_columns: list[str]
    ) -> pl.DataFrame:
    """
    This function/task titlecases all of the values for
    columns/features that are passed into this function/task.
    
    Args:
        df: Input Polars DataFrame
        string_columns: List of column names (strings) to 
            titlecased their values
    
    Returns:
        A Polars DataFrame with the string columns cleaned.
    """
    # Apply cleanup operations on string columns
    for col in string_columns:
        df = df.with_columns([
            pl.col(col)
            .str.to_titlecase()
            .alias(col)
        ])
    return df

@task
def drop_first_duplicate(
    df: pl.DataFrame, 
    column_name: str
    ) -> pl.DataFrame:
    """
    Removes the first occurrence of duplicate rows based on a specified column.

    Parameters:
        - df: Polars DataFrame to process.
        - column_name: The column to identify duplicates on.

    Returns:
        - Polars DataFrame with the first duplicate of each group removed.
    """
    # Add a row number to preserve original order
    df_with_index = df.with_row_index(name="id_row_num")
    
    # Reverse the DataFrame to keep the *last* of the duplicates
    reversed_df = df_with_index.reverse()

    # Keep only the last occurrence (which was originally second+)
    deduplicated = reversed_df.unique(subset=[column_name], keep="first")

    # Restore original order
    deduplicated = deduplicated.sort("id_row_num").drop("id_row_num")

    return deduplicated

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
    cluster = Cluster(['cassandra'])
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
    name="Mock Marketing Dataset", 
    description="This pipeline transfers Mock Marketing dataset from Postgres Database to Apache Cassandra.", 
    log_prints=True)
def pg_to_cassie_flow(
    name: str = "default_run_name"
    ) -> list:
    """
    This defines the Prefect pipeline that 
        - Retrieves data from Postgres
        - Transforms the data
        - Sends the transformed data to Apache Cassandra
    """
    
    context = get_run_context()
    flow_run = context.flow_run

    flow_run.name = f"Run-{name}"
    
    create_pg_connector()
    
    # ---------------------------------------------
    # Account
    # ---------------------------------------------
    
    df_start_account = fetch_data(
        "mock_marketing_pg_account"
    )
    
    account_rename_map = {
        "CUST_ID": "CustomerId",
		"ACQUISITION_COST": "AcquisitionCost",
		"INTERNET_BANKING_INDICATOR": "InternetBankingIndicator",
		"DATE_FIRST_ACCOUNT_OPENED": "DateFirstAccountOpened",
		"DATE_LAST_ACCOUNT_OPENED": "DateLastAccountOpened",
		"PURSUIT": "Pursuit",
		"PRIMARY_ADVISOR_ORGANIZATION_ID": "PrimaryAdvisorOrgId",
		"PRIMARY_BRANCH_PROXIMITY": "PrimaryBranchProximity",
		"PRIMARY_SPOKEN_LANGUAGE": "PrimarySpokenLanguage",
		"PRIMARY_WRITTEN_LANGUAGE": "PrimaryWrittenLanguage",
		"SATISFACTION_RATING_FROM_SURVEY": "SatisfactionRatingFromSurvey",
		"SECONDARY_ADVISOR_ID": "SecondaryAdvisorId",
		"SECONDARY_ADVISOR_ORGANIZATION_ID": "SecondaryAdvisorOrgId",
		"SPECIAL_TERMS_INDICATOR": "SpecialTermsIndicator"
    }
    
    df_account_renamed = rename_columns(
        df_start_account, 
        account_rename_map
    )
    
    account_cols_to_drop = [
        "PrimarySpokenLanguage",
     	"PrimaryWrittenLanguage"
    ]
    
    df_account_w_fewer_features = drop_columns(
        df_account_renamed,
        account_cols_to_drop
    )
    
    
    df_account_titlecased = titlecase_string_values(
        df_account_w_fewer_features,
        ["SatisfactionRatingFromSurvey"]
    )
    
    account_cols_to_remove_all_ws = [
        "Pursuit",
		"SatisfactionRatingFromSurvey"
    ]
    
    # create task to remove ALL whitespace only
    df_account_no_ws = clean_string_columns_remove_all_ws(
        df_account_titlecased,
        account_cols_to_remove_all_ws
    )
    
    account_dates_to_convert = [
        "DateFirstAccountOpened",
		"DateLastAccountOpened"
    ]
    
    df_account_prepped = convert_strings_to_dates(
        df_account_no_ws,
        account_dates_to_convert
    )
    
    # ---------------------------------------------
    # Customer
    # ---------------------------------------------
    
    df_start_customer = fetch_data(
        "mock_marketing_pg_customer"
    )
    
    customer_rename_map = {
        "CUST_ID": "CustomerId",
		"GENDER": "CustomerGender",
		"FIRST_NAME": "CustomerFirstName",
		"LAST_NAME": "CustomerLastName",
		"EMAIL": "CustomerEmail",
		"SSN": "CustomerSocSecNumLastFour",
		"AGE_RANGE": "CustomerAgeRange",
		"ANNUAL_INCOME": "CustomerAnnualIncome",
		"BIRTH_YEAR": "CustomerBirthYear",
		"CURRENT_EMPLOYMENT_START_DATE": "CustomerCurrentEmploymentStartDate",
		"CUSTOMER_BEHAVIOR": "CustomerBehavior",
		"EDUCATION_LEVEL": "CustomerEducationLevel",
		"EMPLOYMENT_STATUS": "CustomerEmploymentStatus",
		"MARITAL_STATUS": "CustomerMaritalStatus",
		"MONTHLY_NET_INCOME": "CustomerMonthlyNetIncome",
		"PROFESSION": "CustomerProfession",
		"RETIREMENT_AGE": "CustomerRetirementAge",
		"STATUS": "CustomerStatus",
		"WALLET_SHARE_PERCENTAGE": "CustomerWalletSharePercentage"
    }
    
    df_customer_renamed = rename_columns(
        df_start_customer, 
        customer_rename_map
    )
    
    customer_cols_to_drop = [
        "CustomerRetirementAge"
    ]
    
    df_customers_w_fewer_features = drop_columns(
        df_customer_renamed,
        customer_cols_to_drop
    )
    
    customer_cols_to_clean = [
        "CustomerFirstName",
		"CustomerLastName",
		"CustomerProfession",
		"CustomerMaritalStatus",
		"CustomerEmploymentStatus",
		"CustomerEducationLevel",
		"CustomerBehavior",
        "CustomerAnnualIncome"
    ]
    
    df_customers_str_cleaned_a = clean_string_columns_remove_all_lt_ws_and_titlecase(
        df_customers_w_fewer_features,
        customer_cols_to_clean
    )
    
    customer_cols_to_clean_dict = {
        "CustomerGender": 
            {
                "Female": "F",
			    "Male": "M"
            },
		"CustomerAgeRange": 
            {
                "25 to 29": "25-29",
                "30 to 39": "30-39",
                "40 to 54": "40-54",
                "55 to 64": "55-64",
                "65 and over": "65+"
            },
		"CustomerEducationLevel": 
            {
                "PhD": "Doctoral"
            }		
        }
    
    df_customers_str_values_cleaned = clean_values_using_dict(
        df_customers_str_cleaned_a,
        customer_cols_to_clean_dict
    )
    
    df_customers_ssn_prefix_removed = remove_prefix(
        df_customers_str_values_cleaned,
        "CustomerSocSecNumLastFour",
        "XXX-XX-"
    )
    
    df_customers_currency_converted = clean_currency_columns(
        df_customers_ssn_prefix_removed,
        ["CustomerAnnualIncome"]
        )
    
    df_customers_prepped = convert_strings_to_dates(
        df_customers_currency_converted,
        ["CustomerCurrentEmploymentStartDate"]
    )
    
    # ----------------------------------------------
    # Financials
    # ----------------------------------------------
    
    df_start_financials = fetch_data(
        "mock_marketing_pg_financials"
    )
    
    financials_rename_map = {
        "CUST_ID": "CustomerId",
		"MONTHLY_HOUSING_COST": "MonthlyHousingCost",
		"CONTACT_PREFERENCE": "ContactPreference",
		"CREDIT_AUTHORITY_LEVEL": "CreditAuthorityLevel",
		"CREDIT_SCORE": "CreditScore",
		"CREDIT_UTILIZATION": "CreditUtilization",
		"DEBT_SERVICE_COVERAGE_RATIO": "DebtServiceCoverageRatio"
    }
    
    df_financials_renamed = rename_columns(
        df_start_financials, 
        financials_rename_map
    )
    
    cols_to_titlecase_string_values_then_remove_all_ws = [
        "CreditAuthorityLevel",
		"ContactPreference"
    ]
    
    df_customers_titlecased = titlecase_string_values(
        df_financials_renamed,
        cols_to_titlecase_string_values_then_remove_all_ws
    )
    
    df_financials_prepped = clean_string_columns_remove_all_ws(
        df_customers_titlecased,
        cols_to_titlecase_string_values_then_remove_all_ws
    )
    
    # -----------------------------------------------
    # Household
    # -----------------------------------------------
    
    df_start_household = fetch_data(
        "mock_marketing_pg_household"
    )
    
    household_rename_map = {
        "CUST_ID": "CustomerId",
		"HOUSEHOLD_ID": "HouseholdId",
		"ADDRESS": "HouseholdAddress",
		"CITY": "HouseholdCity",
		"COUNTRY": "HouseholdCountry",
		"STATE": "HouseholdState",
		"ZIP": "HouseholdZipCode",
		"ADDRESS_LAST_CHANGED_DATE": "HouseholdAddressLastChanged",
		"NUMBER_OF_DEPENDENT_ADULTS": "HouseholdNumOfDependentAdults",
		"NUMBER_OF_DEPENDENT_CHILDREN": "HouseholdNumOfDependentChildren",
		"FAMILY_SIZE": "HouseholdFamilySize",
		"HEAD_OF_HOUSEHOLD_INDICATOR": "HouseholdHeadOfHouseholdIndicator",
		"HOME_OWNER_INDICATOR": "HouseholdHomeOwnerIndicator",
		"URBAN_CODE": "UrbanCode",
		"PRIMARY_ADVISOR_ID": "PrimaryAdvisorId"
    }
        
    df_household_renamed = rename_columns(
        df_start_household, 
        household_rename_map
    )
    
    household_cols_to_drop = [
        "HouseholdNumOfDependentAdults",
		"HouseholdId"
    ]
    
    df_household_w_fewer_features = drop_columns(
        df_household_renamed,
        household_cols_to_drop
    )
    
    cols_to_titlecase_and_remove_all_lt_ws = [
        "HouseholdCity",
		"HouseholdAddress"
    ]
    
    df_household_titlecased_and_no_lt_ws = clean_string_columns_remove_all_lt_ws_and_titlecase(
        df_household_w_fewer_features,
        cols_to_titlecase_and_remove_all_lt_ws
    )
    
    df_household_dates_converted = convert_strings_to_dates(
        df_household_titlecased_and_no_lt_ws,
        ["HouseholdAddressLastChanged"]
    )
    
    customer_strings_cleaning_map = {
        "HouseholdCountry": 
            {
                "United States": "USA"
            },
		"HouseholdState": 
            {
                'Arizona': 'AZ',
                'California': 'CA',
                'Colorado': 'CO',
                'Connecticut': 'CT',
                'District of Columbia': 'DC',
                'Florida': 'FL', 
                'Georgia': 'GA',
                'Illinois': 'IL',
                'Indiana': 'IN',
                'Iowa': 'IA',
                'Kentucky': 'KY',
                'Massachusetts': 'MA',
                'Minnesota': 'MN',
                'Missouri': 'MO',
                'Nebraska': 'NE',
                'Nevada': 'NV',
                'New Jersey': 'NJ',
                'New York': 'NY',
                'Oklahoma': 'OK',
                'Pennsylvania': 'PA',
                'Saskatchewan': 'Sask',
                'South Carolina': 'SC',
                'South Dakota': 'SD',
                'Texas': 'TX',
                'Utah': 'UT',
                'Washington': 'WA',
                'West Virginia': 'WV', 
                'Alberta': 'AB',
                'British Columbia': 'BC',
                'Manitoba': 'MB',
                'New Brunswick': 'NB',
                'Newfoundland and Labrador': 'NL',
                'Nova Scotia': 'NS',
                'Nunavut': 'NU',
                'Ontario': 'ON',
                'Prince Edward Island': 'PE',
                'Québec': 'QC'
            }
        }
    
    df_household_prepped = clean_values_using_dict(
        df_household_dates_converted,
        customer_strings_cleaning_map
    )
    
    # ------------------------------------------------
    # Marketing
    # ------------------------------------------------
    
    df_start_marketing = fetch_data(
        "mock_marketing_pg_marketing"
    )
    
    marketing_rename_map = {
        "CUST_ID": "CustomerId",
		"ADVERTISING_INDICATOR": "AdvertisingIndicator",
		"ATTACHMENT_ALLOWED_INDICATOR": "AttachmentAllowedIndicator",
		"PREFERRED_COMMUNICATION_FORM": "PreferredCommunicationForm",
		"IMPORTANCE_LEVEL_CODE": "ImportanceLevelCode",
		"INFLUENCE_SCORE": "InfluenceScore",
		"MARKET_GROUP": "MarketGroup",
		"LOYALTY_RATING_CODE": "LoyaltyRatingCode",
		"RECORDED_VOICE_SAMPLE_ID": "RecordedVoiceSampleId",
		"REFERRALS_VALUE_CODE": "ReferralsValueCode",
		"RELATIONSHIP_START_DATE": "RelationshipStartDate"
    }
        
    df_marketing_renamed = rename_columns(
        df_start_marketing, 
        marketing_rename_map
    )
    
    cols_titlecase_and_remove_all_ws = [
        "PreferredCommunicationForm",
		"ImportanceLevelCode",
		"MarketGroup",
		"ReferralsValueCode"
    ]
    
    df_marketing_titlecase = titlecase_string_values(
        df_marketing_renamed,
        cols_titlecase_and_remove_all_ws
    )
    
    df_marketing_str_cleaned = clean_string_columns_remove_all_ws(
        df_marketing_titlecase,
        cols_titlecase_and_remove_all_ws
    )
    
    # convert from string to date: RelationshipStartDate
    df_marketing_prepped = convert_strings_to_dates(
        df_marketing_str_cleaned,
        ["RelationshipStartDate"]
    )
    
    # ------------------------------------------------
    # Join DataFrames
    # ------------------------------------------------
    
    df_main = join_dataframes(
        df_account_prepped, 
        df_customers_prepped, 
        on="CustomerId", 
        how="left"
    )
    
    df_a = join_dataframes(
        df_main, 
        df_financials_prepped,
        on="CustomerId", 
        how="left"
    )
    
    df_b = join_dataframes(
        df_a,
        df_household_prepped,
        on="CustomerId", 
        how="left"
    )
    
    df_joined = join_dataframes(
        df_b,
        df_marketing_prepped,
        on="CustomerId", 
        how="left"
    )
    
    # ------------------------------------------------
    # Remove Duplicate CustomerId
    # ------------------------------------------------
    
    df_completed = drop_first_duplicate(
        df_joined,
        "CustomerId"
    )
    
    # ------------------------------------------------
    # Return some metrics about data in pipeline
    # ------------------------------------------------
    
    stats, pdf_path = compute_statistics_with_histograms(df_completed)
    print("Stats Summary:", stats)
    print("PDF Report saved to:", pdf_path)
    
    # ------------------------------------------------
    # Send transformed data to Apache Cassandra Table
    # ------------------------------------------------
    
    write_to_cassandra(
        "mock_marketing_schema_keyspace_cassie",
        "mock_marketing_schema_table_cassie",
        df_completed
    )

###################################################################
#                           Run This Script
###################################################################

if __name__ == "__main__":
    pg_to_cassie_flow()

###################################################################
#                   Additional Helpful Instructions
###################################################################

# Steps to run this pipeline:

# >> docker exec -it prefect-cli bash
# >> cd /root/flows
# >> prefect deploy pipeline_script.py:pg_to_cassie_flow --name "Mock-Marketing-Deployment"
# >> python pipeline_script.py

# To view the Prefect dashboard:
#       http://localhost:4200
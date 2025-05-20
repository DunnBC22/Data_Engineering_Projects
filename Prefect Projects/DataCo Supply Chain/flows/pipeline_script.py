###################################################################
#
#           Prefect Pipeline for DataCo Supply Chain Data
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
            database="dataco_sc_pg_db",
        )
    )
    
    # Save connector
    postgres_connector.save("postgres-connector", overwrite=True)
    return postgres_connector

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
            password="mariadb_pass",
            host="mariadb",
            port=3306,
            database="dataco_sc_mariadb_db"
        )
    )
    
    # Save connector
    mariadb_connector.save("mariadb-connector", overwrite=True)
    return mariadb_connector

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
def convert_strings_to_timestamps(
    df: pl.DataFrame, 
    timestamp_cols: List[str],
    default_date: str = "1900-01-01 00:00"
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
        # Attempt to convert to datetime with the specified format (including time)
        df = df.with_columns(
            pl.when(pl.col(col).str.strptime(pl.Datetime, "%m/%d/%Y %H:%M", strict=False).is_null())
            .then(pl.lit(default_date).str.strptime(pl.Datetime, "%Y-%m-%d %H:%M"))
            .otherwise(pl.col(col).str.strptime(pl.Datetime, "%m/%d/%Y %H:%M", strict=False))
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
def clean_string_columns(
    df: pl.DataFrame, 
    string_columns: list[str]
    ) -> pl.DataFrame:
    """
    This function/task cleans string values in the columns/features that 
    are passed into this function/task via the string_columns parameter.
    
    Cleans string values in specified columns by:
        1. Removing dashes and parentheses
        2. Converting to title case
        3. Removing all whitespace
    
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
            .str.replace_all(r"\-", "")
            .str.replace_all(r"\(", "")
            .str.replace_all(r"\)", "")
            .str.to_titlecase()
            .str.replace_all(r"\s+", "")  # Remove all types of whitespace
            .alias(col)
        ])
    return df

@task
def clean_string_columns_custom(
    df: pl.DataFrame, 
    string_columns: list[str]
    ) -> pl.DataFrame:
    """
    This function/task cleans string values in the columns/features that 
    are passed into this function/task via the string_columns parameter.
    
    Cleans string values in specified columns by applying a series of transformations in order:
        1. Replace '+' with 'Plus'
        2. Replace '_' with space
        3. Replace '&' with 'And'
        4. Remove '-', '÷', and single quotes
        5. Strip leading/trailing spaces
        6. Convert to title case
    
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
            .str.replace_all(r"\+", "Plus")
            .str.replace_all("_", " ")
            .str.replace_all("&", "And")
            .str.replace_all("-", "")
            .str.replace_all("÷", "")
            .str.replace_all("'", "")
            .str.strip_chars()
            .str.to_titlecase()
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

@task
def impute_column_with_another(
    df: pl.DataFrame, 
    target_col: str, 
    source_col: str
    ) -> pl.DataFrame:
    """
    Imputes missing (null) values in `target_col` using the corresponding values from `source_col`.

    Parameters:
    ----------
    df : pl.DataFrame
        The input Polars DataFrame.
    target_col : str
        The name of the column to impute.
    source_col : str
        The name of the column to use as the source for imputation.

    Returns:
    -------
    pl.DataFrame
        The DataFrame with imputed values.
    """
    if target_col in df.columns and source_col in df.columns:
        df = df.with_columns(
            pl.when(pl.col(target_col).is_null())
              .then(pl.col(source_col))
              .otherwise(pl.col(target_col))
              .alias(target_col)
        )
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
        "null_counts": null_counts,
        "dtypes": [str(dt) for dt in dtype_counts],
        "numeric_summary": numeric_stats.to_dict(as_series=False),
        "bar_charts": bar_charts
    }, pdf_path

@task
def write_to_db(
    df: pl.DataFrame, 
    table_name: str, 
    if_exists: str = "append"
    ):
    """
    This function/task sends the transformed data (in Polars) to the database
    table that is named in the arguments passed into this function.
    
    Args:
        df (pl.DataFrame): Polars DataFrame to analyze.
        table_name (str): The name of the table in which to insert the data.
        if_exists (str): What to do if the table already exists.
    """
    # Load the saved Postgre connector block
    connector = SqlAlchemyConnector.load("mariadb-connector")
    
    # Retrieve the SQLAlchemy engine
    engine = connector.get_engine()
    
    # Write the DataFrame to the specified table in the database
    df.write_database(
        table_name=table_name,
        connection=engine,
        if_table_exists=if_exists)

###################################################################
#                              Flow
###################################################################

@flow(
    name="DataCo Supply Chain Dataset", 
    description="This pipeline transfers DataCo Supply Chain Dataset from Postgres to MariaDB.", 
    log_prints=True)
def postgres_to_mariadb_flow(
    name: str = "default_run_name"
    ) -> list:
    """
    This defines the Prefect pipeline that 
        - Retrieves data from Postgres
        - Transforms the data
        - Sends transformed data to MariaDB
    """
    context = get_run_context()
    flow_run = context.flow_run

    flow_run.name = f"Run-{name}"  # Set name dynamically at runtime
    
    postgres_connector = create_postgres_connector()
    mariadb_connector = create_mariadb_connector()
    
    # Retrieve data
    df_start = fetch_data("dataco_sc_pg_table")
    
    # Remove Single-Valued Features
    columns_to_remove_svf = [
        "customer_email",
        "customer_password",
        "product_desc",
        "product_status"
    ]
    
    df_w_fewer_features = drop_columns(
        df_start, 
        columns_to_remove_svf
        )
    
    # Data Transformations
    rename_map = {
        "transaction_type": "TransactionType",
        "actual_days_to_ship": "ActualDaysToShip",
        "scheduled_days_to_ship": "ScheduledDaysToShip",
        "benefit_per_order": "BenefitPerOrder",
        "sales_per_customer": "SalesPerCustomer",
        "delivery_status": "DeliveryStatus",
        "late_delivery_risk": "LateDeliveryRisk",
        "category_id": "CategoryId",
        "category_name": "CategoryName",
        "customer_city": "CustomerCity",
        "customer_country": "CustomerCountry",
        "customer_fname": "CustomerFirstName",
        "customer_id": "CustomerId",
        "customer_lname": "CustomerLastName",
        "customer_segment": "CustomerSegment",
        "customer_state": "CustomerState",
        "customer_street": "CustomerStreet",
        "customer_zipcode": "CustomerZipCode",
        "department_id": "DepartmentId",
        "department_name": "DepartmentName",
        "latitude": "CustomerLatitude",
        "longitude": "CustomerLongitude",
        "market": "MarketName",
        "order_city": "OrderCity",
        "order_country": "OrderCountry",
        "order_customer_id": "OrderCustomerId",
        "order_date": "OrderDate",
        "order_id": "OrderId",
        "order_item_cardprod_id": "OrderItemCardProdId",
        "order_item_discount": "OrderItemDiscount",
        "order_item_discount_rate": "OrderItemDiscountRate",
        "order_item_id": "OrderItemId",
        "order_item_product_price": "OrderItemProductPrice",
        "order_item_profit_ratio": "OrderItemProfitRatio",
        "order_item_quantity": "OrderItemQuantity",
        "sales": "SalesAmount",
        "order_item_total": "OrderItemTotal",
        "order_profit_per_order": "OrderProfitPerOrder",
        "order_region": "OrderRegion",
        "order_state": "OrderState",
        "order_status": "OrderStatus",
        "order_zipcode": "OrderZipCode",
        "product_card_id": "ProductCardId",
        "product_category_id": "ProductCategoryId",
        "product_image": "ProductImage",
        "product_name": "ProductName",
        "product_price": "ProductPrice",
        "shipping_date": "ShippingDate",
        "shipping_mode": "ShippingMode"
        }
    
    # Rename columns
    df_renamed = rename_columns(
        df_w_fewer_features, 
        rename_map
        )
    
    # Handle nulls & nans
    features_to_filter = [
        "customer_lname",
        "customer_zipcode"
    ]
    
    df_filtered_nulls = remove_none_and_null_rows(
        df_renamed, 
        features_to_filter
    )
    
    df_imputed = impute_column_with_another(
        df_filtered_nulls,
        target_col="OrderZipCode",
        source_col="CustomerZipCode"
        )
    
    replacement_values_dict = {
        "CustomerCountry": {
            "EE. UU.": "UnitedStates",
            "Puerto Rico": "PuertoRico"
        },
        "CustomerState": {
            "91732": "CA",
            "95758": "CA"
        },
        "MarketName": {
            "LATAM": "LatinAmerica",
            "USCA": "UnitedStatesOfCentralAmerica"
        },
        "OrderCountry": {
            "Afganist�n": "Afghanistan",
            "Arabia Saud�": "Saudi Arabia",
            "Azerbaiy�n": "Azerbaijan",
            "Banglad�s": "Bangladesh",
            "Bar�in": "Bahrain",
            "Ben�n": "Benin",
            "But�n": "Bhutan",
            "B�lgica": "Belgium",
            "Camer�n": "Cameroon",
            "Emiratos �rabes Unidos": "United Arab Emirates",
            "Espa�a": "Spain",
            "Estados Unidos": "UnitedStates",
            "Etiop�a": "Ethiopia",
            "Gab�n": "GAbon",
            "Hait�": "Haiti",
            "Hungr�a": "Hungary",
            "Ir�n": "Iran",
            "Jap�n": "Japan",
            "Kazajist�n": "Kazakhstan",
            "Kirguist�n": "Kyrgyzstan",
            "L�bano": "Lebanon",
            "M�xico": "Mexico",
            "N�ger": "Niger",
            "Om�n": "Oman",
            "Pakist�n": "Pakistan",
            "Panam�": "Panama",
            "Pap�a Nueva Guinea": "Papua New Guinea",
            "Pa�ses Bajos": "Netherlands",
            "Per�": "Peru",
            "Rep�blica Centroafricana": "Central African Republic",
            "Rep�blica Checa": "Czechia",
            "Rep�blica Democr�tica del Congo": "Democratic Republic Of Congo",
            "Rep�blica Dominicana": "Dominican Republic",
            "Rep�blica de Gambia": "Gambia",
            "Rep�blica del Congo": "Congo",
            "Sud�n": "Sudan",
            "Sud�n del Sur": "Suriname",
            "S�hara Occidental": "Western Sahara",
            "Taiw�n": "Taiwan",
            "Tayikist�n": "Tajikistan",
            "Turkmenist�n": "Turkmenistan",
            "Turqu�a": "Turkey",
            "T�nez": "Tunisia",
            "Uzbekist�n": "Uzbekistan"
        }
    }
        
    df_cleans_strings_a = clean_values_using_dict(
        df_imputed, 
        replacement_values_dict
    )
    
    # Clean up other characters
    custom_string_cleanings = [
        "ProductName",
        "CategoryName",
        "OrderStatus"
    ]
    
    df_custom_str_cleanings_a = clean_string_columns_custom(
        df_cleans_strings_a, 
        string_columns=custom_string_cleanings
        )
    
    # Clean up a few chars (dashes as well as opening and closing parentheses) & titlecase & remove all whitespace:
    str_cols_to_clean = [ 
        "ProductName",
        "TransactionType",
        "DeliveryStatus",
        "CustomerCountry",
        "CustomerState",
        "CustomerSegment",
        "DepartmentName",
        "MarketName",
        "OrderRegion",
        "ShippingMode",
        "OrderCountry",
        "OrderStatus"
    ]
    
    df_st_cleaned = clean_string_columns(
        df_custom_str_cleanings_a,
        str_cols_to_clean
    )
    
    # Create Dimension tables & send them to PostGIS tables:
    categories_dim_cols = [
        "CategoryId",
        "CategoryName"
    ]
    
    df_categories_dim = create_dimension_table(
        df_st_cleaned, 
        categories_dim_cols
        )
    
    write_to_db(
        df=df_categories_dim,
        table_name="CategoriesDim_mariadb_table"
        )
    
    customers_dim_cols = [
        "CustomerCity",
        "CustomerCountry",
        "CustomerFirstName",
        "CustomerId",
        "CustomerLastName",
        "CustomerState",
        "CustomerStreet",
        "CustomerZipCode"
    ]
    
    df_customers_dim = create_dimension_table(
        df_st_cleaned, 
        customers_dim_cols
        )
    
    write_to_db(
        df=df_customers_dim,
        table_name="CustomersDim_mariadb_table"
        )
    
    departments_dim_cols = [
        "DepartmentId",
        "DepartmentName"
    ]
    
    df_departments_dim = create_dimension_table(
        df_st_cleaned, 
        departments_dim_cols
        )
    
    write_to_db(
        df=df_departments_dim,
        table_name="DepartmentsDim_mariadb_table"
        )
    
    
    products_dim_cols = [
        "ProductCardId",
        "ProductImage",
        "ProductName"
    ]
    
    df_products_dim = create_dimension_table(
        df_st_cleaned, 
        products_dim_cols
        )
    
    write_to_db(
        df=df_products_dim,
        table_name="ProductsDim_mariadb_table"
        )
    
    # convert_timestamp_to_date
    dates_to_convert = [
        "OrderDate",
        "ShippingDate"
    ]
    
    df_time_converted = convert_strings_to_timestamps(
        df_st_cleaned,
        dates_to_convert
    )
    
    df_date_parts_extracted_a = extract_date_parts(
        df_time_converted,
        "OrderDate"
    )
    
    df_date_parts_extracted = extract_date_parts(
        df_date_parts_extracted_a,
        "ShippingDate"
    )
    
    # Handle Geo Coordinates
    df_with_point = add_point_column(
        df_date_parts_extracted, 
        lat_col="CustomerLatitude", 
        lon_col="CustomerLongitude"
        )
    
    # Drop Extra Features after creating Dimension tables
    extra_features_to_remove = [
        "CategoryName",
        "CustomerCity",
        "CustomerCountry",
        "CustomerFirstName",
        "CustomerLastName",
        "CustomerState",
        "CustomerStreet",
        "CustomerZipCode",
        "DepartmentName",
        "ProductImage",
        "ProductName",
        "CustomerLatitude",
        "CustomerLongitude"
    ]
    
    df_cleaned = drop_columns(
        df_with_point,
        extra_features_to_remove
    )
    
    # Return some metrics about the data in the pipeline
    stats, pdf_path = compute_statistics_with_histograms(df_cleaned)
    print("Stats Summary:", stats)
    print("PDF Report saved to:", pdf_path)
    
    # Send transformed data to MariaDB
    write_to_db(
        df=df_cleaned,
        table_name="dataco_sc_mariadb_table"
        )

###################################################################
#                           Run This Script
###################################################################

if __name__ == "__main__":
    postgres_to_mariadb_flow()

###################################################################
#                   Additional Helpful Instructions
###################################################################

# Steps to run this pipeline:

# >> docker exec -it prefect-cli bash
# >> cd /root/flows
# >> prefect deploy pipeline_script.py:postgres_to_mariadb_flow --name "DataCo-Supply-Chain-Data-Deployment"
# >> python pipeline_script.py

# To view the Prefect dashboard:
#       http://localhost:4200
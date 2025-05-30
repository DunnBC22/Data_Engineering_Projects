import polars as pl
from sqlalchemy import create_engine

# Define the path to your CSV file
csv_file_path = "/data/flixpatrol.csv"

# Define Schema
schema_values = {
    "Rank": pl.Float64,
    "Title": pl.String,
    "Type": pl.String,
    "Premiere": pl.Int64,
    "Genre": pl.String,
    "Watchtime": pl.String,
    "Watchtime in Million": pl.String
}

# Read the CSV file into a Polars DataFrame
df = pl.read_csv(
    csv_file_path,
    separator=";",
    schema=schema_values,
    infer_schema_length=10000,
    ignore_errors=True
    )
    
# Create a SQLAlchemy engine
engine = create_engine("mysql+pymysql://mariadb_user:mariadb_pass@mariadb:3306/most_watched_movies_and_tv_shows_mariadb_db")

# Define batch size
batch_size = 10000
total_rows = df.height

# Insert data in batches
for start in range(0, total_rows, batch_size):
    end = start + batch_size
    batch_df = df.slice(start, batch_size)
    batch_df.write_database(
        table_name="most_watched_movies_and_tv_shows_mariadb_table",
        connection=engine,
        if_table_exists="append"
    )
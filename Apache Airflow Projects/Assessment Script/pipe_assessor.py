import os
import psycopg2
import pandas as pd


def fetch_all_records_in_pd(
    db_name: str, 
    username: str,
    table_name: str
    ) -> pd.DataFrame:
    
    # Connect to your postgres DB
    conn = psycopg2.connect(f"dbname={db_name} user={username}")

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute a query
    cur.execute(f"SELECT * FROM {table_name}")

    # Retrieve query results
    records = cur.fetchall()
    
    # Get list of column names
    col_names = [col[0] for col in cur.description]
    
    # Create Pandas DataFrame of retrieved records
    dataframe = pd.DataFrame(
        records, 
        columns=col_names
        )

    # Close the cursor and the connection
    cur.close()
    conn.close()
    
    #return all feteched records
    return dataframe


def retrieve_summary_stats(
    db_name: str, 
    table_name: str,
    username: str, 
    output_folder_loc: str
    ):
    df = fetch_all_records_in_pd(
        db_name, 
        username,
        table_name)
    
    # Return descriptive statistics about each feature in the dataframe
    descriptive_stats = df.describe(
        include='all',
        percentiles=[0.01, 0.10, 0.25, 0.50, 0.75, 0.90, 0.99]
        ).fillna(
            "-", 
            inplace = False
            )
    
    kurtosis_vals = df.kurtosis(numeric_only=True)
    null_counts = df.isna().sum()
    
    # Create new folder for all 3 files
    os.mkdir(os.path.join(output_folder_loc, "outputs", table_name))
    
    # Save descriptive statistics
    descriptive_stats.to_csv(
        os.path.join(output_folder_loc, "outputs", table_name, "desc_stats.csv"))
    kurtosis_vals.to_csv(
        os.path.join(output_folder_loc, "outputs", table_name, "kurtosis.csv"),
        header=["Kurtosis Value"])
    null_counts.to_csv(
        os.path.join(output_folder_loc, "outputs", table_name, "null_counts.csv"),
        header=["Number of Null Values"])
    

if __name__ == "__main__":
    retrieve_summary_stats(
        db_name=input("What is the name of database for this analysis?\n"),
        username="airflow",
        output_folder_loc=input("Where do you want this file to go?\n"),
        table_name=input("What is the name of the table to retrieve dataset?\n")
        )
import pandas as pd

def generate_insert_statements_pandas(csv_file_path, table_name, column_definitions, output_file_path):
    try:
        # Read the CSV file into a pandas DataFrame
        df = pd.read_csv(csv_file_path, dtype=column_definitions)
        
        # Open the output file for writing SQL statements
        with open(output_file_path, mode='w', encoding='utf-8') as output_file:
            for _, row in df.iterrows():
                values = []
                for col, col_type in column_definitions.items():
                    value = row[col]
                    
                    if pd.isna(value):  # Handle NULL values
                        values.append('NULL')
                    else:
                        if col_type in ('int', 'float', 'decimal'):
                            values.append(str(value))  # Numeric values directly
                        else:
                            # Escape single quotes for text columns
                            value = str(value).replace("'", "''")
                            values.append(f"'{value}'")
                
                # Construct the SQL INSERT statement
                sql = f"INSERT INTO {table_name} ({', '.join(column_definitions.keys())}) VALUES ({', '.join(values)});"
                output_file.write(sql + '\n')
        
        print(f"SQL statements successfully written to {output_file_path}.")
    
    except FileNotFoundError:
        print(f"Error: The input file '{csv_file_path}' was not found.")
    except pd.errors.EmptyDataError:
        print(f"Error: The output CSV file '{csv_file_path}' is empty.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")





if __name__ == "__main__":
    csv_file_path = './data/data.csv'
    table_name = 'lccd_pg_table'
    column_definitions = {
        'CustomerID': 'int',
        'Gender': 'str',
        'Age': 'int',
        'Geography': 'str',
        'Tenure': 'int',
        'Contract': 'str',
        'MonthlyCharges': 'float64',
        'TotalCharges': 'float64',
        'PaymentMethod': 'str',
        'IsActiveMember': 'int',
        'Churn': 'str'
        }
    
    output_file_path = './pg_init/3_insert_data.sql'

    generate_insert_statements_pandas(csv_file_path, table_name, column_definitions, output_file_path)
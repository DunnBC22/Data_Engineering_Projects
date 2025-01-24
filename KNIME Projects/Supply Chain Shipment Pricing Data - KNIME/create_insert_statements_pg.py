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
        print(f"Error: The file '{csv_file_path}' was not found.")
    except pd.errors.EmptyDataError:
        print(f"Error: The CSV file '{csv_file_path}' is empty.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")





if __name__ == "__main__":
    csv_file_path = ''
    table_name = 'sc_ship_prices_table'
    column_definitions = {
        'id' : 'int',
        'project_code' : 'str',
        'pq_number' : 'str',
        'po_or_so_num' : 'str',
        'asn_or_dn_num' : 'str',
        'country_name' : 'str',
        'managed_by' : 'str',
        'fulfill_via' : 'str',
        'vendor_inco_term' : 'str',
        'shipment_mode' : 'str',
        'pq_first_sent_to_client_date' : 'str',
        'po_sent_to_vendor_date' : 'str',
        'scheduled_delivery_date' : 'str',
        'delivered_to_client_date' : 'str',
        'delivery_recorded_date' : 'str',
        'product_group' : 'str',
        'sub_classification' : 'str',
        'vendor' : 'str',
        'item_desc' : 'str',
        'molecule_or_test_type' : 'str',
        'brand' : 'str',
        'dosage' : 'str',
        'dosage_form' : 'str',
        'unit_of_measure_per_pack' : 'float64',
        'line_item_quantity' : 'float64',
        'line_item_value' : 'float64',
        'pack_price' : 'float64',
        'unit_price' : 'float64',
        'manufacturing_site' : 'str',
        'first_line_designation' : 'str',
        'weight_in_kg' : 'str',
        'freight_cost_in_usd' : 'str',
        'line_item_insurance_in_usd' : 'float'
    }
    
    output_file_path = '/pg_init/3_insert_data.sql'

    generate_insert_statements_pandas(csv_file_path, table_name, column_definitions, output_file_path)
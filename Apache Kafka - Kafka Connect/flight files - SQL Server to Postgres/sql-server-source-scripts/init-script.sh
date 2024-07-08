#!/bin/bash

# Define SQL Server credentials and connection details
SQL_SERVER="localhost"
SQL_USER="SA"
SQL_PASSWORD="YourStrong!Passw0rd"

# Define the directory where SQL scripts are located
SQL_SCRIPTS_DIR="/docker-entrypoint-initdb.d"

# Array of SQL script files to process
SQL_SCRIPTS=(
    "3_schema_inserts_2022_1.sql"
    "3_schema_inserts_2022_2.sql"
    "3_schema_inserts_2022_3.sql"
    "3_schema_inserts_2022_4.sql"
    "3_schema_inserts_2022_5.sql"
    "3_schema_inserts_2022_6.sql"
    "3_schema_inserts_2022_7.sql"
)

# Function to execute SQL script in batches
function execute_sql_script() {
    local script="$1"
    local batch_size=2500

    echo "Executing SQL script in batches: $script"

    total_lines=$(wc -l < "$SQL_SCRIPTS_DIR/$script")
    start_line=1

    while [ $start_line -le $total_lines ]; do
        end_line=$((start_line + batch_size - 1))
        
        # Extract the batch of lines to a temporary file
        sed -n "${start_line},${end_line}p;${end_line}q" "$SQL_SCRIPTS_DIR/$script" > "$SQL_SCRIPTS_DIR/temp_$script"
        
        # Prepend USE db statement to the batch
        sed -i '1i USE flight_files_source_db;' "$SQL_SCRIPTS_DIR/temp_$script"

        # Execute the batch of lines
        /opt/mssql-tools/bin/sqlcmd -S $SQL_SERVER -U $SQL_USER -P $SQL_PASSWORD -i "$SQL_SCRIPTS_DIR/temp_$script"
        
        if [ $? -ne 0 ]; then
            echo "Error executing batch in SQL script: $script"
            exit 1
        fi
        
        start_line=$((end_line + 1))
    done

    echo "SQL script executed successfully in batches: $script"
}

# Loop through each SQL script and execute it in batches
for script in "${SQL_SCRIPTS[@]}"
do
    execute_sql_script "$script" 500
done

echo "All SQL scripts executed successfully in batches."
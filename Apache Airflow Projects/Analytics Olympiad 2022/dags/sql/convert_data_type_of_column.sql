-- params: table_name, col_name_to_update, new_data_type

-- ALTER COLUMN in TABLE
ALTER TABLE {{ params.table_name }}
ALTER COLUMN {{ params.col_name_to_update }} 
SET DATA TYPE {{ params.new_data_type }};
-- params: table_name: airflow_complaints, col_name: Consumer_disputed
UPDATE {{ params.table_name }} 
SET {{ params.col_name }} = {{ params.default_value }}
WHERE {{ params.col_name }} IS NULL;
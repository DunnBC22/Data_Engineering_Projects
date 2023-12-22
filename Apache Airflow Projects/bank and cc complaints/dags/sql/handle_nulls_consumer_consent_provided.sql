-- params: "table_name": "airflow_complaints",
-- "col_to_fill": "Consumer_consent_provided",
-- "value_to_fill_in": "Not_yet_60_days"
UPDATE {{ params.table_name }} 
SET {{ params.col_to_fill }} = {{ params.value_to_fill_in }}
WHERE {{ params.col_to_fill }} IS NULL;
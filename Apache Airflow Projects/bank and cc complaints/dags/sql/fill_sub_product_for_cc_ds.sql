-- params: "table_name": "airflow_complaints", 
-- "set_col_vals": "Sub_product", 
-- "other_col_ref": "product", 
-- "value_to_set_null_to": "Credit card"
UPDATE {{ params.table_name }}
SET {{ params.set_col_vals }} = {{ params.value_to_set_null_to }}
WHERE {{ params.set_col_vals }} IS NULL
AND {{ params.other_col_ref }} = {{ params.value_to_set_null_to }};
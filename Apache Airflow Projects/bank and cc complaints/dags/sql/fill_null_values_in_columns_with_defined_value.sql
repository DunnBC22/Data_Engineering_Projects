-- params: "table_name", "column_name", 
-- "default_value_to_set", 
-- "col_based_on"= 'product', 
-- "col_value_for_bool"= 'credit card'
UPDATE {{ params.table_name }}
SET {{ params.column_name }} = {{ params.default_value }}
WHERE {{ params.column_name }} IS NULL & {{ params.col_based_on }} == {{ params.col_value_for_bool }};
-- params: table_name, col_name, bool_value_gt
DELETE FROM {{ params.table_name }}
WHERE {{ params.col_name }} > {{ params.bool_value_gt }};
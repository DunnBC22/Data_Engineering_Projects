-- params: table_name, col_name, operator, comparison_value
DELETE FROM {{ params.table_name }}
WHERE {{ params.col_name }} {{ params.operator }} {{ params.comparison_value }}
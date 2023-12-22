-- params: table_name, col_for_bool
DELETE FROM {{ params.table_name }}
WHERE {{ params.col_for_bool }} < 1801;
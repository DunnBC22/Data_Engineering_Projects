-- params: table_name, column_name
DELETE FROM {{ params.table_name }}
WHERE {{ params.column_name }} is NULL;
-- params: table_name, column_name
DELETE FROM {{ params.table_name }}
WHERE {{ params.column_name }} IS NOT NULL
    AND {{ params.column_name }}::date IS NULL;
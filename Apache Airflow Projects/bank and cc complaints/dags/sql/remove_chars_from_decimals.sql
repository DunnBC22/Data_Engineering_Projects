-- params: table_name, col_name
UPDATE {{ params.table_name }}
SET {{ params.col_name }} = TRIM(REGEXP_REPLACE({{ params.col_name }},'[^0-9]', '','','g'));
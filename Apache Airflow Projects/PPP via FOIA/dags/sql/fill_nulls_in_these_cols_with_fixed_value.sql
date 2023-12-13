-- params: table_name, col_to_fill, value_to_fill_in
UPDATE {{ params.table_name }} 
SET {{ params.col_to_fill }} = {{ params.value_to_fill_in }}
WHERE {{ params.col_to_fill }} IS NULL;
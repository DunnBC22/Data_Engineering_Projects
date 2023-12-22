-- params: table_name, column_name, height_value, weight_value
ALTER TABLE {{ params.table_name }}
ADD COLUMN {{ params.column_name }} FLOAT;

UPDATE {{ params.table_name }}
SET {{ params.column_name }} = {{ params.weight_value }}/({{ params.height_value }} * {{ params.height_value }})
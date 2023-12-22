-- params: table_name, new_col_name, numerator, denominator
ALTER TABLE {{ params.table_name }}
ADD COLUMN {{ params.new_col_name }} INTEGER;
UPDATE {{ params.table_name }}
SET {{ params.new_col_name }} = {{ params.numerator }}/{{ params.denominator }};
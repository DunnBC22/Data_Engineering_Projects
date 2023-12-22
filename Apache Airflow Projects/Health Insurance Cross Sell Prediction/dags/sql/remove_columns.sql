-- table_name, column_name
ALTER TABLE {{ params.table_name }}
DROP COLUMN {{ params.column_name }};
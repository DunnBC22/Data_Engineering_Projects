-- params: table_name, col_name, month_col_name, year_col_name, dom_col_name

-- Add columns
ALTER TABLE {{ params.table_name }}
ADD COLUMN IF NOT EXISTS {{ params.month_col_name }} VARCHAR, 
ADD COLUMN IF NOT EXISTS {{ params.year_col_name }} VARCHAR;

-- fill columns with their proper values
UPDATE {{ params.table_name }}
SET 
    {{ params.month_col_name }} = SPLIT_PART('{{ params.col_name }}', '-', 2),
    {{ params.year_col_name }} = SPLIT_PART('{{ params.col_name }}', '-', 1);

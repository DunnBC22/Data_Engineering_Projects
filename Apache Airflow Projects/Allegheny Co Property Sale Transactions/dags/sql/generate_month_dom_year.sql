-- params: table_name, col_name, month_col_name, year_col_name, dom_col_name

-- Add columns
ALTER TABLE {{ params.table_name }}
ADD COLUMN IF NOT EXISTS {{ params.month_col_name }} INTEGER, 
ADD COLUMN IF NOT EXISTS {{ params.year_col_name }} INTEGER, 
ADD COLUMN IF NOT EXISTS {{ params.dom_col_name }} INTEGER;

-- Fill columns with their proper values
UPDATE {{ params.table_name }}
SET 
    {{ params.month_col_name }} = EXTRACT(MONTH FROM {{ params.col_name }}),
    {{ params.year_col_name }} = EXTRACT(YEAR FROM {{ params.col_name }}),
    {{ params.dom_col_name }} = EXTRACT(DAY FROM {{ params.col_name }});
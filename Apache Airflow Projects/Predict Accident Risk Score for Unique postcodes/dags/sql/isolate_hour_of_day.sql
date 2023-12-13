-- params: table_name, col_name, hour_of_day_col_name

-- Add column
ALTER TABLE {{ params.table_name }}
ADD COLUMN IF NOT EXISTS {{ params.hour_of_day_col_name }} INTEGER;

-- fill column with their proper value
UPDATE {{ params.table_name }}
SET 
    {{ params.hour_of_day_col_name }} = EXTRACT(HOUR FROM {{ params.col_name }});
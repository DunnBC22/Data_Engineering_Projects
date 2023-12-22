-- params: table_name, dimension_col

/*
Steps 1-3 were completed in the create_dim_table.sql 
file & associated PostgresOperator
*/


-- Step 4: Add foreign key column to fact table
ALTER TABLE {{ params.table_name }}
ADD COLUMN {{ params.dimension_col }}_id INTEGER;

-- Step 4: Update foreign key column to fact table with 
-- appropriate id (that matches with dim table)
UPDATE {{ params.table_name }}
SET {{ params.dimension_col }}_id = dimension_table_{{ params.dimension_col }}.id
FROM dimension_table_{{ params.dimension_col }}
WHERE COALESCE({{ params.table_name }}.{{ params.dimension_col }}::text, '') = COALESCE(dimension_table_{{ params.dimension_col }}.{{ params.dimension_col }}::text, '');
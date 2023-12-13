-- params: table_name, dimension_col, data_type

-- Step 1: Extract Unique Values
CREATE TEMPORARY TABLE unique_values_{{ params.dimension_col }} AS
SELECT DISTINCT {{ params.dimension_col }} FROM {{ params.table_name }};

-- Step 2: Create Dimension Table
DROP TABLE IF EXISTS dimension_table_{{ params.dimension_col }};
CREATE TABLE dimension_table_{{ params.dimension_col }} (
    id SERIAL PRIMARY KEY,
    {{ params.dimension_col }} {{ params.data_type }}
    );

-- Step 3: Insert unique values into dimension table
INSERT INTO dimension_table_{{ params.dimension_col }} ({{ params.dimension_col }})
SELECT * FROM unique_values_{{ params.dimension_col }};

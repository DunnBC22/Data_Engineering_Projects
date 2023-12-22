-- params: new_table_name, orig_table_name

-- Drop the table if it exists (so you get a clean copy)
DROP TABLE IF EXISTS {{ params.new_table_name }};

-- Create copy of table
CREATE TABLE IF NOT EXISTS {{ params.new_table_name }} AS
SELECT * 
FROM {{ params.orig_table_name }};

-- Grant additional permissions on the table
GRANT SELECT, INSERT, UPDATE, DELETE ON {{ params.new_table_name }} TO airflow;
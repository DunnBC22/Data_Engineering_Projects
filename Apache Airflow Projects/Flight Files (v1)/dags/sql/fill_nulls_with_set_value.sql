-- params: table_name, col_to_fill, value_to_fill_in, primary_key

BEGIN;

WITH cte AS (
    SELECT *
    FROM {{ params.table_name }}
    WHERE {{ params.col_to_fill }} IS NULL
    ORDER BY {{ params.primary_key }}
    FOR UPDATE
)
-- Update the selected rows
UPDATE {{ params.table_name }}
SET {{ params.col_to_fill }} = {{ params.value_to_fill_in }}
FROM cte
WHERE {{ params.table_name }}.{{ params.primary_key }} = cte.{{ params.primary_key }};

-- Commit the transaction
COMMIT;

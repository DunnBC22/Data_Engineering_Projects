-- params: table_name, column_name

UPDATE {{ params.table_name }}
SET {{ params.column_name }} = subquery.median_value
FROM (
    SELECT 
        {{ params.column_name }},
        CASE 
            WHEN COUNT(*) % 2 = 1 THEN percentile_cont(0.5) WITHIN GROUP (ORDER BY {{ params.column_name }}::numeric) 
            ELSE AVG(CASE WHEN {{ params.column_name }} ~ E'^\\d+(\\.\\d+)?$' THEN {{ params.column_name }}::numeric END) 
            --ELSE AVG({{ params.column_name }}::numeric) 
        END AS median_value
    FROM {{ params.table_name }}
    WHERE {{ params.table_name }}.{{ params.column_name }} IS NOT NULL
        AND {{ params.column_name }} ~ E'^\\d+(\\.\\d+)?$' -- Exclude non-numeric values
    GROUP BY {{ params.table_name }}.{{ params.column_name }}
) AS subquery
WHERE {{ params.table_name }}.{{ params.column_name }} IS NULL;
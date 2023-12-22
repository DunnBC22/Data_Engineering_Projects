-- params: table_name, column_name

UPDATE {{ params.table_name }}
SET {{ params.column_name }} = subquery.median_value
FROM (
    SELECT 
        {{ params.column_name }},
        CASE 
            WHEN COUNT(*) % 2 = 1 THEN percentile_cont(0.5) WITHIN GROUP (ORDER BY CAST({{ params.column_name }} AS NUMERIC)) 
            ELSE AVG(CASE WHEN {{ params.column_name }} IS NOT NULL THEN CAST({{ params.column_name }} AS NUMERIC) END)
        END AS median_value
    FROM {{ params.table_name }}
    WHERE {{ params.table_name }}.{{ params.column_name }} IS NOT NULL
    GROUP BY {{ params.table_name }}.{{ params.column_name }}
) AS subquery
WHERE {{ params.table_name }}.{{ params.column_name }} IS NULL;
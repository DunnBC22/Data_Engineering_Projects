-- params: table_name, column_name

UPDATE {{ params.table_name }}
SET {{ params.column_name }} = (
    SELECT {{ params.column_name }} 
    FROM {{ params.table_name }}
    WHERE {{ params.column_name }} IS NOT NULL
    GROUP BY {{ params.column_name }}
    ORDER BY COUNT(*) DESC
    LIMIT 1
)
WHERE {{ params.column_name }} IS NULL;
-- params: table_name, duplicate_col_name

DELETE FROM {{ params.table_name }}
WHERE ctid NOT IN (
    SELECT MAX(ctid) AS max_ctid
    FROM table_name
    GROUP BY duplicate_col_name
    HAVING COUNT(*) > 1
);

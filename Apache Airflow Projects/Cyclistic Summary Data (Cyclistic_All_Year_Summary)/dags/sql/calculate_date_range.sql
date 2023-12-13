-- params: table_name, start_date_col, stop_date_col, date_range_col_name
ALTER TABLE {{ params.table_name }}
ADD COLUMN {{ params.date_range_col_name }} INTEGER;

UPDATE {{ params.table_name }}
SET {{ params.date_range_col_name }} = (
    EXTRACT(
        epoch FROM {{ params.stop_date_col }}
        ) - EXTRACT(
            epoch FROM {{ params.start_date_col }})
            ) / (24 * 3600);

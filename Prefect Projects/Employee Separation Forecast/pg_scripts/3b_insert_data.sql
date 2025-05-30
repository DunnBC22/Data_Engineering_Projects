\c employee_separation_forecast_pg_db;

COPY test_results_ee_sep_forecast_pg_table (
    "ID",
    "Label"
)
FROM '/data/test_results.csv'
DELIMITER ','
CSV HEADER;
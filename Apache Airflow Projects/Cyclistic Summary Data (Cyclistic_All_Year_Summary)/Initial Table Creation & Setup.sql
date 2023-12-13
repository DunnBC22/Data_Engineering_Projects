-- database name: cyclistic_summary_db
-- owner: airflow

CREATE TABLE cyclistic_summary (
    usertype VARCHAR,
    zip_code_start INTEGER,
    borough_start VARCHAR,
    neighborhood_start VARCHAR,
    zip_code_end INTEGER,
    borough_end VARCHAR,
    neighborhood_end VARCHAR,
    start_day TIMESTAMP,
    stop_day TIMESTAMP,
    day_mean_temperature FLOAT,
    day_mean_wind_speed FLOAT,
    day_total_precipitation FLOAT,
    trip_minutes INTEGER,
    trip_count INTEGER
);

COPY cyclistic_summary(
    usertype,
    zip_code_start,
    borough_start,
    neighborhood_start,
    zip_code_end,
    borough_end,
    neighborhood_end,
    start_day,
    stop_day,
    day_mean_temperature,
    day_mean_wind_speed,
    day_total_precipitation,
    trip_minutes,
    trip_count
    )
FROM '/Users/briandunn/Desktop/Projects 2/Cyclistic Summary Data (Cyclistic_All_Year_Summary)/Cyclistic_All_Year_Summary.csv'
DELIMITER ','
CSV HEADER;
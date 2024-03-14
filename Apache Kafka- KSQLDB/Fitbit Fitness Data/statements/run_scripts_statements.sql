/*
#docker compose command to develop interactively:

docker exec -it ksqldb-cli ksql http://ksqldb-server:8088

*/

-- This is the RUN SCRIPT statement for the create_streams file
RUN SCRIPT '/statements/create_streams.sql';

-- These are the RUN SCRIPT statements for the producers

RUN SCRIPT '/statements/producers/daily_activity_inserts.sql';
RUN SCRIPT '/statements/producers/daily_intensities_inserts.sql';
RUN SCRIPT '/statements/producers/daily_calories_inserts.sql';
RUN SCRIPT '/statements/producers/daily_steps_inserts.sql';
RUN SCRIPT '/statements/producers/sleep_day_inserts.sql';

RUN SCRIPT '/statements/producers/hourly_intensities_inserts.sql';
RUN SCRIPT '/statements/producers/hourly_calories_inserts.sql';
RUN SCRIPT '/statements/producers/hourly_steps_inserts.sql';

/*
RUN SCRIPT '/statements/producers/minute_sleep_inserts.sql'; -- it would take too long to run
RUN SCRIPT '/statements/producers/minute_METs_narrow_inserts.sql'; -- it would take too long to run
RUN SCRIPT '/statements/producers/minute_calories_narrow_inserts.sql'; -- it would take too long to run
RUN SCRIPT '/statements/producers/minute_intensities_narrow_inserts.sql'; -- it would take too long to run
RUN SCRIPT '/statements/producers/minute_steps_narrow_inserts.sql'; -- it would take too long to run
*/

-- update the auto.offset.reset setting
SET 'auto.offset.reset' = 'earliest';

-- These are the RUN SCRIPT statements for the consumers
RUN SCRIPT '/statements/consumers/consumers-group_by.sql';
RUN SCRIPT '/statements/consumers/consumers-daily_stream.sql';
RUN SCRIPT '/statements/consumers/consumers-daily_sums.sql';
RUN SCRIPT '/statements/consumers/consumers-hourly.sql';
RUN SCRIPT '/statements/consumers/consumers-hourly-averages.sql';
RUN SCRIPT '/statements/consumers/consumers-filtering.sql';

-- RUN SCRIPT '/statements/consumers/consumers-minutes_narrow.sql'; -- it would take too long to run the insert statements

-- print out 25 records for each consumer to check that they work appropriately
PRINT DAILY_STREAM_FITBIT_DATA FROM BEGINNING LIMIT 25;
PRINT STREAM_HOURLY_FITBIT_DATA FROM BEGINNING LIMIT 25;



-- print out 25 records from these tables to check they work appropriately
SELECT * FROM DAILY_GROUP_BY_FITBIT_DATA LIMIT 25;
SELECT * FROM DAILY_SUMS_FITBIT_DATA LIMIT 25;
SELECT * FROM AVERAGE_HOURLY_FITBIT_DATA LIMIT 25;
SELECT * FROM DAILY_FILTERED_FITBIT_DATA LIMIT 25;

-- other statements
SHOW TOPICS;
SHOW STREAMS;
SHOW TABLES;
SHOW PROPERTIES;
SHOW QUERIES;

-- producers
DESCRIBE minute_METs_narrow EXTENDED;
DESCRIBE minute_steps_narrow EXTENDED;
DESCRIBE minute_calories_narrow EXTENDED;
DESCRIBE minute_sleep EXTENDED;

DESCRIBE minute_intensities_narrow EXTENDED;
DESCRIBE hourly_intensities EXTENDED;
DESCRIBE hourly_calories EXTENDED;
DESCRIBE hourly_steps EXTENDED;

DESCRIBE daily_activity EXTENDED;
DESCRIBE daily_intensities EXTENDED;
DESCRIBE daily_steps EXTENDED;

DESCRIBE daily_calories EXTENDED;
DESCRIBE sleep_day EXTENDED;

-- consumers
DESCRIBE DAILY_STREAM_FITBIT_DATA EXTENDED;
DESCRIBE DAILY_GROUP_BY_FITBIT_DATA EXTENDED;
DESCRIBE DAILY_SUMS_FITBIT_DATA EXTENDED;

DESCRIBE STREAM_HOURLY_FITBIT_DATA EXTENDED;
DESCRIBE AVERAGE_HOURLY_FITBIT_DATA EXTENDED;
DESCRIBE DAILY_FILTERED_FITBIT_DATA EXTENDED;
/*
#docker compose command to develop interactively:

docker exec -it ksqldb-cli ksql http://ksqldb-server:8088

*/

-- This is the RUN SCRIPT statement for the create_streams file
RUN SCRIPT '/statements/create_streams.sql';

-- These are the RUN SCRIPT statements for the producers
RUN SCRIPT '/statements/producers/car_spec_inserts.sql';

-- update the auto.offset.reset setting
SET 'auto.offset.reset' = 'earliest';

-- These are the RUN SCRIPT statements for the consumers
RUN SCRIPT '/statements/consumers/consumer-acura_car_specs.sql';
RUN SCRIPT '/statements/consumers/consumer-feature_histograms.sql';
RUN SCRIPT '/statements/consumers/consumer-almost_all_car_spec_data.sql';
RUN SCRIPT '/statements/consumers/consumer-all_car_spec_data.sql';

-- print out 25 records for each consumer to check that they work appropriately
PRINT ALL_CAR_SPEC_DATA FROM BEGINNING LIMIT 25;
PRINT ALMOST_ALL_CAR_SPEC_DATA FROM BEGINNING LIMIT 25;
PRINT ACURA_CAR_SPECS FROM BEGINNING LIMIT 25;

-- SELECT records from tables
SELECT * FROM CAR_SPECS_HISTOGRAM LIMIT 25;

-- other statements
SHOW TOPICS;
SHOW STREAMS;
SHOW TABLES;
SHOW PROPERTIES;
SHOW QUERIES;

DESCRIBE ALL_CAR_SPEC_DATA EXTENDED;
DESCRIBE ALMOST_ALL_CAR_SPEC_DATA EXTENDED;
DESCRIBE CAR_SPECS_HISTOGRAM EXTENDED;
DESCRIBE ACURA_CAR_SPECS EXTENDED;
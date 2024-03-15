/*
#docker compose command to develop interactively:

docker exec -it ksqldb-cli ksql http://ksqldb-server:8088

*/

-- This is the RUN SCRIPT statement for the create_streams file
RUN SCRIPT '/statements/create_streams.sql';

-- These are the RUN SCRIPT statements for the producers
RUN SCRIPT '/statements/producers/household_energy_inserts.sql';

-- update the auto.offset.reset setting
SET 'auto.offset.reset' = 'earliest';

-- These are the RUN SCRIPT statements for the consumers
RUN SCRIPT '/statements/consumers/consumer-stream_all_data.sql';

-- print out 25 records for each consumer to check that they work appropriately
PRINT STREAM_ALL_HOUSEHOLD_ENERGY_DATA FROM BEGINNING LIMIT 25;

SHOW TOPICS;
SHOW STREAMS;
SHOW TABLES;
SHOW PROPERTIES;
SHOW QUERIES;

DESCRIBE household_energy_data EXTENDED;
DESCRIBE STREAM_ALL_HOUSEHOLD_ENERGY_DATA EXTENDED;
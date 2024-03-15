/*
#docker compose command to develop interactively:

docker exec -it ksqldb-cli ksql http://ksqldb-server:8088

*/

-- This is the RUN SCRIPT statement for the create_streams file
RUN SCRIPT '/statements/create_streams.sql';

-- These are the RUN SCRIPT statements for the producers
RUN SCRIPT '/statements/producers/ontario_fuel_prices_inserts.sql';

-- update the auto.offset.reset setting
SET 'auto.offset.reset' = 'earliest';

-- These are the RUN SCRIPT statements for the consumers
RUN SCRIPT '/statements/consumers/consumers-stream_all_data.sql';
RUN SCRIPT '/statements/consumers/consumers-stream_all_prices_from_1995_to_2005.sql';

-- print out 25 records for each consumer to check that they work appropriately
PRINT STREAM_ALL_ONTARIO_FUEL_PRICES FROM BEGINNING LIMIT 25;
PRINT STREAM_ONTARIO_FUEL_PRICES_1995_2005 FROM BEGINNING LIMIT 25;

SHOW TOPICS;
SHOW STREAMS;
SHOW TABLES;
SHOW PROPERTIES;
SHOW QUERIES;

DESCRIBE ontario_fuel_prices EXTENDED;
DESCRIBE STREAM_ALL_ONTARIO_FUEL_PRICES EXTENDED;
DESCRIBE STREAM_ONTARIO_FUEL_PRICES_1995_2005 EXTENDED;
/*
#docker compose command to develop interactively:

docker exec -it ksqldb-cli ksql http://ksqldb-server:8088

*/

-- This is the RUN SCRIPT statement for the create_streams file
RUN SCRIPT '/statements/create_streams.sql';

-- These are the RUN SCRIPT statements for the producers
RUN SCRIPT '/statements/producers/account_inserts.sql';
RUN SCRIPT '/statements/producers/customer_inserts.sql';
RUN SCRIPT '/statements/producers/financials_inserts.sql';
RUN SCRIPT '/statements/producers/household_inserts.sql';
RUN SCRIPT '/statements/producers/marketing_inserts.sql';

-- update the auto.offset.reset setting
SET 'auto.offset.reset' = 'earliest';


-- These are the RUN SCRIPT statements for the consumers
RUN SCRIPT '/statements/consumers/consumer-histograms.sql';
RUN SCRIPT '/statements/consumers/consumer-retirement_planning_marketing_data.sql';
RUN SCRIPT '/statements/consumers/consumer-stream_all_mock_marketing_schema_data.sql';

-- print out 25 records for each consumer stream to check that they work appropriately
PRINT STREAM_ALL_MOCK_MARKETING_SCHEMA_DATA FROM BEGINNING LIMIT 25;
PRINT RETIREMENT_PLANNING_MARKETING_DATA FROM BEGINNING LIMIT 25;

-- print out 25 records for each consumer table to check that they work appropriately
SELECT * FROM MOCK_MARKETING_SCHEMA_HISTOGRAMS LIMIT 25;


SHOW TOPICS;
SHOW STREAMS;
SHOW TABLES;
SHOW PROPERTIES;
SHOW QUERIES;

-- producers
DESCRIBE account EXTENDED;
DESCRIBE customer EXTENDED;
DESCRIBE financials EXTENDED;
DESCRIBE household EXTENDED;
DESCRIBE marketing EXTENDED;

-- consumers
DESCRIBE MOCK_MARKETING_SCHEMA_HISTOGRAMS EXTENDED;
DESCRIBE RETIREMENT_PLANNING_MARKETING_DATA EXTENDED;
DESCRIBE STREAM_ALL_MOCK_MARKETING_SCHEMA_DATA EXTENDED;
/*
#docker compose command to develop interactively:

docker exec -it ksqldb-cli ksql http://ksqldb-server:8088

*/

-- This is the RUN SCRIPT statement for the create_streams file
RUN SCRIPT '/statements/create_streams.sql';

-- These are the RUN SCRIPT statements for the producers
RUN SCRIPT '/statements/producers/economic_data_inserts.sql';
RUN SCRIPT '/statements/producers/companies_inserts.sql';
RUN SCRIPT '/statements/producers/purchases_inserts.sql';

-- update the auto.offset.reset setting
SET 'auto.offset.reset' = 'earliest';

-- These are the RUN SCRIPT statements for the consumers

RUN SCRIPT '/statements/consumers/consumer-revenue generated and quantity for each company.sql';
RUN SCRIPT '/statements/consumers/consumer-all_data.sql';

-- print out 25 records for each consumer stream to check that they work appropriately
PRINT PURCHASES_W_COMPANY_INFO FROM BEGINNING LIMIT 25;

-- print out 25 records for each consumer table to check that they work appropriately
SELECT * FROM REVENUE_GEN_AND_QUANTITY_EACH_COMPANY LIMIT 25;

-- other statements
SHOW TOPICS;
SHOW STREAMS;
SHOW TABLES;
SHOW PROPERTIES;
SHOW QUERIES;

-- producers
DESCRIBE economic_data EXTENDED;
DESCRIBE companies EXTENDED;
DESCRIBE purchases EXTENDED;

-- consumers
DESCRIBE PURCHASES_W_COMPANY_INFO EXTENDED;
DESCRIBE REVENUE_GEN_AND_QUANTITY_EACH_COMPANY EXTENDED;
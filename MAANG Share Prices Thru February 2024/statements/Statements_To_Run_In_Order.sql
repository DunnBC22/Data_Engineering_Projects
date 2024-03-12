/*
#docker compose command to develop interactively:

docker exec -it ksqldb-cli ksql http://ksqldb-server:8088

*/

-- This is the RUN SCRIPT statement for the create_streams file
RUN SCRIPT '/statements/create_streams.sql';

-- These are the RUN SCRIPT statements for the producers
RUN SCRIPT '/statements/producers/netflix_inserts.sql';
RUN SCRIPT '/statements/producers/meta_inserts.sql';
RUN SCRIPT '/statements/producers/google_inserts.sql';
RUN SCRIPT '/statements/producers/apple_inserts.sql';
RUN SCRIPT '/statements/producers/amazon_inserts.sql';

-- update the auto.offset.reset setting
SET 'auto.offset.reset' = 'earliest';

-- merge all of the streams into one
RUN SCRIPT '/statements/producers/merged_streams.sql';

-- These are the RUN SCRIPT statements for the consumers
RUN SCRIPT '/statements/consumers/consumer-stream_volume_and_adj_close.sql';
RUN SCRIPT '/statements/consumers/consumer-stream_all_data.sql';

-- print out 25 records for each consumer to check that they work appropriately
PRINT STREAM_VOLUME_AND_ADJ_CLOSE_MAANG_STOCK_DATA FROM BEGINNING LIMIT 75;
PRINT STREAM_ALL_MAANG_STOCK_DATA FROM BEGINNING LIMIT 75;

-- other statements
SHOW TOPICS;
SHOW STREAMS;
SHOW TABLES;
SHOW PROPERTIES;
SHOW QUERIES;

DESCRIBE maang_stock_amazon_stock EXTENDED;
DESCRIBE maang_stock_apple_stock EXTENDED;
DESCRIBE maang_stock_google_stock EXTENDED;
DESCRIBE maang_stock_meta_stock EXTENDED;
DESCRIBE maang_stock_netflix_stock EXTENDED;
DESCRIBE all_maang_stock EXTENDED;
DESCRIBE STREAM_ALL_MAANG_STOCK_DATA EXTENDED;
DESCRIBE STREAM_VOLUME_AND_ADJ_CLOSE_MAANG_STOCK_DATA EXTENDED;
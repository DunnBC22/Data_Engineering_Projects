/*
#docker compose command to develop interactively:

docker exec -it ksqldb-cli ksql http://ksqldb-server:8088

*/

-- This is the RUN SCRIPT statement for the create_streams file
RUN SCRIPT '/statements/create_streams.sql';

-- These are the RUN SCRIPT statements for the producers
RUN SCRIPT '/statements/producers/ada_inserts.sql';
RUN SCRIPT '/statements/producers/xrp_inserts.sql';
RUN SCRIPT '/statements/producers/usdt_inserts.sql';
RUN SCRIPT '/statements/producers/trx_inserts.sql';
RUN SCRIPT '/statements/producers/sol_inserts.sql';
RUN SCRIPT '/statements/producers/eth_inserts.sql';
RUN SCRIPT '/statements/producers/doge_inserts.sql';
RUN SCRIPT '/statements/producers/btc_inserts.sql';
RUN SCRIPT '/statements/producers/bnb_inserts.sql';
RUN SCRIPT '/statements/producers/avax_inserts.sql';

-- update the auto.offset.reset setting
SET 'auto.offset.reset' = 'earliest';

-- Run Script to merge the Streams
RUN SCRIPT '/statements/producers/merged_streams.sql'

-- These are the RUN SCRIPT statements for the consumers
RUN SCRIPT '/statements/consumers/all_records-adj_close.sql';
RUN SCRIPT '/statements/consumers/all_records_from_2023-adj_close.sql';
RUN SCRIPT '/statements/consumers/stream_all_records.sql';


-- Print out a sample of events from streams
PRINT ADJ_CLOSING_PRICE_FOR_ALL_CRYPTO FROM BEGINNING LIMIT 36;
PRINT ADJ_CLOSING_PRICE_FOR_ALL_CRYPTO_IN_2023 FROM BEGINNING LIMIT 36;
PRINT STREAM_ALL_CRYPTO_DATA FROM BEGINNING LIMIT 36;

SHOW TOPICS;
SHOW STREAMS;
SHOW TABLES;
SHOW PROPERTIES;
SHOW QUERIES;

DESCRIBE crypto_ada_usd EXTENDED;
DESCRIBE crypto_avax_usd EXTENDED;
DESCRIBE crypto_bnb_usd EXTENDED;
DESCRIBE crypto_btc_usd EXTENDED;
DESCRIBE crypto_doge_usd EXTENDED;
DESCRIBE crypto_eth_usd EXTENDED;
DESCRIBE crypto_sol_usd EXTENDED;
DESCRIBE crypto_trx_usd EXTENDED;
DESCRIBE crypto_usdt_usd EXTENDED;
DESCRIBE crypto_xrp_usd EXTENDED;

DESCRIBE all_crypto_stock EXTENDED;

DESCRIBE STREAM_ALL_CRYPTO_DATA EXTENDED;
DESCRIBE ADJ_CLOSING_PRICE_FOR_ALL_CRYPTO EXTENDED;
DESCRIBE ADJ_CLOSING_PRICE_FOR_ALL_CRYPTO_IN_2023 EXTENDED;
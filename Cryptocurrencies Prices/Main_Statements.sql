-- Make sure that the data is imported into the postgres tables correctly (run this in bash, not the docker CLI)
echo 'SELECT * FROM crypto_ada_usd LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(trading_id) FROM crypto_ada_usd;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

echo 'SELECT * FROM crypto_avax_usd LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(trading_id) FROM crypto_avax_usd;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

echo 'SELECT * FROM crypto_bnb_usd LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(trading_id) FROM crypto_bnb_usd;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

echo 'SELECT * FROM crypto_btc_usd LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(trading_id) FROM crypto_btc_usd;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

echo 'SELECT * FROM crypto_doge_usd LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(trading_id) FROM crypto_doge_usd;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

echo 'SELECT * FROM crypto_eth_usd LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(trading_id) FROM crypto_eth_usd;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

echo 'SELECT * FROM crypto_sol_usd LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(trading_id) FROM crypto_sol_usd;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

echo 'SELECT * FROM crypto_trx_usd LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(trading_id) FROM crypto_trx_usd;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

echo 'SELECT * FROM crypto_usdt_usd LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(trading_id) FROM crypto_usdt_usd;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

echo 'SELECT * FROM crypto_xrp_usd LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(trading_id) FROM crypto_xrp_usd;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

/*
#docker compose command to develop interactively:

docker exec -it ksqldb-cli ksql http://ksqldb-server:8088
*/

-- update the auto.offset.reset setting
SET 'auto.offset.reset' = 'earliest';


-- Define SOURCE CONNECTOR(s)
CREATE SOURCE CONNECTOR IF NOT EXISTS pg_ada_usd_stream_source_conn WITH (
    'name' = 'source_connector_from_pg_crypto_stocks_to_stream_ada',
    'connector.class' = 'io.confluent.connect.jdbc.JdbcSourceConnector',
    'connection.url' = 'jdbc:postgresql://postgres:5432/crypto_prices',
    'connection.user' = 'pg',
    'connection.password' = 'pg',
    'mode' = 'incrementing',
    'topic.prefix' = 'pg_',
    'incrementing.column.name' = 'trading_id',
    'timestamp.column.name' = 'trading_date',
    'timestamp.initial' = 20171116,
    'table.whitelist' = 'crypto_ada_usd',
    'validate.non.null' = true,
    'transforms' = 'copyFieldToKey,extractKeyFromStruct,removeKeyFromValue',
    'transforms.copyFieldToKey.type' = 'org.apache.kafka.connect.transforms.ValueToKey',
    'transforms.copyFieldToKey.fields' = 'trading_id',
    'transforms.extractKeyFromStruct.type' = 'org.apache.kafka.connect.transforms.ExtractField$Key',
    'transforms.extractKeyFromStruct.field' = 'trading_id',
    'transforms.removeKeyFromValue.type' = 'org.apache.kafka.connect.transforms.ReplaceField$Value',
    'transforms.removeKeyFromValue.blacklist' = 'trading_id',
    'key.converter' = 'org.apache.kafka.connect.converters.IntegerConverter'
);

CREATE SOURCE CONNECTOR IF NOT EXISTS pg_avax_usd_stream_source_conn WITH (
    'name' = 'source_connector_from_pg_crypto_stocks_to_stream_avax',
    'connector.class' = 'io.confluent.connect.jdbc.JdbcSourceConnector',
    'connection.url' = 'jdbc:postgresql://postgres:5432/crypto_prices',
    'connection.user' = 'pg',
    'connection.password' = 'pg',
    'mode' = 'incrementing ',
    'topic.prefix' = 'pg_',
    'incrementing.column.name' = 'trading_id',
    'timestamp.column.name' = 'trading_date',
    'timestamp.initial' = 20171116,
    'table.whitelist' = 'crypto_avax_usd',
    'validate.non.null' = true,
    'transforms' = 'copyFieldToKey,extractKeyFromStruct,removeKeyFromValue',
    'transforms.copyFieldToKey.type' = 'org.apache.kafka.connect.transforms.ValueToKey',
    'transforms.copyFieldToKey.fields' = 'trading_id',
    'transforms.extractKeyFromStruct.type' = 'org.apache.kafka.connect.transforms.ExtractField$Key',
    'transforms.extractKeyFromStruct.field' = 'trading_id',
    'transforms.removeKeyFromValue.type' = 'org.apache.kafka.connect.transforms.ReplaceField$Value',
    'transforms.removeKeyFromValue.blacklist' = 'trading_id',
    'key.converter' = 'org.apache.kafka.connect.converters.IntegerConverter'
);

CREATE SOURCE CONNECTOR IF NOT EXISTS pg_bnb_usd_stream_source_conn WITH (
    'name' = 'source_connector_from_pg_crypto_stocks_to_stream_bnb',
    'connector.class' = 'io.confluent.connect.jdbc.JdbcSourceConnector',
    'connection.url' = 'jdbc:postgresql://postgres:5432/crypto_prices',
    'connection.user' = 'pg',
    'connection.password' = 'pg',
    'mode' = 'incrementing ',
    'topic.prefix' = 'pg_',
    'incrementing.column.name' = 'trading_id',
    'timestamp.column.name' = 'trading_date',
    'timestamp.initial' = 20171116,
    'table.whitelist' = 'crypto_bnb_usd',
    'validate.non.null' = true,
    'transforms' = 'copyFieldToKey,extractKeyFromStruct,removeKeyFromValue',
    'transforms.copyFieldToKey.type' = 'org.apache.kafka.connect.transforms.ValueToKey',
    'transforms.copyFieldToKey.fields' = 'trading_id',
    'transforms.extractKeyFromStruct.type' = 'org.apache.kafka.connect.transforms.ExtractField$Key',
    'transforms.extractKeyFromStruct.field' = 'trading_id',
    'transforms.removeKeyFromValue.type' = 'org.apache.kafka.connect.transforms.ReplaceField$Value',
    'transforms.removeKeyFromValue.blacklist' = 'trading_id',
    'key.converter' = 'org.apache.kafka.connect.converters.IntegerConverter'
);

CREATE SOURCE CONNECTOR IF NOT EXISTS pg_btc_usd_stream_source_conn WITH (
    'name' = 'source_connector_from_pg_crypto_stocks_to_stream_btc',
    'connector.class' = 'io.confluent.connect.jdbc.JdbcSourceConnector',
    'connection.url' = 'jdbc:postgresql://postgres:5432/crypto_prices',
    'connection.user' = 'pg',
    'connection.password' = 'pg',
    'mode' = 'incrementing ',
    'topic.prefix' = 'pg_',
    'incrementing.column.name' = 'trading_id',
    'timestamp.column.name' = 'trading_date',
    'timestamp.initial' = 20171116,
    'table.whitelist' = 'crypto_btc_usd',
    'validate.non.null' = true,
    'transforms' = 'copyFieldToKey,extractKeyFromStruct,removeKeyFromValue',
    'transforms.copyFieldToKey.type' = 'org.apache.kafka.connect.transforms.ValueToKey',
    'transforms.copyFieldToKey.fields' = 'trading_id',
    'transforms.extractKeyFromStruct.type' = 'org.apache.kafka.connect.transforms.ExtractField$Key',
    'transforms.extractKeyFromStruct.field' = 'trading_id',
    'transforms.removeKeyFromValue.type' = 'org.apache.kafka.connect.transforms.ReplaceField$Value',
    'transforms.removeKeyFromValue.blacklist' = 'trading_id',
    'key.converter' = 'org.apache.kafka.connect.converters.IntegerConverter'
);

CREATE SOURCE CONNECTOR IF NOT EXISTS pg_doge_usd_stream_source_conn WITH (
    'name' = 'source_connector_from_pg_crypto_stocks_to_stream_doge',
    'connector.class' = 'io.confluent.connect.jdbc.JdbcSourceConnector',
    'connection.url' = 'jdbc:postgresql://postgres:5432/crypto_prices',
    'connection.user' = 'pg',
    'connection.password' = 'pg',
    'mode' = 'incrementing ',
    'topic.prefix' = 'pg_',
    'incrementing.column.name' = 'trading_id',
    'timestamp.column.name' = 'trading_date',
    'timestamp.initial' = 20171116,
    'table.whitelist' = 'crypto_doge_usd',
    'validate.non.null' = true,
    'transforms' = 'copyFieldToKey,extractKeyFromStruct,removeKeyFromValue',
    'transforms.copyFieldToKey.type' = 'org.apache.kafka.connect.transforms.ValueToKey',
    'transforms.copyFieldToKey.fields' = 'trading_id',
    'transforms.extractKeyFromStruct.type' = 'org.apache.kafka.connect.transforms.ExtractField$Key',
    'transforms.extractKeyFromStruct.field' = 'trading_id',
    'transforms.removeKeyFromValue.type' = 'org.apache.kafka.connect.transforms.ReplaceField$Value',
    'transforms.removeKeyFromValue.blacklist' = 'trading_id',
    'key.converter' = 'org.apache.kafka.connect.converters.IntegerConverter'
);

CREATE SOURCE CONNECTOR IF NOT EXISTS pg_eth_usd_stream_source_conn WITH (
    'name' = 'source_connector_from_pg_crypto_stocks_to_stream_eth',
    'connector.class' = 'io.confluent.connect.jdbc.JdbcSourceConnector',
    'connection.url' = 'jdbc:postgresql://postgres:5432/crypto_prices',
    'connection.user' = 'pg',
    'connection.password' = 'pg',
    'mode' = 'incrementing ',
    'topic.prefix' = 'pg_',
    'incrementing.column.name' = 'trading_id',
    'timestamp.column.name' = 'trading_date',
    'timestamp.initial' = 20171116,
    'table.whitelist' = 'crypto_eth_usd',
    'validate.non.null' = true,
    'transforms' = 'copyFieldToKey,extractKeyFromStruct,removeKeyFromValue',
    'transforms.copyFieldToKey.type' = 'org.apache.kafka.connect.transforms.ValueToKey',
    'transforms.copyFieldToKey.fields' = 'trading_id',
    'transforms.extractKeyFromStruct.type' = 'org.apache.kafka.connect.transforms.ExtractField$Key',
    'transforms.extractKeyFromStruct.field' = 'trading_id',
    'transforms.removeKeyFromValue.type' = 'org.apache.kafka.connect.transforms.ReplaceField$Value',
    'transforms.removeKeyFromValue.blacklist' = 'trading_id',
    'key.converter' = 'org.apache.kafka.connect.converters.IntegerConverter'
);

CREATE SOURCE CONNECTOR IF NOT EXISTS pg_sol_usd_stream_source_conn WITH (
    'name' = 'source_connector_from_pg_crypto_stocks_to_stream_sol',
    'connector.class' = 'io.confluent.connect.jdbc.JdbcSourceConnector',
    'connection.url' = 'jdbc:postgresql://postgres:5432/crypto_prices',
    'connection.user' = 'pg',
    'connection.password' = 'pg',
    'mode' = 'incrementing ',
    'topic.prefix' = 'pg_',
    'incrementing.column.name' = 'trading_id',
    'timestamp.column.name' = 'trading_date',
    'timestamp.initial' = 20171116,
    'table.whitelist' = 'crypto_sol_usd',
    'validate.non.null' = true,
    'transforms' = 'copyFieldToKey,extractKeyFromStruct,removeKeyFromValue',
    'transforms.copyFieldToKey.type' = 'org.apache.kafka.connect.transforms.ValueToKey',
    'transforms.copyFieldToKey.fields' = 'trading_id',
    'transforms.extractKeyFromStruct.type' = 'org.apache.kafka.connect.transforms.ExtractField$Key',
    'transforms.extractKeyFromStruct.field' = 'trading_id',
    'transforms.removeKeyFromValue.type' = 'org.apache.kafka.connect.transforms.ReplaceField$Value',
    'transforms.removeKeyFromValue.blacklist' = 'trading_id',
    'key.converter' = 'org.apache.kafka.connect.converters.IntegerConverter'
);

CREATE SOURCE CONNECTOR IF NOT EXISTS pg_trx_usd_stream_source_conn WITH (
    'name' = 'source_connector_from_pg_crypto_stocks_to_stream_trx',
    'connector.class' = 'io.confluent.connect.jdbc.JdbcSourceConnector',
    'connection.url' = 'jdbc:postgresql://postgres:5432/crypto_prices',
    'connection.user' = 'pg',
    'connection.password' = 'pg',
    'mode' = 'incrementing ',
    'topic.prefix' = 'pg_',
    'incrementing.column.name' = 'trading_id',
    'timestamp.column.name' = 'trading_date',
    'timestamp.initial' = 20171116,
    'table.whitelist' = 'crypto_trx_usd',
    'validate.non.null' = true,
    'transforms' = 'copyFieldToKey,extractKeyFromStruct,removeKeyFromValue',
    'transforms.copyFieldToKey.type' = 'org.apache.kafka.connect.transforms.ValueToKey',
    'transforms.copyFieldToKey.fields' = 'trading_id',
    'transforms.extractKeyFromStruct.type' = 'org.apache.kafka.connect.transforms.ExtractField$Key',
    'transforms.extractKeyFromStruct.field' = 'trading_id',
    'transforms.removeKeyFromValue.type' = 'org.apache.kafka.connect.transforms.ReplaceField$Value',
    'transforms.removeKeyFromValue.blacklist' = 'trading_id',
    'key.converter' = 'org.apache.kafka.connect.converters.IntegerConverter'
);

CREATE SOURCE CONNECTOR IF NOT EXISTS pg_usdt_usd_stream_source_conn WITH (
    'name' = 'source_connector_from_pg_crypto_stocks_to_stream_usdt',
    'connector.class' = 'io.confluent.connect.jdbc.JdbcSourceConnector',
    'connection.url' = 'jdbc:postgresql://postgres:5432/crypto_prices',
    'connection.user' = 'pg',
    'connection.password' = 'pg',
    'mode' = 'incrementing ',
    'topic.prefix' = 'pg_',
    'incrementing.column.name' = 'trading_id',
    'timestamp.column.name' = 'trading_date',
    'timestamp.initial' = 20171116,
    'table.whitelist' = 'crypto_usdt_usd',
    'validate.non.null' = true,
    'transforms' = 'copyFieldToKey,extractKeyFromStruct,removeKeyFromValue',
    'transforms.copyFieldToKey.type' = 'org.apache.kafka.connect.transforms.ValueToKey',
    'transforms.copyFieldToKey.fields' = 'trading_id',
    'transforms.extractKeyFromStruct.type' = 'org.apache.kafka.connect.transforms.ExtractField$Key',
    'transforms.extractKeyFromStruct.field' = 'trading_id',
    'transforms.removeKeyFromValue.type' = 'org.apache.kafka.connect.transforms.ReplaceField$Value',
    'transforms.removeKeyFromValue.blacklist' = 'trading_id',
    'key.converter' = 'org.apache.kafka.connect.converters.IntegerConverter'
);

CREATE SOURCE CONNECTOR IF NOT EXISTS pg_xrp_usd_stream_source_conn WITH (
    'name' = 'source_connector_from_pg_crypto_stocks_to_stream_xrp',
    'connector.class' = 'io.confluent.connect.jdbc.JdbcSourceConnector',
    'connection.url' = 'jdbc:postgresql://postgres:5432/crypto_prices',
    'connection.user' = 'pg',
    'connection.password' = 'pg',
    'mode' = 'incrementing ',
    'topic.prefix' = 'pg_',
    'incrementing.column.name' = 'trading_id',
    'timestamp.column.name' = 'trading_date',
    'timestamp.initial' = 20171116,
    'table.whitelist' = 'crypto_xrp_usd',
    'validate.non.null' = true,
    'transforms' = 'copyFieldToKey,extractKeyFromStruct,removeKeyFromValue',
    'transforms.copyFieldToKey.type' = 'org.apache.kafka.connect.transforms.ValueToKey',
    'transforms.copyFieldToKey.fields' = 'trading_id',
    'transforms.extractKeyFromStruct.type' = 'org.apache.kafka.connect.transforms.ExtractField$Key',
    'transforms.extractKeyFromStruct.field' = 'trading_id',
    'transforms.removeKeyFromValue.type' = 'org.apache.kafka.connect.transforms.ReplaceField$Value',
    'transforms.removeKeyFromValue.blacklist' = 'trading_id',
    'key.converter' = 'org.apache.kafka.connect.converters.IntegerConverter'
);


--Define input STREAM(s)
CREATE STREAM ada_usd (trading_id INTEGER KEY) WITH (KAFKA_TOPIC='pg_crypto_ada_usd', VALUE_FORMAT='AVRO', PARTITIONS=1);
CREATE STREAM avax_usd (trading_id INTEGER KEY) WITH (KAFKA_TOPIC='pg_crypto_avax_usd', VALUE_FORMAT='AVRO', PARTITIONS=1);
CREATE STREAM bnb_usd (trading_id INTEGER KEY) WITH (KAFKA_TOPIC='pg_crypto_bnb_usd', VALUE_FORMAT='AVRO', PARTITIONS=1);
CREATE STREAM btc_usd (trading_id INTEGER KEY) WITH (KAFKA_TOPIC='pg_crypto_btc_usd', VALUE_FORMAT='AVRO', PARTITIONS=1);
CREATE STREAM doge_usd (trading_id INTEGER KEY) WITH (KAFKA_TOPIC='pg_crypto_doge_usd', VALUE_FORMAT='AVRO', PARTITIONS=1);
CREATE STREAM eth_usd (trading_id INTEGER KEY) WITH (KAFKA_TOPIC='pg_crypto_eth_usd', VALUE_FORMAT='AVRO', PARTITIONS=1);
CREATE STREAM sol_usd (trading_id INTEGER KEY) WITH (KAFKA_TOPIC='pg_crypto_sol_usd', VALUE_FORMAT='AVRO', PARTITIONS=1);
CREATE STREAM trx_usd (trading_id INTEGER KEY) WITH (KAFKA_TOPIC='pg_crypto_trx_usd', VALUE_FORMAT='AVRO', PARTITIONS=1);
CREATE STREAM usdt_usd (trading_id INTEGER KEY) WITH (KAFKA_TOPIC='pg_crypto_usdt_usd', VALUE_FORMAT='AVRO', PARTITIONS=1);
CREATE STREAM xrp_usd (trading_id INTEGER KEY) WITH (KAFKA_TOPIC='pg_crypto_usdt_usd', VALUE_FORMAT='AVRO', PARTITIONS=1);

-- Create the stream for all stock data and then insert the data from each individual input stream into it
CREATE STREAM all_crypto_stock AS 
    SELECT
        TRADING_ID as Trading_ID,
        'ada' AS ticker_symbol,
        trading_date,
        trading_open,
        trading_high,
        trading_low,
        trading_close,
        trading_adj_close,
        trading_volume
    FROM 
        ada_usd
EMIT CHANGES;


INSERT INTO all_crypto_stock
    SELECT
        TRADING_ID as Trading_ID,
        'avax' AS ticker_symbol,
        trading_date,
        trading_open,
        trading_high,
        trading_low,
        trading_close,
        trading_adj_close,
        trading_volume
    FROM 
        avax_usd
EMIT CHANGES;

INSERT INTO all_crypto_stock
    SELECT
        TRADING_ID as Trading_ID,
        'bnb' AS ticker_symbol,
        trading_date,
        trading_open,
        trading_high,
        trading_low,
        trading_close,
        trading_adj_close,
        trading_volume
    FROM 
        bnb_usd
EMIT CHANGES;

INSERT INTO all_crypto_stock
    SELECT
        TRADING_ID as Trading_ID,
        'btc' AS ticker_symbol,
        trading_date,
        trading_open,
        trading_high,
        trading_low,
        trading_close,
        trading_adj_close,
        trading_volume
    FROM 
        btc_usd
EMIT CHANGES;

INSERT INTO all_crypto_stock 
    SELECT
        TRADING_ID as Trading_ID,
        'doge' AS ticker_symbol,
        trading_date,
        trading_open,
        trading_high,
        trading_low,
        trading_close,
        trading_adj_close,
        trading_volume
    FROM 
        doge_usd
EMIT CHANGES;

INSERT INTO all_crypto_stock 
    SELECT
        TRADING_ID as Trading_ID,
        'eth' AS ticker_symbol,
        trading_date,
        trading_open,
        trading_high,
        trading_low,
        trading_close,
        trading_adj_close,
        trading_volume
    FROM 
        eth_usd
EMIT CHANGES;

INSERT INTO all_crypto_stock
    SELECT
        TRADING_ID as Trading_ID,
        'sol' AS ticker_symbol,
        trading_date,
        trading_open,
        trading_high,
        trading_low,
        trading_close,
        trading_adj_close,
        trading_volume
    FROM 
        sol_usd
EMIT CHANGES;

INSERT INTO all_crypto_stock
    SELECT
        TRADING_ID as Trading_ID,
        'trx' AS ticker_symbol,
        trading_date,
        trading_open,
        trading_high,
        trading_low,
        trading_close,
        trading_adj_close,
        trading_volume
    FROM 
        trx_usd
EMIT CHANGES;

INSERT INTO all_crypto_stock
    SELECT
        TRADING_ID as Trading_ID,
        'usdt' AS ticker_symbol,
        trading_date,
        trading_open,
        trading_high,
        trading_low,
        trading_close,
        trading_adj_close,
        trading_volume
    FROM 
        usdt_usd
EMIT CHANGES;

INSERT INTO all_crypto_stock 
    SELECT
        TRADING_ID as Trading_ID,
        'xrp' AS ticker_symbol,
        trading_date,
        trading_open,
        trading_high,
        trading_low,
        trading_close,
        trading_adj_close,
        trading_volume
    FROM 
        xrp_usd
EMIT CHANGES;

-- Define intermediate STREAM(s)
-- all data (cleaned up)
CREATE STREAM STREAM_ALL_CRYPTO_DATA AS 
    SELECT
        TRADING_ID as Trading_ID,
        TRIM(ticker_symbol) AS Ticker_Symbol,
        CAST(trading_date AS VARCHAR) AS Trading_Date,
        SUBSTRING(CAST(trading_date AS VARCHAR), 1, 4) AS Trading_Year,
        trading_open AS Trading_Open,
        trading_high AS Trading_High,
        trading_low AS Trading_Low,
        trading_close AS Trading_Close,
        trading_adj_close AS Trading_Adjusted_Closing_Price,
        trading_volume AS Trading_Volume
    FROM
        all_crypto_stock
    EMIT CHANGES;

-- adjusted closing price for all crypto stocks during the year 2023
CREATE STREAM ADJ_CLOSING_PRICE_FOR_ALL_CRYPTO_IN_2023 AS
    SELECT
        TRADING_ID as Trading_ID,
        ticker_symbol AS Ticker_Symbol,
        CAST(trading_date AS VARCHAR) AS Trading_Date,
        SUBSTRING(CAST(trading_date AS VARCHAR), 1, 4) AS Trading_Year,
        trading_adj_close AS Trading_Adjusted_Closing_Price
    FROM 
        all_crypto_stock
    WHERE 
        FORMAT_DATE(trading_date, 'yyyy') = '2023'
    EMIT CHANGES;

--- Adjusted Closing price for all crypto stocks (for all years within the dataset)
CREATE STREAM ADJ_CLOSING_PRICE_FOR_ALL_CRYPTO AS
    SELECT
        TRADING_ID as Trading_ID,
        ticker_symbol AS Ticker_Symbol,
        CAST(trading_date AS VARCHAR) AS Trading_Date,
        SUBSTRING(CAST(trading_date AS VARCHAR), 1, 4) AS Trading_Year,
        trading_adj_close AS Trading_Adjusted_Closing_Price
    FROM 
        all_crypto_stock
    EMIT CHANGES;

-- Define SINK CONNECTOR(s)
CREATE SINK CONNECTOR IF NOT EXISTS pg_all_crypto_stocks_stream_sink_conn WITH (
  'name'                = 'pg_all_crypto_stocks_stream_sink_conn',
  'connector.class'     = 'io.confluent.connect.jdbc.JdbcSinkConnector',
  'connection.url'      = 'jdbc:postgresql://postgres:5432/output_crypto_prices',
  'connection.user'     = 'pg',
  'connection.password' = 'pg',
  'output.data.format'  = 'AVRO',
  'topics'              = 'STREAM_ALL_CRYPTO_DATA',
  'auto.create'         = 'true',
  'auto.evolve'         = 'true'
);

CREATE SINK CONNECTOR IF NOT EXISTS pg_adj_close_price_all_crypto_in_2023_stream_sink_conn WITH (
  'name'                = 'pg_adj_close_price_all_crypto_in_2023_stream_sink_conn',
  'connector.class'     = 'io.confluent.connect.jdbc.JdbcSinkConnector',
  'connection.url'      = 'jdbc:postgresql://postgres:5432/output_crypto_prices',
  'connection.user'     = 'pg',
  'connection.password' = 'pg',
  'output.data.format'  = 'AVRO',
  'topics'              = 'ADJ_CLOSING_PRICE_FOR_ALL_CRYPTO_IN_2023',
  'auto.create'         = 'true',
  'auto.evolve'         = 'true'
);

CREATE SINK CONNECTOR IF NOT EXISTS pg_adj_close_price_all_crypto_stream_sink_conn WITH (
  'name'                = 'pg_adj_close_price_all_crypto_stream_sink_conn',
  'connector.class'     = 'io.confluent.connect.jdbc.JdbcSinkConnector',
  'connection.url'      = 'jdbc:postgresql://postgres:5432/output_crypto_prices',
  'connection.user'     = 'pg',
  'connection.password' = 'pg',
  'output.data.format'  = 'AVRO',
  'topics'              = 'ADJ_CLOSING_PRICE_FOR_ALL_CRYPTO',
  'auto.create'         = 'true',
  'auto.evolve'         = 'true'
);

-- other statements
SHOW TOPICS;
SHOW STREAMS;
SHOW TABLES;
SHOW PROPERTIES;
SHOW QUERIES;

echo 'SELECT * FROM "STREAM_ALL_CRYPTO_DATA" LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_crypto_prices'
echo 'SELECT COUNT("TICKER_SYMBOL") FROM "STREAM_ALL_CRYPTO_DATA";' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_crypto_prices'

echo 'SELECT * FROM "ADJ_CLOSING_PRICE_FOR_ALL_CRYPTO" LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_crypto_prices'
echo 'SELECT COUNT("TICKER_SYMBOL") FROM "ADJ_CLOSING_PRICE_FOR_ALL_CRYPTO";' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_crypto_prices'

echo 'SELECT * FROM "ADJ_CLOSING_PRICE_FOR_ALL_CRYPTO_IN_2023" LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_crypto_prices'
echo 'SELECT COUNT("TICKER_SYMBOL") FROM "ADJ_CLOSING_PRICE_FOR_ALL_CRYPTO_IN_2023";' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_crypto_prices'





-- DESCRIBE components (streams, tables, and connectors)
/* 
source connectors 
    - I am going to only include a few of the source connectors as they 
    are all the same, with the excception of the crypto stock ticker.

*/
DESCRIBE CONNECTOR pg_ada_usd_stream_source_conn;
DESCRIBE CONNECTOR pg_doge_usd_stream_source_conn;
DESCRIBE CONNECTOR pg_xrp_usd_stream_source_conn;

-- sink connectors
DESCRIBE CONNECTOR pg_all_crypto_stocks_stream_sink_conn;
DESCRIBE CONNECTOR pg_adj_close_price_all_crypto_in_2023_stream_sink_conn;
DESCRIBE CONNECTOR pg_adj_close_price_all_crypto_stream_sink_conn;

-- streams & tables 
/*
    - For the input streams, I am only going to show a select few as they 
    are all the same with the only difference being the ticker symbol).
*/
DESCRIBE ada_usd EXTENDED;
DESCRIBE trx_usd EXTENDED;
DESCRIBE doge_usd EXTENDED;

DESCRIBE all_crypto_stock EXTENDED;

DESCRIBE STREAM_ALL_CRYPTO_DATA EXTENDED;
DESCRIBE ADJ_CLOSING_PRICE_FOR_ALL_CRYPTO_IN_2023 EXTENDED;
DESCRIBE ADJ_CLOSING_PRICE_FOR_ALL_CRYPTO EXTENDED;
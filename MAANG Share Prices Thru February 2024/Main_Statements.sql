-- Make sure that the data is imported into the postgres tables correctly (run this in bash, not the docker CLI)
echo 'SELECT * FROM maang_source_amazon LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(trading_date) FROM maang_source_amazon;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

echo 'SELECT * FROM maang_source_apple LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(trading_date) FROM maang_source_apple;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

echo 'SELECT * FROM maang_source_google LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(trading_date) FROM maang_source_google;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

echo 'SELECT * FROM maang_source_meta LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(trading_date) FROM maang_source_meta;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

echo 'SELECT * FROM maang_source_netflix LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(trading_date) FROM maang_source_netflix;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

/*
#docker compose command to develop interactively:

docker exec -it ksqldb-cli ksql http://ksqldb-server:8088
*/

-- update the auto.offset.reset setting
SET 'auto.offset.reset' = 'earliest';

-- Create SOURCE CONNECTOR for all db tables
CREATE SOURCE CONNECTOR IF NOT EXISTS pg_maang_stream_source_conn WITH (
    'name' = 'source_connector_from_pg_maang_to_stream_all_data_records',
    'connector.class' = 'io.confluent.connect.jdbc.JdbcSourceConnector',
    'connection.url' = 'jdbc:postgresql://postgres:5432/maang_stock_source',
    'connection.user' = 'pg',
    'connection.password' = 'pg',
    'mode'='incrementing',
    'topic.prefix' = 'pg_',
    'incrementing.column.name' = 'id',
    'timestamp.column.name' = 'trading_date',
    'timestamp.initial' = 883634400, -- 1998-01-01
    'validate.non.null' = true,
    'table.whitelist' = 'maang_source_amazon,maang_source_apple,maang_source_google,maang_source_meta,maang_source_netflix'
);

-- create input streams
CREATE STREAM source_stream_maang_source_amazon (
    id INTEGER,
    trading_date VARCHAR,
    trading_open DOUBLE,
    trading_high DOUBLE,
    trading_low DOUBLE,
    trading_close DOUBLE,
    trading_adj_close DOUBLE,
    trading_volume BIGINT
)
WITH 
(
    KAFKA_TOPIC='pg_maang_source_amazon',
    VALUE_FORMAT='AVRO', 
    PARTITIONS=1
);

CREATE STREAM source_stream_maang_source_apple (
    id INTEGER,
    trading_date VARCHAR,
    trading_open DOUBLE,
    trading_high DOUBLE,
    trading_low DOUBLE,
    trading_close DOUBLE,
    trading_adj_close DOUBLE,
    trading_volume BIGINT
)
WITH 
(
    KAFKA_TOPIC='pg_maang_source_apple',
    VALUE_FORMAT='AVRO', 
    PARTITIONS=1
);

CREATE STREAM source_stream_maang_source_google (
    id INTEGER,
    trading_date VARCHAR,
    trading_open DOUBLE,
    trading_high DOUBLE,
    trading_low DOUBLE,
    trading_close DOUBLE,
    trading_adj_close DOUBLE,
    trading_volume BIGINT
)
WITH 
(
    KAFKA_TOPIC='pg_maang_source_google',
    VALUE_FORMAT='AVRO', 
    PARTITIONS=1
);

CREATE STREAM source_stream_maang_source_meta (
    id INTEGER,
    trading_date VARCHAR,
    trading_open DOUBLE,
    trading_high DOUBLE,
    trading_low DOUBLE,
    trading_close DOUBLE,
    trading_adj_close DOUBLE,
    trading_volume BIGINT
)
WITH 
(
    KAFKA_TOPIC='pg_maang_source_meta',
    VALUE_FORMAT='AVRO', 
    PARTITIONS=1
);

CREATE STREAM source_stream_maang_source_netflix (
    id INTEGER,
    trading_date VARCHAR,
    trading_open DOUBLE,
    trading_high DOUBLE,
    trading_low DOUBLE,
    trading_close DOUBLE,
    trading_adj_close DOUBLE,
    trading_volume BIGINT
)
WITH 
(
    KAFKA_TOPIC='pg_maang_source_netflix',
    VALUE_FORMAT='AVRO', 
    PARTITIONS=1
);

SHOW STREAMS;
SHOW TOPICS;

-- merge all individual stock tables into one table & 
-- make sure to add/include company name of stock
CREATE STREAM all_stock_data (
    Stock_Company_Name VARCHAR,
    Trading_Date VARCHAR,
    Trading_Open DOUBLE,
    Trading_High DOUBLE,
    Trading_Low DOUBLE,
    Trading_Close DOUBLE,
    Trading_Adj_Close DOUBLE,
    Trading_Volume BIGINT
) WITH (
    KAFKA_TOPIC='pg_maang_merged_source',
    VALUE_FORMAT='AVRO', 
    PARTITIONS=1
);

INSERT INTO 
    all_stock_data
SELECT 
    'Amazon' AS Stock_Company_Name, 
    trading_date, 
    trading_open, 
    trading_high, 
    trading_low, 
    trading_close, 
    trading_adj_close, 
    trading_volume 
FROM 
    source_stream_maang_source_amazon
EMIT CHANGES;

INSERT INTO 
    all_stock_data
SELECT 
    'Apple' AS Stock_Company_Name, 
    trading_date, 
    trading_open, 
    trading_high, 
    trading_low, 
    trading_close, 
    trading_adj_close, 
    trading_volume 
FROM 
    source_stream_maang_source_apple
EMIT CHANGES;

INSERT INTO 
    all_stock_data
SELECT 
    'Google' AS Stock_Company_Name, 
    trading_date, 
    trading_open, 
    trading_high, 
    trading_low, 
    trading_close, 
    trading_adj_close, 
    trading_volume
FROM 
    source_stream_maang_source_google
EMIT CHANGES;

INSERT INTO 
    all_stock_data
SELECT 
    'Meta' AS Stock_Company_Name,
    trading_date, 
    trading_open, 
    trading_high, 
    trading_low, 
    trading_close, 
    trading_adj_close, 
    trading_volume 
FROM 
    source_stream_maang_source_meta
EMIT CHANGES;

INSERT INTO 
    all_stock_data
SELECT 
    'Netflix' AS Stock_Company_Name,
    trading_date, 
    trading_open, 
    trading_high, 
    trading_low, 
    trading_close, 
    trading_adj_close, 
    trading_volume 
FROM 
    source_stream_maang_source_netflix
EMIT CHANGES;

--- Write intermediate streams
CREATE STREAM all_data_for_google_and_meta AS 
    SELECT
        Stock_Company_Name,
        trading_date, 
        trading_open, 
        trading_high, 
        trading_low, 
        trading_close, 
        trading_adj_close, 
        trading_volume 
    FROM 
        all_stock_data
    WHERE
        Stock_Company_Name = 'Google'
        OR 
        Stock_Company_Name = 'Meta'
    EMIT CHANGES;

-- stream volume-related data for all of the stocks
CREATE STREAM volume_for_all_stocks AS 
    SELECT
        Stock_Company_Name,
        trading_date,
        trading_adj_close,
        trading_volume
    FROM 
        all_stock_data
    EMIT CHANGES;

-- Write Sink Connectors

-- all data
CREATE SINK CONNECTOR IF NOT EXISTS all_data_all_tables_sink WITH (
  'connector.class'     = 'io.confluent.connect.jdbc.JdbcSinkConnector',
  'connection.url'      = 'jdbc:postgresql://postgres:5432/output_maang_stocks',
  'connection.user'     = 'pg',
  'connection.password' = 'pg',
  'output.data.format'  = 'AVRO',
  'topics'              = 'pg_maang_merged_source',
  'auto.create'         = 'true',
  'auto.evolve'         = 'true',
  'table.name.format'   = 'output_${topic}'
);

-- all data for google & meta sink connector
CREATE SINK CONNECTOR IF NOT EXISTS all_data_for_google_and_meta_sink WITH (
  'connector.class'     = 'io.confluent.connect.jdbc.JdbcSinkConnector',
  'connection.url'      = 'jdbc:postgresql://postgres:5432/output_maang_stocks',
  'connection.user'     = 'pg',
  'connection.password' = 'pg',
  'output.data.format'  = 'AVRO',
  'topics'              = 'ALL_DATA_FOR_GOOGLE_AND_META',
  'auto.create'         = 'true',
  'auto.evolve'         = 'true',
  'table.name.format'   = 'output_${topic}'
);
-- output_ALL_DATA_FOR_GOOGLE_AND_META


-- maang stock google sink connector
CREATE SINK CONNECTOR IF NOT EXISTS maang_stock_google_sink WITH (
  'connector.class'     = 'io.confluent.connect.jdbc.JdbcSinkConnector',
  'connection.url'      = 'jdbc:postgresql://postgres:5432/output_maang_stocks',
  'connection.user'     = 'pg',
  'connection.password' = 'pg',
  'output.data.format'  = 'AVRO',
  'topics'              = 'pg_maang_source_google',
  'auto.create'         = 'true',
  'auto.evolve'         = 'true',
  'table.name.format'   = 'output_${topic}'
);
-- output_pg_maang_source_google

-- volume_for_all_stocks_sink connector
CREATE SINK CONNECTOR IF NOT EXISTS volume_for_all_stocks_sink WITH (
  'name'                = 'volume_for_all_stocks_sink',
  'connector.class'     = 'io.confluent.connect.jdbc.JdbcSinkConnector',
  'connection.url'      = 'jdbc:postgresql://postgres:5432/output_maang_stocks',
  'connection.user'     = 'pg',
  'connection.password' = 'pg',
  'output.data.format'  = 'AVRO',
  'topics'              = 'VOLUME_FOR_ALL_STOCKS',
  'auto.create'         = 'true',
  'auto.evolve'         = 'true',
  'table.name.format'   = 'output_${topic}'
);

-- make sure that data was pushed to new db's tables as expected
echo 'SELECT * FROM "output_pg_maang_merged_source" LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_maang_stocks'
echo 'SELECT COUNT("TRADING_DATE") FROM "output_pg_maang_merged_source";' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_maang_stocks'

echo 'SELECT * FROM "output_ALL_DATA_FOR_GOOGLE_AND_META" LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_maang_stocks'
echo 'SELECT COUNT("TRADING_DATE") FROM "output_ALL_DATA_FOR_GOOGLE_AND_META";' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_maang_stocks'

echo 'SELECT * FROM "output_pg_maang_source_google" LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_maang_stocks'
echo 'SELECT COUNT("trading_open") FROM "output_pg_maang_source_google";' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_maang_stocks'

echo 'SELECT * FROM "output_VOLUME_FOR_ALL_STOCKS" LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_maang_stocks'
echo 'SELECT COUNT("TRADING_DATE") FROM "output_VOLUME_FOR_ALL_STOCKS";' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_maang_stocks'

-- other statements
SHOW TOPICS;
SHOW STREAMS;
SHOW TABLES;
SHOW PROPERTIES;
SHOW QUERIES;

-- DESCRIBE components (streams, tables, and connectors)
-- source connector(s)
DESCRIBE CONNECTOR pg_maang_stream_source_conn;

-- sink connectors
DESCRIBE CONNECTOR all_data_all_tables_sink;
DESCRIBE CONNECTOR all_data_for_google_and_meta_sink;
DESCRIBE CONNECTOR maang_stock_google_sink;
DESCRIBE CONNECTOR volume_for_all_stocks_sink;

-- streams & tables
DESCRIBE  EXTENDED;
DESCRIBE  EXTENDED;
DESCRIBE  EXTENDED;
DESCRIBE  EXTENDED;
DESCRIBE  EXTENDED;
DESCRIBE  EXTENDED;
DESCRIBE  EXTENDED;
DESCRIBE  EXTENDED;
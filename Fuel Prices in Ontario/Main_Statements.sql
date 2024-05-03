-- Make sure that the data is imported into the postgres tables correctly (run this in bash, not the docker CLI)
echo 'SELECT * FROM ontario_fuel_prices LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(gas_price_id) FROM ontario_fuel_prices;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

/*
#docker compose command to develop interactively:

docker exec -it ksqldb-cli ksql http://ksqldb-server:8088
*/

-- update the auto.offset.reset setting
SET 'auto.offset.reset' = 'earliest';

CREATE SOURCE CONNECTOR IF NOT EXISTS pg_ontario_fuel_prices_stream_source_conn WITH (
    'name' ='source_connector_from_pg_ontario_fuel_prices_to_stream',
    'connector.class' = 'io.confluent.connect.jdbc.JdbcSourceConnector',
    'connection.url' = 'jdbc:postgresql://postgres:5432/ontario_fuel_prices_db',
    'connection.user' = 'pg',
    'connection.password' = 'pg',
    'mode' = 'incrementing',
    'topic.prefix' = 'pg_',
    'incrementing.column.name' = 'gas_price_id',
    'timestamp.column.name' = 'gas_price_date',
    'timestamp.initial' = 631324800,
    'validate.non.null' = true,
    'transforms' = 'copyFieldToKey,extractKeyFromStruct,removeKeyFromValue',
    'transforms.copyFieldToKey.type' = 'org.apache.kafka.connect.transforms.ValueToKey',
    'transforms.copyFieldToKey.fields' = 'gas_price_id',
    'transforms.extractKeyFromStruct.type' = 'org.apache.kafka.connect.transforms.ExtractField$Key',
    'transforms.extractKeyFromStruct.field' = 'gas_price_id',
    'transforms.removeKeyFromValue.type' = 'org.apache.kafka.connect.transforms.ReplaceField$Value',
    'transforms.removeKeyFromValue.blacklist' = 'gas_price_id',
    'key.converter' = 'org.apache.kafka.connect.converters.IntegerConverter'
);

-- Define input STREAM(s)
CREATE STREAM ofp_stream (gas_price_id INTEGER KEY) WITH (KAFKA_TOPIC='pg_ontario_fuel_prices', VALUE_FORMAT='AVRO');

-- Create intermediate & sink STREAMs
-- clean all data
CREATE STREAM stream_cleaned_ofp AS 
    SELECT
        gas_price_id AS Gas_Price_Id,
        PARSE_TIMESTAMP(gas_price_date, 'yyyy-MM-DD''T''HH:mm:ss') AS Gas_Price_Date,
        ottawa AS Ottawa,
        toronto_west_region AS Toronto_West_Region,
        toronto_east_region AS Toronto_East_Region,
        windsor AS Windsor,
        london AS London,
        peterborough_city AS Peterborough_City,
        st_catharines AS St_Catharines,
        sudbury AS Sudbury,
        sault_saint_marie AS Sault_Saint_Marie,
        thunder_bay AS Thunder_Bay,
        north_bay AS North_Bay,
        timmins AS Timmins,
        kenora AS Kenora,
        parry_sound AS Parry_Sound,
        ontario_avg AS Ontario_Avg,
        southern_avg AS Southern_Avg,
        northern_avg AS Northern_Avg,
        fuel_type AS Fuel_Type,
        type_de_carburant AS Type_of_Carburant
    FROM 
        ofp_stream
    EMIT CHANGES;

-- Create TABLE: Average ontario_fuel_prices by month of year
CREATE TABLE table_cleaned_ofp_average_by_month_of_year AS 
    SELECT
        FORMAT_TIMESTAMP(gas_price_date, 'MM') AS Gas_Price_Month,
        AVG(ottawa) AS Average_Price_in_Ottawa,
        AVG(toronto_west_region) AS Average_Price_in_Toronto_West_Region,
        AVG(toronto_east_region) AS Average_Price_in_Toronto_East_Region,
        AVG(windsor) AS Average_Price_in_Windsor,
        AVG(london) AS Average_Price_in_London,
        AVG(peterborough_city) AS Average_Price_in_Peterborough_City,
        AVG(st_catharines) AS Average_Price_in_St_Catharines,
        AVG(sudbury) AS Average_Price_in_Sudbury,
        AVG(sault_saint_marie) AS Average_Price_in_Sault_Saint_Marie,
        AVG(thunder_bay) AS Average_Price_in_Thunder_Bay,
        AVG(north_bay) AS Average_Price_in_North_Bay,
        AVG(timmins) AS Average_Price_in_Timmins,
        AVG(kenora) AS Average_Price_in_Kenora,
        AVG(parry_sound) AS Average_Price_in_Parry_Sound,
        AVG(ontario_avg) AS Average_Price_in_Ontario_Avg,
        AVG(southern_avg) AS Average_Price_in_Southern_Avg,
        AVG(northern_avg) AS Average_Price_in_Northern_Avg
    FROM 
        stream_cleaned_ofp
    GROUP BY
        FORMAT_TIMESTAMP(gas_price_date, 'MM')
    EMIT CHANGES;

-- Create TABLE: average Diesel Fuel Type price ontario_fuel_prices by month of year
CREATE TABLE table_diesel_fuel_type_ofp_average_by_month_of_year AS 
    SELECT
        CONCAT(TRIM(fuel_type), '_', FORMAT_TIMESTAMP(gas_price_date, 'MM')) AS Month_And_Type,
        AVG(ottawa) AS Average_Price_in_Ottawa,
        AVG(toronto_west_region) AS Average_Price_in_Toronto_West_Region,
        AVG(toronto_east_region) AS Average_Price_in_Toronto_East_Region,
        AVG(windsor) AS Average_Price_in_Windsor,
        AVG(london) AS Average_Price_in_London,
        AVG(peterborough_city) AS Average_Price_in_Peterborough_City,
        AVG(st_catharines) AS Average_Price_in_St_Catharines,
        AVG(sudbury) AS Average_Price_in_Sudbury,
        AVG(sault_saint_marie) AS Average_Price_in_Sault_Saint_Marie,
        AVG(thunder_bay) AS Average_Price_in_Thunder_Bay,
        AVG(north_bay) AS Average_Price_in_North_Bay,
        AVG(timmins) AS Average_Price_in_Timmins,
        AVG(kenora) AS Average_Price_in_Kenora,
        AVG(parry_sound) AS Average_Price_in_Parry_Sound,
        AVG(ontario_avg) AS Average_Price_in_Ontario_Avg,
        AVG(southern_avg) AS Average_Price_in_Southern_Avg,
        AVG(northern_avg) AS Average_Price_in_Northern_Avg
    FROM 
        stream_cleaned_ofp
    WHERE
        fuel_type='Diesel'
    GROUP BY
        CONCAT(TRIM(fuel_type), '_', FORMAT_TIMESTAMP(gas_price_date, 'MM'))
    EMIT CHANGES;

-- Create TABLE: average ontario_fuel_prices for Diesel Type of Carburant by month of year
CREATE TABLE table_diesel_fuel_type_ofp_average AS 
    SELECT
        CONCAT(FORMAT_TIMESTAMP(gas_price_date, 'MM'), '_', TRIM(Type_of_Carburant)) AS Month_And_Type,
        AVG(ottawa) AS Average_Price_in_Ottawa,
        AVG(toronto_west_region) AS Average_Price_in_Toronto_West_Region,
        AVG(toronto_east_region) AS Average_Price_in_Toronto_East_Region,
        AVG(windsor) AS Average_Price_in_Windsor,
        AVG(london) AS Average_Price_in_London,
        AVG(peterborough_city) AS Average_Price_in_Peterborough_City,
        AVG(st_catharines) AS Average_Price_in_St_Catharines,
        AVG(sudbury) AS Average_Price_in_Sudbury,
        AVG(sault_saint_marie) AS Average_Price_in_Sault_Saint_Marie,
        AVG(thunder_bay) AS Average_Price_in_Thunder_Bay,
        AVG(north_bay) AS Average_Price_in_North_Bay,
        AVG(timmins) AS Average_Price_in_Timmins,
        AVG(kenora) AS Average_Price_in_Kenora,
        AVG(parry_sound) AS Average_Price_in_Parry_Sound,
        AVG(ontario_avg) AS Average_Price_in_Ontario_Avg,
        AVG(southern_avg) AS Average_Price_in_Southern_Avg,
        AVG(northern_avg) AS Average_Price_in_Northern_Avg
    FROM 
        stream_cleaned_ofp
    WHERE
        TRIM(Type_of_Carburant) = 'Diesel'
    GROUP BY
        CONCAT(FORMAT_TIMESTAMP(gas_price_date, 'MM'), '_', TRIM(Type_of_Carburant))
    EMIT CHANGES;



-- Define SINK CONNECTOR(s)
CREATE SINK CONNECTOR IF NOT EXISTS pg_cleaned_ofp_stream_sink_conn WITH (
  'name'                = 'cleaned_ofp_stream_sink_conn',
  'connector.class'     = 'io.confluent.connect.jdbc.JdbcSinkConnector',
  'connection.url'      = 'jdbc:postgresql://postgres:5432/output_ontario_fuel_prices_db',
  'connection.user'     = 'pg',
  'connection.password' = 'pg',
  'output.data.format'  = 'AVRO',
  'topics'              = 'STREAM_CLEANED_OFP',
  'auto.create'         = 'true',
  'auto.evolve'         = 'true',
  'table.name.format'   = 'output_${topic}'
);

CREATE SINK CONNECTOR IF NOT EXISTS pg_cleaned_ofp_avg_by_month_table_sink_conn WITH (
  'name'                = 'cleaned_ofp_avg_by_month_table_sink_conn',
  'connector.class'     = 'io.confluent.connect.jdbc.JdbcSinkConnector',
  'connection.url'      = 'jdbc:postgresql://postgres:5432/output_ontario_fuel_prices_db',
  'connection.user'     = 'pg',
  'connection.password' = 'pg',
  'output.data.format'  = 'AVRO',
  'topics'              = 'TABLE_CLEANED_OFP_AVERAGE_BY_MONTH_OF_YEAR',
  'auto.create'         = 'true',
  'auto.evolve'         = 'true',
  'table.name.format'   = 'output_${topic}'
);


CREATE SINK CONNECTOR IF NOT EXISTS pg_diesel_carb_type_ofp_avg_by_month_table_sink_conn WITH (
  'name'                = 'diesel_carb_type_ofp_avg_by_month_table_sink_conn',
  'connector.class'     = 'io.confluent.connect.jdbc.JdbcSinkConnector',
  'connection.url'      = 'jdbc:postgresql://postgres:5432/output_ontario_fuel_prices_db',
  'connection.user'     = 'pg',
  'connection.password' = 'pg',
  'output.data.format'  = 'AVRO',
  'topics'              = 'TABLE_DIESEL_FUEL_TYPE_OFP_AVERAGE',
  'auto.create'         = 'true',
  'auto.evolve'         = 'true',
  'table.name.format'   = 'output_${topic}'
);


CREATE SINK CONNECTOR IF NOT EXISTS pg_table_diesel_fuel_type_ofp_avg_by_month_stream_sink_conn WITH (
  'name'                = 'table_diesel_fuel_type_ofp_avg_by_month_stream_sink_conn',
  'connector.class'     = 'io.confluent.connect.jdbc.JdbcSinkConnector',
  'connection.url'      = 'jdbc:postgresql://postgres:5432/output_ontario_fuel_prices_db',
  'connection.user'     = 'pg',
  'connection.password' = 'pg',
  'output.data.format'  = 'AVRO',
  'topics'              = 'TABLE_DIESEL_FUEL_TYPE_OFP_AVERAGE_BY_MONTH_OF_YEAR',
  'auto.create'         = 'true',
  'auto.evolve'         = 'true',
  'table.name.format'   = 'output_${topic}'
);

-- other statements
SHOW TOPICS;
SHOW STREAMS;
SHOW TABLES;
SHOW PROPERTIES;
SHOW QUERIES;

-- DESCRIBE components (streams, tables, and connectors)
-- source connectors
DESCRIBE CONNECTOR pg_ontario_fuel_prices_stream_source_conn;

-- sink connectors
DESCRIBE CONNECTOR pg_cleaned_ofp_stream_sink_conn;
DESCRIBE CONNECTOR pg_cleaned_ofp_avg_by_month_table_sink_conn;
DESCRIBE CONNECTOR pg_diesel_carb_type_ofp_avg_by_month_table_sink_conn;
DESCRIBE CONNECTOR pg_table_diesel_fuel_type_ofp_avg_by_month_stream_sink_conn;

-- streams & tables
DESCRIBE ofp_stream EXTENDED;

DESCRIBE stream_cleaned_ofp EXTENDED;
DESCRIBE OFP_STREAM EXTENDED;

DESCRIBE TABLE_CLEANED_OFP_AVERAGE_BY_MONTH_OF_YEAR EXTENDED;
DESCRIBE TABLE_DIESEL_FUEL_TYPE_OFP_AVERAGE EXTENDED;
DESCRIBE TABLE_DIESEL_FUEL_TYPE_OFP_AVERAGE_BY_MONTH_OF_YEAR EXTENDED;



STREAM_CLEANED_OFP
TABLE_CLEANED_OFP_AVERAGE_BY_MONTH_OF_YEAR
TABLE_DIESEL_FUEL_TYPE_OFP_AVERAGE
TABLE_DIESEL_FUEL_TYPE_OFP_AVERAGE_BY_MONTH_OF_YEAR

-- echo statements to make sure data actually made it to target db tables as expected
echo 'SELECT * FROM "output_STREAM_CLEANED_OFP" LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_ontario_fuel_prices_db'
echo 'SELECT COUNT("GAS_PRICE_DATE") FROM "output_STREAM_CLEANED_OFP";' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_ontario_fuel_prices_db'

echo 'SELECT * FROM "output_TABLE_CLEANED_OFP_AVERAGE_BY_MONTH_OF_YEAR" LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_ontario_fuel_prices_db'
echo 'SELECT COUNT("AVERAGE_PRICE_IN_OTTAWA") FROM "output_TABLE_CLEANED_OFP_AVERAGE_BY_MONTH_OF_YEAR";' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_ontario_fuel_prices_db'

echo 'SELECT * FROM "output_TABLE_DIESEL_FUEL_TYPE_OFP_AVERAGE" LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_ontario_fuel_prices_db'
echo 'SELECT COUNT("AVERAGE_PRICE_IN_OTTAWA") FROM "output_TABLE_DIESEL_FUEL_TYPE_OFP_AVERAGE";' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_ontario_fuel_prices_db'

echo 'SELECT * FROM "output_TABLE_DIESEL_FUEL_TYPE_OFP_AVERAGE_BY_MONTH_OF_YEAR" LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_ontario_fuel_prices_db'
echo 'SELECT COUNT("AVERAGE_PRICE_IN_OTTAWA") FROM "output_TABLE_DIESEL_FUEL_TYPE_OFP_AVERAGE_BY_MONTH_OF_YEAR";' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_ontario_fuel_prices_db'


-- DROP SINK CONNECTOR(s)
DROP CONNECTOR PG_TABLE_DIESEL_FUEL_TYPE_OFP_AVG_BY_MONTH_STREAM_SINK_CONN;
DROP CONNECTOR PG_DIESEL_CARB_TYPE_OFP_AVG_BY_MONTH_TABLE_SINK_CONN;
DROP CONNECTOR PG_CLEANED_OFP_AVG_BY_MONTH_TABLE_SINK_CONN;
DROP CONNECTOR PG_CLEANED_OFP_STREAM_SINK_CONN;

-- DROP TABLES (& their associated topics);
DROP TABLE TABLE_CLEANED_OFP_AVERAGE_BY_MONTH_OF_YEAR DELETE TOPIC;
DROP TABLE TABLE_DIESEL_FUEL_TYPE_OFP_AVERAGE DELETE TOPIC;
DROP TABLE TABLE_DIESEL_FUEL_TYPE_OFP_AVERAGE_BY_MONTH_OF_YEAR DELETE TOPIC;

-- DROP STREAMS (& their associated topics);
DROP STREAM STREAM_CLEANED_OFP DELETE TOPIC;
DROP STREAM OFP_STREAM DELETE TOPIC;

-- DROP SOURCE CONNECTOR
DROP CONNECTOR PG_ONTARIO_FUEL_PRICES_STREAM_SOURCE_CONN;
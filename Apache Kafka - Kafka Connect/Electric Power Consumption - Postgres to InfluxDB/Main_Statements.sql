/*
Source Database: Postgres
Target Database: InfluxDB
*/

-- Make sure that the data is imported into the postgres tables correctly (run this in bash, not the docker CLI)
-- For selecting data from Postgres
echo 'SELECT * FROM epc_table LIMIT 8;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

-- For counting rows in Postgres
echo 'SELECT COUNT(*) AS Num_Of_Records FROM epc_table;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

/*
#docker compose command to develop interactively:

docker exec -it ksqldb-cli ksql http://ksqldb-server:8088
*/

-- update the auto.offset.reset setting
SET 'auto.offset.reset' = 'earliest';

-- CREATE SOURCE CONNECTOR(s)
CREATE SOURCE CONNECTOR IF NOT EXISTS epc_pg_source_conn WITH (
    "name" = 'epc_pg_source_conn',
    "connector.class" = 'io.confluent.connect.jdbc.JdbcSourceConnector',
    "connection.url" = 'jdbc:postgresql://postgres:5432/epc_db',
    "connection.user" = 'pg',
    "connection.password" = 'pg',
    "table.whitelist" = 'epc_table',
    "tasks.max" = '1',
    "numeric.mapping" = 'best_fit',
    "dialect.name" = 'PostgreSqlDatabaseDialect',
    "mode" = 'incrementing',
    "incrementing.column.name" = 'id',
    "transforms" = 'copyFieldToKey,extractKeyFromStruct',
    "transforms.copyFieldToKey.type" = 'org.apache.kafka.connect.transforms.ValueToKey',
    "transforms.copyFieldToKey.fields" = 'id',
    "transforms.extractKeyFromStruct.type" = 'org.apache.kafka.connect.transforms.ExtractField$Key',
    "transforms.extractKeyFromStruct.field" = 'id',
    "key.converter" = 'org.apache.kafka.connect.converters.IntegerConverter'
);

CREATE STREAM epc_stream (
    id INT KEY,
    epc_datetime VARCHAR,
    temperature DOUBLE,
    humidity DOUBLE,
    wind_speed DOUBLE,
    general_diffuse_flows DOUBLE,
    diffuse_flows DOUBLE,
    power_consumption_zone_1 DOUBLE,
    power_consumption_zone_2 DOUBLE,
    power_consumption_zone_3 DOUBLE
) 
WITH 
(
    PARTITIONS = 1,
    VALUE_FORMAT = 'AVRO',
    KAFKA_TOPIC = 'epc_table'
);

SHOW CONNECTORS;
SHOW TOPICS;
SHOW STREAMS;
DESCRIBE CONNECTOR EPC_PG_SOURCE_CONN;

PRINT epc_table FROM BEGINNING LIMIT 25;
SELECT * FROM epc_stream EMIT CHANGES;

-- create stream to clean up the datetime value (epc_datetime)
CREATE STREAM EPC_TABLE_INFLUXDB AS
    SELECT
        id,
        UNIX_TIMESTAMP(PARSE_TIMESTAMP(epc_datetime, 'M/d/yyyy H:mm')) AS epc_datetime,
        temperature,
        humidity,
        wind_speed,
        general_diffuse_flows,
        diffuse_flows,
        power_consumption_zone_1,
        power_consumption_zone_2,
        power_consumption_zone_3
    FROM
        epc_stream;


SHOW CONNECTORS;
SHOW TOPICS;
SHOW STREAMS;

DESCRIBE epc_stream;
DESCRIBE EPC_TABLE_INFLUXDB;

PRINT EPC_TABLE_INFLUXDB FROM BEGINNING LIMIT 25;
SELECT * FROM EPC_TABLE_INFLUXDB EMIT CHANGES;

CREATE SINK CONNECTOR IF NOT EXISTS epc_influxdb_sink_conn WITH (
    "name" = 'epc_influxdb_sink_conn',
    "connector.class" = 'io.confluent.influxdb.InfluxDBSinkConnector',
    "tasks.max" = 1,
    "influxdb.url" = 'http://influxdb:8086',
    "topics" = 'EPC_TABLE_INFLUXDB',
    "influxdb.db" = 'epc_influx_db',
    "influxdb.username" = 'influx_kafka_user',
    "influxdb.gzip.enable" = 'true',
    "influxdb.log.level" = 'FULL',
    "event.time.fieldname" = 'EPC_DATETIME',
    "measurement.name.format" = '${topic}'
);

SHOW CONNECTORS;
SHOW TOPICS;
SHOW STREAMS;
DESCRIBE CONNECTOR EPC_INFLUXDB_SINK_CONN;

-- Run the next two commands in the docker bash shell, not the ksqldb-cli terminal
-- Show the count of the number of records in each column in the InfluxDB data
echo 'SELECT COUNT(*) FROM EPC_TABLE_INFLUXDB;' | docker exec -i influxdb influx -database epc_influx_db

-- Show 15 records from the InfluxDB database
echo 'SELECT * FROM EPC_TABLE_INFLUXDB LIMIT 15;' | docker exec -i influxdb influx -database epc_influx_db

-- Tear Down the project
-- Start with removing the SINK CONNECTOR
DROP CONNECTOR EPC_PG_SOURCE_CONN;

-- Then, remove the STREAMs
DROP STREAM EPC_TABLE_INFLUXDB DELETE TOPIC;
DROP STREAM EPC_STREAM DELETE TOPIC;

-- Finally, drop the SOURCE CONNECTOR
DROP CONNECTOR EPC_INFLUXDB_SINK_CONN;

-- Check that DROP statements worked as expected
SHOW CONNECTORS;
SHOW TOPICS;
SHOW STREAMS;
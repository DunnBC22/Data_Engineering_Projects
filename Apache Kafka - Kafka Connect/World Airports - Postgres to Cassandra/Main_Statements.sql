/*
Source Database: Postgres
Target Database: Apache Cassandra
*/

-- Return the first 25 records from the Postgres db
echo "SELECT * FROM world_airports_table LIMIT 25;" | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

-- Return a count of how many records are in the Postgres db
echo 'SELECT COUNT(*) FROM world_airports_table;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'


-- How do get the Data Center for Cassandra
docker exec cassie cqlsh -e 'SELECT data_center FROM system.local;' | head -4 | tail -1 | tr -d ' '

/*
#docker compose command to develop interactively:

docker exec -it ksqldb-cli ksql http://ksqldb-server:8088
*/

-- update the auto.offset.reset setting
SET 'auto.offset.reset' = 'earliest';

CREATE SOURCE CONNECTOR IF NOT EXISTS world_airports_pg_source_conn WITH (
    "name" = 'world_airports_pg_source_conn',
    "connector.class" = 'io.confluent.connect.jdbc.JdbcSourceConnector',
    "connection.url" = 'jdbc:postgresql://postgres:5432/world_airports_source',
    "connection.user" = 'pg',
    "connection.password" = 'pg',
    "table.whitelist" = 'world_airports_table',
    "numeric.mapping" = 'best_fit',
    "poll.interval.ms" = '1000',
    "validate.non.null" = 'false',
    "dialect.name" = 'PostgreSqlDatabaseDialect',
    "mode" = 'incrementing',
    "incrementing.column.name" = 'id',
    "batch.max.rows" = 1000,
    "transforms" = 'copyFieldToKey,extractKeyFromStruct',
    "transforms.copyFieldToKey.type" = 'org.apache.kafka.connect.transforms.ValueToKey',
    "transforms.copyFieldToKey.fields" = 'id',
    "transforms.extractKeyFromStruct.type" = 'org.apache.kafka.connect.transforms.ExtractField$Key',
    "transforms.extractKeyFromStruct.field" = 'id'
);

CREATE STREAM world_airports_pg_source_stream (
    x_coord DOUBLE,
    y_coord DOUBLE,
    object_id INT,
    id INT KEY,
    airport_identifier VARCHAR,
    airport_type VARCHAR,
    airport_name VARCHAR,
    latitude_coord DOUBLE,
    longitude_coord DOUBLE,
    elevation_ft INT,
    continent VARCHAR,
    iso_country VARCHAR,
    iso_region VARCHAR,
    municipality VARCHAR,
    scheduled_service VARCHAR,
    gps_code VARCHAR,
    iata_code VARCHAR,
    local_code VARCHAR,
    home_link VARCHAR,
    wikipedia_link VARCHAR,
    keywords VARCHAR,
    communications_desc VARCHAR,
    frequency_mhz DOUBLE,
    runway_length_ft INT,
    runway_width_ft INT,
    runway_surface VARCHAR,
    runway_lighted INT,
    runway_closed INT
)
WITH
(
    partitions=1,
    value_format='AVRO',
    kafka_topic='world_airports_table'
);

SHOW CONNECTORS;
SHOW STREAMS;
SHOW TOPICS;
DESCRIBE CONNECTOR WORLD_AIRPORTS_PG_SOURCE_CONN;


PRINT world_airports_table FROM BEGINNING LIMIT 10;

SELECT * FROM world_airports_pg_source_stream EMIT CHANGES;


-- CREATE SINK CONNECTOR(s)
CREATE SINK CONNECTOR IF NOT EXISTS world_airports_cassandra_sink_conn WITH (
    "name" = 'world_airports_cassandra_sink_conn',
    "connector.class" = 'com.datastax.oss.kafka.sink.CassandraSinkConnector',
    "tasks.max" = 1,
    "topics" = 'world_airports_table',
    "cassandra.contact.points" = 'cassie',
    "cassandra.keyspace" = 'world_airports_keyspace',
    "cassandra.port" = 9042,
    "contactPoints" = 'cassie',
    "loadBalancing.localDc" = 'datacenter1',
    "datastax-java-driver.basic.contact-poindocts" = 'cassie:9042',
    "maxNumberOfRecordsInBatch" = 1024,
    "connectionPoolLocalSize" = 8,
    "queryExecutionTimeout" = 60,
    "jmx" = 'true',
    "compression" = 'SNAPPY',
    "topic.world_airports_table.world_airports_keyspace.world_airports_table.ttl" = -1,
    "topic.world_airports_table.world_airports_keyspace.world_airports_table.nullToUnset" = 'true',
    "topic.world_airports_table.world_airports_keyspace.world_airports_table.consistencyLevel" = 'LOCAL_ONE',
    "topic.world_airports_table.world_airports_keyspace.world_airports_table.mapping" = 'id=value.id,x_coord=value.x_coord,y_coord=value.y_coord,object_id=value.object_id,airport_identifier=value.airport_identifier,airport_type=value.airport_type,airport_name=value.airport_name,latitude_coord=value.latitude_coord,longitude_coord=value.longitude_coord,elevation_ft=value.elevation_ft,continent=value.continent,iso_country=value.iso_country,iso_region=value.iso_region,municipality=value.municipality,scheduled_service=value.scheduled_service,gps_code=value.gps_code,iata_code=value.iata_code,local_code=value.local_code,home_link=value.home_link,wikipedia_link=value.wikipedia_link,keywords=value.keywords,communications_desc=value.communications_desc,frequency_mhz=value.frequency_mhz,runway_length_ft=value.runway_length_ft,runway_width_ft=value.runway_width_ft,runway_surface=value.runway_surface,runway_lighted=value.runway_lighted,runway_closed=value.runway_closed'
);

-- Go to the bash shell for the docker project for the next two commands:
-- Check to make sure that the data made it to Apache Cassandra db
echo 'USE world_airports_keyspace; SELECT * FROM world_airports_table LIMIT 18;' | docker exec -i cassie cqlsh

-- Return a count of how many records are in the Apache Cassandra db
echo 'USE world_airports_keyspace; SELECT COUNT(*) FROM world_airports_table;' | docker exec -i cassie cqlsh


/*
#docker compose command to develop interactively:

docker exec -it ksqldb-cli ksql http://ksqldb-server:8088
*/

-- Statements to remove STREAM(s) & CONNECTOR(s)
-- start with the SINK CONNECTOR(s)
DROP CONNECTOR world_airports_cassandra_sink_conn;

-- Next, the input STREAM [& their associated TOPIC]
DROP STREAM world_airports_pg_source_stream DELETE TOPIC;

-- Finally, the SOURCE CONNECTOR(s)
DROP CONNECTOR world_airports_pg_source_conn;
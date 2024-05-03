-- Make sure that the data is imported into the postgres tables correctly (run this in bash, not the docker CLI)
echo 'SELECT * FROM household_energy_data LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(hh_nrg_id) FROM household_energy_data;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

/*
#docker compose command to develop interactively:

docker exec -it ksqldb-cli ksql http://ksqldb-server:8088
*/

-- update the auto.offset.reset setting
SET 'auto.offset.reset' = 'earliest';

CREATE SOURCE CONNECTOR IF NOT EXISTS pg_hh_nrg_stream_source_conn WITH (
    'name'='source_connector_from_pg_hh_nrg_to_stream',
    'connector.class' = 'io.confluent.connect.jdbc.JdbcSourceConnector',
    'connection.url' = 'jdbc:postgresql://postgres:5432/hh_nrg_db',
    'dialect.name' = 'PostgreSqlDatabaseDialect',
    'connection.user' = 'pg',
    'connection.password' = 'pg',
    'mode' = 'bulk',
    'topic.prefix' = 'pg_',
    'incrementing.column.name' = 'hh_nrg_id',
    'timestamp.column.name' = 'energy_date',
    'timestamp.initial' = 1477027200,
    'validate.non.null' = true,
    'table.whitelist' = 'household_energy_data',
    'errors.log.enable' = 'true',
    'tasks.max' = 1,
    'numeric.mapping' = 'best_fit',
    'poll.interval.ms' = 360000,
    'batch.max.rows' = 15000,
    'transforms' = 'copyFieldToKey,extractKeyFromStruct,removeKeyFromValue',
    'transforms.copyFieldToKey.type' = 'org.apache.kafka.connect.transforms.ValueToKey',
    'transforms.copyFieldToKey.fields' = 'hh_nrg_id',
    'transforms.extractKeyFromStruct.type' = 'org.apache.kafka.connect.transforms.ExtractField$Key',
    'transforms.extractKeyFromStruct.field' = 'hh_nrg_id',
    'transforms.removeKeyFromValue.type' = 'org.apache.kafka.connect.transforms.ReplaceField$Value',
    'transforms.removeKeyFromValue.blacklist' = 'hh_nrg_id',
    'key.converter' = 'org.apache.kafka.connect.converters.IntegerConverter'
);

CREATE STREAM household_energy_data_source (hh_nrg_id INTEGER KEY) WITH (KAFKA_TOPIC='pg_household_energy_data', VALUE_FORMAT='AVRO', PARTITIONS=1);

CREATE STREAM STREAM_ALL_HOUSEHOLD_ENERGY_DATA_CLEANED AS
    SELECT
        HH_NRG_ID AS Household_Energy_ID,
        TRIM(energy_type) AS Energy_Type,
        energy_date AS Energy_Date,
        start_time AS Start_Time,
        end_time AS End_Time,
        energy_usage AS Energy_Usage,
        TRIM(energy_units) AS Energy_Units,
        CAST(TRIM(REPLACE(REPLACE(energy_cost, '$', ''), ',', '')) AS DOUBLE) AS Energy_Cost_in_Dollars,
        TRIM(notes) AS Notes
    FROM
        household_energy_data_source
    EMIT CHANGES;

PRINT 'pg_household_energy_data' FROM BEGINNING LIMIT 12;
PRINT 'STREAM_ALL_HOUSEHOLD_ENERGY_DATA_CLEANED' FROM BEGINNING LIMIT 12;

-- CREATE SINK CONNECTOR(s)
CREATE SINK CONNECTOR IF NOT EXISTS pg_all_clean_hh_nrg_data_sink_conn WITH (
  'connector.class'     = 'io.confluent.connect.jdbc.JdbcSinkConnector',
  'connection.url'      = 'jdbc:postgresql://postgres:5432/output_hh_nrg_db',
  'connection.user'     = 'pg',
  'connection.password' = 'pg',
  'output.data.format'  = 'AVRO',
  'topics'              = 'STREAM_ALL_HOUSEHOLD_ENERGY_DATA_CLEANED',
  'auto.create'         = 'true',
  'auto.evolve'         = 'true',
  'table.name.format'   = 'output_${topic}'
);

-- other statements
SHOW TOPICS;
SHOW STREAMS;
SHOW PROPERTIES;
SHOW QUERIES;

-- DESCRIBE components (streams, tables, and connectors)
-- source connectors
DESCRIBE CONNECTOR pg_hh_nrg_stream_source_conn;

-- sink connectors
DESCRIBE CONNECTOR pg_all_clean_hh_nrg_data_sink_conn;

-- streams & tables
DESCRIBE household_energy_data_source EXTENDED;
DESCRIBE STREAM_ALL_HOUSEHOLD_ENERGY_DATA_CLEANED EXTENDED;

-- echo statements to make sure data actually made it to target db tables as expected
echo 'SELECT * FROM "output_STREAM_ALL_HOUSEHOLD_ENERGY_DATA_CLEANED" LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_hh_nrg_db'
echo 'SELECT COUNT("ENERGY_DATE") FROM "output_STREAM_ALL_HOUSEHOLD_ENERGY_DATA_CLEANED";' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_hh_nrg_db'
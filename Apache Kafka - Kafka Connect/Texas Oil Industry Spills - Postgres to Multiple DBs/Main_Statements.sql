/*
Source Database: Postgres
Target Databases: MariaDB, MongoDB, & MySQL
*/

--- Make sure that the data is imported into the postgres tables correctly ---
-- texas_ois_district table
-- For selecting 12 records from Postgres
echo 'SELECT * FROM texas_ois_district LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
-- For counting rows in Postgres
echo 'SELECT COUNT(id) AS Num_Of_Records FROM texas_ois_district;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

-- texas_ois_central table
-- For selecting 12 records from Postgres
echo 'SELECT * FROM texas_ois_central LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
-- For counting rows in Postgres
echo 'SELECT COUNT(id) AS Num_Of_Records FROM texas_ois_central;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'


/*
#docker compose command to develop interactively:

docker exec -it ksqldb-cli ksql http://ksqldb-server:8088
*/

-- update the auto.offset.reset setting
SET 'auto.offset.reset' = 'earliest';

-- CREATE SOURCE CONNECTOR(s)
CREATE SOURCE CONNECTOR IF NOT EXISTS texas_ois_pg_source_conn WITH (
    "name" = 'texas_ois_pg_source_conn',
    "connector.class" = 'io.confluent.connect.jdbc.JdbcSourceConnector',
    'connection.url' = 'jdbc:postgresql://postgres:5432/texas_ois',
    "table.whitelist" = 'texas_ois_district, texas_ois_central',
    "connection.user" = 'pg',
    "connection.password" = 'pg',
    "topic.prefix" = 'ois_',
    "tasks.max" = '2',
    "numeric.mapping" = 'best_fit',
    "mode" = 'incrementing',
    "incrementing.column.name" = 'id',
    "transforms" = 'copyFieldToKey,extractKeyFromStruct',
    "transforms.copyFieldToKey.type" = 'org.apache.kafka.connect.transforms.ValueToKey',
    "transforms.copyFieldToKey.fields" = 'id',
    "transforms.extractKeyFromStruct.type" = 'org.apache.kafka.connect.transforms.ExtractField$Key',
    "transforms.extractKeyFromStruct.field" = 'id',
    'key.converter' = 'org.apache.kafka.connect.converters.IntegerConverter',
    "validate.non.null" = 'false'
);

-- Metadata statements
SHOW CONNECTORS;
SHOW TOPICS;
SHOW STREAMS;
DESCRIBE CONNECTOR texas_ois_pg_source_conn;

-- Input Stream for the texas_ois_district table
CREATE STREAM texas_ois_district_stream (
    id INT KEY,
    dist VARCHAR,
    district_edit VARCHAR,
    date_of_spill VARCHAR,
    date_of_spill_edit VARCHAR,
    date_called_in VARCHAR,
    date_called_in_edit VARCHAR,
    spill_number VARCHAR,
    rrc_job_number VARCHAR,
    operator_rp VARCHAR,
    operator_edit VARCHAR,
    lease_facility_name VARCHAR,
    rrc_id_number VARCHAR,
    county_name VARCHAR,
    county_edited VARCHAR,
    type_operation VARCHAR,
    source VARCHAR,
    probable_cause VARCHAR,
    probable_cause_edit VARCHAR,
    release_crude_oil VARCHAR,
    release_crude_oil_edit VARCHAR,
    release_cond VARCHAR,
    release_prod_wtr VARCHAR,
    release_prod_water_edit DOUBLE,
    release_gas VARCHAR,
    recovery_crude_oil VARCHAR,
    recovery_crude_oil_edit DOUBLE,
    recovery_cond VARCHAR,
    recovery_prod_wtr VARCHAR,
    recovery_prod_water_edit VARCHAR,
    basis VARCHAR,
    other_rptd_loss_type VARCHAR,
    loss VARCHAR,
    recovery_num VARCHAR,
    affected_area VARCHAR,
    spill_on_water VARCHAR,
    spill_on_water_edit VARCHAR,
    ospra VARCHAR,
    swr_20 VARCHAR,
    swr_98exempt VARCHAR,
    cleanup_criteria_swr_91 VARCHAR,
    cleanup_criteria_7_00_doc VARCHAR,
    cleanup_criteria_case_specific VARCHAR,
    form_h_8rqrd VARCHAR,
    form_h8rqrd_edit VARCHAR,
    date_h_8rcvd VARCHAR,
    date_h8rcvd_edit VARCHAR,
    cleanup_oversight_district VARCHAR,
    cleanup_oversight_austin VARCHAR,
    status_or_phase VARCHAR,
    comments VARCHAR,
    compliance_date VARCHAR,
    isocspill DOUBLE,
    ocinsp DOUBLE,
    ispwspill DOUBLE,
    pwinsp DOUBLE,
    isotherspill DOUBLE,
    otinsp DOUBLE,
    last_inspection_date VARCHAR,
    cleanup_criteria VARCHAR,
    cleanup_oversight VARCHAR,
    notes VARCHAR,
    inspection_id VARCHAR,
    soil_water_samples_required VARCHAR,
    spill_letter_date VARCHAR,
    inspector VARCHAR,
    witn_tech VARCHAR,
    date_witnessed VARCHAR,
    witn_results VARCHAR,
    cleanup_method VARCHAR,
    tph_rcvd VARCHAR,
    tph_comments VARCHAR,
    duplicate VARCHAR
)
WITH 
(
    PARTITIONS = 1,
    VALUE_FORMAT = 'AVRO',
    KAFKA_TOPIC = 'ois_texas_ois_district'
);

-- Input Stream for the texas_ois_central table
CREATE STREAM texas_ois_central_stream (
    id INT KEY,
    dist VARCHAR,
    district_edit VARCHAR,
    date_called_in VARCHAR,
    date_called_in_edit VARCHAR,
    date_of_spill VARCHAR,
    date_of_spill_edit VARCHAR,
    spill_number VARCHAR,
    rrc_job_number VARCHAR,
    operator_rp VARCHAR,
    operator_edit VARCHAR,
    lease_facility_name VARCHAR,
    rrc_id_number VARCHAR,
    county VARCHAR,
    county_edit VARCHAR,
    type_operation VARCHAR,
    source VARCHAR,
    probable_cause VARCHAR,
    probable_cause_edit VARCHAR,
    release_crude_oil VARCHAR,
    release_crude_oil_edit DOUBLE,
    release_cond VARCHAR,
    release_prod_wtr VARCHAR,
    release_prod_water_edit DOUBLE,
    release_gas VARCHAR,
    recovery_crude_oil VARCHAR,
    recovery_crude_oil_edit DOUBLE,
    recovery_cond VARCHAR,
    recovery_prod_wtr VARCHAR,
    recovery_prod_water_edit VARCHAR,
    basis VARCHAR,
    other_rptd_loss_type VARCHAR,
    loss VARCHAR,
    recovery_num DOUBLE,
    affected_area VARCHAR,
    spill_on_water VARCHAR,
    spill_on_water_edit VARCHAR,
    ospra VARCHAR,
    swr_20 VARCHAR,
    swr_98exempt VARCHAR,
    cleanup_criteria_swr_91 VARCHAR,
    cleanup_criteria_7_00_doc VARCHAR,
    cleanup_criteria_case_specific VARCHAR,
    form_h_8rqrd VARCHAR,
    form_h_8rqrd_edit VARCHAR,
    date_h_8rcvd VARCHAR,
    cleanup_oversight_district VARCHAR,
    cleanup_oversight_austin VARCHAR,
    status_or_phase VARCHAR,
    comments VARCHAR,
    compliance_date VARCHAR,
    file_name VARCHAR,
    sheet VARCHAR,
    cleanup_criteria VARCHAR,
    cleanup_oversight VARCHAR,
    rrc_job_number_2 VARCHAR,
    my_of_spill VARCHAR
) 
WITH 
(
    PARTITIONS = 1,
    VALUE_FORMAT = 'AVRO',
    KAFKA_TOPIC = 'ois_texas_ois_central'
);

SHOW TOPICS;
SHOW STREAMS;
DESCRIBE texas_ois_district_stream EXTENDED;
DESCRIBE texas_ois_central_stream EXTENDED;

PRINT ois_texas_ois_central FROM BEGINNING LIMIT 25;
SELECT * FROM texas_ois_central_stream EMIT CHANGES;

PRINT ois_texas_ois_district FROM BEGINNING LIMIT 25;
SELECT * FROM texas_ois_district_stream EMIT CHANGES;

-- CREATE SINK CONNECTOR(s)
--- MariaDB ---
CREATE SINK CONNECTOR IF NOT EXISTS texas_ois_mariadb_sink_conn WITH (
    "name" = 'texas_ois_mariadb_sink_conn',
    "connector.class" = 'io.confluent.connect.jdbc.JdbcSinkConnector',
    "tasks.max" = '2',
    "topics" = 'ois_texas_ois_central,ois_texas_ois_district',
    "connection.url" = 'jdbc:mariadb://mariadb:3306/texas_ois_mariadb_target_db', 
    "connection.user" = 'mariadb_user',
    "connection.password" = 'mariadb_password',
    "auto.create" = 'true'
);

--- MongoDB ---
-- texas_ois_central
CREATE SINK CONNECTOR IF NOT EXISTS central_texas_ois_mongo_sink_conn WITH (
    "name" = 'central_texas_ois_mongo_sink_conn',
    "tasks.max" = '1',
    "topics" = 'ois_texas_ois_central',
    "connector.class" = 'com.mongodb.kafka.connect.MongoSinkConnector',
    "connection.uri" = 'mongodb://mongodb_user:mongodb_password@mongo:27017',
    "database" = 'texas_ois_mongo_target_db',
    "collection" = 'district_texas_ois_mongo_target_collection',
    "key.converter" = 'org.apache.kafka.connect.storage.StringConverter',
    "key.converter.schema.registry.url" = 'http://schema-registry:8081',
    "value.converter" = 'io.confluent.connect.avro.AvroConverter',
    "value.converter.schema.registry.url" = 'http://schema-registry:8081',
    "document.id.strategy" = 'com.mongodb.kafka.connect.sink.processor.id.strategy.BsonOidStrategy',
    "post.processor.chain" = 'com.mongodb.kafka.connect.sink.processor.DocumentIdAdder',
    "delete.on.null.values" = 'false',
    "writemodel.strategy" = 'com.mongodb.kafka.connect.sink.writemodel.strategy.ReplaceOneDefaultStrategy',
    "max.batch.size" = 0,
    "rate.limiting.timeout" = 0,
    "rate.limiting.every.n" = 0
);

-- ois_texas_ois_district table
CREATE SINK CONNECTOR IF NOT EXISTS district_texas_ois_mongo_sink_conn WITH (
    "name" = 'district_texas_ois_mongo_sink_conn',
    "tasks.max" = '1',
    "topics" = 'ois_texas_ois_district',
    "connector.class" = 'com.mongodb.kafka.connect.MongoSinkConnector',
    "connection.uri" = 'mongodb://mongodb_user:mongodb_password@mongo:27017',
    "database" = 'texas_ois_mongo_target_db',
    "collection" = 'central_texas_ois_mongo_target_collection',
    "key.converter" = 'org.apache.kafka.connect.storage.StringConverter',
    "key.converter.schema.registry.url" = 'http://schema-registry:8081',
    "value.converter" = 'io.confluent.connect.avro.AvroConverter',
    "value.converter.schema.registry.url" = 'http://schema-registry:8081',
    "document.id.strategy" = 'com.mongodb.kafka.connect.sink.processor.id.strategy.BsonOidStrategy',
    "post.processor.chain" = 'com.mongodb.kafka.connect.sink.processor.DocumentIdAdder',
    "delete.on.null.values" = 'false',
    "writemodel.strategy" = 'com.mongodb.kafka.connect.sink.writemodel.strategy.ReplaceOneDefaultStrategy',
    "max.batch.size" = 0,
    "rate.limiting.timeout" = 0,
    "rate.limiting.every.n" = 0
);

--- MySQL ---
CREATE SINK CONNECTOR IF NOT EXISTS texas_ois_mysql_sink_conn WITH (
    "name" = 'district_texas_ois_mysql_sink_conn',
    "connector.class" = 'io.confluent.connect.jdbc.JdbcSinkConnector',
    'connection.url' = 'jdbc:mysql://mysql:3306/texas_ois_mysql_target_db',
    'connection.user' = 'mysql',
    'connection.password' = 'mysql',
    "topics" = 'ois_texas_ois_central,ois_texas_ois_district',
    "tasks.max" = '2',
    "auto.create" = 'true',
    "dialect.name" = 'MySqlDatabaseDialect'
);

-- Some Metadata Statements
SHOW CONNECTORS;
SHOW TOPICS;
SHOW STREAMS;

--- DESCRIBE CONNECTOR(s) ---
-- Source Connector(s)
DESCRIBE CONNECTOR TEXAS_OIS_PG_SOURCE_CONN;

-- Sink Connector(s)
DESCRIBE CONNECTOR TEXAS_OIS_MARIADB_SINK_CONN;
DESCRIBE CONNECTOR CENTRAL_TEXAS_OIS_MONGO_SINK_CONN;
DESCRIBE CONNECTOR DISTRICT_TEXAS_OIS_MONGO_SINK_CONN;
DESCRIBE CONNECTOR TEXAS_OIS_MYSQL_SINK_CONN;


-- Go to the bash shell for the docker project for the following commands: 

--- MariaDB ---
-- Number of records in ois_texas_ois_central MariaDB table
docker exec mariadb bash -c "mariadb --user=mariadb_user --password=mariadb_password texas_ois_mariadb_target_db -e 'SELECT COUNT(*) FROM ois_texas_ois_central;'"
-- Show 8 records in ois_texas_ois_central MariaDB table
docker exec mariadb bash -c "mariadb --user=mariadb_user --password=mariadb_password texas_ois_mariadb_target_db -e 'SELECT * FROM ois_texas_ois_central LIMIT 8;'"

-- Number of records in ois_texas_ois_district MariaDB table
docker exec mariadb bash -c "mariadb --user=mariadb_user --password=mariadb_password texas_ois_mariadb_target_db -e 'SELECT COUNT(*) FROM ois_texas_ois_district;'"
-- Show 8 records in ois_texas_ois_district MariaDB table
docker exec mariadb bash -c "mariadb --user=mariadb_user --password=mariadb_password texas_ois_mariadb_target_db -e 'SELECT * FROM ois_texas_ois_district LIMIT 8;'"

--- MongoDB ---
-- Show 8 documents in the district_ois_texas_ois_district MongoDB collection
echo 'db.district_texas_ois_mongo_target_collection.find().limit(8).pretty()' | docker exec -i mongodb mongosh --username mongodb_user --password mongodb_password --authenticationDatabase admin texas_ois_mongo_target_db
-- Return a count of how many records are in the ois_texas_ois_district MongoDB collection
echo 'db.district_texas_ois_mongo_target_collection.countDocuments({})' | docker exec -i mongodb mongosh --username mongodb_user --password mongodb_password --authenticationDatabase admin texas_ois_mongo_target_db

-- Show 8 documents in the central_ois_texas_ois_central MongoDB collection
echo 'db.central_texas_ois_mongo_target_collection.find().limit(8).pretty()' | docker exec -i mongodb mongosh --username mongodb_user --password mongodb_password --authenticationDatabase admin texas_ois_mongo_target_db
-- Return a count of how many records are in the ois_texas_ois_central MongoDB collection
echo 'db.central_texas_ois_mongo_target_collection.countDocuments({})' | docker exec -i mongodb mongosh --username mongodb_user --password mongodb_password --authenticationDatabase admin texas_ois_mongo_target_db

----- MySQL -----
-- ois_texas_ois_central table
-- For selecting data from MySQL
echo 'SELECT * FROM ois_texas_ois_central LIMIT 8;' | docker exec -i mysql mysql -u mysql -pmysql texas_ois_mysql_target_db
-- For counting rows in MySQL
echo 'SELECT COUNT(*) AS Num_Of_Records FROM ois_texas_ois_central;' | docker exec -i mysql mysql -u mysql -pmysql texas_ois_mysql_target_db

--- ois_texas_ois_district table
-- For selecting data from MySQL
echo 'SELECT * FROM ois_texas_ois_district LIMIT 8;' | docker exec -i mysql mysql -u mysql -pmysql texas_ois_mysql_target_db
-- For counting rows in MySQL
echo 'SELECT COUNT(*) AS Num_Of_Records FROM ois_texas_ois_district;' | docker exec -i mysql mysql -u mysql -pmysql texas_ois_mysql_target_db

/*
#docker compose command to develop interactively:

docker exec -it ksqldb-cli ksql http://ksqldb-server:8088
*/


---- Tear Down the project ----
-- Start with removing the SINK CONNECTORs
DROP CONNECTOR TEXAS_OIS_MARIADB_SINK_CONN;
DROP CONNECTOR DISTRICT_TEXAS_OIS_MONGO_SINK_CONN;
DROP CONNECTOR CENTRAL_TEXAS_OIS_MONGO_SINK_CONN;
DROP CONNECTOR TEXAS_OIS_MYSQL_SINK_CONN;

-- Then, remove the STREAMs
DROP STREAM TEXAS_OIS_CENTRAL_STREAM DELETE TOPIC;
DROP STREAM TEXAS_OIS_DISTRICT_STREAM DELETE TOPIC;

-- Finally, drop the SOURCE CONNECTOR
DROP CONNECTOR TEXAS_OIS_PG_SOURCE_CONN;

-- Check that DROP statements worked as expected
SHOW CONNECTORS;
SHOW TOPICS;
SHOW STREAMS;
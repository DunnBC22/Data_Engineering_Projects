/*
Source Database: Postgres
Target Database: MongoDB
*/

-- Return the first 25 records from the Postgres db
echo "SELECT * FROM dataco_scd_table LIMIT 25;" | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

-- Return a count of how many records are in the Postgres db
echo 'SELECT COUNT(*) FROM dataco_scd_table;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

/*
#docker compose command to develop interactively:

docker exec -it ksqldb-cli ksql http://ksqldb-server:8088
*/

-- update the auto.offset.reset setting
SET 'auto.offset.reset' = 'earliest';

CREATE SOURCE CONNECTOR IF NOT EXISTS DataCo_SCD_pg_source_conn WITH (
    "name" = 'DataCo_SCD_pg_source_conn',
    "connector.class" = 'io.confluent.connect.jdbc.JdbcSourceConnector',
    "connection.url" = 'jdbc:postgresql://postgres:5432/dataco_scd_db',
    "connection.user" = 'pg',
    "connection.password" = 'pg',
    "table.whitelist" = 'dataco_scd_table',
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

CREATE STREAM IF NOT EXISTS dataco_scd_table (
    transaction_type VARCHAR,
    actual_days_to_ship INTEGER,
    scheduled_days_to_ship INTEGER,
    benefit_per_order DOUBLE,
    sales_per_customer DOUBLE,
    delivery_status VARCHAR,
    late_delivery_risk INTEGER,
    category_id INTEGER,
    category_name VARCHAR,
    customer_city VARCHAR,
    customer_country VARCHAR,
    customer_email VARCHAR,
    customer_fname VARCHAR,
    customer_id INTEGER,
    customer_lname VARCHAR,
    customer_password VARCHAR,
    customer_segment VARCHAR,
    customer_state VARCHAR,
    customer_street VARCHAR,
    customer_zipcode INTEGER,
    department_id INTEGER,
    department_name VARCHAR,
    latitude DOUBLE,
    longitude DOUBLE,
    market VARCHAR,
    order_city VARCHAR,
    order_country VARCHAR,
    order_customer_id INTEGER,
    order_date VARCHAR,
    order_id INTEGER,
    order_item_cardprod_id INTEGER,
    order_item_discount DOUBLE,
    order_item_discount_rate DOUBLE,
    order_item_id INTEGER,
    order_item_product_price DOUBLE,
    order_item_profit_ratio DOUBLE,
    order_item_quantity INTEGER,
    sales DOUBLE,
    order_item_total DOUBLE,
    order_profit_per_order DOUBLE,
    order_region VARCHAR,
    order_state VARCHAR,
    order_status VARCHAR,
    order_zipcode INTEGER,
    product_card_id INTEGER,
    product_category_id INTEGER,
    product_desc VARCHAR,
    product_image VARCHAR,
    product_name VARCHAR,
    product_price DOUBLE,
    product_status INTEGER,
    shipping_date VARCHAR,
    shipping_mode VARCHAR
)
WITH
(
    partitions=1,
    value_format='AVRO',
    kafka_topic='dataco_scd_table'
);

SHOW CONNECTORS;
SHOW STREAMS;
SHOW TOPICS;
DESCRIBE CONNECTOR DATACO_SCD_PG_SOURCE_CONN;


PRINT dataco_scd_table FROM BEGINNING LIMIT 10;

SELECT * FROM dataco_scd_table EMIT CHANGES;


-- CREATE SINK CONNECTOR(s)
CREATE SINK CONNECTOR IF NOT EXISTS DataCo_SCD_mongo_sink_conn WITH (
    "name" = 'DataCo_SCD_mongo_sink_conn',
    "connector.class" = 'com.mongodb.kafka.connect.MongoSinkConnector',
    "topics" = 'dataco_scd_table',
    "tasks.max"=1,
    "connection.uri" = 'mongodb://mongodb_user:mongodb_password@mongo:27017',
    "database" = 'dataco_scd_db_mongo',
    "collection" = 'dataco_scd_mongo_collection',
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

SHOW CONNECTORS;
SHOW STREAMS;
SHOW TOPICS;
DESCRIBE CONNECTOR DATACO_SCD_MONGO_SINK_CONN;


-- Go to the bash shell for the docker project for the next two commands:
-- Check to make sure that the data made it to MongoDB
echo 'db.dataco_scd_mongo_collection.find().limit(12).pretty()' | docker exec -i mongodb mongosh --username mongodb_user --password mongodb_password --authenticationDatabase admin dataco_scd_db_mongo

-- Return a count of how many records are in the MongoDB
echo 'db.dataco_scd_mongo_collection.countDocuments({})' | docker exec -i mongodb mongosh --username mongodb_user --password mongodb_password --authenticationDatabase admin dataco_scd_db_mongo


/*
#docker compose command to develop interactively:

docker exec -it ksqldb-cli ksql http://ksqldb-server:8088
*/

-- Statements to remove STREAM(s) & CONNECTOR(s)
-- start with the SINK CONNECTOR(s)
DROP CONNECTOR DATACO_SCD_MONGO_SINK_CONN;

-- Next, the input STREAM [& their associated TOPIC]
DROP STREAM DATACO_SCD_TABLE DELETE TOPIC;

-- Finally, the SOURCE CONNECTOR(s)
DROP CONNECTOR DATACO_SCD_PG_SOURCE_CONN;
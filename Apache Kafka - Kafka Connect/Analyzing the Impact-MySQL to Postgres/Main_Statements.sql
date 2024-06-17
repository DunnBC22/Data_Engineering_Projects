-- Make sure that the data is imported into the postgres tables correctly (run this in bash, not the docker CLI)
-- companies table
echo 'SELECT * FROM companies LIMIT 12;' | docker exec -i mysql mysql -u mysql -pmysql impact_analysis
echo 'SELECT COUNT(company_id) FROM companies;' | docker exec -i mysql mysql -u mysql -pmysql impact_analysis

-- economic_data table
echo 'SELECT * FROM economic_data LIMIT 12;' | docker exec -i mysql mysql -u mysql -pmysql impact_analysis
echo 'SELECT COUNT(econ_data_id) FROM economic_data;' | docker exec -i mysql mysql -u mysql -pmysql impact_analysis

-- purchases table
echo 'SELECT * FROM purchases LIMIT 8;' | docker exec -i mysql mysql -u mysql -pmysql impact_analysis
echo 'SELECT COUNT(purchase_id) FROM purchases;' | docker exec -i mysql mysql -u mysql -pmysql impact_analysis

/*
#docker compose command to develop interactively:

docker exec -it ksqldb-cli ksql http://ksqldb-server:8088
*/

-- update the auto.offset.reset setting
SET 'auto.offset.reset' = 'earliest';

-- CREATE SOURCE CONNECTORs
-- Create the companies SOURCE CONNECTOR
CREATE SOURCE CONNECTOR IF NOT EXISTS mysql_companies_table_source_conn WITH (
    'name' = 'source_connector_from_mysql_purchases_to_stream',
    'connector.class' = 'io.confluent.connect.jdbc.JdbcSourceConnector',
    'connection.url' = 'jdbc:mysql://mysql:3306/impact_analysis', 
    'connection.user' = 'mysql',
    'connection.password' = 'mysql',
    'mode' = 'incrementing',
    'topic.prefix' = 'mysql_',
    'table.whitelist' = 'companies',
    'incrementing.column.name' = 'company_id',
    'transforms' = 'copyFieldToKey,extractKeyFromStruct,removeKeyFromValue',
    'transforms.copyFieldToKey.type' = 'org.apache.kafka.connect.transforms.ValueToKey',
    'transforms.copyFieldToKey.fields' = 'company_id',
    'transforms.extractKeyFromStruct.type' = 'org.apache.kafka.connect.transforms.ExtractField$Key',
    'transforms.extractKeyFromStruct.field' = 'company_id',
    'transforms.removeKeyFromValue.type' = 'org.apache.kafka.connect.transforms.ReplaceField$Value',
    'transforms.removeKeyFromValue.blacklist' = 'company_id',
    'key.converter' = 'org.apache.kafka.connect.converters.IntegerConverter'
);

-- Create the economic_data SOURCE CONNECTOR
CREATE SOURCE CONNECTOR IF NOT EXISTS mysql_econ_data_table_source_conn WITH (
    'name' = 'source_connector_from_mysql_econ_data_to_table',
    'connector.class' = 'io.confluent.connect.jdbc.JdbcSourceConnector',
    'dialect.name' = 'MySqlDatabaseDialect',
    'connection.url' = 'jdbc:mysql://mysql:3306/impact_analysis',
    'connection.user' = 'mysql',
    'connection.password' = 'mysql',
    'mode' = 'incrementing',
    'topic.prefix' = 'mysql_',
    'incrementing.column.name' = 'econ_data_id',
    'table.whitelist' = 'economic_data',
    'numeric.mapping' = 'best_fit',
    'transforms' = 'copyFieldToKey,extractKeyFromStruct,removeKeyFromValue',
    'transforms.copyFieldToKey.type' = 'org.apache.kafka.connect.transforms.ValueToKey',
    'transforms.copyFieldToKey.fields' = 'econ_data_id',
    'transforms.extractKeyFromStruct.type' = 'org.apache.kafka.connect.transforms.ExtractField$Key',
    'transforms.extractKeyFromStruct.field' = 'econ_data_id',
    'transforms.removeKeyFromValue.type' = 'org.apache.kafka.connect.transforms.ReplaceField$Value',
    'transforms.removeKeyFromValue.blacklist' = 'econ_data_id',
    'key.converter' = 'org.apache.kafka.connect.converters.IntegerConverter'
);

-- Create the purchases SOURCE CONNECTOR
CREATE SOURCE CONNECTOR IF NOT EXISTS mysql_purchases_stream_source_conn WITH (
    'name' = 'source_connector_from_mysql_purchases_to_stream',
    'connector.class' = 'io.confluent.connect.jdbc.JdbcSourceConnector',
    'connection.url' = 'jdbc:mysql://mysql:3306/impact_analysis',
    'connection.user' = 'mysql',
    'connection.password' = 'mysql',
    'mode' = 'incrementing',
    'topic.prefix' = 'mysql_',
    'incrementing.column.name' = 'purchase_id',
    'timestamp.column.name' = 'purchases_date',
    'timestamp.initial' =2592010,
    'validate.non.null' =true,
    'transforms' = 'copyFieldToKey,extractKeyFromStruct,removeKeyFromValue',
    'transforms.copyFieldToKey.type' = 'org.apache.kafka.connect.transforms.ValueToKey',
    'transforms.copyFieldToKey.fields' = 'purchase_id',
    'transforms.extractKeyFromStruct.type' = 'org.apache.kafka.connect.transforms.ExtractField$Key',
    'transforms.extractKeyFromStruct.field' = 'purchase_id',
    'transforms.removeKeyFromValue.type' = 'org.apache.kafka.connect.transforms.ReplaceField$Value',
    'transforms.removeKeyFromValue.blacklist' = 'purchase_id',
    'key.converter' = 'org.apache.kafka.connect.converters.IntegerConverter',
    'table.whitelist' = 'purchases'
);

SHOW CONNECTORS;

-- create the input STREAMS
CREATE STREAM companies (
    company_id INTEGER KEY,
    company_name VARCHAR,
    company_location VARCHAR,
    company_type VARCHAR,
    employees VARCHAR
) 
WITH 
(
    KAFKA_TOPIC = 'mysql_companies', 
    VALUE_FORMAT = 'AVRO', 
    partitions = 1
);

CREATE STREAM economic_data (
    econ_data_id INTEGER KEY,
    econ_date VARCHAR,
    unemployment_rate DOUBLE,
    gdp_value VARCHAR,
    cpi DOUBLE,
    mortgage_rate_30y DOUBLE
) 
WITH 
(
    KAFKA_TOPIC = 'mysql_economic_data', 
    VALUE_FORMAT = 'AVRO', 
    partitions = 1
);

CREATE STREAM purchases (
    purchase_id INTEGER KEY,
    purchases_date TIMESTAMP,
    company_id INTEGER,
    product_category VARCHAR,
    quantity INTEGER,
    revenue DOUBLE
) 
WITH 
(
    KAFKA_TOPIC = 'mysql_purchases', 
    VALUE_FORMAT = 'AVRO', 
    partitions = 1
);

--all data
CREATE STREAM analyzing_purchases_and_company_data AS 
    SELECT
        p.purchases_date AS Purchase_Date,
        c.company_id AS Company_ID,
        p.product_category AS Product_Category,
        p.quantity AS Quantity,
        p.revenue AS Revenue,
        c.company_name AS Company_Name,
        c.company_location AS Company_Location,
        c.company_type AS Company_Type,
        c.employees AS Number_of_Employees
    FROM 
        purchases p
    LEFT JOIN
        companies c
    WITHIN 
        1 HOURS
    GRACE PERIOD 
        1 HOURS
    ON
        p.company_id=c.company_id
    EMIT CHANGES;

-- all data for the product_category of 'Gaming'
CREATE STREAM analyze_purchases_company_of_gaming_prod_category AS 
    SELECT
        p.purchases_date AS Purchase_Date,
        p.company_id AS Company_ID,
        p.product_category AS Product_Category,
        p.quantity AS Quantity,
        p.revenue AS Revenue,
        c.company_name AS Company_Name,
        c.company_location AS Company_Location,
        c.company_type AS Company_Type,
        c.employees AS Number_of_Employees
    FROM 
        purchases p
    LEFT JOIN
        companies c
    WITHIN 
        1 HOURS
    GRACE PERIOD 
        1 HOURS
    ON
        p.company_id = c.company_id
    WHERE
        p.product_category = 'Gaming'
    EMIT CHANGES;

-- all data for the company_name of 'Johnston and Sons'
CREATE STREAM ANALYZE_PURCHASES_COMPANY_FROM_JOHNSTON_SONS AS 
    SELECT
        p.purchases_date AS Purchase_Date,
        p.company_id AS Company_ID,
        p.product_category AS Product_Category,
        p.quantity AS Quantity,
        p.revenue AS Revenue,
        c.company_name AS Company_Name,
        c.company_location AS Company_Location,
        c.company_type AS Company_Type,
        c.employees AS Number_of_Employees
    FROM 
        purchases p
    LEFT JOIN
        companies c
    WITHIN 
        1 HOURS
    GRACE PERIOD 
        1 HOURS
    ON
        p.company_id=c.company_id
    WHERE
        c.company_name = 'Johnston and Sons'
    EMIT CHANGES;

-- all data for 'public' company_types
CREATE STREAM analyze_purchases_company_of_public_companies AS 
    SELECT
        p.purchases_date AS Purchase_Date,
        p.company_id AS Company_ID,
        p.product_category AS Product_Category,
        p.quantity AS Quantity,
        p.revenue AS Revenue,
        c.company_name AS Company_Name,
        c.company_location AS Company_Location,
        c.company_type AS Company_Type,
        c.employees AS Number_of_Employees
    FROM 
        purchases p
    LEFT JOIN
        companies c
    WITHIN 
        1 HOURS
    GRACE PERIOD 
        1 HOURS
    ON
        p.company_id=c.company_id
    WHERE
        c.company_type = 'public'
    EMIT CHANGES;

-- Create SINK CONNECTOR(s)
CREATE SINK CONNECTOR IF NOT EXISTS pg_analyze_impact_companies_stream_sink_conn WITH (
  'name'                = 'pg_analyze_impact_companies_stream_sink_conn',
  'connector.class'     = 'io.confluent.connect.jdbc.JdbcSinkConnector',
  'connection.url'      = 'jdbc:postgresql://postgres:5432/impact_analysis_target',
  'connection.user'     = 'pg',
  'connection.password' = 'pg',
  'output.data.format'  = 'avro',
  'topics'              = 'mysql_companies',
  'auto.create'         = 'true',
  'auto.evolve'         = 'true',
  'table.name.format'   = 'pg_${topic}'
);

CREATE SINK CONNECTOR IF NOT EXISTS pg_analyze_impact_economic_data_stream_sink_conn WITH (
  'name'                = 'pg_analyze_impact_economic_data_stream_sink_conn',
  'connector.class'     = 'io.confluent.connect.jdbc.JdbcSinkConnector',
  'connection.url'      = 'jdbc:postgresql://postgres:5432/impact_analysis_target',
  'connection.user'     = 'pg',
  'connection.password' = 'pg',
  'output.data.format'  = 'avro',
  'topics'              = 'mysql_economic_data',
  'auto.create'         = 'true',
  'auto.evolve'         = 'true',
  'table.name.format'   = 'pg_${topic}'
);

CREATE SINK CONNECTOR IF NOT EXISTS pg_analyze_impact_purchases_stream_sink_conn WITH (
  'name'                = 'pg_analyze_impact_purchases_stream_sink_conn',
  'connector.class'     = 'io.confluent.connect.jdbc.JdbcSinkConnector',
  'connection.url'      = 'jdbc:postgresql://postgres:5432/impact_analysis_target',
  'connection.user'     = 'pg',
  'connection.password' = 'pg',
  'output.data.format'  = 'avro',
  'topics'              = 'mysql_purchases',
  'auto.create'         = 'true',
  'auto.evolve'         = 'true',
  'table.name.format'   = 'pg_${topic}'
);

CREATE SINK CONNECTOR IF NOT EXISTS pg_analyze_impact_purchases_co_data_stream_sink_conn WITH (
  'name'                = 'pg_analyze_impact_purchases_co_data_stream_sink_conn',
  'connector.class'     = 'io.confluent.connect.jdbc.JdbcSinkConnector',
  'connection.url'      = 'jdbc:postgresql://postgres:5432/impact_analysis_target',
  'connection.user'     = 'pg',
  'connection.password' = 'pg',
  'output.data.format'  = 'avro',
  'topics'              = 'ANALYZING_PURCHASES_AND_COMPANY_DATA',
  'auto.create'         = 'true',
  'auto.evolve'         = 'true',
  'table.name.format'   = 'pg_${topic}'
);

CREATE SINK CONNECTOR IF NOT EXISTS pg_analyze_impact_pur_co_from_johnson_sons_stream_sink_conn WITH (
  'name'                = 'pg_analyze_impact_pur_co_from_johnson_sons_stream_sink_conn',
  'connector.class'     = 'io.confluent.connect.jdbc.JdbcSinkConnector',
  'connection.url'      = 'jdbc:postgresql://postgres:5432/impact_analysis_target',
  'connection.user'     = 'pg',
  'connection.password' = 'pg',
  'output.data.format'  = 'avro',
  'topics'              = 'ANALYZE_PURCHASES_COMPANY_FROM_JOHNSTON_SONS',
  'auto.create'         = 'true',
  'auto.evolve'         = 'true',
  'table.name.format'   = 'pg_${topic}'
);

CREATE SINK CONNECTOR IF NOT EXISTS pg_analyze_impact_pur_co_gaming_prod_cat_stream_sink_conn WITH (
  'name'                = 'pg_analyze_impact_pur_co_gaming_prod_cat_stream_sink_conn',
  'connector.class'     = 'io.confluent.connect.jdbc.JdbcSinkConnector',
  'connection.url'      = 'jdbc:postgresql://postgres:5432/impact_analysis_target',
  'connection.user'     = 'pg',
  'connection.password' = 'pg',
  'output.data.format'  = 'avro',
  'topics'              = 'ANALYZE_PURCHASES_COMPANY_OF_GAMING_PROD_CATEGORY',
  'auto.create'         = 'true',
  'auto.evolve'         = 'true',
  'table.name.format'   = 'pg_${topic}'
);

CREATE SINK CONNECTOR IF NOT EXISTS pg_analyze_impact_public_companies_stream_sink_conn WITH (
  'name'                = 'pg_analyze_impact_public_companies_stream_sink_conn',
  'connector.class'     = 'io.confluent.connect.jdbc.JdbcSinkConnector',
  'connection.url'      = 'jdbc:postgresql://postgres:5432/impact_analysis_target',
  'connection.user'     = 'pg',
  'connection.password' = 'pg',
  'output.data.format'  = 'avro',
  'topics'              = 'ANALYZE_PURCHASES_COMPANY_OF_PUBLIC_COMPANIES',
  'auto.create'         = 'true',
  'auto.evolve'         = 'true',
  'table.name.format'   = 'pg_${topic}'
);

SHOW TOPICS;
SHOW STREAMS;
SHOW CONNECTORS;

-- DESCRIBE components (streams, tables, and connectors)
-- source connectors
DESCRIBE CONNECTOR mysql_companies_table_source_conn;
DESCRIBE CONNECTOR mysql_econ_data_table_source_conn;
DESCRIBE CONNECTOR mysql_purchases_stream_source_conn;

-- streams & tables
DESCRIBE companies EXTENDED;
DESCRIBE economic_data EXTENDED;
DESCRIBE purchases EXTENDED;
DESCRIBE ANALYZING_PURCHASES_AND_COMPANY_DATA EXTENDED;
DESCRIBE ANALYZE_PURCHASES_COMPANY_OF_GAMING_PROD_CATEGORY EXTENDED;
DESCRIBE ANALYZE_PURCHASES_COMPANY_FROM_JOHNSTON_SONS EXTENDED;
DESCRIBE ANALYZE_PURCHASES_COMPANY_OF_PUBLIC_COMPANIES EXTENDED;

SELECT * FROM ANALYZING_PURCHASES_AND_COMPANY_DATA LIMIT 12;
SELECT * FROM ANALYZE_PURCHASES_COMPANY_OF_GAMING_PROD_CATEGORY LIMIT 12;
SELECT * FROM ANALYZE_PURCHASES_COMPANY_FROM_JOHNSTON_SONS LIMIT 12;
SELECT * FROM ANALYZE_PURCHASES_COMPANY_OF_PUBLIC_COMPANIES LIMIT 12;

-- Run these scripts to make sure that the data successfully made its way to the target database
-- companies
echo 'SELECT * FROM "pg_mysql_companies" LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER impact_analysis_target'
echo 'SELECT COUNT(company_name) FROM "pg_mysql_companies";' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER impact_analysis_target'

-- economic_data
echo 'SELECT * FROM "pg_mysql_economic_data" LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER impact_analysis_target'
echo 'SELECT COUNT(econ_date) FROM "pg_mysql_economic_data";' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER impact_analysis_target'

-- purchases
echo 'SELECT * FROM pg_mysql_purchases LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER impact_analysis_target'
echo 'SELECT COUNT(purchases_date) FROM "pg_mysql_purchases";' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER impact_analysis_target'

-- analyzing_purchases_and_company_data
echo 'SELECT * FROM "pg_ANALYZING_PURCHASES_AND_COMPANY_DATA" LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER impact_analysis_target'
echo 'SELECT COUNT("PURCHASE_DATE") FROM "pg_ANALYZING_PURCHASES_AND_COMPANY_DATA";' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER impact_analysis_target'

-- analyze_purchases_company_of_gaming_prod_category
echo 'SELECT * FROM "pg_ANALYZE_PURCHASES_COMPANY_OF_GAMING_PROD_CATEGORY" LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER impact_analysis_target'
echo 'SELECT COUNT("PURCHASE_DATE") FROM "pg_ANALYZE_PURCHASES_COMPANY_OF_GAMING_PROD_CATEGORY";' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER impact_analysis_target'

-- analyze_purchases_company_of_public_companies
echo 'SELECT * FROM "pg_ANALYZE_PURCHASES_COMPANY_OF_PUBLIC_COMPANIES" LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER impact_analysis_target'
echo 'SELECT COUNT("PURCHASE_DATE") FROM "pg_ANALYZE_PURCHASES_COMPANY_OF_PUBLIC_COMPANIES";' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER impact_analysis_target'

-- analyze_purchases_company_from_johnston_sons
echo 'SELECT * FROM "pg_ANALYZE_PURCHASES_COMPANY_FROM_JOHNSTON_SONS" LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER impact_analysis_target'
echo 'SELECT COUNT("PURCHASE_DATE") FROM "pg_ANALYZE_PURCHASES_COMPANY_FROM_JOHNSTON_SONS";' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER impact_analysis_target'

/*
#docker compose command to develop interactively:

docker exec -it ksqldb-cli ksql http://ksqldb-server:8088
*/

-- sink connectors
DESCRIBE CONNECTOR pg_analyze_impact_companies_stream_sink_conn;
DESCRIBE CONNECTOR pg_analyze_impact_economic_data_stream_sink_conn;
DESCRIBE CONNECTOR pg_analyze_impact_purchases_stream_sink_conn;
DESCRIBE CONNECTOR pg_analyze_impact_purchases_co_data_stream_sink_conn;
DESCRIBE CONNECTOR pg_analyze_impact_public_companies_stream_sink_conn;
DESCRIBE CONNECTOR pg_analyze_impact_pur_co_gaming_prod_cat_stream_sink_conn;
DESCRIBE CONNECTOR pg_analyze_impact_pur_co_from_johnson_sons_stream_sink_conn;

-- DROP statements
DROP CONNECTOR mysql_PURCHASES_STREAM_SOURCE_CONN;
DROP CONNECTOR mysql_ECON_DATA_TABLE_SOURCE_CONN;
DROP CONNECTOR mysql_COMPANIES_TABLE_SOURCE_CONN;

DROP CONNECTOR pg_ANALYZE_IMPACT_PUR_CO_GAMING_PROD_CAT_STREAM_SINK_CONN;
DROP CONNECTOR pg_ANALYZE_IMPACT_PURCHASES_STREAM_SINK_CONN;
DROP CONNECTOR pg_ANALYZE_IMPACT_PUR_CO_FROM_JOHNSON_SONS_STREAM_SINK_CONN;
DROP CONNECTOR pg_ANALYZE_IMPACT_PUBLIC_COMPANIES_STREAM_SINK_CONN;
DROP CONNECTOR pg_ANALYZE_IMPACT_COMPANIES_STREAM_SINK_CONN;
DROP CONNECTOR pg_ANALYZE_IMPACT_ECONOMIC_DATA_STREAM_SINK_CONN;
DROP CONNECTOR pg_ANALYZE_IMPACT_PURCHASES_CO_DATA_STREAM_SINK_CONN;

DROP STREAM ANALYZING_PURCHASES_AND_COMPANY_DATA DELETE TOPIC;
DROP STREAM ANALYZE_PURCHASES_COMPANY_OF_GAMING_PROD_CATEGORY DELETE TOPIC;
DROP STREAM ANALYZE_PURCHASES_COMPANY_FROM_JOHNSTON_SONS DELETE TOPIC;
DROP STREAM ANALYZE_PURCHASES_COMPANY_OF_PUBLIC_COMPANIES DELETE TOPIC;
DROP STREAM companies DELETE TOPIC;
DROP STREAM economic_data DELETE TOPIC;
DROP STREAM purchases DELETE TOPIC;
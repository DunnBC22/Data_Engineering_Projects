-- Make sure that the data is imported into the postgres tables correctly (run this in bash, not the docker CLI)
echo 'SELECT * FROM account LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(id) FROM account;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

echo 'SELECT * FROM customer LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(id) FROM customer;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

echo 'SELECT * FROM financials LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(id) FROM financials;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

echo 'SELECT * FROM household LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(id) FROM household;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

echo 'SELECT * FROM marketing LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(id) FROM marketing;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

/*
#docker compose command to develop interactively:

docker exec -it ksqldb-cli ksql http://ksqldb-server:8088
*/

-- update the auto.offset.reset setting
SET 'auto.offset.reset' = 'earliest';

-- Create SOURCE CONNECTOR for all db tables
CREATE SOURCE CONNECTOR IF NOT EXISTS pg_account_stream_source_conn WITH (
    'name' = 'source_connector_from_pg_account',
    'connector.class' = 'io.confluent.connect.jdbc.JdbcSourceConnector',
    'connection.url' = 'jdbc:postgresql://postgres:5432/mock_marketing_data',
    'connection.user' = 'pg',
    'connection.password' = 'pg',
    'mode' = 'incrementing',
    'topic.prefix' = 'pg_',
    'incrementing.column.name' = 'id',
    'validate.non.null' = true,
    'table.whitelist' = 'account',
    'transforms'= 'copyFieldToKey,extractKeyFromStruct,removeKeyFromValue',
    'transforms.copyFieldToKey.type'= 'org.apache.kafka.connect.transforms.ValueToKey',
    'transforms.copyFieldToKey.fields'= 'id',
    'transforms.extractKeyFromStruct.type'= 'org.apache.kafka.connect.transforms.ExtractField$Key',
    'transforms.extractKeyFromStruct.field'= 'id',
    'transforms.removeKeyFromValue.type'= 'org.apache.kafka.connect.transforms.ReplaceField$Value',
    'transforms.removeKeyFromValue.blacklist'= 'id',
    'key.converter' = 'org.apache.kafka.connect.converters.IntegerConverter'
);

CREATE SOURCE CONNECTOR IF NOT EXISTS pg_customer_stream_source_conn WITH (
    'name' = 'source_connector_from_pg_customer',
    'connector.class' = 'io.confluent.connect.jdbc.JdbcSourceConnector',
    'connection.url' = 'jdbc:postgresql://postgres:5432/mock_marketing_data',
    'connection.user' = 'pg',
    'connection.password' = 'pg',
    'mode' = 'incrementing',
    'topic.prefix' = 'pg_',
    'incrementing.column.name' = 'id',
    'validate.non.null' = true,
    'table.whitelist' = 'customer',
    'transforms'= 'copyFieldToKey,extractKeyFromStruct,removeKeyFromValue',
    'transforms.copyFieldToKey.type'= 'org.apache.kafka.connect.transforms.ValueToKey',
    'transforms.copyFieldToKey.fields'= 'id',
    'transforms.extractKeyFromStruct.type'= 'org.apache.kafka.connect.transforms.ExtractField$Key',
    'transforms.extractKeyFromStruct.field'= 'id',
    'transforms.removeKeyFromValue.type'= 'org.apache.kafka.connect.transforms.ReplaceField$Value',
    'transforms.removeKeyFromValue.blacklist'= 'id',
    'key.converter' = 'org.apache.kafka.connect.converters.IntegerConverter'
);

CREATE SOURCE CONNECTOR IF NOT EXISTS pg_financials_stream_source_conn WITH (
    'name' = 'source_connector_from_pg_financials',
    'connector.class' = 'io.confluent.connect.jdbc.JdbcSourceConnector',
    'connection.url' = 'jdbc:postgresql://postgres:5432/mock_marketing_data',
    'connection.user' = 'pg',
    'connection.password' = 'pg',
    'mode' = 'incrementing',
    'topic.prefix' = 'pg_',
    'incrementing.column.name' = 'id',
    'validate.non.null' = true,
    'table.whitelist' = 'financials',
    'transforms'= 'copyFieldToKey,extractKeyFromStruct,removeKeyFromValue',
    'transforms.copyFieldToKey.type'= 'org.apache.kafka.connect.transforms.ValueToKey',
    'transforms.copyFieldToKey.fields'= 'id',
    'transforms.extractKeyFromStruct.type'= 'org.apache.kafka.connect.transforms.ExtractField$Key',
    'transforms.extractKeyFromStruct.field'= 'id',
    'transforms.removeKeyFromValue.type'= 'org.apache.kafka.connect.transforms.ReplaceField$Value',
    'transforms.removeKeyFromValue.blacklist'= 'id',
    'key.converter' = 'org.apache.kafka.connect.converters.IntegerConverter'
);


CREATE SOURCE CONNECTOR IF NOT EXISTS pg_household_stream_source_conn WITH (
    'name' = 'source_connector_from_pg_household',
    'connector.class' = 'io.confluent.connect.jdbc.JdbcSourceConnector',
    'connection.url' = 'jdbc:postgresql://postgres:5432/mock_marketing_data',
    'connection.user' = 'pg',
    'connection.password' = 'pg',
    'mode' = 'incrementing',
    'topic.prefix' = 'pg_',
    'incrementing.column.name' = 'id',
    'validate.non.null' = true,
    'table.whitelist' = 'household',
    'transforms'= 'copyFieldToKey,extractKeyFromStruct,removeKeyFromValue',
    'transforms.copyFieldToKey.type'= 'org.apache.kafka.connect.transforms.ValueToKey',
    'transforms.copyFieldToKey.fields'= 'id',
    'transforms.extractKeyFromStruct.type'= 'org.apache.kafka.connect.transforms.ExtractField$Key',
    'transforms.extractKeyFromStruct.field'= 'id',
    'transforms.removeKeyFromValue.type'= 'org.apache.kafka.connect.transforms.ReplaceField$Value',
    'transforms.removeKeyFromValue.blacklist'= 'id',
    'key.converter' = 'org.apache.kafka.connect.converters.IntegerConverter'
);

CREATE SOURCE CONNECTOR IF NOT EXISTS pg_marketing_stream_source_conn WITH (
    'name' = 'source_connector_from_pg_marketing',
    'connector.class' = 'io.confluent.connect.jdbc.JdbcSourceConnector',
    'connection.url' = 'jdbc:postgresql://postgres:5432/mock_marketing_data',
    'connection.user' = 'pg',
    'connection.password' = 'pg',
    'mode' = 'incrementing',
    'topic.prefix' = 'pg_',
    'incrementing.column.name' = 'id',
    'validate.non.null' = true,
    'table.whitelist' = 'marketing',
    'transforms'= 'copyFieldToKey,extractKeyFromStruct,removeKeyFromValue',
    'transforms.copyFieldToKey.type'= 'org.apache.kafka.connect.transforms.ValueToKey',
    'transforms.copyFieldToKey.fields'= 'id',
    'transforms.extractKeyFromStruct.type'= 'org.apache.kafka.connect.transforms.ExtractField$Key',
    'transforms.extractKeyFromStruct.field'= 'id',
    'transforms.removeKeyFromValue.type'= 'org.apache.kafka.connect.transforms.ReplaceField$Value',
    'transforms.removeKeyFromValue.blacklist'= 'id',
    'key.converter' = 'org.apache.kafka.connect.converters.IntegerConverter'
);

-- Define input STREAMs
CREATE STREAM account (id INTEGER KEY) WITH (KAFKA_TOPIC='pg_account', VALUE_FORMAT='AVRO');
CREATE STREAM customer (id VARCHAR KEY) WITH (KAFKA_TOPIC='pg_customer', VALUE_FORMAT='AVRO');
CREATE STREAM financials (id VARCHAR KEY) WITH (KAFKA_TOPIC='pg_financials', VALUE_FORMAT='AVRO');
CREATE STREAM household (id VARCHAR KEY) WITH (KAFKA_TOPIC='pg_household', VALUE_FORMAT='AVRO');
CREATE STREAM marketing (id VARCHAR KEY) WITH (KAFKA_TOPIC='pg_marketing', VALUE_FORMAT='AVRO');


-- Define intermediate STREAM(s) &/or TABLE(s)
--all data
CREATE STREAM STREAM_ALL_MOCK_MARKETING_SCHEMA_DATA AS 
    SELECT
        a.cust_id AS Customer_ID,
        a.acquisition_cost AS Acquisition_Cost,
        a.internet_banking_indicator AS Internet_Banking_Indicator,
        a.date_first_account_opened AS Date_First_Account_Opened,
        a.date_last_account_opened AS Date_Last_Account_Opened,
        a.pursuit AS Pursuit,
        a.primary_advisor_organization_id AS Primary_Advisor_Organization_Id,
        a.primary_branch_proximity AS Primary_Branch_Proximity,
        a.primary_spoken_language AS Primary_Spoken_Language,
        a.primary_written_language AS Primary_Written_Language,
        a.satisfaction_rating_from_survey AS Satisfaction_rating_from_survey,
        a.secondary_advisor_id AS Secondary_Advisor_Id,
        a.secondary_advisor_organization_id AS Secondary_Advisor_Organization_Id,
        a.special_te AS Special_Terms_Indicator,
        c.gender AS Gender,
        c.first_name AS First_Name,
        c.last_name AS Last_Name,
        c.email AS Email_Address,
        c.ssn AS Social_Security_Number,
        c.age_range AS Age_Range, 
        c.annual_income AS Annual_Income,
        c.birth_year AS Birth_Year,
        c.current_employment_start_date AS Current_Employment_Start_Date,
        c.customer_behavior AS Customer_Behavior,
        c.education_level AS Education_Level,
        c.employment_status AS Employment_Status,
        c.marital_status AS Marital_Status,
        c.monthly_net_income AS Monthly_Net_Income,
        c.profession AS Profession,
        c.retirement_age AS Retirement_Age,
        c.customer_status AS Customer_Status,
        c.wallet_share_percentage AS Wallet_Share_Percentage,
        f.monthly_housing_cost AS Monthly_Housing_Cost,
        f.contact_preference AS Contact_Preference,
        f.credit_authority_level AS Credit_Authority_Level,
        f.credit_score AS Credit_Score,
        f.credit_utilization AS Credit_Utilization,
        f.debt_service_coverage_ratio AS Debt_Service_Coverage_Ratio,
        h.household_address AS Household_Address,
        h.household_city AS Household_City,
        h.household_country AS Household_Country,
        h.household_state AS Household_State,
        h.household_zip_code AS Household_Zip_Code,
        h.address_last_changed_date AS Address_Last_Changed_Date,
        h.number_of_dependent_adults AS Number_Of_Dependent_Adults,
        h.number_of_dependent_children AS Number_Of_Dependent_Children,
        h.family_size AS Family_Size,
        h.head_of_household_indicator AS Head_Of_Household_Indicator,
        h.home_owner_indicator AS Home_Owner_Indicator,
        h.urban_code AS Urban_Code,
        h.primary_advisor_id AS Primary_Advisor_Id,
        m.advertising_indicator AS Advertising_Indicator,
        m.attachment_allowed_indicator AS Attachment_Allowed_Indicator,
        m.preferred_communication_form AS Preferred_Communication_Form,
        m.importance_level_code AS Importance_Level_code,
        m.influence_score AS Influence_Score,
        m.market_group AS Market_Group,
        m.loyalty_rating_code AS Loyalty_Rating_Code,
        m.recorded_voice_sample_id AS Recorded_Voice_Sample_Id,
        m.referrals_value_code AS Referrals_Value_Code,
        m.relationship_start_date AS Relationship_Start_Date
    FROM
        account a
    LEFT JOIN
        customer c
    WITHIN
        10 HOURS
    ON
        a.cust_id=c.cust_id
    LEFT JOIN
        financials f
    WITHIN
        10 HOURS
    ON
        a.cust_id=f.cust_id
    LEFT JOIN
        household h
    WITHIN
        10 HOURS
    ON
        a.cust_id=h.cust_id
    LEFT JOIN
        marketing m
    WITHIN
        10 HOURS
    ON 
        a.cust_id=m.cust_id
    EMIT CHANGES;

-- basic data (or condensed version of the dataset)
CREATE STREAM STREAM_BASIC_MARKETING_SCHEMA_DATA AS 
    SELECT
        a.cust_id AS Customer_ID,
        a.acquisition_cost AS Acquisition_Cost,
        a.internet_banking_indicator AS Internet_Banking_Indicator,
        a.date_first_account_opened AS Date_First_Account_Opened,
        a.date_last_account_opened AS Date_Last_Account_Opened,
        a.pursuit AS Pursuit,
        a.primary_advisor_organization_id AS Primary_Advisor_Organization_Id,
        a.primary_branch_proximity AS Primary_Branch_Proximity,
        a.primary_spoken_language AS Primary_Spoken_Language,
        a.primary_written_language AS Primary_Written_Language,
        a.satisfaction_rating_from_survey AS Satisfaction_rating_from_survey,
        a.secondary_advisor_id AS Secondary_Advisor_Id,
        a.secondary_advisor_organization_id AS Secondary_Advisor_Organization_Id,
        a.special_te AS Special_Terms_Indicator,
        c.gender AS Gender,
        c.first_name AS First_Name,
        c.last_name AS Last_Name,
        c.email AS Email_Address,
        c.ssn AS Social_Security_Number,
        c.age_range AS Age_Range, 
        c.annual_income AS Annual_Income,
        c.birth_year AS Birth_Year,
        c.current_employment_start_date AS Current_Employment_Start_Date,
        c.customer_behavior AS Customer_Behavior,
        c.education_level AS Education_Level,
        c.employment_status AS Employment_Status,
        c.marital_status AS Marital_Status,
        c.monthly_net_income AS Monthly_Net_Income,
        c.profession AS Profession,
        c.retirement_age AS Retirement_Age,
        c.customer_status AS Customer_Status,
        c.wallet_share_percentage AS Wallet_Share_Percentage,
        f.monthly_housing_cost AS Monthly_Housing_Cost,
        f.contact_preference AS Contact_Preference,
        f.credit_authority_level AS Credit_Authority_Level,
        f.credit_score AS Credit_Score
    FROM
        account a
    LEFT JOIN
        customer c
    WITHIN
        10 HOURS
    ON
        a.cust_id=c.cust_id
    LEFT JOIN
        financials f
    WITHIN
        10 HOURS
    ON
        a.cust_id=f.cust_id
    EMIT CHANGES;

-- retirement_planning_marketing_data
CREATE STREAM RETIREMENT_PLANNING_MARKETING_DATA AS 
    SELECT
        c.cust_id AS Customer_ID,
        c.first_name AS First_Name,
        c.last_name AS Last_Name,
        c.gender AS Gender,
        c.email AS Email_Address,
        c.birth_year AS Birth_Year,
        c.profession AS Profession,
        c.monthly_net_income AS Monthly_Net_Income,
        c.education_level AS Education_Level,
        c.employment_status AS Employment_Status,
        c.marital_status AS Marital_Status,
        c.age_range AS Age_Range,
        a.acquisition_cost AS Acquisition_Cost,
        a.internet_banking_indicator AS Internet_Banking_Indicator,
        a.primary_advisor_organization_id AS Primary_Advisor_Organization_Id,
        a.primary_branch_proximity AS Primary_Branch_Proximity,
        a.satisfaction_rating_from_survey AS Satisfaction_rating_from_survey,
        a.special_te AS Special_Terms_Indicator,
        c.current_employment_start_date AS Current_Employment_Start_Date,
        c.customer_behavior AS Customer_Behavior,
        c.retirement_age AS Retirement_Age,
        c.customer_status AS Customer_Status,
        c.wallet_share_percentage AS Wallet_Share_Percentage,
        f.monthly_housing_cost AS Monthly_Housing_Cost,
        f.contact_preference AS Contact_Preference,
        f.credit_authority_level AS Credit_Authority_Level,
        f.credit_score AS Credit_Score,
        f.credit_utilization AS Credit_Utilization,
        f.debt_service_coverage_ratio AS Debt_Service_Coverage_Ratio,
        h.household_address AS Household_Address,
        h.household_city AS Household_City,
        h.household_country AS Household_Country,
        h.household_state AS Household_State,
        h.household_zip_code AS Household_Zip_Code,
        h.number_of_dependent_adults AS Number_Of_Dependent_Adults,
        h.number_of_dependent_children AS Number_Of_Dependent_Children,
        h.family_size AS Family_Size,
        h.head_of_household_indicator AS Head_Of_Household_Indicator,
        h.home_owner_indicator AS Home_Owner_Indicator,
        h.urban_code AS Urban_Code,
        m.advertising_indicator AS Advertising_Indicator,
        m.attachment_allowed_indicator AS Attachment_Allowed_Indicator,
        m.preferred_communication_form AS Preferred_Communication_Form,
        m.importance_level_code AS Importance_Level_code,
        m.market_group AS Market_Group
    FROM
        account a
    LEFT JOIN
        customer c
    WITHIN
        10 HOURS
    ON
        a.cust_id=c.cust_id
    LEFT JOIN
        financials f
    WITHIN
        10 HOURS
    ON
        a.cust_id=f.cust_id
    LEFT JOIN
        household h
    WITHIN
        10 HOURS
    ON
        a.cust_id=h.cust_id
    LEFT JOIN
        marketing m
    WITHIN
        10 HOURS
    ON 
        a.cust_id=m.cust_id
    WHERE 
        a.pursuit = 'Retirement Planning'
    EMIT CHANGES;

-- Define SINK CONNECTOR(s)
CREATE SINK CONNECTOR IF NOT EXISTS pg_STREAM_ALL_MOCK_MARKETING_SCHEMA_DATA_sink_conn WITH (
  'name'                = 'pg_STREAM_ALL_MOCK_MARKETING_SCHEMA_DATA_sink_conn',
  'connector.class'     = 'io.confluent.connect.jdbc.JdbcSinkConnector',
  'connection.url'      = 'jdbc:postgresql://postgres:5432/output_mock_marketing_data',
  'connection.user'     = 'pg',
  'connection.password' = 'pg',
  'output.data.format'  = 'AVRO',
  'topics'              = 'STREAM_ALL_MOCK_MARKETING_SCHEMA_DATA',
  'auto.create'         = 'true',
  'auto.evolve'         = 'true',
  'table.name.format'   = 'output_${topic}'
);

CREATE SINK CONNECTOR IF NOT EXISTS pg_STREAM_BASIC_MARKETING_SCHEMA_DATA_sink_conn WITH (
  'name'                = 'pg_STREAM_BASIC_MARKETING_SCHEMA_DATA_sink_conn',
  'connector.class'     = 'io.confluent.connect.jdbc.JdbcSinkConnector',
  'connection.url'      = 'jdbc:postgresql://postgres:5432/output_mock_marketing_data',
  'connection.user'     = 'pg',
  'connection.password' = 'pg',
  'output.data.format'  = 'AVRO',
  'topics'              = 'STREAM_BASIC_MARKETING_SCHEMA_DATA',
  'auto.create'         = 'true',
  'auto.evolve'         = 'true',
  'table.name.format'   = 'output_${topic}'
);

CREATE SINK CONNECTOR IF NOT EXISTS pg_RETIREMENT_PLANNING_MARKETING_DATA_sink_conn WITH (
  'name'                = 'pg_RETIREMENT_PLANNING_MARKETING_DATA_sink_conn',
  'connector.class'     = 'io.confluent.connect.jdbc.JdbcSinkConnector',
  'connection.url'      = 'jdbc:postgresql://postgres:5432/output_mock_marketing_data',
  'connection.user'     = 'pg',
  'connection.password' = 'pg',
  'output.data.format'  = 'AVRO',
  'topics'              = 'RETIREMENT_PLANNING_MARKETING_DATA',
  'auto.create'         = 'true',
  'auto.evolve'         = 'true',
  'table.name.format'   = 'output_${topic}'
);

-- other statements to run
SHOW TOPICS;
SHOW STREAMS;
SHOW CONNECTORS;
SHOW TABLES;
SHOW PROPERTIES;
SHOW QUERIES;

-- Run these echo commands in normal shell to make sure that everything works as expected
echo 'SELECT * FROM "output_RETIREMENT_PLANNING_MARKETING_DATA" LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_mock_marketing_data'
echo 'SELECT COUNT("LAST_NAME") FROM "output_RETIREMENT_PLANNING_MARKETING_DATA";' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_mock_marketing_data'

echo 'SELECT * FROM "output_STREAM_ALL_MOCK_MARKETING_SCHEMA_DATA" LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_mock_marketing_data'
echo 'SELECT COUNT("LAST_NAME") FROM "output_STREAM_ALL_MOCK_MARKETING_SCHEMA_DATA";' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_mock_marketing_data'

echo 'SELECT * FROM "output_STREAM_BASIC_MARKETING_SCHEMA_DATA" LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_mock_marketing_data'
echo 'SELECT COUNT("PURSUIT") FROM "output_STREAM_BASIC_MARKETING_SCHEMA_DATA";' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_mock_marketing_data'


-- DESCRIBE components (streams, tables, and connectors)
-- DESCRIBE source connectors
DESCRIBE CONNECTOR pg_account_stream_source_conn;
DESCRIBE CONNECTOR pg_customer_stream_source_conn;
DESCRIBE CONNECTOR pg_financials_stream_source_conn;
DESCRIBE CONNECTOR pg_household_stream_source_conn;
DESCRIBE CONNECTOR pg_marketing_stream_source_conn;

-- DESCRIBE sink connectors
DESCRIBE CONNECTOR pg_STREAM_ALL_MOCK_MARKETING_SCHEMA_DATA_sink_conn;
DESCRIBE CONNECTOR pg_mock_marketing_schema_histograms_sink_conn;
DESCRIBE CONNECTOR pg_RETIREMENT_PLANNING_MARKETING_DATA_sink_conn;

-- DESCRIBE streams & tables (EXTENDED)
DESCRIBE account EXTENDED;
DESCRIBE customer EXTENDED;
DESCRIBE financials EXTENDED;
DESCRIBE household EXTENDED;
DESCRIBE marketing EXTENDED;

DESCRIBE STREAM_ALL_MOCK_MARKETING_SCHEMA_DATA EXTENDED;
DESCRIBE mock_marketing_schema_histograms EXTENDED;
DESCRIBE RETIREMENT_PLANNING_MARKETING_DATA EXTENDED;
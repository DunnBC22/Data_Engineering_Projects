-- Create STREAMs & TABLEs
CREATE TABLE companies (
    company_id INTEGER PRIMARY KEY,
    company_name VARCHAR,
    company_location VARCHAR,
    company_type VARCHAR,
    employees VARCHAR
)
WITH 
(
    kafka_topic='companies',
    value_format='json',
    partitions=4
);


CREATE TABLE economic_data (
    econ_data_id INTEGER PRIMARY KEY,
    econ_date VARCHAR,
    unemployment_rate DOUBLE,
    gdp_value VARCHAR,
    cpi DOUBLE,
    mortgage_rate_30y DOUBLE
)
WITH 
(
    kafka_topic='economic_data',
    value_format='json',
    partitions=4
);


CREATE STREAM purchases (
    purchase_id INTEGER KEY,
    purchases_date VARCHAR,
    company_id INTEGER,
    product_category VARCHAR,
    quantity INTEGER,
    revenue DOUBLE
)
WITH 
(
    kafka_topic='purchases',
    value_format='json',
    partitions=4
);
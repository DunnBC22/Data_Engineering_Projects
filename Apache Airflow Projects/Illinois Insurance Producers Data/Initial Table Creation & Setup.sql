-- database name: iipd_db
-- owner: airflow

CREATE TABLE iipd (
    id INTEGER,
    index_id INTEGER,
    LAST_NAME_OR_BUSINESS_NAME VARCHAR,
    FIRST_NAME VARCHAR,
    MLG_ADDRESS1 VARCHAR,
    MLG_ADDRESS2 VARCHAR,
    MAILING_CITY VARCHAR,
    MAILING_STATE VARCHAR,
    ZIP VARCHAR,
    LOA_NAME VARCHAR
);

COPY iipd(
    id,
    index_id,
    LAST_NAME_OR_BUSINESS_NAME,
    FIRST_NAME,
    MLG_ADDRESS1,
    MLG_ADDRESS2,
    MAILING_CITY,
    MAILING_STATE,
    ZIP,
    LOA_NAME
    )
FROM '/Users/briandunn/Desktop/Projects/Illinois Insurance Producers Data/doi-insurance-producers-1.csv'
DELIMITER ','
CSV HEADER;
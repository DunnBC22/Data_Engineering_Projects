\c ecomm_logs_db_pg;

CREATE TABLE ecomm_logs_table_pg (
    accessed_date VARCHAR,
    duration_secs INTEGER,
    network_protocol VARCHAR,
    ip VARCHAR,
    bytes INTEGER,
    accessed_from VARCHAR,
    age VARCHAR,
    gender VARCHAR,
    country VARCHAR,
    membership VARCHAR,
    language_in_log VARCHAR,
    sales FLOAT,
    returned VARCHAR,
    returned_amount FLOAT,
    pay_method VARCHAR
);


COPY ecomm_logs_table_pg (
    accessed_date,
    duration_secs,
    network_protocol,
    ip,
    bytes,
    accessed_from,
    age,
    gender,
    country,
    membership,
    language_in_log,
    sales,
    returned,
    returned_amount,
    pay_method
)
FROM '/docker-entrypoint-initdb.d/data.csv'
DELIMITER ','
CSV HEADER;
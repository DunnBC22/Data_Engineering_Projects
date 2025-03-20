GRANT SELECT ON ecomm_data_analysis_db_mysql.* TO 'mysql'@'%';
FLUSH PRIVILEGES;

USE ecomm_data_analysis_db_mysql;

-- drop tables, if exists, to start from scratch
DROP TABLE IF EXISTS fact_table_mysql;
DROP TABLE IF EXISTS customer_dim_table_mysql;
DROP TABLE IF EXISTS item_dim_table_mysql;
DROP TABLE IF EXISTS store_dim_table_mysql;
DROP TABLE IF EXISTS time_dim_table_mysql;
DROP TABLE IF EXISTS transaction_dim_table_mysql;


-- Fact Table
CREATE TABLE fact_table_mysql (
	payment_key VARCHAR(6),
    customer_key VARCHAR(10),
    time_key VARCHAR(10),
    item_key VARCHAR(9),
    store_key VARCHAR(9),
    quantity INTEGER,
    unit VARCHAR(12),
    unit_price FLOAT,
    total_price FLOAT
);


-- Customer Dimension Table
CREATE TABLE customer_dim_table_mysql (
	customer_key VARCHAR(10),
    customer_name VARCHAR(60),
    contact_no BIGINT,
    nid BIGINT
);


-- Item Dimension Table
CREATE TABLE item_dim_table_mysql (
	item_key VARCHAR(9),
    item_name VARCHAR(50),
    item_desc VARCHAR(36),
    unit_price FLOAT,
    man_country VARCHAR(18),
    supplier VARCHAR(36),
    unit VARCHAR(12)
);


-- Store Dimension Table
CREATE TABLE store_dim_table_mysql (
	store_key VARCHAR(9),
    division VARCHAR(16),
    district VARCHAR(24),
    upazila VARCHAR(16)
);


-- create time dimension table
CREATE TABLE time_dim_table_mysql (
    time_key VARCHAR(10),
    trans_date VARCHAR(20),
    trans_hour INTEGER,
    trans_day INTEGER,
    trans_week VARCHAR(10),
    trans_month INTEGER,
    trans_quarter VARCHAR(4),
    trans_year INTEGER
);


-- Transaction Dimension Table
CREATE TABLE transaction_dim_table_mysql (
	payment_key VARCHAR(6),
    trans_type VARCHAR(10),
    bank_name VARCHAR(60)
);
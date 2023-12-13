-- database name: diff_store_sales_db
-- owner: airflow

CREATE TABLE diff_store_sales (
    invoice_no VARCHAR,
    invoice_date TIMESTAMP,
    customer_id VARCHAR,
    gender VARCHAR,
    age INTEGER,
    category VARCHAR,
    quantity INTEGER,
    selling_price_per_unit FLOAT,
    cost_price_per_unit FLOAT,
    payment_method VARCHAR,
    region VARCHAR,
    state_name VARCHAR,
    shopping_mall VARCHAR
);

COPY diff_store_sales(
    invoice_no,
    invoice_date,
    customer_id,
    gender,
    age,
    category,
    quantity,
    selling_price_per_unit,
    cost_price_per_unit,
    payment_method,
    region,
    state_name,
    shopping_mall 
    )
FROM '/Users/briandunn/Desktop/Projects 2/Different Store Sales/Different_stores_dataset.csv'
DELIMITER ','
CSV HEADER;
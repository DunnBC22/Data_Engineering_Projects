\c beverage_sales_pg_db;

GRANT ALL PRIVILEGES ON DATABASE beverage_sales_pg_db TO pg;

CREATE TABLE IF NOT EXISTS beverage_sales_pg_table (
    order_id VARCHAR(15),
    customer_id VARCHAR(12),
    customer_type VARCHAR(6),
    product VARCHAR(25),
    category VARCHAR(25),
    unit_price FLOAT,
    quantity INTEGER,
    discount FLOAT,
    total_price FLOAT,
    region VARCHAR(28),
    order_date VARCHAR(15)
);
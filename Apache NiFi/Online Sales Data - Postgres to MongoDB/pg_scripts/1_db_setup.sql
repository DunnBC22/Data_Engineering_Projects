\c online_sales_data_db_pg;

-- Orders Table
CREATE TABLE orders_table_pg (
	order_id VARCHAR(7) PRIMARY KEY,
    order_date VARCHAR(10),
    customer_name VARCHAR(15),
    state_name VARCHAR(20),
    city_name VARCHAR(20)
);

COPY orders_table_pg (
	order_id,
    order_date,
    customer_name,
    state_name,
    city_name
)
FROM '/docker-entrypoint-initdb.d/Orders.csv'
DELIMITER ','
CSV HEADER;

-- Details Table
CREATE TABLE details_table_pg (
	order_id VARCHAR(7),
    amount INTEGER,
    profit INTEGER,
    quantity INTEGER,
    category VARCHAR(14),
    sub_category VARCHAR(20),
    payment_mode VARCHAR(14),
    FOREIGN KEY (order_id) REFERENCES orders_table_pg(order_id)
);

COPY details_table_pg (
	order_id,
    amount,
    profit,
    quantity,
    category,
    sub_category,
    payment_mode
)
FROM '/docker-entrypoint-initdb.d/Details.csv'
DELIMITER ','
CSV HEADER;
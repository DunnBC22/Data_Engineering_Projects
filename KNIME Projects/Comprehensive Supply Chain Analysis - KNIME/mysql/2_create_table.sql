USE csca_mysql_db;

-- Create csca_mysql_table table
DROP TABLE IF EXISTS csca_mysql_table;
CREATE TABLE csca_mysql_table (
    order_number VARCHAR(15),
    sales_channel VARCHAR(15),
    warehouse_code VARCHAR(15),
    procured_date VARCHAR(12),
    order_date VARCHAR(12),
    ship_date VARCHAR(12),
    delivery_date VARCHAR(12),
    currency_code VARCHAR(5),
    sales_team_id INT,
    customer_id INT,
    store_id INT,
    product_id INT,
    order_quantity INT,
    discount_applied FLOAT,
    unit_cost VARCHAR(12),
    unit_price VARCHAR(12)
);

-- Grant SELECT permission to mysql
GRANT SELECT ON csca_mysql_table TO 'mysql'@'%';
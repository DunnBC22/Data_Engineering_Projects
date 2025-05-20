USE brazilian_ecomm_public_dataset_mysql_db;

-- Create customers_bepd_mysql_table table
DROP TABLE IF EXISTS customers_bepd_mysql_table;
CREATE TABLE customers_bepd_mysql_table (
    customer_id VARCHAR(36),
    customer_unique_id VARCHAR(36),
    customer_zip_code_prefix VARCHAR(6),
    customer_city VARCHAR(36),
    customer_state VARCHAR(4)
);

-- Grant SELECT permission to mysql
GRANT SELECT, UPDATE, INSERT ON customers_bepd_mysql_table TO 'mysql'@'%';
FLUSH PRIVILEGES;

-- Create geolocation_bepd_mysql_table table
DROP TABLE IF EXISTS geolocation_bepd_mysql_table;
CREATE TABLE geolocation_bepd_mysql_table (
    geolocation_zip_code_prefix VARCHAR(6),
    geolocation_lat DOUBLE,
    geolocation_lng DOUBLE,
    geolocation_city VARCHAR(45),
    geolocation_state VARCHAR(4)
);

-- Grant SELECT permission to mysql
GRANT SELECT, UPDATE, INSERT ON geolocation_bepd_mysql_table TO 'mysql'@'%';
FLUSH PRIVILEGES;

-- Create order_items_bepd_mysql_table table
DROP TABLE IF EXISTS order_items_bepd_mysql_table;
CREATE TABLE order_items_bepd_mysql_table (
    order_id VARCHAR(36),
    order_item_id INTEGER,
    product_id VARCHAR(36),
    seller_id VARCHAR(36),
    shipping_limit_date VARCHAR(24),
    price FLOAT,
    freight_value FLOAT
);

-- Grant SELECT permission to mysql
GRANT SELECT, UPDATE, INSERT ON order_items_bepd_mysql_table TO 'mysql'@'%';
FLUSH PRIVILEGES;


-- Create order_payments_bepd_mysql_table table
DROP TABLE IF EXISTS order_payments_bepd_mysql_table;
CREATE TABLE order_payments_bepd_mysql_table (
    order_id VARCHAR(36),
    payment_sequential INTEGER,
    payment_type VARCHAR(15),
    payment_installments INTEGER,
    payment_value FLOAT
);

-- Grant SELECT permission to mysql
GRANT SELECT, UPDATE, INSERT ON order_payments_bepd_mysql_table TO 'mysql'@'%';
FLUSH PRIVILEGES;


-- Create order_reviews_bepd_mysql_table table
DROP TABLE IF EXISTS order_reviews_bepd_mysql_table;
CREATE TABLE order_reviews_bepd_mysql_table (
    review_id VARCHAR(36),
    order_id VARCHAR(36),
    review_score INTEGER,
    review_comment_title VARCHAR(32),
    review_comment_message VARCHAR(225),
    review_creation_date VARCHAR(24),
    review_answer_timestamp VARCHAR(24)
);

-- Grant SELECT permission to mysql
GRANT SELECT, UPDATE, INSERT ON order_reviews_bepd_mysql_table TO 'mysql'@'%';
FLUSH PRIVILEGES;


-- Create orders_bepd_mysql_table table
DROP TABLE IF EXISTS orders_bepd_mysql_table;
CREATE TABLE orders_bepd_mysql_table (
    order_id VARCHAR(36),
    customer_id VARCHAR(36),
    order_status VARCHAR(15),
    order_purchase_timestamp VARCHAR(24),
    order_approved_at VARCHAR(24),
    order_delivered_carrier_date VARCHAR(24),
    order_delivered_customer_date VARCHAR(24),
    order_estimated_delivery_date VARCHAR(24)
);

-- Grant SELECT permission to mysql
GRANT SELECT, UPDATE, INSERT ON orders_bepd_mysql_table TO 'mysql'@'%';
FLUSH PRIVILEGES;


-- Create product_category_bepd_mysql_table table
DROP TABLE IF EXISTS product_category_bepd_mysql_table;
CREATE TABLE product_category_bepd_mysql_table (
    product_category_name VARCHAR(50),
    product_category_name_english VARCHAR(50)
);

-- Grant SELECT permission to mysql
GRANT SELECT, UPDATE, INSERT ON product_category_bepd_mysql_table TO 'mysql'@'%';
FLUSH PRIVILEGES;


-- Create products_bepd_mysql_table table
DROP TABLE IF EXISTS products_bepd_mysql_table;
CREATE TABLE products_bepd_mysql_table (
    product_id VARCHAR(36),
    product_category_name VARCHAR(60),
    product_name_lenght INTEGER,
    product_description_lenght INTEGER,
    product_photos_qty INTEGER,
    product_weight_g INTEGER,
    product_length_cm INTEGER,
    product_height_cm INTEGER,
    product_width_cm INTEGER 
);

-- Grant SELECT permission to mysql
GRANT SELECT, UPDATE, INSERT ON products_bepd_mysql_table TO 'mysql'@'%';
FLUSH PRIVILEGES;



-- Create sellers_bepd_mysql_table table
DROP TABLE IF EXISTS sellers_bepd_mysql_table;
CREATE TABLE sellers_bepd_mysql_table (
    seller_id VARCHAR(36),
    seller_zip_code_prefix VARCHAR(8),
    seller_city VARCHAR(50),
    seller_state VARCHAR(4)
);

-- Grant SELECT permission to mysql
GRANT SELECT, UPDATE, INSERT ON sellers_bepd_mysql_table TO 'mysql'@'%';
FLUSH PRIVILEGES;
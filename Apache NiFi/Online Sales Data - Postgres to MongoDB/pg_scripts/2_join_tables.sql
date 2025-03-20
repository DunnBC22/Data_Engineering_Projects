\c online_sales_data_db_pg;

CREATE TABLE online_sales_data_table_pg AS
    SELECT 
        o.order_id AS order_id,
        o.order_date AS order_date,
        o.customer_name AS customer_name,
        o.state_name AS state_name,
        o.city_name AS city_name,
        d.amount AS amount,
        d.profit AS profit,
        d.quantity AS quantity,
        d.category AS category,
        d.sub_category AS sub_category,
        d.payment_mode AS payment_mode
    FROM orders_table_pg o
    JOIN details_table_pg d 
    ON o.order_id = d.order_id;
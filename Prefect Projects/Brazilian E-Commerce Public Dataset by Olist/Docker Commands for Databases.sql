
/* MySQL */
-- customers_bepd_mysql_table table
echo 'SELECT * FROM customers_bepd_mysql_table LIMIT 12;' | docker exec -i mysql mysql -u mysql -pmysql brazilian_ecomm_public_dataset_mysql_db
echo 'SELECT COUNT(*) FROM customers_bepd_mysql_table;' | docker exec -i mysql mysql -u mysql -pmysql brazilian_ecomm_public_dataset_mysql_db

-- geolocation_bepd_mysql_table table
echo 'SELECT * FROM geolocation_bepd_mysql_table LIMIT 12;' | docker exec -i mysql mysql -u mysql -pmysql brazilian_ecomm_public_dataset_mysql_db
echo 'SELECT COUNT(*) FROM geolocation_bepd_mysql_table;' | docker exec -i mysql mysql -u mysql -pmysql brazilian_ecomm_public_dataset_mysql_db

-- order_items_bepd_mysql_table table
echo 'SELECT * FROM order_items_bepd_mysql_table LIMIT 12;' | docker exec -i mysql mysql -u mysql -pmysql brazilian_ecomm_public_dataset_mysql_db
echo 'SELECT COUNT(*) FROM order_items_bepd_mysql_table;' | docker exec -i mysql mysql -u mysql -pmysql brazilian_ecomm_public_dataset_mysql_db

-- order_payments_bepd_mysql_table table
echo 'SELECT * FROM order_payments_bepd_mysql_table LIMIT 12;' | docker exec -i mysql mysql -u mysql -pmysql brazilian_ecomm_public_dataset_mysql_db
echo 'SELECT COUNT(*) FROM order_payments_bepd_mysql_table;' | docker exec -i mysql mysql -u mysql -pmysql brazilian_ecomm_public_dataset_mysql_db

-- order_reviews_bepd_mysql_table table
echo 'SELECT * FROM order_reviews_bepd_mysql_table LIMIT 12;' | docker exec -i mysql mysql -u mysql -pmysql brazilian_ecomm_public_dataset_mysql_db
echo 'SELECT COUNT(*) FROM order_reviews_bepd_mysql_table;' | docker exec -i mysql mysql -u mysql -pmysql brazilian_ecomm_public_dataset_mysql_db

-- orders_bepd_mysql_table table
echo 'SELECT * FROM orders_bepd_mysql_table LIMIT 12;' | docker exec -i mysql mysql -u mysql -pmysql brazilian_ecomm_public_dataset_mysql_db
echo 'SELECT COUNT(*) FROM orders_bepd_mysql_table;' | docker exec -i mysql mysql -u mysql -pmysql brazilian_ecomm_public_dataset_mysql_db

-- product_category_bepd_mysql_table table
echo 'SELECT * FROM product_category_bepd_mysql_table LIMIT 12;' | docker exec -i mysql mysql -u mysql -pmysql brazilian_ecomm_public_dataset_mysql_db
echo 'SELECT COUNT(*) FROM product_category_bepd_mysql_table;' | docker exec -i mysql mysql -u mysql -pmysql brazilian_ecomm_public_dataset_mysql_db

-- products_bepd_mysql_table table
echo 'SELECT * FROM products_bepd_mysql_table LIMIT 12;' | docker exec -i mysql mysql -u mysql -pmysql brazilian_ecomm_public_dataset_mysql_db
echo 'SELECT COUNT(*) FROM products_bepd_mysql_table;' | docker exec -i mysql mysql -u mysql -pmysql brazilian_ecomm_public_dataset_mysql_db

-- sellers_bepd_mysql_table table
echo 'SELECT * FROM sellers_bepd_mysql_table LIMIT 12;' | docker exec -i mysql mysql -u mysql -pmysql brazilian_ecomm_public_dataset_mysql_db
echo 'SELECT COUNT(*) FROM sellers_bepd_mysql_table;' | docker exec -i mysql mysql -u mysql -pmysql brazilian_ecomm_public_dataset_mysql_db


/* Postgres */

-- *** For each table, there is a statement to return:
-- * 12 records from the table 
-- * the count of how many records are in the table

-- geo_bepd_pg_table table in Postgres
echo 'SELECT * FROM geo_bepd_pg_table LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(*) FROM geo_bepd_pg_table;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

-- main_bepd_pg_table table in Postgres
echo 'SELECT * FROM main_bepd_pg_table LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(*) FROM main_bepd_pg_table;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

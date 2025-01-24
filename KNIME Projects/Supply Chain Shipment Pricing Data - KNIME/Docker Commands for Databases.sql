-- Make sure that the data is imported into the Postgres table(s) correctly (run this in terminal)
-- sc_ship_prices_table table in Postgres
echo 'SELECT * FROM sc_ship_prices_table LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(managed_by) FROM sc_ship_prices_table;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

-- Make sure that the data is exported into the MySQL table(s) correctly (run this in terminal)
-- scsp_mysql table
echo 'SELECT * FROM scsp_mysql LIMIT 12;' | docker exec -i mysql mysql -u mysql -pmysql sc_shipping_prices_mysql
echo 'SELECT COUNT(*) FROM scsp_mysql;' | docker exec -i mysql mysql -u mysql -pmysql sc_shipping_prices_mysql
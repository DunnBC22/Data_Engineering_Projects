-- Make sure that the data is exported into the Postgres table(s) correctly (run this in terminal)
-- beverage_sales_pg_table table in Postgres
echo 'SELECT * FROM "public"."beverage_sales_pg_table" LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(*) FROM "public"."beverage_sales_pg_table";' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

-- Make sure that the data is exported into the MySQL table(s) correctly (run this in terminal)
-- beverage_sales_mysql_table table
echo 'SELECT * FROM beverage_sales_mysql_table LIMIT 12;' | docker exec -i mysql mysql -u mysql -pmysql beverage_sales_mysql_db
echo 'SELECT COUNT(*) FROM beverage_sales_mysql_table;' | docker exec -i mysql mysql -u mysql -pmysql beverage_sales_mysql_db
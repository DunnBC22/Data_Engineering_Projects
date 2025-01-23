-- Make sure that the data is imported into the Postgres table(s) correctly (run this in terminal)
-- lccd_pg_table table in Postgres
echo 'SELECT * FROM lccd_pg_table LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(managed_by) FROM lccd_pg_table;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

-- Make sure that the data is exported into the MySQL table(s) correctly (run this in terminal)
-- lccd_mysql_table table
echo 'SELECT * FROM lccd_mysql_table LIMIT 12;' | docker exec -i mysql mysql -u mysql -pmysql lccd_mysql_db
echo 'SELECT COUNT(*) FROM lccd_mysql_table;' | docker exec -i mysql mysql -u mysql -pmysql lccd_mysql_db
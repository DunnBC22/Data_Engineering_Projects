/* Postgres */
-- ha_risk_pg_table table in Postgres
echo 'SELECT * FROM ha_risk_pg_table LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT("Age") FROM ha_risk_pg_table;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'



/* MySQL */

--- Return the first 12 records from the 'ha_risk_mysql_table' table
echo 'SELECT * FROM ha_risk_mysql_table LIMIT 12;' | docker exec -i mysql mysql -u mysql -pmysql ha_risk_mysql_db

--- Return a count of how many records are in the 'ha_risk_mysql_table' table
echo 'SELECT COUNT(*) FROM ha_risk_mysql_table;' | docker exec -i mysql mysql -u mysql -pmysql ha_risk_mysql_db

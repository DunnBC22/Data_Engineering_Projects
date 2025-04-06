

/* MySQL */
-- Return 12 random records from 'csca_mysql_table' table
echo 'SELECT * FROM csca_mysql_table LIMIT 12;' | docker exec -i mysql mysql -u mysql -pmysql csca_mysql_db

-- Return number of records in 'csca_mysql_table' table
echo 'SELECT COUNT(*) FROM csca_mysql_table;' | docker exec -i mysql mysql -u mysql -pmysql csca_mysql_db



/* Postgres */

-- Return 12 random records from 'csca_pg_table' table
echo 'SELECT * FROM csca_pg_table LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'


-- Return number of records from 'csca_pg_table' table
echo 'SELECT COUNT(*) FROM csca_pg_table;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
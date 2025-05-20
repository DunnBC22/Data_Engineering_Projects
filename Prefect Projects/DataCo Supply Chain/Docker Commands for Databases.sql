


/* Postgres */

-- dataco_sc_pg_table table in Postgres
echo 'SELECT * FROM public.dataco_sc_pg_table LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT("transaction_type") FROM dataco_sc_pg_table;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'



/* MariaDB */

-- Return 12 random samples from dataco_sc_mariadb_table
docker exec -i mariadb mariadb -u mariadb_user -pmariadb_pass dataco_sc_mariadb_db -e "SELECT * FROM dataco_sc_mariadb_table LIMIT 12;"

-- Return a count of the number of records in dataco_sc_mariadb_table
docker exec -i mariadb mariadb -u mariadb_user -pmariadb_pass dataco_sc_mariadb_db -e "SELECT COUNT(*) FROM dataco_sc_mariadb_table;"
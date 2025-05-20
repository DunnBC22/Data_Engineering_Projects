

/* MariaDB */

--- Return the first 12 records from the 'gcrd_mariadb_table' table
docker exec -i mariadb mariadb -u mariadb_user -pmariadb_pass gcrd_mariadb_db -e "SELECT * FROM gcrd_mariadb_table LIMIT 12;"

--- Return a count of how many records are in the 'gcrd_mariadb_table' table
docker exec -i mariadb mariadb -u mariadb_user -pmariadb_pass gcrd_mariadb_db -e "SELECT COUNT(*) FROM gcrd_mariadb_table;"


/* PostGIS */

--- Return the first 12 records from the 'gcrd_table_pg' table
echo "SELECT * FROM public.gcrd_table_pg LIMIT 12;" | docker exec -i postgis bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

--- Return a count of how many records are in the 'gcrd_table_pg' table
echo 'SELECT COUNT(*) FROM public.gcrd_table_pg;' | docker exec -i postgis bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
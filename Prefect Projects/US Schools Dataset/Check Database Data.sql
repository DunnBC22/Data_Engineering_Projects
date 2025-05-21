/* 
Code to check & make sure data is in database tables as expected
*/

/* MySQL */

-- public schools table
--- Return the first 12 records from the 'us_schools_geo_mysql_table_public' table
echo 'SELECT * FROM us_schools_geo_mysql_table_public LIMIT 12;' | docker exec -i mysql mysql -u mysql -pmysql us_schools_geo_mysql_db

--- Return a count of how many records are in the 'us_schools_geo_mysql_table_public' table
echo 'SELECT COUNT(*) FROM us_schools_geo_mysql_table_public;' | docker exec -i mysql mysql -u mysql -pmysql us_schools_geo_mysql_db

-- private schools table
--- Return the first 12 records from the 'us_schools_geo_mysql_table_private' table
echo 'SELECT * FROM us_schools_geo_mysql_table_private LIMIT 12;' | docker exec -i mysql mysql -u mysql -pmysql us_schools_geo_mysql_db

--- Return a count of how many records are in the 'us_schools_geo_mysql_table_private' table
echo 'SELECT COUNT(*) FROM us_schools_geo_mysql_table_private;' | docker exec -i mysql mysql -u mysql -pmysql us_schools_geo_mysql_db


/* Postgres */

--- Return the first 12 records from the 'us_schools_geo_table_pg' table
echo "SELECT * FROM public.us_schools_geo_table_pg LIMIT 12;" | docker exec -i postgis bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

--- Return a count of how many records are in the 'us_schools_geo_table_pg' table
echo 'SELECT COUNT(*) FROM public.us_schools_geo_table_pg;' | docker exec -i postgis bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
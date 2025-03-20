/* 
Code to check & make sure data is in database tables as expected
*/

/* postgres */
--- Return the first 12 records from the 'ctcpd_table_pg'
echo "SELECT * FROM public.ctcpd_table_pg LIMIT 12;" | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

--- Return a count of how many records are in the 'ctcpd_table_pg'
echo 'SELECT COUNT(*) FROM public.ctcpd_table_pg;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'


/* MySQL */
--- Return the first 12 records from the 'ctcpd_table_mysql'
echo "SELECT * FROM ctcpd_table_mysql LIMIT 12;" | docker exec -i mysql bash -c 'mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE'

--- Return a count of how many records are in the 'ctcpd_table_mysql'
echo 'SELECT COUNT(*) FROM ctcpd_table_mysql;' | docker exec -i mysql bash -c 'mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE'
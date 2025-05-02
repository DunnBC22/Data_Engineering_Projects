/* 
Code to check & make sure data is in database tables as expected
*/


/* MySQL */
--- Return the first 12 records from the 'rhmcd20_table_mysql'
echo "SELECT * FROM rhmcd20_table_mysql LIMIT 12;" | docker exec -i mysql bash -c 'mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE'

--- Return a count of how many records are in the 'rhmcd20_table_mysql'
echo 'SELECT COUNT(*) FROM rhmcd20_table_mysql;' | docker exec -i mysql bash -c 'mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE'



/* Apache Cassandra */
--- Return the first 12 records from the 'rhmcd20_table_cassandra'
echo "SELECT * FROM rhmcd20_keyspace_cassandra.rhmcd20_table_cassandra LIMIT 12;" | docker exec -i cassandra bash -c 'cqlsh -e "SELECT * FROM rhmcd20_keyspace_cassandra.rhmcd20_table_cassandra LIMIT 12;"'

--- Return a count of how many records are in the 'rhmcd20_table_cassandra'
echo 'SELECT COUNT(*) FROM rhmcd20_keyspace_cassandra.rhmcd20_table_cassandra;' | docker exec -i cassandra bash -c 'cqlsh -e "SELECT COUNT(*) FROM rhmcd20_keyspace_cassandra.rhmcd20_table_cassandra;"'

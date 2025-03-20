/* 
Code to check & make sure data is in database tables as expected
*/


/* MySQL */

/* --- Fact Table --- */

--- Return the first 12 records from the 'fact_table_mysql'
echo "SELECT * FROM fact_table_mysql LIMIT 12;" | docker exec -i mysql bash -c 'mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE'

--- Return a count of how many records are in the 'fact_table_mysql'
echo 'SELECT COUNT(*) FROM fact_table_mysql;' | docker exec -i mysql bash -c 'mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE'

/* --- Customer Dimension --- */

--- Return the first 12 records from the 'customer_dim_table_mysql'
echo "SELECT * FROM customer_dim_table_mysql LIMIT 12;" | docker exec -i mysql bash -c 'mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE'

--- Return a count of how many records are in the 'customer_dim_table_mysql'
echo 'SELECT COUNT(*) FROM customer_dim_table_mysql;' | docker exec -i mysql bash -c 'mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE'

/* --- Item Dimension --- */

--- Return the first 12 records from the 'item_dim_table_mysql'
echo "SELECT * FROM item_dim_table_mysql LIMIT 12;" | docker exec -i mysql bash -c 'mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE'

--- Return a count of how many records are in the 'item_dim_table_mysql'
echo 'SELECT COUNT(*) FROM item_dim_table_mysql;' | docker exec -i mysql bash -c 'mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE'

/* --- Store Dimension --- */

--- Return the first 12 records from the 'store_dim_table_mysql'
echo "SELECT * FROM store_dim_table_mysql LIMIT 12;" | docker exec -i mysql bash -c 'mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE'

--- Return a count of how many records are in the 'store_dim_table_mysql'
echo 'SELECT COUNT(*) FROM store_dim_table_mysql;' | docker exec -i mysql bash -c 'mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE'

/* --- Time Dimension --- */

--- Return the first 12 records from the 'time_dim_table_mysql'
echo "SELECT * FROM time_dim_table_mysql LIMIT 12;" | docker exec -i mysql bash -c 'mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE'

--- Return a count of how many records are in the 'time_dim_table_mysql'
echo 'SELECT COUNT(*) FROM time_dim_table_mysql;' | docker exec -i mysql bash -c 'mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE'

/* --- Transaction Dimension --- */

--- Return the first 12 records from the 'transaction_dim_table_mysql'
echo "SELECT * FROM transaction_dim_table_mysql LIMIT 12;" | docker exec -i mysql bash -c 'mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE'

--- Return a count of how many records are in the 'transaction_dim_table_mysql'
echo 'SELECT COUNT(*) FROM transaction_dim_table_mysql;' | docker exec -i mysql bash -c 'mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE'



/* SFTP Server */


-- Check that file made it to the SFTP server
docker exec -it sftp ls -l /home/nifi_user/upload

------ check the contents of the file(s) ------ 

-- Navigate to the docker container's shell
docker exec -it sftp sh

-- navigate to the folder
cd /home/nifi_user/upload/<table-subdirectory>

-- Lists the files and subdirectories
ls -l

-- Check the file contents:
cat <copy filename to here>
-- OR USE --
less <copy filename to here>
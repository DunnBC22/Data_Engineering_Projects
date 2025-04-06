/* 
Code to check & make sure data is in database tables as expected
*/


/* MongoDB */

--- Return the first 12 documents from the 'ecomm_web_logs_mongo_coll' collection
echo 'db.ecomm_web_logs_mongo_coll.find().limit(12).pretty()' | docker exec -i mongodb bash -c 'mongosh -u $MONGO_INITDB_ROOT_USERNAME -p $MONGO_INITDB_ROOT_PASSWORD --authenticationDatabase admin ecomm_web_logs_mongo_db'

--- Return a count of how many documents are in the 'ecomm_web_logs_mongo_coll' collection
echo 'db.ecomm_web_logs_mongo_coll.countDocuments()' | docker exec -i mongodb bash -c 'mongosh -u $MONGO_INITDB_ROOT_USERNAME -p $MONGO_INITDB_ROOT_PASSWORD --authenticationDatabase admin ecomm_web_logs_mongo_db'


/* MySQL */
--- Return the first 12 records from the 'ecomm_web_logs_mysql_table'
echo "SELECT * FROM ecomm_web_logs_mysql_table LIMIT 12;" | docker exec -i mysql bash -c 'mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE'

--- Return a count of how many records are in the 'ecomm_web_logs_mysql_table'
echo 'SELECT COUNT(*) FROM ecomm_web_logs_mysql_table;' | docker exec -i mysql bash -c 'mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE'
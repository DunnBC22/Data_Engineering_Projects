/* 
Code to check & make sure data is in database tables as expected
*/


/* postgres */
--- Return the first 12 records from the 'ecomm_logs_table_pg'
echo "SELECT * FROM ecomm_logs_table_pg LIMIT 12;" | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

--- Return a count of how many records are in the 'ecomm_logs_table_pg'
echo 'SELECT COUNT(*) FROM ecomm_logs_table_pg;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'


/* MongoDB */
--- Return the first 12 documents from the 'ecomm_logs_coll_mongo' collection
echo 'db.ecomm_logs_coll_mongo.find().limit(12).pretty();' | docker exec -i mongodb bash -c 'mongosh -u $MONGO_INITDB_ROOT_USERNAME -p $MONGO_INITDB_ROOT_PASSWORD --authenticationDatabase admin $MONGO_INITDB_DATABASE'

--- Return a count of how many documents are in the 'ecomm_logs_coll_mongo' collection
echo 'db.ecomm_logs_coll_mongo.countDocuments();' | docker exec -i mongodb bash -c 'mongosh -u $MONGO_INITDB_ROOT_USERNAME -p $MONGO_INITDB_ROOT_PASSWORD --authenticationDatabase admin $MONGO_INITDB_DATABASE'
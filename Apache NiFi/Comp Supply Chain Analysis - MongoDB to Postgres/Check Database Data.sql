/* 
Code to check & make sure data is in database tables as expected
*/

/* MongoDB */
--- Return the first 12 documents from the 'comp_supply_chain_analysis_mongo_coll' collection
echo 'db.comp_supply_chain_analysis_mongo_coll.find().limit(12).pretty()' | docker exec -i mongodb bash -c 'mongosh -u $MONGO_INITDB_ROOT_USERNAME -p $MONGO_INITDB_ROOT_PASSWORD --authenticationDatabase admin comp_supply_chain_analysis_db_mongo'

--- Return a count of how many documents are in the 'comp_supply_chain_analysis_mongo_coll' collection
echo 'db.comp_supply_chain_analysis_mongo_coll.countDocuments()' | docker exec -i mongodb bash -c 'mongosh -u $MONGO_INITDB_ROOT_USERNAME -p $MONGO_INITDB_ROOT_PASSWORD --authenticationDatabase admin comp_supply_chain_analysis_db_mongo'


/* postgres */
--- Return the first 12 records from the 'comp_sc_analysis_table_pg'
echo "SELECT * FROM comp_sc_analysis_table_pg LIMIT 12;" | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

--- Return a count of how many records are in the 'comp_sc_analysis_table_pg'
echo 'SELECT COUNT(*) FROM comp_sc_analysis_table_pg;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
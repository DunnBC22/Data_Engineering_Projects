-- Make sure that the data is imported into the Postgres table(s) correctly (run this in terminal)
-- ha_risk_pg_table table in Postgres
echo 'SELECT * FROM ha_risk_pg_table LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(age) FROM ha_risk_pg_table;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'



-- Make sure that the data is exported into the Mongo collection(s) correctly (run this in terminal)
-- har_mongo_col collection
echo 'db.har_mongo_col.find().limit(12).pretty()' | docker exec -i mongodb mongosh --username mongodb_user --password mongodb_password --authenticationDatabase admin har_db_mongo
echo 'db.har_mongo_col.countDocuments({})' | docker exec -i mongodb mongosh --username mongodb_user --password mongodb_password --authenticationDatabase admin har_db_mongo

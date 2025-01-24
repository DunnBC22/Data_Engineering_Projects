-- Make sure that the data is exported into the MongoDB collection(s) correctly (run this in terminal)
-- top_sci_researchers_mongo_col collection 
echo 'db.top_sci_researchers_mongo_col.find().limit(12).pretty()' | docker exec -i mongodb mongosh --username mongodb_user --password mongodb_password --authenticationDatabase admin top_sci_researchers_db_mongo
echo 'db.top_sci_researchers_mongo_col.countDocuments({})' | docker exec -i mongodb mongosh --username mongodb_user --password mongodb_password --authenticationDatabase admin top_sci_researchers_db_mongo

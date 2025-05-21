/* 
Code to check & make sure data is in database tables as expected
*/

/* MongoDB */

--- Return the first 12 documents from the 'tsr_mongo_coll' collection
echo 'db.tsr_mongo_coll.find().limit(12).pretty()' | docker exec -i mongodb bash -c 'mongosh -u $MONGO_INITDB_ROOT_USERNAME -p $MONGO_INITDB_ROOT_PASSWORD --authenticationDatabase admin tsr_mongo_db'

--- Return a count of how many documents are in the 'tsr_mongo_coll' collection
echo 'db.tsr_mongo_coll.countDocuments()' | docker exec -i mongodb bash -c 'mongosh -u $MONGO_INITDB_ROOT_USERNAME -p $MONGO_INITDB_ROOT_PASSWORD --authenticationDatabase admin tsr_mongo_db'


/* Elasticsearch */

-- return 12 random samples
curl -u elastic:es_prefect_pass -X GET "http://localhost:9200/top_scientists_researchers/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 12,
  "query": {
    "function_score": {
      "query": {
        "match_all": {}
      },
      "random_score": {}
    }
  }
}'

-- Return a count of the number of transactions in elasticsearch
curl -u elastic:es_prefect_pass -X GET "http://localhost:9200/top_scientists_researchers/_count?pretty"
/* 
Code to check & make sure data is in database tables as expected
*/


/* Elasticsearch */

-- Return 12 random samples
curl -u elastic:es_prefect_pass -X GET "http://localhost:9200/flights_data/_search?pretty" -H 'Content-Type: application/json' -d'
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
curl -u elastic:es_prefect_pass -X GET "http://localhost:9200/flights_data/_count?pretty"


/* Postgres */

-- flights_table_pg table
echo 'SELECT * FROM flights_table_pg LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(*) FROM flights_table_pg;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

-- airports_table_pg table
echo 'SELECT * FROM airports_table_pg LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(*) FROM airports_table_pg;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
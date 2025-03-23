/* 
Code to check & make sure data is in database tables as expected
*/


/* Elasticsearch */
-- return 12 random samples
curl -u elastic:es_nifi_pass -X GET "http://localhost:9200/dcsc_transactions/_search?pretty" -H 'Content-Type: application/json' -d'
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

-- Return a count of the number of dcsc_transactions in elasticsearch
curl -u elastic:es_nifi_pass -X GET "http://localhost:9200/dcsc_transactions/_count?pretty"


/* Postgres */
--- Return the first 12 records from the 'dataco_sc_table_pg'
echo "SELECT * FROM dataco_sc_table_pg LIMIT 12;" | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

--- Return a count of how many records are in the 'dataco_sc_table_pg'
echo 'SELECT COUNT(*) FROM dataco_sc_table_pg;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
/* 
Code to check & make sure data is in database tables as expected
*/

/* Postgres */

-- *** For each table, there is a statement to return:
-- * 12 records from the table 
-- * the count of how many records are in the table

-- insur_claim_info_pg_table table in Postgres
echo 'SELECT * FROM insur_claim_info_pg_table LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(*) FROM insur_claim_info_pg_table;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

-- insur_date_data_pg_table table in Postgres
echo 'SELECT * FROM insur_date_data_pg_table LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(*) FROM insur_date_data_pg_table;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

-- insur_result_data_pg_table table in Postgres
echo 'SELECT * FROM insur_result_data_pg_table LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(*) FROM insur_result_data_pg_table;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'


/* Elasticsearch */
-- Return 12 random samples
curl -u elastic:es_prefect_pass -X GET "http://localhost:9200/insurance_disposition_clf/_search?pretty" -H 'Content-Type: application/json' -d'
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
curl -u elastic:es_prefect_pass -X GET "http://localhost:9200/insurance_disposition_clf/_count?pretty"
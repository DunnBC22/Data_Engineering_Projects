/* 
Code to check & make sure data is in database tables as expected
*/

/* Elasticsearch */

-- Return 12 random samples
curl -u elastic:es_prefect_pass -X GET "http://localhost:9200/csca_data/_search?pretty" -H 'Content-Type: application/json' -d'
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
curl -u elastic:es_prefect_pass -X GET "http://localhost:9200/csca_data/_count?pretty"


/* MariaDB */

-- Return 12 random samples from csca_mariadb_table
docker exec -i mariadb mariadb -u mariadb_user -pmariadb_password csca_mariadb_db -e "SELECT * FROM csca_mariadb_table LIMIT 12;"

-- Return a count of the number of records in csca_mariadb_table
docker exec -i mariadb mariadb -u mariadb_user -pmariadb_password csca_mariadb_db -e "SELECT COUNT(*) FROM csca_mariadb_table;"
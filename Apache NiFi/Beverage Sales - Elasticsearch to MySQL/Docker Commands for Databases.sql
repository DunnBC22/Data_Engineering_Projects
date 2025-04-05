/* 
Code to check & make sure data is in database tables as expected
*/


/* Elasticsearch */

-- return 12 random records
curl -u elastic:es_nifi_pass -X GET "http://localhost:9200/beverage_sales_data/_search?pretty" -H 'Content-Type: application/json' -d'
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

-- Return a count of the number of beverage_sales_data in elasticsearch
curl -u elastic:es_nifi_pass -X GET "http://localhost:9200/beverage_sales_data/_count?pretty"


/* Elasticsearch */

-- Return 12 (random) records from beverage_sales_mysql_table table
echo 'SELECT * FROM beverage_sales_mysql_table LIMIT 12;' | docker exec -i mysql mysql -u mysql -pmysql beverage_sales_mysql_db

-- Return a count of the number of beverage_sales_data in MySQL
echo 'SELECT COUNT(*) FROM beverage_sales_mysql_table;' | docker exec -i mysql mysql -u mysql -pmysql beverage_sales_mysql_db
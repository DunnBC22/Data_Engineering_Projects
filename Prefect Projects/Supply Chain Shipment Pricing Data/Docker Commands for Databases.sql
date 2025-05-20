

-- Make sure that the data is exported into the MySQL table(s) correctly (run this in terminal)
-- supply_chain_shipment_pricing_data_table_mysql table
echo 'SELECT * FROM supply_chain_shipment_pricing_data_table_mysql LIMIT 12;' | docker exec -i mysql mysql -u mysql -pmysql supply_chain_shipment_pricing_data_db_mysql
echo 'SELECT COUNT(*) FROM supply_chain_shipment_pricing_data_table_mysql;' | docker exec -i mysql mysql -u mysql -pmysql supply_chain_shipment_pricing_data_db_mysql




/* Elasticsearch */

-- return 12 random samples
curl -u elastic:es_prefect_pass -X GET "http://localhost:9200/supply_chain_shipment_pricing_data/_search?pretty" -H 'Content-Type: application/json' -d'
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
curl -u elastic:es_prefect_pass -X GET "http://localhost:9200/supply_chain_shipment_pricing_data/_count?pretty"
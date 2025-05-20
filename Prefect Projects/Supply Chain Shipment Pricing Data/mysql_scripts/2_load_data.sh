#!/bin/bash
mysql --local-infile=1 -u mysql -p$MYSQL_PASSWORD supply_chain_shipment_pricing_data_db_mysql -e "
LOAD DATA LOCAL INFILE '/data/dataset.csv'
INTO TABLE supply_chain_shipment_pricing_data_table_mysql 
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS;"
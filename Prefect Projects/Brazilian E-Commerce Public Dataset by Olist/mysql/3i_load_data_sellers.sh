#!/bin/bash
mysql --local-infile=1 -u mysql -p$MYSQL_PASSWORD brazilian_ecomm_public_dataset_mysql_db -e "
LOAD DATA LOCAL INFILE '/data/sellers_dataset.csv'
INTO TABLE sellers_bepd_mysql_table
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS;"
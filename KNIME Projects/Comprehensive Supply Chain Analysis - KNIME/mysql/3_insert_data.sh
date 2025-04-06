#!/bin/bash
mysql --local-infile=1 -u mysql -p$MYSQL_PASSWORD --enable-local-infile csca_mysql_db -e "
LOAD DATA LOCAL INFILE '/docker-entrypoint-initdb.d/dataset.csv'
INTO TABLE csca_mysql_table
FIELDS TERMINATED BY ',' 
ENCLOSED BY '\"'
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS;"
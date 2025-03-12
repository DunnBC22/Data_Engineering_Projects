#!/bin/bash
mysql --local-infile=1 -u mysql -p$MYSQL_PASSWORD rhmcd20_db_mysql -e "
LOAD DATA LOCAL INFILE '/docker-entrypoint-initdb.d/data.csv'
INTO TABLE rhmcd20_table_mysql 
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS;"
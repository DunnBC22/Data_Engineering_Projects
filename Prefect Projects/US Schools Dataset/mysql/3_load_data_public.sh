#!/bin/bash
mysql --local-infile=1 -u mysql -p$MYSQL_PASSWORD us_schools_geo_mysql_db -e "
LOAD DATA LOCAL INFILE '/data/Public_Schools.csv'
INTO TABLE us_schools_geo_mysql_table_public 
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS;"
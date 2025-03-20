#!/bin/bash
mysql --local-infile=1 -u mysql -p$MYSQL_PASSWORD ecomm_data_analysis_db_mysql -e "
LOAD DATA LOCAL INFILE '/docker-entrypoint-initdb.d/fact_table.csv'
INTO TABLE fact_table_mysql 
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS;"

mysql --local-infile=1 -u mysql -p$MYSQL_PASSWORD ecomm_data_analysis_db_mysql -e "
LOAD DATA LOCAL INFILE '/docker-entrypoint-initdb.d/customer_dim.csv'
INTO TABLE customer_dim_table_mysql 
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS;"

mysql --local-infile=1 -u mysql -p$MYSQL_PASSWORD ecomm_data_analysis_db_mysql -e "
LOAD DATA LOCAL INFILE '/docker-entrypoint-initdb.d/item_dim.csv'
INTO TABLE item_dim_table_mysql  
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS;"

mysql --local-infile=1 -u mysql -p$MYSQL_PASSWORD ecomm_data_analysis_db_mysql -e "
LOAD DATA LOCAL INFILE '/docker-entrypoint-initdb.d/store_dim.csv'
INTO TABLE store_dim_table_mysql 
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS;"

mysql --local-infile=1 -u mysql -p$MYSQL_PASSWORD ecomm_data_analysis_db_mysql -e "
LOAD DATA LOCAL INFILE '/docker-entrypoint-initdb.d/time_dim.csv'
INTO TABLE time_dim_table_mysql 
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS;"

mysql --local-infile=1 -u mysql -p$MYSQL_PASSWORD ecomm_data_analysis_db_mysql -e "
LOAD DATA LOCAL INFILE '/docker-entrypoint-initdb.d/trans_dim.csv'
INTO TABLE transaction_dim_table_mysql 
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS;"
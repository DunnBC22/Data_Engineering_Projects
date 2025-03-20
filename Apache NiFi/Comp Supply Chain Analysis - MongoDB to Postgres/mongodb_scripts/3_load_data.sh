#!/bin/bash
mongoimport -u mongodb_user -p mongodb_password --authenticationDatabase admin \
  -d comp_supply_chain_analysis_db_mongo -c comp_supply_chain_analysis_mongo_coll --type csv \
  --file /docker-entrypoint-initdb.d/data.csv --headerline
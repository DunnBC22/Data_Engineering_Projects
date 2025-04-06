#!/bin/bash
mongoimport -u mongodb_user -p mongodb_password --authenticationDatabase admin \
  -d ecomm_web_logs_mongo_db -c ecomm_web_logs_mongo_coll --type csv \
  --file /docker-entrypoint-initdb.d/data/data.csv --headerline
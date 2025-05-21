#!/bin/bash
mongoimport -u mongodb_user -p mongodb_password --authenticationDatabase admin \
  -d tsr_mongo_db -c tsr_mongo_coll --type csv \
  --file /data/dataset.csv --headerline
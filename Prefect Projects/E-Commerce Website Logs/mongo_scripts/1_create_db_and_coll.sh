#!/bin/bash
mongosh <<EOF
use ecomm_web_logs_mongo_db
if (!db.getCollection("ecomm_web_logs_mongo_coll")) {
  db.createCollection("ecomm_web_logs_mongo_coll")
}
EOF
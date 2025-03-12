#!/bin/bash
mongosh <<EOF
use ecomm_logs_db_mongo
if (!db.getCollection("ecomm_logs_coll_mongo")) {
  db.createCollection("ecomm_logs_coll_mongo")
}
EOF
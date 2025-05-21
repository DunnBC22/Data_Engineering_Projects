#!/bin/bash
mongosh <<EOF
use tsr_mongo_db
if (!db.getCollection("tsr_mongo_coll")) {
  db.createCollection("tsr_mongo_coll")
}
EOF
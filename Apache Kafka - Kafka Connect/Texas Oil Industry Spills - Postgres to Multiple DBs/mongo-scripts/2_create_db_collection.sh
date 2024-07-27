#!/bin/bash
mongosh <<EOF
use texas_ois_db_mongo
db.createCollection("texas_ois_mongo_collection")
EOF
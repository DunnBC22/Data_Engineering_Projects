#!/bin/bash
mongosh <<EOF
use har_db_mongo
db.createCollection("har_mongo_col")
EOF
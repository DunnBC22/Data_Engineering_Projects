#!/bin/bash
mongosh <<EOF
use dataco_scd_db_mongo
db.createCollection("dataco_scd_mongo_collection")
EOF

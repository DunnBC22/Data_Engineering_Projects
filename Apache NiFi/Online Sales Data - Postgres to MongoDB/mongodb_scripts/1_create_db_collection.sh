#!/bin/bash
mongosh <<EOF
use online_sales_data_db_mongo
db.createCollection("online_sales_data_coll_mongo")
EOF
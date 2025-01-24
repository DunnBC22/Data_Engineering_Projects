#!/bin/bash
mongosh <<EOF
use top_sci_researchers_db_mongo
db.createCollection("top_sci_researchers_mongo_col")
EOF
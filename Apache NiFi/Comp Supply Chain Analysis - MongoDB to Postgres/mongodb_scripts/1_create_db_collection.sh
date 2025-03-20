#!/bin/bash
mongosh <<EOF
use comp_supply_chain_analysis_db_mongo
if (!db.getCollection("comp_supply_chain_analysis_mongo_coll")) {
  db.createCollection("comp_supply_chain_analysis_mongo_coll")
}
EOF
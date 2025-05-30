#!/bin/bash
mongosh <<EOF
use employee_separation_forecast_mongo_db
if (!db.getCollection("employee_separation_forecast_mongo_coll")) {
  db.createCollection("employee_separation_forecast_mongo_coll")
}
EOF
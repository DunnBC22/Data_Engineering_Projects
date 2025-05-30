#!/bin/bash
mongosh <<EOF
use admin
// Check if the user already exists, and create if not
if (!db.getUser("mongodb_user")) {
  db.createUser({
    user: "mongodb_user",
    pwd: "mongodb_password",
    roles: [
      { role: "readWrite", db: "employee_separation_forecast_mongo_db" },
      { role: "dbOwner", db: "employee_separation_forecast_mongo_db" }
    ]
  });
}
EOF
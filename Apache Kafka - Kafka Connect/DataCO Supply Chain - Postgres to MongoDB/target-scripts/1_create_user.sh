#!/bin/bash
mongosh <<EOF
use admin
db.createUser(
{
user: "mongodb_user",
pwd: "mongodb_password",
roles: ["dbOwner"]
}
)
EOF
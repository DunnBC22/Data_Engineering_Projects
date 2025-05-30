#!/bin/bash
mongosh <<EOF
use most_watched_movies_and_tv_shows_mongo_db
if (!db.getCollection("most_watched_movies_and_tv_shows_mongo_coll")) {
  db.createCollection("most_watched_movies_and_tv_shows_mongo_coll")
}
EOF
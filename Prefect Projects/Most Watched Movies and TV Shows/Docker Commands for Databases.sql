
/* MariaDB */

--- Return the first 12 records from the 'most_watched_movies_and_tv_shows_mariadb_table' table
docker exec -i mariadb mariadb -u mariadb_user -pmariadb_pass most_watched_movies_and_tv_shows_mariadb_db -e "SELECT * FROM most_watched_movies_and_tv_shows_mariadb_table LIMIT 12;"

--- Return a count of how many records are in the 'most_watched_movies_and_tv_shows_mariadb_table' table
docker exec -i mariadb mariadb -u mariadb_user -pmariadb_pass most_watched_movies_and_tv_shows_mariadb_db -e "SELECT COUNT(*) FROM most_watched_movies_and_tv_shows_mariadb_table;"


/* MongoDB */

most_watched_movies_and_tv_shows_mongo_db
most_watched_movies_and_tv_shows_mongo_coll

--- Return the first 12 documents from the 'most_watched_movies_and_tv_shows_mongo_coll' collection
echo 'db.most_watched_movies_and_tv_shows_mongo_coll.find().limit(12).pretty()' | docker exec -i mongodb bash -c 'mongosh -u $MONGO_INITDB_ROOT_USERNAME -p $MONGO_INITDB_ROOT_PASSWORD --authenticationDatabase admin most_watched_movies_and_tv_shows_mongo_db'

--- Return a count of how many documents are in the 'most_watched_movies_and_tv_shows_mongo_coll' collection
echo 'db.most_watched_movies_and_tv_shows_mongo_coll.countDocuments()' | docker exec -i mongodb bash -c 'mongosh -u $MONGO_INITDB_ROOT_USERNAME -p $MONGO_INITDB_ROOT_PASSWORD --authenticationDatabase admin most_watched_movies_and_tv_shows_mongo_db'
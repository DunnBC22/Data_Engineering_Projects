
/* Postgres */

--- Return the first 12 records from the 'train_ee_sep_forecast_pg_table' table
echo "SELECT * FROM public.train_ee_sep_forecast_pg_table LIMIT 12;" | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

--- Return a count of how many records are in the 'train_ee_sep_forecast_pg_table' table
echo 'SELECT COUNT(*) FROM public.train_ee_sep_forecast_pg_table;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'


--- Return the first 12 records from the 'test_wo_results_ee_sep_forecast_pg_table' table
echo "SELECT * FROM public.test_wo_results_ee_sep_forecast_pg_table LIMIT 12;" | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

--- Return a count of how many records are in the 'test_wo_results_ee_sep_forecast_pg_table' table
echo 'SELECT COUNT(*) FROM public.test_wo_results_ee_sep_forecast_pg_table;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'


--- Return the first 12 records from the 'test_results_ee_sep_forecast_pg_table' table
echo "SELECT * FROM public.test_results_ee_sep_forecast_pg_table LIMIT 12;" | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

--- Return a count of how many records are in the 'test_results_ee_sep_forecast_pg_table' table
echo 'SELECT COUNT(*) FROM public.test_results_ee_sep_forecast_pg_table;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'



/* MongoDB */

--- Return the first 12 records from the 'employee_separation_forecast_mongo_coll' collection
echo 'db.employee_separation_forecast_mongo_coll.find().limit(12).pretty()' | docker exec -i mongodb bash -c 'mongosh -u $MONGO_INITDB_ROOT_USERNAME -p $MONGO_INITDB_ROOT_PASSWORD --authenticationDatabase admin employee_separation_forecast_mongo_db'

--- Return a count of how many records are in the 'employee_separation_forecast_mongo_coll' collection
echo 'db.employee_separation_forecast_mongo_coll.countDocuments()' | docker exec -i mongodb bash -c 'mongosh -u $MONGO_INITDB_ROOT_USERNAME -p $MONGO_INITDB_ROOT_PASSWORD --authenticationDatabase admin employee_separation_forecast_mongo_db'

/* Postgres */


--- *** mock_marketing_pg_account table *** ---
--- Return the first 12 records from the 'mock_marketing_pg_account' table
echo "SELECT * FROM public.mock_marketing_pg_account LIMIT 12;" | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

--- Return a count of how many records are in the 'mock_marketing_pg_account' table
echo 'SELECT COUNT(*) FROM public.mock_marketing_pg_account;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

--- *** mock_marketing_pg_customer table *** ---
--- Return the first 12 records from the 'mock_marketing_pg_customer' table
echo "SELECT * FROM public.mock_marketing_pg_customer LIMIT 12;" | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

--- Return a count of how many records are in the 'mock_marketing_pg_customer' table
echo 'SELECT COUNT(*) FROM public.mock_marketing_pg_customer;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

--- *** mock_marketing_pg_financials table *** ---
--- Return the first 12 records from the 'mock_marketing_pg_financials' table
echo "SELECT * FROM public.mock_marketing_pg_financials LIMIT 12;" | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

--- Return a count of how many records are in the 'mock_marketing_pg_financials' table
echo 'SELECT COUNT(*) FROM public.mock_marketing_pg_financials;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

--- *** mock_marketing_pg_household table *** ---
--- Return the first 12 records from the 'mock_marketing_pg_household' table
echo "SELECT * FROM public.mock_marketing_pg_household LIMIT 12;" | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

--- Return a count of how many records are in the 'mock_marketing_pg_household' table
echo 'SELECT COUNT(*) FROM public.mock_marketing_pg_household;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

--- *** mock_marketing_pg_marketing table *** ---
--- Return the first 12 records from the 'mock_marketing_pg_marketing' table
echo "SELECT * FROM public.mock_marketing_pg_marketing LIMIT 12;" | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

--- Return a count of how many records are in the 'mock_marketing_pg_marketing' table
echo 'SELECT COUNT(*) FROM public.mock_marketing_pg_marketing;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'




/* Apache Cassandra */
--- Return the first 12 records from the 'mock_marketing_schema_table_cassie'
echo "SELECT * FROM mock_marketing_schema_keyspace_cassie.mock_marketing_schema_table_cassie LIMIT 12;" | docker exec -i cassandra bash -c 'cqlsh -e "SELECT * FROM mock_marketing_schema_keyspace_cassie.mock_marketing_schema_table_cassie LIMIT 12;"'

--- Return a count of how many records are in the 'mock_marketing_schema_table_cassie'
echo 'SELECT COUNT(*) FROM mock_marketing_schema_keyspace_cassie.mock_marketing_schema_table_cassie;' | docker exec -i cassandra bash -c 'cqlsh -e "SELECT COUNT(*) FROM mock_marketing_schema_keyspace_cassie.mock_marketing_schema_table_cassie;"'
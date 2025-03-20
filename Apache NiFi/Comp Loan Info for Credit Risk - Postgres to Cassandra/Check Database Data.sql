/* 
Code to check & make sure data is in database tables as expected
*/


/* postgres */
--- Return the first 12 records from the 'comp_loan_info_credit_risk_table_pg'
echo "SELECT * FROM comp_loan_info_credit_risk_table_pg LIMIT 12;" | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

--- Return a count of how many records are in the 'comp_loan_info_credit_risk_table_pg'
echo 'SELECT COUNT(*) FROM comp_loan_info_credit_risk_table_pg;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'


/* Apache Cassandra */
--- Return the first 12 records from the 'comp_loan_info_credit_risk_table_cassie'
echo "SELECT * FROM comp_loan_info_credit_risk_keyspace.comp_loan_info_credit_risk_table_cassie LIMIT 12;" | docker exec -i cassandra bash -c 'cqlsh -e "SELECT * FROM comp_loan_info_credit_risk_keyspace.comp_loan_info_credit_risk_table_cassie LIMIT 12;"'

--- Return a count of how many records are in the 'comp_loan_info_credit_risk_table_cassie'
echo 'SELECT COUNT(*) FROM comp_loan_info_credit_risk_keyspace.comp_loan_info_credit_risk_table_cassie;' | docker exec -i cassandra bash -c 'cqlsh -e "SELECT COUNT(*) FROM comp_loan_info_credit_risk_keyspace.comp_loan_info_credit_risk_table_cassie;"'

-- Show the data types for each column
echo 'DESCRIBE TABLE comp_loan_info_credit_risk_keyspace.comp_loan_info_credit_risk_table_cassie;' | docker exec -i cassandra cqlsh -e "DESCRIBE TABLE comp_loan_info_credit_risk_keyspace.comp_loan_info_credit_risk_table_cassie;"
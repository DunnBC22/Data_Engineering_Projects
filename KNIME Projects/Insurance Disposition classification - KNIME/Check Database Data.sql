/* 
Code to check & make sure data is in database tables as expected
*/

/* Postgres */

-- *** For each table, there is a statement to return:
--          - 12 records from the table 
--          - the count of how many records are in the table

-- insur_claim_info_pg_table table in Postgres
echo 'SELECT * FROM insur_claim_info_pg_table LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(*) FROM insur_claim_info_pg_table;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

-- insur_date_data_pg_table table in Postgres
echo 'SELECT * FROM insur_date_data_pg_table LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(*) FROM insur_date_data_pg_table;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

-- insur_result_data_pg_table table in Postgres
echo 'SELECT * FROM insur_result_data_pg_table LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(*) FROM insur_result_data_pg_table;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'


/* SFTP */

-- Check that file made it to the SFTP server
docker exec -it sftp ls -l /home/knime_user/upload

-- Return the number of files (excluding the directories/sub-directories) in specified directory
docker exec -it sftp sh -c "find /home/knime_user/upload -type f | wc -l"


------ check the contents of the file(s) ------ 

-- Navigate to the docker container's shell
docker exec -it sftp sh

-- navigate to the folder
cd /home/knime_user/upload/<table-subdirectory>

-- Lists the files and subdirectories
ls -l

-- Check the file contents:
cat <filename>
-- OR USE --
less <filename>
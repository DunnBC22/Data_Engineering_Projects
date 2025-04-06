/* 
Code to check & make sure data is in database tables as expected
*/


/* SFTP Server */


-- Check that file made it to the SFTP server
docker exec -it sftp ls -l /home/knime_user/upload/tmp_folder

------ check the contents of the file(s) ------ 

-- Navigate to the docker container's shell
docker exec -it sftp sh

-- navigate to the folder
cd /home/knime_user/upload/<table-subdirectory>

-- Lists the files and subdirectories
ls -al

-- Check the file contents:
cat <copy filename to here>
-- OR USE --
less <copy filename to here>





/* Postgres */
--- Return the first 12 records from the 'car_specs_table_pg'
echo "SELECT * FROM public.car_specs_table_pg LIMIT 12;" | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

--- Return a count of how many records are in the 'car_specs_table_pg'
echo 'SELECT COUNT(*) FROM public.car_specs_table_pg;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
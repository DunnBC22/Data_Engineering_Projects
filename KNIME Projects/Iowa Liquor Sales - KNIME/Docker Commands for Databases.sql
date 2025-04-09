/* 
Code to check & make sure data is in database tables as expected
*/


/* SFTP Server */


-- Check that file made it to the SFTP server
docker exec -it sftp ls -l /home/knime_user/upload

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


/* MySQL */

-- Display 12 random records from the iowa_liquor_sales_mysql_table table
echo 'SELECT * FROM iowa_liquor_sales_mysql_table LIMIT 12;' | docker exec -i mysql mysql -u mysql -pmysql iowa_liquor_sales_mysql_db

-- Display number of records in the iowa_liquor_sales_mysql_table table
echo 'SELECT COUNT(*) FROM iowa_liquor_sales_mysql_table;' | docker exec -i mysql mysql -u mysql -pmysql iowa_liquor_sales_mysql_db
/* 
Code to check & make sure data is in database tables as expected
*/

/* SFTP-input Server */

-- Check that file made it to the SFTP server
docker exec -it sftp-input ls -l /home/knime_user/upload

-- Return the number of files (excluding the directories/sub-directories) in specified directory
docker exec -it sftp-input sh -c "find /home/knime_user/upload -type f | wc -l"



------ check the contents of the file(s) ------ 

-- Navigate to the docker container's shell
docker exec -it sftp-input sh

-- navigate to the folder
cd /home/knime_user/upload/<table-subdirectory>

-- Lists the files and subdirectories
ls -l

-- Check the file contents:
cat <filename>
-- OR USE --
less <filename>



/* SFTP-output Server */

-- Check that file made it to the SFTP server
docker exec -it sftp-output ls -l /home/knime_user/output

-- Return the number of files (excluding the directories/sub-directories) in specified directory
docker exec -it sftp-output sh -c "find /home/knime_user/output -type f | wc -l"

------ check the contents of the file(s) ------ 

-- Navigate to the docker container's shell
docker exec -it sftp-output sh

-- navigate to the folder
cd /home/knime_user/output/<table-subdirectory>

-- Lists the files and subdirectories
ls -l

-- Check the file contents:
cat <filename>
-- OR USE --
less <filename>
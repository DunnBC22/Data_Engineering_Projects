/* 
Code to check & make sure data is in database tables as expected
*/

/* SFTP Server */


-- Check that file made it to the SFTP server
docker exec -it sftp ls -l /home/nifi_user/upload

------ check the contents of the file(s) ------ 

-- Navigate to the docker container's shell
docker exec -it sftp sh

-- navigate to the folder
cd /home/nifi_user/upload/<table-subdirectory>

-- Lists the files and subdirectories
ls -l

-- Check the file contents:
cat <copy filename to here>
-- OR USE --
less <copy filename to here>



/* Samba */

-- to list the contents of the share:
docker exec -it samba ls -l /share


-- to view file contents:
docker exec -it samba cat /share/2009_quarter_1.csv


-- to Mount the Samba share on your host machine (on a mac):
mkdir /tmp/samba
mount_smbfs //samba_nifi_user:samba_nifi_pass@localhost/nifi_share /tmp/samba
-- Then browse the contents in /tmp/samba
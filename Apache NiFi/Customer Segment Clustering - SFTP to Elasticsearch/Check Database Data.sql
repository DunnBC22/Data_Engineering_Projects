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



/* Elasticsearch */

-- return 12 random samples
curl -u elastic:es_nifi_pass -X GET "http://localhost:9200/csc_data/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 12,
  "query": {
    "function_score": {
      "query": {
        "match_all": {}
      },
      "random_score": {}
    }
  }
}'

-- Return a count of the number of transactions in elasticsearch
curl -u elastic:es_nifi_pass -X GET "http://localhost:9200/csc_data/_count?pretty"
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



/* Postgres */
--- Return the first 12 records from the 'consumer_complaints_table_pg'
echo "SELECT * FROM public.consumer_complaints_table_pg LIMIT 12;" | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

--- Return a count of how many records are in the 'consumer_complaints_table_pg'
echo 'SELECT COUNT(*) FROM public.consumer_complaints_table_pg;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'





/* Neo4j */
MATCH (a:Airport)
RETURN a.code AS code, a.name AS name
LIMIT 25;


MATCH (a:Airport {code: "JFK"})-[:FLIGHT]->(dest:Airport)
RETURN dest.code AS destination, dest.name AS name;



MATCH (origin:Airport)-[:FLIGHT]->(a:Airport {code: "JFK"})
RETURN origin.code AS origin, origin.name AS name;



MATCH (a1:Airport)-[f:FLIGHT]->(a2:Airport)
RETURN a1.code AS origin, a2.code AS destination, f.flight_number, f.departure_time
LIMIT 25;



CALL db.labels()
YIELD label
RETURN label, 
       size([() WHERE $label IN labels(()) | 1]) AS count;


CALL db.labels()
YIELD label
CALL {
  WITH label
  RETURN count(*) AS count
  MATCH (n)
  WHERE label IN labels(n)
}
RETURN label, count
ORDER BY count DESC;



MATCH (a:Airport)
RETURN count(a) AS airport_count;



MATCH ()-[f:FLIGHT]->()
RETURN count(f) AS flight_count;



CALL db.relationshipTypes()
YIELD relationshipType AS relType
RETURN relType, 
       size([(a)-[r:`${relType}`]->() | 1]) AS count;

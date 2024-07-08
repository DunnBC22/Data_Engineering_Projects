/*
source dbms: SQL Server
target dbms: Postgres
*/

-- To check that connectors plugins were installed successfully
-- http://localhost:8083/connector-plugins

echo 'SELECT * FROM flights_2022_1 ORDER BY id OFFSET 0 ROWS FETCH FIRST 1 ROWS ONLY;' | docker exec -i sql-server /opt/mssql-tools/bin/sqlcmd -U kafka_user -P 'VeryStrong!Passw0rd' -d flight_files_source_db
-- For counting rows in Microsoft SQL Server
echo 'SELECT COUNT(flight_date) AS Num_Of_Records FROM flights_2022_1;' | docker exec -i sql-server /opt/mssql-tools/bin/sqlcmd -U kafka_user -P 'VeryStrong!Passw0rd' -d flight_files_source_db
echo 'SELECT COUNT(flight_date) AS Num_Of_Records FROM flights_2022_2;' | docker exec -i sql-server /opt/mssql-tools/bin/sqlcmd -U kafka_user -P 'VeryStrong!Passw0rd' -d flight_files_source_db
echo 'SELECT COUNT(flight_date) AS Num_Of_Records FROM flights_2022_3;' | docker exec -i sql-server /opt/mssql-tools/bin/sqlcmd -U kafka_user -P 'VeryStrong!Passw0rd' -d flight_files_source_db
echo 'SELECT COUNT(flight_date) AS Num_Of_Records FROM flights_2022_4;' | docker exec -i sql-server /opt/mssql-tools/bin/sqlcmd -U kafka_user -P 'VeryStrong!Passw0rd' -d flight_files_source_db
echo 'SELECT COUNT(flight_date) AS Num_Of_Records FROM flights_2022_5;' | docker exec -i sql-server /opt/mssql-tools/bin/sqlcmd -U kafka_user -P 'VeryStrong!Passw0rd' -d flight_files_source_db
echo 'SELECT COUNT(flight_date) AS Num_Of_Records FROM flights_2022_6;' | docker exec -i sql-server /opt/mssql-tools/bin/sqlcmd -U kafka_user -P 'VeryStrong!Passw0rd' -d flight_files_source_db
echo 'SELECT COUNT(flight_date) AS Num_Of_Records FROM flights_2022_7;' | docker exec -i sql-server /opt/mssql-tools/bin/sqlcmd -U kafka_user -P 'VeryStrong!Passw0rd' -d flight_files_source_db


/*
#docker compose command to develop interactively:

docker exec -it ksqldb-cli ksql http://ksqldb-server:8088
*/

-- update the auto.offset.reset setting
SET 'auto.offset.reset' = 'earliest';

-- CREATE SOURCE CONNECTOR(s)
CREATE SOURCE CONNECTOR IF NOT EXISTS flight_data_records_source_conn_ms_ss WITH (
    "name" = 'flight_data_records_source_conn_ms_ss',
    "connector.class" = 'io.confluent.connect.jdbc.JdbcSourceConnector',
    "connection.url" = 'jdbc:sqlserver://sql-server;databaseName=flight_files_source_db',
    "dialect.name" = 'SqlServerDatabaseDialect',
    "connection.user" = 'kafka_user',
    "connection.password" = 'VeryStrong!Passw0rd',
    "table.whitelist" = 'flights_2022_1,flights_2022_2,flights_2022_3,flights_2022_4,flights_2022_5,flights_2022_6,flights_2022_7', 
    "numeric.mapping" = 'best_fit',
    "tasks.max" = 7,
    "mode" = 'incrementing',
    "incrementing.column.name" = 'id',
    "validate.non.null" = 'true',
    "table.types" = 'TABLE',
    "errors.log.enable" = 'true',
    "transforms" = 'copyFieldToKey,extractKeyFromStruct',
    "transforms.copyFieldToKey.type" = 'org.apache.kafka.connect.transforms.ValueToKey',
    "transforms.copyFieldToKey.fields" = 'id',
    "transforms.extractKeyFromStruct.type" = 'org.apache.kafka.connect.transforms.ExtractField$Key',
    "transforms.extractKeyFromStruct.field" = 'id'
);

-- Create Input STREAM(s) 
CREATE STREAM flights_2022_1 (id INT KEY, flight_year VARCHAR, flight_quarter VARCHAR, flight_month VARCHAR, flight_day_of_month VARCHAR, flight_day_of_week VARCHAR, flight_date VARCHAR, marketing_airline_network VARCHAR, operated_or_branded_code_share_partners VARCHAR, dot_id_marketing_airline VARCHAR, iata_code_marketing_airline VARCHAR, flight_number_marketing_airline VARCHAR, originally_scheduled_code_share_airline VARCHAR, dot_id_originally_scheduled_code_share_airline VARCHAR, iata_code_originally_scheduled_code_share_airline VARCHAR, flight_num_originally_scheduled_code_share_airline VARCHAR, operating_airline VARCHAR, dot_id_operating_airline VARCHAR, iata_code_operating_airline VARCHAR, tail_number VARCHAR, flight_number_operating_airline VARCHAR, origin_airport_id VARCHAR, origin_airport_seq_id VARCHAR, origin_city_market_id VARCHAR, origin VARCHAR, origin_city_name VARCHAR, origin_state VARCHAR, origin_state_fips VARCHAR, origin_state_name VARCHAR, origin_wac VARCHAR, dest_airport_id VARCHAR, dest_airport_seq_id VARCHAR, dest_city_market_id VARCHAR, dest VARCHAR, dest_city_name VARCHAR, dest_state VARCHAR, dest_state_fips VARCHAR, dest_state_name VARCHAR, dest_wac VARCHAR, crs_dep_time VARCHAR, dep_time VARCHAR, dep_delay VARCHAR, dep_delay_minutes VARCHAR, dep_del_15 VARCHAR, departure_delay_groups VARCHAR, dep_time_blk VARCHAR, taxi_out VARCHAR, wheels_off VARCHAR, wheels_on VARCHAR, taxi_in VARCHAR, crs_arr_time VARCHAR, arr_time VARCHAR, arr_delay VARCHAR, arr_delay_minutes VARCHAR, arr_del_15 VARCHAR, arrival_delay_groups VARCHAR, arr_time_blk VARCHAR, cancelled VARCHAR, cancellation_code VARCHAR, diverted VARCHAR, crse_lapsed_time VARCHAR, actual_elapsed_time VARCHAR, air_time VARCHAR, flights VARCHAR, distance VARCHAR, distance_group VARCHAR, carrier_delay VARCHAR, weather_delay VARCHAR, nas_delay VARCHAR, security_delay VARCHAR, late_aircraft_delay VARCHAR, first_dep_time VARCHAR, total_add_g_time VARCHAR, longest_add_g_time VARCHAR, div_airport_landings VARCHAR, div_reached_dest VARCHAR, div_actual_elapsed_time VARCHAR, div_arr_delay VARCHAR, div_distance VARCHAR, div1_airport VARCHAR, div1_airport_id VARCHAR, div1_airport_seq_id VARCHAR, div1_wheels_on VARCHAR, div1_total_g_time VARCHAR, div1_longest_g_time VARCHAR, div1_wheels_off VARCHAR, div1_tail_num VARCHAR, div2_airport VARCHAR, div2_airport_id VARCHAR, div2_airport_seq_id VARCHAR, div2_wheels_on VARCHAR, div2_total_g_time VARCHAR, div2_longest_g_time VARCHAR, div2_wheels_off VARCHAR, div2_tail_num VARCHAR, div3_airport VARCHAR, div3_airport_id VARCHAR, div3_airport_seq_id VARCHAR, div3_wheels_on VARCHAR, div3_total_g_time VARCHAR, div3_longest_g_time VARCHAR, div3_wheels_off VARCHAR, div3_tail_num VARCHAR, div4_airport VARCHAR, div4_airport_id VARCHAR, div4_airport_seq_id VARCHAR, div4_wheels_on VARCHAR, div4_total_g_time VARCHAR, div4_longest_g_time VARCHAR, div4_wheels_off VARCHAR, div4_tail_num VARCHAR, div5_airport VARCHAR, div5_airport_id VARCHAR, div5_airport_seq_id VARCHAR, div5_wheels_on VARCHAR, div5_total_g_time VARCHAR, div5_longest_g_time VARCHAR, div5_wheels_off VARCHAR, div5_tail_num VARCHAR, duplicate VARCHAR) WITH (KAFKA_TOPIC='flights_2022_1', VALUE_FORMAT='AVRO', PARTITIONS=1);
CREATE STREAM flights_2022_2 (id INT KEY, flight_year VARCHAR, flight_quarter VARCHAR, flight_month VARCHAR, flight_day_of_month VARCHAR, flight_day_of_week VARCHAR, flight_date VARCHAR, marketing_airline_network VARCHAR, operated_or_branded_code_share_partners VARCHAR, dot_id_marketing_airline VARCHAR, iata_code_marketing_airline VARCHAR, flight_number_marketing_airline VARCHAR, originally_scheduled_code_share_airline VARCHAR, dot_id_originally_scheduled_code_share_airline VARCHAR, iata_code_originally_scheduled_code_share_airline VARCHAR, flight_num_originally_scheduled_code_share_airline VARCHAR, operating_airline VARCHAR, dot_id_operating_airline VARCHAR, iata_code_operating_airline VARCHAR, tail_number VARCHAR, flight_number_operating_airline VARCHAR, origin_airport_id VARCHAR, origin_airport_seq_id VARCHAR, origin_city_market_id VARCHAR, origin VARCHAR, origin_city_name VARCHAR, origin_state VARCHAR, origin_state_fips VARCHAR, origin_state_name VARCHAR, origin_wac VARCHAR, dest_airport_id VARCHAR, dest_airport_seq_id VARCHAR, dest_city_market_id VARCHAR, dest VARCHAR, dest_city_name VARCHAR, dest_state VARCHAR, dest_state_fips VARCHAR, dest_state_name VARCHAR, dest_wac VARCHAR, crs_dep_time VARCHAR, dep_time VARCHAR, dep_delay VARCHAR, dep_delay_minutes VARCHAR, dep_del_15 VARCHAR, departure_delay_groups VARCHAR, dep_time_blk VARCHAR, taxi_out VARCHAR, wheels_off VARCHAR, wheels_on VARCHAR, taxi_in VARCHAR, crs_arr_time VARCHAR, arr_time VARCHAR, arr_delay VARCHAR, arr_delay_minutes VARCHAR, arr_del_15 VARCHAR, arrival_delay_groups VARCHAR, arr_time_blk VARCHAR, cancelled VARCHAR, cancellation_code VARCHAR, diverted VARCHAR, crse_lapsed_time VARCHAR, actual_elapsed_time VARCHAR, air_time VARCHAR, flights VARCHAR, distance VARCHAR, distance_group VARCHAR, carrier_delay VARCHAR, weather_delay VARCHAR, nas_delay VARCHAR, security_delay VARCHAR, late_aircraft_delay VARCHAR, first_dep_time VARCHAR, total_add_g_time VARCHAR, longest_add_g_time VARCHAR, div_airport_landings VARCHAR, div_reached_dest VARCHAR, div_actual_elapsed_time VARCHAR, div_arr_delay VARCHAR, div_distance VARCHAR, div1_airport VARCHAR, div1_airport_id VARCHAR, div1_airport_seq_id VARCHAR, div1_wheels_on VARCHAR, div1_total_g_time VARCHAR, div1_longest_g_time VARCHAR, div1_wheels_off VARCHAR, div1_tail_num VARCHAR, div2_airport VARCHAR, div2_airport_id VARCHAR, div2_airport_seq_id VARCHAR, div2_wheels_on VARCHAR, div2_total_g_time VARCHAR, div2_longest_g_time VARCHAR, div2_wheels_off VARCHAR, div2_tail_num VARCHAR, div3_airport VARCHAR, div3_airport_id VARCHAR, div3_airport_seq_id VARCHAR, div3_wheels_on VARCHAR, div3_total_g_time VARCHAR, div3_longest_g_time VARCHAR, div3_wheels_off VARCHAR, div3_tail_num VARCHAR, div4_airport VARCHAR, div4_airport_id VARCHAR, div4_airport_seq_id VARCHAR, div4_wheels_on VARCHAR, div4_total_g_time VARCHAR, div4_longest_g_time VARCHAR, div4_wheels_off VARCHAR, div4_tail_num VARCHAR, div5_airport VARCHAR, div5_airport_id VARCHAR, div5_airport_seq_id VARCHAR, div5_wheels_on VARCHAR, div5_total_g_time VARCHAR, div5_longest_g_time VARCHAR, div5_wheels_off VARCHAR, div5_tail_num VARCHAR, duplicate VARCHAR) WITH (KAFKA_TOPIC='flights_2022_2', VALUE_FORMAT='AVRO', PARTITIONS=1);
CREATE STREAM flights_2022_3 (id INT KEY, flight_year VARCHAR, flight_quarter VARCHAR, flight_month VARCHAR, flight_day_of_month VARCHAR, flight_day_of_week VARCHAR, flight_date VARCHAR, marketing_airline_network VARCHAR, operated_or_branded_code_share_partners VARCHAR, dot_id_marketing_airline VARCHAR, iata_code_marketing_airline VARCHAR, flight_number_marketing_airline VARCHAR, originally_scheduled_code_share_airline VARCHAR, dot_id_originally_scheduled_code_share_airline VARCHAR, iata_code_originally_scheduled_code_share_airline VARCHAR, flight_num_originally_scheduled_code_share_airline VARCHAR, operating_airline VARCHAR, dot_id_operating_airline VARCHAR, iata_code_operating_airline VARCHAR, tail_number VARCHAR, flight_number_operating_airline VARCHAR, origin_airport_id VARCHAR, origin_airport_seq_id VARCHAR, origin_city_market_id VARCHAR, origin VARCHAR, origin_city_name VARCHAR, origin_state VARCHAR, origin_state_fips VARCHAR, origin_state_name VARCHAR, origin_wac VARCHAR, dest_airport_id VARCHAR, dest_airport_seq_id VARCHAR, dest_city_market_id VARCHAR, dest VARCHAR, dest_city_name VARCHAR, dest_state VARCHAR, dest_state_fips VARCHAR, dest_state_name VARCHAR, dest_wac VARCHAR, crs_dep_time VARCHAR, dep_time VARCHAR, dep_delay VARCHAR, dep_delay_minutes VARCHAR, dep_del_15 VARCHAR, departure_delay_groups VARCHAR, dep_time_blk VARCHAR, taxi_out VARCHAR, wheels_off VARCHAR, wheels_on VARCHAR, taxi_in VARCHAR, crs_arr_time VARCHAR, arr_time VARCHAR, arr_delay VARCHAR, arr_delay_minutes VARCHAR, arr_del_15 VARCHAR, arrival_delay_groups VARCHAR, arr_time_blk VARCHAR, cancelled VARCHAR, cancellation_code VARCHAR, diverted VARCHAR, crse_lapsed_time VARCHAR, actual_elapsed_time VARCHAR, air_time VARCHAR, flights VARCHAR, distance VARCHAR, distance_group VARCHAR, carrier_delay VARCHAR, weather_delay VARCHAR, nas_delay VARCHAR, security_delay VARCHAR, late_aircraft_delay VARCHAR, first_dep_time VARCHAR, total_add_g_time VARCHAR, longest_add_g_time VARCHAR, div_airport_landings VARCHAR, div_reached_dest VARCHAR, div_actual_elapsed_time VARCHAR, div_arr_delay VARCHAR, div_distance VARCHAR, div1_airport VARCHAR, div1_airport_id VARCHAR, div1_airport_seq_id VARCHAR, div1_wheels_on VARCHAR, div1_total_g_time VARCHAR, div1_longest_g_time VARCHAR, div1_wheels_off VARCHAR, div1_tail_num VARCHAR, div2_airport VARCHAR, div2_airport_id VARCHAR, div2_airport_seq_id VARCHAR, div2_wheels_on VARCHAR, div2_total_g_time VARCHAR, div2_longest_g_time VARCHAR, div2_wheels_off VARCHAR, div2_tail_num VARCHAR, div3_airport VARCHAR, div3_airport_id VARCHAR, div3_airport_seq_id VARCHAR, div3_wheels_on VARCHAR, div3_total_g_time VARCHAR, div3_longest_g_time VARCHAR, div3_wheels_off VARCHAR, div3_tail_num VARCHAR, div4_airport VARCHAR, div4_airport_id VARCHAR, div4_airport_seq_id VARCHAR, div4_wheels_on VARCHAR, div4_total_g_time VARCHAR, div4_longest_g_time VARCHAR, div4_wheels_off VARCHAR, div4_tail_num VARCHAR, div5_airport VARCHAR, div5_airport_id VARCHAR, div5_airport_seq_id VARCHAR, div5_wheels_on VARCHAR, div5_total_g_time VARCHAR, div5_longest_g_time VARCHAR, div5_wheels_off VARCHAR, div5_tail_num VARCHAR, duplicate VARCHAR) WITH (KAFKA_TOPIC='flights_2022_3', VALUE_FORMAT='AVRO', PARTITIONS=1);
CREATE STREAM flights_2022_4 (id INT KEY, flight_year VARCHAR, flight_quarter VARCHAR, flight_month VARCHAR, flight_day_of_month VARCHAR, flight_day_of_week VARCHAR, flight_date VARCHAR, marketing_airline_network VARCHAR, operated_or_branded_code_share_partners VARCHAR, dot_id_marketing_airline VARCHAR, iata_code_marketing_airline VARCHAR, flight_number_marketing_airline VARCHAR, originally_scheduled_code_share_airline VARCHAR, dot_id_originally_scheduled_code_share_airline VARCHAR, iata_code_originally_scheduled_code_share_airline VARCHAR, flight_num_originally_scheduled_code_share_airline VARCHAR, operating_airline VARCHAR, dot_id_operating_airline VARCHAR, iata_code_operating_airline VARCHAR, tail_number VARCHAR, flight_number_operating_airline VARCHAR, origin_airport_id VARCHAR, origin_airport_seq_id VARCHAR, origin_city_market_id VARCHAR, origin VARCHAR, origin_city_name VARCHAR, origin_state VARCHAR, origin_state_fips VARCHAR, origin_state_name VARCHAR, origin_wac VARCHAR, dest_airport_id VARCHAR, dest_airport_seq_id VARCHAR, dest_city_market_id VARCHAR, dest VARCHAR, dest_city_name VARCHAR, dest_state VARCHAR, dest_state_fips VARCHAR, dest_state_name VARCHAR, dest_wac VARCHAR, crs_dep_time VARCHAR, dep_time VARCHAR, dep_delay VARCHAR, dep_delay_minutes VARCHAR, dep_del_15 VARCHAR, departure_delay_groups VARCHAR, dep_time_blk VARCHAR, taxi_out VARCHAR, wheels_off VARCHAR, wheels_on VARCHAR, taxi_in VARCHAR, crs_arr_time VARCHAR, arr_time VARCHAR, arr_delay VARCHAR, arr_delay_minutes VARCHAR, arr_del_15 VARCHAR, arrival_delay_groups VARCHAR, arr_time_blk VARCHAR, cancelled VARCHAR, cancellation_code VARCHAR, diverted VARCHAR, crse_lapsed_time VARCHAR, actual_elapsed_time VARCHAR, air_time VARCHAR, flights VARCHAR, distance VARCHAR, distance_group VARCHAR, carrier_delay VARCHAR, weather_delay VARCHAR, nas_delay VARCHAR, security_delay VARCHAR, late_aircraft_delay VARCHAR, first_dep_time VARCHAR, total_add_g_time VARCHAR, longest_add_g_time VARCHAR, div_airport_landings VARCHAR, div_reached_dest VARCHAR, div_actual_elapsed_time VARCHAR, div_arr_delay VARCHAR, div_distance VARCHAR, div1_airport VARCHAR, div1_airport_id VARCHAR, div1_airport_seq_id VARCHAR, div1_wheels_on VARCHAR, div1_total_g_time VARCHAR, div1_longest_g_time VARCHAR, div1_wheels_off VARCHAR, div1_tail_num VARCHAR, div2_airport VARCHAR, div2_airport_id VARCHAR, div2_airport_seq_id VARCHAR, div2_wheels_on VARCHAR, div2_total_g_time VARCHAR, div2_longest_g_time VARCHAR, div2_wheels_off VARCHAR, div2_tail_num VARCHAR, div3_airport VARCHAR, div3_airport_id VARCHAR, div3_airport_seq_id VARCHAR, div3_wheels_on VARCHAR, div3_total_g_time VARCHAR, div3_longest_g_time VARCHAR, div3_wheels_off VARCHAR, div3_tail_num VARCHAR, div4_airport VARCHAR, div4_airport_id VARCHAR, div4_airport_seq_id VARCHAR, div4_wheels_on VARCHAR, div4_total_g_time VARCHAR, div4_longest_g_time VARCHAR, div4_wheels_off VARCHAR, div4_tail_num VARCHAR, div5_airport VARCHAR, div5_airport_id VARCHAR, div5_airport_seq_id VARCHAR, div5_wheels_on VARCHAR, div5_total_g_time VARCHAR, div5_longest_g_time VARCHAR, div5_wheels_off VARCHAR, div5_tail_num VARCHAR, duplicate VARCHAR) WITH (KAFKA_TOPIC='flights_2022_4', VALUE_FORMAT='AVRO', PARTITIONS=1);
CREATE STREAM flights_2022_5 (id INT KEY, flight_year VARCHAR, flight_quarter VARCHAR, flight_month VARCHAR, flight_day_of_month VARCHAR, flight_day_of_week VARCHAR, flight_date VARCHAR, marketing_airline_network VARCHAR, operated_or_branded_code_share_partners VARCHAR, dot_id_marketing_airline VARCHAR, iata_code_marketing_airline VARCHAR, flight_number_marketing_airline VARCHAR, originally_scheduled_code_share_airline VARCHAR, dot_id_originally_scheduled_code_share_airline VARCHAR, iata_code_originally_scheduled_code_share_airline VARCHAR, flight_num_originally_scheduled_code_share_airline VARCHAR, operating_airline VARCHAR, dot_id_operating_airline VARCHAR, iata_code_operating_airline VARCHAR, tail_number VARCHAR, flight_number_operating_airline VARCHAR, origin_airport_id VARCHAR, origin_airport_seq_id VARCHAR, origin_city_market_id VARCHAR, origin VARCHAR, origin_city_name VARCHAR, origin_state VARCHAR, origin_state_fips VARCHAR, origin_state_name VARCHAR, origin_wac VARCHAR, dest_airport_id VARCHAR, dest_airport_seq_id VARCHAR, dest_city_market_id VARCHAR, dest VARCHAR, dest_city_name VARCHAR, dest_state VARCHAR, dest_state_fips VARCHAR, dest_state_name VARCHAR, dest_wac VARCHAR, crs_dep_time VARCHAR, dep_time VARCHAR, dep_delay VARCHAR, dep_delay_minutes VARCHAR, dep_del_15 VARCHAR, departure_delay_groups VARCHAR, dep_time_blk VARCHAR, taxi_out VARCHAR, wheels_off VARCHAR, wheels_on VARCHAR, taxi_in VARCHAR, crs_arr_time VARCHAR, arr_time VARCHAR, arr_delay VARCHAR, arr_delay_minutes VARCHAR, arr_del_15 VARCHAR, arrival_delay_groups VARCHAR, arr_time_blk VARCHAR, cancelled VARCHAR, cancellation_code VARCHAR, diverted VARCHAR, crse_lapsed_time VARCHAR, actual_elapsed_time VARCHAR, air_time VARCHAR, flights VARCHAR, distance VARCHAR, distance_group VARCHAR, carrier_delay VARCHAR, weather_delay VARCHAR, nas_delay VARCHAR, security_delay VARCHAR, late_aircraft_delay VARCHAR, first_dep_time VARCHAR, total_add_g_time VARCHAR, longest_add_g_time VARCHAR, div_airport_landings VARCHAR, div_reached_dest VARCHAR, div_actual_elapsed_time VARCHAR, div_arr_delay VARCHAR, div_distance VARCHAR, div1_airport VARCHAR, div1_airport_id VARCHAR, div1_airport_seq_id VARCHAR, div1_wheels_on VARCHAR, div1_total_g_time VARCHAR, div1_longest_g_time VARCHAR, div1_wheels_off VARCHAR, div1_tail_num VARCHAR, div2_airport VARCHAR, div2_airport_id VARCHAR, div2_airport_seq_id VARCHAR, div2_wheels_on VARCHAR, div2_total_g_time VARCHAR, div2_longest_g_time VARCHAR, div2_wheels_off VARCHAR, div2_tail_num VARCHAR, div3_airport VARCHAR, div3_airport_id VARCHAR, div3_airport_seq_id VARCHAR, div3_wheels_on VARCHAR, div3_total_g_time VARCHAR, div3_longest_g_time VARCHAR, div3_wheels_off VARCHAR, div3_tail_num VARCHAR, div4_airport VARCHAR, div4_airport_id VARCHAR, div4_airport_seq_id VARCHAR, div4_wheels_on VARCHAR, div4_total_g_time VARCHAR, div4_longest_g_time VARCHAR, div4_wheels_off VARCHAR, div4_tail_num VARCHAR, div5_airport VARCHAR, div5_airport_id VARCHAR, div5_airport_seq_id VARCHAR, div5_wheels_on VARCHAR, div5_total_g_time VARCHAR, div5_longest_g_time VARCHAR, div5_wheels_off VARCHAR, div5_tail_num VARCHAR, duplicate VARCHAR) WITH (KAFKA_TOPIC='flights_2022_5', VALUE_FORMAT='AVRO', PARTITIONS=1);
CREATE STREAM flights_2022_6 (id INT KEY, flight_year VARCHAR, flight_quarter VARCHAR, flight_month VARCHAR, flight_day_of_month VARCHAR, flight_day_of_week VARCHAR, flight_date VARCHAR, marketing_airline_network VARCHAR, operated_or_branded_code_share_partners VARCHAR, dot_id_marketing_airline VARCHAR, iata_code_marketing_airline VARCHAR, flight_number_marketing_airline VARCHAR, originally_scheduled_code_share_airline VARCHAR, dot_id_originally_scheduled_code_share_airline VARCHAR, iata_code_originally_scheduled_code_share_airline VARCHAR, flight_num_originally_scheduled_code_share_airline VARCHAR, operating_airline VARCHAR, dot_id_operating_airline VARCHAR, iata_code_operating_airline VARCHAR, tail_number VARCHAR, flight_number_operating_airline VARCHAR, origin_airport_id VARCHAR, origin_airport_seq_id VARCHAR, origin_city_market_id VARCHAR, origin VARCHAR, origin_city_name VARCHAR, origin_state VARCHAR, origin_state_fips VARCHAR, origin_state_name VARCHAR, origin_wac VARCHAR, dest_airport_id VARCHAR, dest_airport_seq_id VARCHAR, dest_city_market_id VARCHAR, dest VARCHAR, dest_city_name VARCHAR, dest_state VARCHAR, dest_state_fips VARCHAR, dest_state_name VARCHAR, dest_wac VARCHAR, crs_dep_time VARCHAR, dep_time VARCHAR, dep_delay VARCHAR, dep_delay_minutes VARCHAR, dep_del_15 VARCHAR, departure_delay_groups VARCHAR, dep_time_blk VARCHAR, taxi_out VARCHAR, wheels_off VARCHAR, wheels_on VARCHAR, taxi_in VARCHAR, crs_arr_time VARCHAR, arr_time VARCHAR, arr_delay VARCHAR, arr_delay_minutes VARCHAR, arr_del_15 VARCHAR, arrival_delay_groups VARCHAR, arr_time_blk VARCHAR, cancelled VARCHAR, cancellation_code VARCHAR, diverted VARCHAR, crse_lapsed_time VARCHAR, actual_elapsed_time VARCHAR, air_time VARCHAR, flights VARCHAR, distance VARCHAR, distance_group VARCHAR, carrier_delay VARCHAR, weather_delay VARCHAR, nas_delay VARCHAR, security_delay VARCHAR, late_aircraft_delay VARCHAR, first_dep_time VARCHAR, total_add_g_time VARCHAR, longest_add_g_time VARCHAR, div_airport_landings VARCHAR, div_reached_dest VARCHAR, div_actual_elapsed_time VARCHAR, div_arr_delay VARCHAR, div_distance VARCHAR, div1_airport VARCHAR, div1_airport_id VARCHAR, div1_airport_seq_id VARCHAR, div1_wheels_on VARCHAR, div1_total_g_time VARCHAR, div1_longest_g_time VARCHAR, div1_wheels_off VARCHAR, div1_tail_num VARCHAR, div2_airport VARCHAR, div2_airport_id VARCHAR, div2_airport_seq_id VARCHAR, div2_wheels_on VARCHAR, div2_total_g_time VARCHAR, div2_longest_g_time VARCHAR, div2_wheels_off VARCHAR, div2_tail_num VARCHAR, div3_airport VARCHAR, div3_airport_id VARCHAR, div3_airport_seq_id VARCHAR, div3_wheels_on VARCHAR, div3_total_g_time VARCHAR, div3_longest_g_time VARCHAR, div3_wheels_off VARCHAR, div3_tail_num VARCHAR, div4_airport VARCHAR, div4_airport_id VARCHAR, div4_airport_seq_id VARCHAR, div4_wheels_on VARCHAR, div4_total_g_time VARCHAR, div4_longest_g_time VARCHAR, div4_wheels_off VARCHAR, div4_tail_num VARCHAR, div5_airport VARCHAR, div5_airport_id VARCHAR, div5_airport_seq_id VARCHAR, div5_wheels_on VARCHAR, div5_total_g_time VARCHAR, div5_longest_g_time VARCHAR, div5_wheels_off VARCHAR, div5_tail_num VARCHAR, duplicate VARCHAR) WITH (KAFKA_TOPIC='flights_2022_6', VALUE_FORMAT='AVRO', PARTITIONS=1);
CREATE STREAM flights_2022_7 (id INT KEY, flight_year VARCHAR, flight_quarter VARCHAR, flight_month VARCHAR, flight_day_of_month VARCHAR, flight_day_of_week VARCHAR, flight_date VARCHAR, marketing_airline_network VARCHAR, operated_or_branded_code_share_partners VARCHAR, dot_id_marketing_airline VARCHAR, iata_code_marketing_airline VARCHAR, flight_number_marketing_airline VARCHAR, originally_scheduled_code_share_airline VARCHAR, dot_id_originally_scheduled_code_share_airline VARCHAR, iata_code_originally_scheduled_code_share_airline VARCHAR, flight_num_originally_scheduled_code_share_airline VARCHAR, operating_airline VARCHAR, dot_id_operating_airline VARCHAR, iata_code_operating_airline VARCHAR, tail_number VARCHAR, flight_number_operating_airline VARCHAR, origin_airport_id VARCHAR, origin_airport_seq_id VARCHAR, origin_city_market_id VARCHAR, origin VARCHAR, origin_city_name VARCHAR, origin_state VARCHAR, origin_state_fips VARCHAR, origin_state_name VARCHAR, origin_wac VARCHAR, dest_airport_id VARCHAR, dest_airport_seq_id VARCHAR, dest_city_market_id VARCHAR, dest VARCHAR, dest_city_name VARCHAR, dest_state VARCHAR, dest_state_fips VARCHAR, dest_state_name VARCHAR, dest_wac VARCHAR, crs_dep_time VARCHAR, dep_time VARCHAR, dep_delay VARCHAR, dep_delay_minutes VARCHAR, dep_del_15 VARCHAR, departure_delay_groups VARCHAR, dep_time_blk VARCHAR, taxi_out VARCHAR, wheels_off VARCHAR, wheels_on VARCHAR, taxi_in VARCHAR, crs_arr_time VARCHAR, arr_time VARCHAR, arr_delay VARCHAR, arr_delay_minutes VARCHAR, arr_del_15 VARCHAR, arrival_delay_groups VARCHAR, arr_time_blk VARCHAR, cancelled VARCHAR, cancellation_code VARCHAR, diverted VARCHAR, crse_lapsed_time VARCHAR, actual_elapsed_time VARCHAR, air_time VARCHAR, flights VARCHAR, distance VARCHAR, distance_group VARCHAR, carrier_delay VARCHAR, weather_delay VARCHAR, nas_delay VARCHAR, security_delay VARCHAR, late_aircraft_delay VARCHAR, first_dep_time VARCHAR, total_add_g_time VARCHAR, longest_add_g_time VARCHAR, div_airport_landings VARCHAR, div_reached_dest VARCHAR, div_actual_elapsed_time VARCHAR, div_arr_delay VARCHAR, div_distance VARCHAR, div1_airport VARCHAR, div1_airport_id VARCHAR, div1_airport_seq_id VARCHAR, div1_wheels_on VARCHAR, div1_total_g_time VARCHAR, div1_longest_g_time VARCHAR, div1_wheels_off VARCHAR, div1_tail_num VARCHAR, div2_airport VARCHAR, div2_airport_id VARCHAR, div2_airport_seq_id VARCHAR, div2_wheels_on VARCHAR, div2_total_g_time VARCHAR, div2_longest_g_time VARCHAR, div2_wheels_off VARCHAR, div2_tail_num VARCHAR, div3_airport VARCHAR, div3_airport_id VARCHAR, div3_airport_seq_id VARCHAR, div3_wheels_on VARCHAR, div3_total_g_time VARCHAR, div3_longest_g_time VARCHAR, div3_wheels_off VARCHAR, div3_tail_num VARCHAR, div4_airport VARCHAR, div4_airport_id VARCHAR, div4_airport_seq_id VARCHAR, div4_wheels_on VARCHAR, div4_total_g_time VARCHAR, div4_longest_g_time VARCHAR, div4_wheels_off VARCHAR, div4_tail_num VARCHAR, div5_airport VARCHAR, div5_airport_id VARCHAR, div5_airport_seq_id VARCHAR, div5_wheels_on VARCHAR, div5_total_g_time VARCHAR, div5_longest_g_time VARCHAR, div5_wheels_off VARCHAR, div5_tail_num VARCHAR, duplicate VARCHAR) WITH (KAFKA_TOPIC='flights_2022_7', VALUE_FORMAT='AVRO', PARTITIONS=1);


SHOW CONNECTORS;
SHOW TOPICS;
SHOW STREAMS;


PRINT flights_2022_1 FROM BEGINNING LIMIT 25;
PRINT flights_2022_2 FROM BEGINNING LIMIT 25;
PRINT flights_2022_3 FROM BEGINNING LIMIT 25;
PRINT flights_2022_4 FROM BEGINNING LIMIT 25;
PRINT flights_2022_5 FROM BEGINNING LIMIT 25;
PRINT flights_2022_6 FROM BEGINNING LIMIT 25;
PRINT flights_2022_7 FROM BEGINNING LIMIT 25;

SELECT * FROM FLIGHTS_2022_1 EMIT CHANGES;
SELECT * FROM FLIGHTS_2022_2 EMIT CHANGES;
SELECT * FROM FLIGHTS_2022_3 EMIT CHANGES;
SELECT * FROM FLIGHTS_2022_4 EMIT CHANGES;
SELECT * FROM FLIGHTS_2022_5 EMIT CHANGES;
SELECT * FROM FLIGHTS_2022_6 EMIT CHANGES;
SELECT * FROM FLIGHTS_2022_7 EMIT CHANGES;

-- Create STREAM that will be the combination of all individual flight_data streams
CREATE STREAM AllFlightData (
    id INT KEY,
    flight_year VARCHAR,
    flight_quarter VARCHAR,
    flight_month VARCHAR,
    flight_day_of_month VARCHAR,
    flight_day_of_week VARCHAR,
    flight_date VARCHAR,
    marketing_airline_network VARCHAR,
    operated_or_branded_code_share_partners VARCHAR,
    dot_id_marketing_airline VARCHAR,
    iata_code_marketing_airline VARCHAR,
    flight_number_marketing_airline VARCHAR,
    originally_scheduled_code_share_airline VARCHAR,
    dot_id_originally_scheduled_code_share_airline VARCHAR,
    iata_code_originally_scheduled_code_share_airline VARCHAR,
    flight_num_originally_scheduled_code_share_airline VARCHAR,
    operating_airline VARCHAR,
    dot_id_operating_airline VARCHAR,
    iata_code_operating_airline VARCHAR,
    tail_number VARCHAR,
    flight_number_operating_airline VARCHAR,
    origin_airport_id VARCHAR,
    origin_airport_seq_id VARCHAR,
    origin_city_market_id VARCHAR,
    origin VARCHAR,
    origin_city_name VARCHAR,
    origin_state VARCHAR,
    origin_state_fips VARCHAR,
    origin_state_name VARCHAR,
    origin_wac VARCHAR,
    dest_airport_id VARCHAR,
    dest_airport_seq_id VARCHAR,
    dest_city_market_id VARCHAR,
    dest VARCHAR,
    dest_city_name VARCHAR,
    dest_state VARCHAR,
    dest_state_fips VARCHAR,
    dest_state_name VARCHAR,
    dest_wac VARCHAR,
    crs_dep_time VARCHAR,
    dep_time VARCHAR,
    dep_delay VARCHAR,
    dep_delay_minutes VARCHAR,
    dep_del_15 VARCHAR,
    departure_delay_groups VARCHAR,
    dep_time_blk VARCHAR,
    taxi_out VARCHAR,
    wheels_off VARCHAR,
    wheels_on VARCHAR,
    taxi_in VARCHAR,
    crs_arr_time VARCHAR,
    arr_time VARCHAR,
    arr_delay VARCHAR,
    arr_delay_minutes VARCHAR,
    arr_del_15 VARCHAR,
    arrival_delay_groups VARCHAR,
    arr_time_blk VARCHAR,
    cancelled VARCHAR,
    cancellation_code VARCHAR,
    diverted VARCHAR,
    crse_lapsed_time VARCHAR,
    actual_elapsed_time VARCHAR,
    air_time VARCHAR,
    flights VARCHAR,
    distance VARCHAR,
    distance_group VARCHAR,
    carrier_delay VARCHAR,
    weather_delay VARCHAR,
    nas_delay VARCHAR,
    security_delay VARCHAR,
    late_aircraft_delay VARCHAR,
    first_dep_time VARCHAR,
    total_add_g_time VARCHAR,
    longest_add_g_time VARCHAR,
    div_airport_landings VARCHAR,
    div_reached_dest VARCHAR,
    div_actual_elapsed_time VARCHAR,
    div_arr_delay VARCHAR,
    div_distance VARCHAR,
    div1_airport VARCHAR,
    div1_airport_id VARCHAR,
    div1_airport_seq_id VARCHAR,
    div1_wheels_on VARCHAR,
    div1_total_g_time VARCHAR,
    div1_longest_g_time VARCHAR,
    div1_wheels_off VARCHAR,
    div1_tail_num VARCHAR,
    div2_airport VARCHAR,
    div2_airport_id VARCHAR,
    div2_airport_seq_id VARCHAR,
    div2_wheels_on VARCHAR,
    div2_total_g_time VARCHAR,
    div2_longest_g_time VARCHAR,
    div2_wheels_off VARCHAR,
    div2_tail_num VARCHAR,
    div3_airport VARCHAR,
    div3_airport_id VARCHAR,
    div3_airport_seq_id VARCHAR,
    div3_wheels_on VARCHAR,
    div3_total_g_time VARCHAR,
    div3_longest_g_time VARCHAR,
    div3_wheels_off VARCHAR,
    div3_tail_num VARCHAR,
    div4_airport VARCHAR,
    div4_airport_id VARCHAR,
    div4_airport_seq_id VARCHAR,
    div4_wheels_on VARCHAR,
    div4_total_g_time VARCHAR,
    div4_longest_g_time VARCHAR,
    div4_wheels_off VARCHAR,
    div4_tail_num VARCHAR,
    div5_airport VARCHAR,
    div5_airport_id VARCHAR,
    div5_airport_seq_id VARCHAR,
    div5_wheels_on VARCHAR,
    div5_total_g_time VARCHAR,
    div5_longest_g_time VARCHAR,
    div5_wheels_off VARCHAR,
    div5_tail_num VARCHAR,
    duplicate VARCHAR
) WITH (
    KAFKA_TOPIC='AllFlightData',
    VALUE_FORMAT='AVRO',
    PARTITIONS=1
);

-- INSERT records from each stream INTO the merged/combined stream
INSERT INTO 
    AllFlightData
SELECT 
    id,
    flight_year,
    flight_quarter,
    flight_month,
    flight_day_of_month,
    flight_day_of_week,
    flight_date, 
    marketing_airline_network, 
    operated_or_branded_code_share_partners,
    dot_id_marketing_airline,
    iata_code_marketing_airline,
    flight_number_marketing_airline,
    originally_scheduled_code_share_airline,
    dot_id_originally_scheduled_code_share_airline, 
    iata_code_originally_scheduled_code_share_airline,
    flight_num_originally_scheduled_code_share_airline, 
    operating_airline,
    dot_id_operating_airline,
    iata_code_operating_airline,
    tail_number, 
    flight_number_operating_airline,
    origin_airport_id,
    origin_airport_seq_id,
    origin_city_market_id,
    origin,
    origin_city_name, 
    origin_state,
    origin_state_fips,
    origin_state_name,
    origin_wac origin_wac,
    dest_airport_id,
    dest_airport_seq_id,
    dest_city_market_id,
    dest, 
    dest_city_name,
    dest_state,
    dest_state_fips,
    dest_state_name, 
    dest_wac,
    crs_dep_time,
    dep_time,
    dep_delay,
    dep_delay_minutes,
    dep_del_15,
    departure_delay_groups,
    dep_time_blk, 
    taxi_out,
    wheels_off,
    wheels_on,
    taxi_in,
    crs_arr_time,
    arr_time,
    arr_delay,
    arr_delay_minutes,
    arr_del_15,
    arrival_delay_groups,
    arr_time_blk,
    cancelled,
    cancellation_code,
    diverted,
    crse_lapsed_time,
    actual_elapsed_time,
    air_time,
    flights,
    distance,
    distance_group,
    carrier_delay,
    weather_delay,
    nas_delay,
    security_delay,
    late_aircraft_delay,
    first_dep_time,
    total_add_g_time,
    longest_add_g_time,
    div_airport_landings,
    div_reached_dest, 
    div_actual_elapsed_time,
    div_arr_delay, 
    div_distance,
    div1_airport, 
    div1_airport_id,
    div1_airport_seq_id, 
    div1_wheels_on,
    div1_total_g_time, 
    div1_longest_g_time,
    div1_wheels_off, 
    div1_tail_num,
    div2_airport, 
    div2_airport_id,
    div2_airport_seq_id, 
    div2_wheels_on,
    div2_total_g_time, 
    div2_longest_g_time,
    div2_wheels_off, 
    div2_tail_num,
    div3_airport, 
    div3_airport_id,
    div3_airport_seq_id, 
    div3_wheels_on,
    div3_total_g_time, 
    div3_longest_g_time,
    div3_wheels_off, 
    div3_tail_num,
    div4_airport, 
    div4_airport_id,
    div4_airport_seq_id, 
    div4_wheels_on,
    div4_total_g_time, 
    div4_longest_g_time,
    div4_wheels_off, 
    div4_tail_num,
    div5_airport, 
    div5_airport_id,
    div5_airport_seq_id, 
    div5_wheels_on,
    div5_total_g_time, 
    div5_longest_g_time,
    div5_wheels_off, 
    div5_tail_num,
    duplicate
FROM 
    flights_2022_1
EMIT CHANGES;

INSERT INTO 
    AllFlightData
SELECT  
    id,
    flight_year,
    flight_quarter,
    flight_month,
    flight_day_of_month,
    flight_day_of_week,
    flight_date, 
    marketing_airline_network, 
    operated_or_branded_code_share_partners,
    dot_id_marketing_airline,
    iata_code_marketing_airline,
    flight_number_marketing_airline,
    originally_scheduled_code_share_airline,
    dot_id_originally_scheduled_code_share_airline, 
    iata_code_originally_scheduled_code_share_airline,
    flight_num_originally_scheduled_code_share_airline, 
    operating_airline,
    dot_id_operating_airline,
    iata_code_operating_airline,
    tail_number, 
    flight_number_operating_airline,
    origin_airport_id,
    origin_airport_seq_id,
    origin_city_market_id,
    origin,
    origin_city_name, 
    origin_state,
    origin_state_fips,
    origin_state_name,
    origin_wac origin_wac,
    dest_airport_id,
    dest_airport_seq_id,
    dest_city_market_id,
    dest, 
    dest_city_name,
    dest_state,
    dest_state_fips,
    dest_state_name, 
    dest_wac,
    crs_dep_time,
    dep_time,
    dep_delay,
    dep_delay_minutes,
    dep_del_15,
    departure_delay_groups,
    dep_time_blk, 
    taxi_out,
    wheels_off,
    wheels_on,
    taxi_in,
    crs_arr_time,
    arr_time,
    arr_delay,
    arr_delay_minutes,
    arr_del_15,
    arrival_delay_groups,
    arr_time_blk,
    cancelled,
    cancellation_code,
    diverted,
    crse_lapsed_time,
    actual_elapsed_time,
    air_time,
    flights,
    distance,
    distance_group,
    carrier_delay,
    weather_delay,
    nas_delay,
    security_delay,
    late_aircraft_delay,
    first_dep_time,
    total_add_g_time,
    longest_add_g_time,
    div_airport_landings,
    div_reached_dest, 
    div_actual_elapsed_time,
    div_arr_delay, 
    div_distance,
    div1_airport, 
    div1_airport_id,
    div1_airport_seq_id, 
    div1_wheels_on,
    div1_total_g_time, 
    div1_longest_g_time,
    div1_wheels_off, 
    div1_tail_num,
    div2_airport, 
    div2_airport_id,
    div2_airport_seq_id, 
    div2_wheels_on,
    div2_total_g_time, 
    div2_longest_g_time,
    div2_wheels_off, 
    div2_tail_num,
    div3_airport, 
    div3_airport_id,
    div3_airport_seq_id, 
    div3_wheels_on,
    div3_total_g_time, 
    div3_longest_g_time,
    div3_wheels_off, 
    div3_tail_num,
    div4_airport, 
    div4_airport_id,
    div4_airport_seq_id, 
    div4_wheels_on,
    div4_total_g_time, 
    div4_longest_g_time,
    div4_wheels_off, 
    div4_tail_num,
    div5_airport, 
    div5_airport_id,
    div5_airport_seq_id, 
    div5_wheels_on,
    div5_total_g_time, 
    div5_longest_g_time,
    div5_wheels_off, 
    div5_tail_num,
    duplicate
FROM 
    flights_2022_2
EMIT CHANGES;

INSERT INTO 
    AllFlightData
SELECT  
    id,
    flight_year,
    flight_quarter,
    flight_month,
    flight_day_of_month,
    flight_day_of_week,
    flight_date, 
    marketing_airline_network, 
    operated_or_branded_code_share_partners,
    dot_id_marketing_airline,
    iata_code_marketing_airline,
    flight_number_marketing_airline,
    originally_scheduled_code_share_airline,
    dot_id_originally_scheduled_code_share_airline, 
    iata_code_originally_scheduled_code_share_airline,
    flight_num_originally_scheduled_code_share_airline, 
    operating_airline,
    dot_id_operating_airline,
    iata_code_operating_airline,
    tail_number, 
    flight_number_operating_airline,
    origin_airport_id,
    origin_airport_seq_id,
    origin_city_market_id,
    origin,
    origin_city_name, 
    origin_state,
    origin_state_fips,
    origin_state_name,
    origin_wac origin_wac,
    dest_airport_id,
    dest_airport_seq_id,
    dest_city_market_id,
    dest, 
    dest_city_name,
    dest_state,
    dest_state_fips,
    dest_state_name, 
    dest_wac,
    crs_dep_time,
    dep_time,
    dep_delay,
    dep_delay_minutes,
    dep_del_15,
    departure_delay_groups,
    dep_time_blk, 
    taxi_out,
    wheels_off,
    wheels_on,
    taxi_in,
    crs_arr_time,
    arr_time,
    arr_delay,
    arr_delay_minutes,
    arr_del_15,
    arrival_delay_groups,
    arr_time_blk,
    cancelled,
    cancellation_code,
    diverted,
    crse_lapsed_time,
    actual_elapsed_time,
    air_time,
    flights,
    distance,
    distance_group,
    carrier_delay,
    weather_delay,
    nas_delay,
    security_delay,
    late_aircraft_delay,
    first_dep_time,
    total_add_g_time,
    longest_add_g_time,
    div_airport_landings,
    div_reached_dest, 
    div_actual_elapsed_time,
    div_arr_delay, 
    div_distance,
    div1_airport, 
    div1_airport_id,
    div1_airport_seq_id, 
    div1_wheels_on,
    div1_total_g_time, 
    div1_longest_g_time,
    div1_wheels_off, 
    div1_tail_num,
    div2_airport, 
    div2_airport_id,
    div2_airport_seq_id, 
    div2_wheels_on,
    div2_total_g_time, 
    div2_longest_g_time,
    div2_wheels_off, 
    div2_tail_num,
    div3_airport, 
    div3_airport_id,
    div3_airport_seq_id, 
    div3_wheels_on,
    div3_total_g_time, 
    div3_longest_g_time,
    div3_wheels_off, 
    div3_tail_num,
    div4_airport, 
    div4_airport_id,
    div4_airport_seq_id, 
    div4_wheels_on,
    div4_total_g_time, 
    div4_longest_g_time,
    div4_wheels_off, 
    div4_tail_num,
    div5_airport, 
    div5_airport_id,
    div5_airport_seq_id, 
    div5_wheels_on,
    div5_total_g_time, 
    div5_longest_g_time,
    div5_wheels_off, 
    div5_tail_num,
    duplicate
FROM 
    flights_2022_3
EMIT CHANGES;

INSERT INTO 
    AllFlightData
SELECT  
    id,
    flight_year,
    flight_quarter,
    flight_month,
    flight_day_of_month,
    flight_day_of_week,
    flight_date, 
    marketing_airline_network, 
    operated_or_branded_code_share_partners,
    dot_id_marketing_airline,
    iata_code_marketing_airline,
    flight_number_marketing_airline,
    originally_scheduled_code_share_airline,
    dot_id_originally_scheduled_code_share_airline, 
    iata_code_originally_scheduled_code_share_airline,
    flight_num_originally_scheduled_code_share_airline, 
    operating_airline,
    dot_id_operating_airline,
    iata_code_operating_airline,
    tail_number, 
    flight_number_operating_airline,
    origin_airport_id,
    origin_airport_seq_id,
    origin_city_market_id,
    origin,
    origin_city_name, 
    origin_state,
    origin_state_fips,
    origin_state_name,
    origin_wac origin_wac,
    dest_airport_id,
    dest_airport_seq_id,
    dest_city_market_id,
    dest, 
    dest_city_name,
    dest_state,
    dest_state_fips,
    dest_state_name, 
    dest_wac,
    crs_dep_time,
    dep_time,
    dep_delay,
    dep_delay_minutes,
    dep_del_15,
    departure_delay_groups,
    dep_time_blk, 
    taxi_out,
    wheels_off,
    wheels_on,
    taxi_in,
    crs_arr_time,
    arr_time,
    arr_delay,
    arr_delay_minutes,
    arr_del_15,
    arrival_delay_groups,
    arr_time_blk,
    cancelled,
    cancellation_code,
    diverted,
    crse_lapsed_time,
    actual_elapsed_time,
    air_time,
    flights,
    distance,
    distance_group,
    carrier_delay,
    weather_delay,
    nas_delay,
    security_delay,
    late_aircraft_delay,
    first_dep_time,
    total_add_g_time,
    longest_add_g_time,
    div_airport_landings,
    div_reached_dest, 
    div_actual_elapsed_time,
    div_arr_delay, 
    div_distance,
    div1_airport, 
    div1_airport_id,
    div1_airport_seq_id, 
    div1_wheels_on,
    div1_total_g_time, 
    div1_longest_g_time,
    div1_wheels_off, 
    div1_tail_num,
    div2_airport, 
    div2_airport_id,
    div2_airport_seq_id, 
    div2_wheels_on,
    div2_total_g_time, 
    div2_longest_g_time,
    div2_wheels_off, 
    div2_tail_num,
    div3_airport, 
    div3_airport_id,
    div3_airport_seq_id, 
    div3_wheels_on,
    div3_total_g_time, 
    div3_longest_g_time,
    div3_wheels_off, 
    div3_tail_num,
    div4_airport, 
    div4_airport_id,
    div4_airport_seq_id, 
    div4_wheels_on,
    div4_total_g_time, 
    div4_longest_g_time,
    div4_wheels_off, 
    div4_tail_num,
    div5_airport, 
    div5_airport_id,
    div5_airport_seq_id, 
    div5_wheels_on,
    div5_total_g_time, 
    div5_longest_g_time,
    div5_wheels_off, 
    div5_tail_num,
    duplicate
FROM 
    flights_2022_4
EMIT CHANGES;

INSERT INTO 
    AllFlightData
SELECT  
    id,
    flight_year,
    flight_quarter,
    flight_month,
    flight_day_of_month,
    flight_day_of_week,
    flight_date, 
    marketing_airline_network, 
    operated_or_branded_code_share_partners,
    dot_id_marketing_airline,
    iata_code_marketing_airline,
    flight_number_marketing_airline,
    originally_scheduled_code_share_airline,
    dot_id_originally_scheduled_code_share_airline, 
    iata_code_originally_scheduled_code_share_airline,
    flight_num_originally_scheduled_code_share_airline, 
    operating_airline,
    dot_id_operating_airline,
    iata_code_operating_airline,
    tail_number, 
    flight_number_operating_airline,
    origin_airport_id,
    origin_airport_seq_id,
    origin_city_market_id,
    origin,
    origin_city_name, 
    origin_state,
    origin_state_fips,
    origin_state_name,
    origin_wac origin_wac,
    dest_airport_id,
    dest_airport_seq_id,
    dest_city_market_id,
    dest, 
    dest_city_name,
    dest_state,
    dest_state_fips,
    dest_state_name, 
    dest_wac,
    crs_dep_time,
    dep_time,
    dep_delay,
    dep_delay_minutes,
    dep_del_15,
    departure_delay_groups,
    dep_time_blk, 
    taxi_out,
    wheels_off,
    wheels_on,
    taxi_in,
    crs_arr_time,
    arr_time,
    arr_delay,
    arr_delay_minutes,
    arr_del_15,
    arrival_delay_groups,
    arr_time_blk,
    cancelled,
    cancellation_code,
    diverted,
    crse_lapsed_time,
    actual_elapsed_time,
    air_time,
    flights,
    distance,
    distance_group,
    carrier_delay,
    weather_delay,
    nas_delay,
    security_delay,
    late_aircraft_delay,
    first_dep_time,
    total_add_g_time,
    longest_add_g_time,
    div_airport_landings,
    div_reached_dest, 
    div_actual_elapsed_time,
    div_arr_delay, 
    div_distance,
    div1_airport, 
    div1_airport_id,
    div1_airport_seq_id, 
    div1_wheels_on,
    div1_total_g_time, 
    div1_longest_g_time,
    div1_wheels_off, 
    div1_tail_num,
    div2_airport, 
    div2_airport_id,
    div2_airport_seq_id, 
    div2_wheels_on,
    div2_total_g_time, 
    div2_longest_g_time,
    div2_wheels_off, 
    div2_tail_num,
    div3_airport, 
    div3_airport_id,
    div3_airport_seq_id, 
    div3_wheels_on,
    div3_total_g_time, 
    div3_longest_g_time,
    div3_wheels_off, 
    div3_tail_num,
    div4_airport, 
    div4_airport_id,
    div4_airport_seq_id, 
    div4_wheels_on,
    div4_total_g_time, 
    div4_longest_g_time,
    div4_wheels_off, 
    div4_tail_num,
    div5_airport, 
    div5_airport_id,
    div5_airport_seq_id, 
    div5_wheels_on,
    div5_total_g_time, 
    div5_longest_g_time,
    div5_wheels_off, 
    div5_tail_num,
    duplicate
FROM 
    flights_2022_5
EMIT CHANGES;

INSERT INTO 
    AllFlightData
SELECT  
    id,
    flight_year,
    flight_quarter,
    flight_month,
    flight_day_of_month,
    flight_day_of_week,
    flight_date, 
    marketing_airline_network, 
    operated_or_branded_code_share_partners,
    dot_id_marketing_airline,
    iata_code_marketing_airline,
    flight_number_marketing_airline,
    originally_scheduled_code_share_airline,
    dot_id_originally_scheduled_code_share_airline, 
    iata_code_originally_scheduled_code_share_airline,
    flight_num_originally_scheduled_code_share_airline, 
    operating_airline,
    dot_id_operating_airline,
    iata_code_operating_airline,
    tail_number, 
    flight_number_operating_airline,
    origin_airport_id,
    origin_airport_seq_id,
    origin_city_market_id,
    origin,
    origin_city_name, 
    origin_state,
    origin_state_fips,
    origin_state_name,
    origin_wac origin_wac,
    dest_airport_id,
    dest_airport_seq_id,
    dest_city_market_id,
    dest, 
    dest_city_name,
    dest_state,
    dest_state_fips,
    dest_state_name, 
    dest_wac,
    crs_dep_time,
    dep_time,
    dep_delay,
    dep_delay_minutes,
    dep_del_15,
    departure_delay_groups,
    dep_time_blk, 
    taxi_out,
    wheels_off,
    wheels_on,
    taxi_in,
    crs_arr_time,
    arr_time,
    arr_delay,
    arr_delay_minutes,
    arr_del_15,
    arrival_delay_groups,
    arr_time_blk,
    cancelled,
    cancellation_code,
    diverted,
    crse_lapsed_time,
    actual_elapsed_time,
    air_time,
    flights,
    distance,
    distance_group,
    carrier_delay,
    weather_delay,
    nas_delay,
    security_delay,
    late_aircraft_delay,
    first_dep_time,
    total_add_g_time,
    longest_add_g_time,
    div_airport_landings,
    div_reached_dest, 
    div_actual_elapsed_time,
    div_arr_delay, 
    div_distance,
    div1_airport, 
    div1_airport_id,
    div1_airport_seq_id, 
    div1_wheels_on,
    div1_total_g_time, 
    div1_longest_g_time,
    div1_wheels_off, 
    div1_tail_num,
    div2_airport, 
    div2_airport_id,
    div2_airport_seq_id, 
    div2_wheels_on,
    div2_total_g_time, 
    div2_longest_g_time,
    div2_wheels_off, 
    div2_tail_num,
    div3_airport, 
    div3_airport_id,
    div3_airport_seq_id, 
    div3_wheels_on,
    div3_total_g_time, 
    div3_longest_g_time,
    div3_wheels_off, 
    div3_tail_num,
    div4_airport, 
    div4_airport_id,
    div4_airport_seq_id, 
    div4_wheels_on,
    div4_total_g_time, 
    div4_longest_g_time,
    div4_wheels_off, 
    div4_tail_num,
    div5_airport, 
    div5_airport_id,
    div5_airport_seq_id, 
    div5_wheels_on,
    div5_total_g_time, 
    div5_longest_g_time,
    div5_wheels_off, 
    div5_tail_num,
    duplicate
FROM 
    flights_2022_6
EMIT CHANGES;

INSERT INTO 
    AllFlightData
SELECT  
    id,
    flight_year,
    flight_quarter,
    flight_month,
    flight_day_of_month,
    flight_day_of_week,
    flight_date, 
    marketing_airline_network, 
    operated_or_branded_code_share_partners,
    dot_id_marketing_airline,
    iata_code_marketing_airline,
    flight_number_marketing_airline,
    originally_scheduled_code_share_airline,
    dot_id_originally_scheduled_code_share_airline, 
    iata_code_originally_scheduled_code_share_airline,
    flight_num_originally_scheduled_code_share_airline, 
    operating_airline,
    dot_id_operating_airline,
    iata_code_operating_airline,
    tail_number, 
    flight_number_operating_airline,
    origin_airport_id,
    origin_airport_seq_id,
    origin_city_market_id,
    origin,
    origin_city_name, 
    origin_state,
    origin_state_fips,
    origin_state_name,
    origin_wac origin_wac,
    dest_airport_id,
    dest_airport_seq_id,
    dest_city_market_id,
    dest, 
    dest_city_name,
    dest_state,
    dest_state_fips,
    dest_state_name, 
    dest_wac,
    crs_dep_time,
    dep_time,
    dep_delay,
    dep_delay_minutes,
    dep_del_15,
    departure_delay_groups,
    dep_time_blk, 
    taxi_out,
    wheels_off,
    wheels_on,
    taxi_in,
    crs_arr_time,
    arr_time,
    arr_delay,
    arr_delay_minutes,
    arr_del_15,
    arrival_delay_groups,
    arr_time_blk,
    cancelled,
    cancellation_code,
    diverted,
    crse_lapsed_time,
    actual_elapsed_time,
    air_time,
    flights,
    distance,
    distance_group,
    carrier_delay,
    weather_delay,
    nas_delay,
    security_delay,
    late_aircraft_delay,
    first_dep_time,
    total_add_g_time,
    longest_add_g_time,
    div_airport_landings,
    div_reached_dest, 
    div_actual_elapsed_time,
    div_arr_delay, 
    div_distance,
    div1_airport, 
    div1_airport_id,
    div1_airport_seq_id, 
    div1_wheels_on,
    div1_total_g_time, 
    div1_longest_g_time,
    div1_wheels_off, 
    div1_tail_num,
    div2_airport, 
    div2_airport_id,
    div2_airport_seq_id, 
    div2_wheels_on,
    div2_total_g_time, 
    div2_longest_g_time,
    div2_wheels_off, 
    div2_tail_num,
    div3_airport, 
    div3_airport_id,
    div3_airport_seq_id, 
    div3_wheels_on,
    div3_total_g_time, 
    div3_longest_g_time,
    div3_wheels_off, 
    div3_tail_num,
    div4_airport, 
    div4_airport_id,
    div4_airport_seq_id, 
    div4_wheels_on,
    div4_total_g_time, 
    div4_longest_g_time,
    div4_wheels_off, 
    div4_tail_num,
    div5_airport, 
    div5_airport_id,
    div5_airport_seq_id, 
    div5_wheels_on,
    div5_total_g_time, 
    div5_longest_g_time,
    div5_wheels_off, 
    div5_tail_num,
    duplicate
FROM 
    flights_2022_7
EMIT CHANGES;

SHOW QUERIES;
PRINT AllFlightData FROM BEGINNING LIMIT 25;
SELECT * FROM AllFlightData EMIT CHANGES;


-- Create the Intermediate STREAM(s) &/or TABLE(s)
CREATE STREAM AllRecordsMainFeatures
WITH 
(
    KAFKA_TOPIC='AllRecordsMainFeatures', 
    VALUE_FORMAT='AVRO', 
    partitions=1
)
AS 
SELECT    
    id,
    flight_year, flight_quarter,
    flight_month, flight_day_of_month,
    flight_day_of_week, flight_date,
    marketing_airline_network, operated_or_branded_code_share_partners,
    dot_id_marketing_airline, iata_code_marketing_airline,
    flight_number_marketing_airline, originally_scheduled_code_share_airline,
    dot_id_originally_scheduled_code_share_airline, iata_code_originally_scheduled_code_share_airline,
    flight_num_originally_scheduled_code_share_airline, operating_airline,
    dot_id_operating_airline, iata_code_operating_airline,
    tail_number, flight_number_operating_airline,
    origin_airport_id, origin_airport_seq_id,
    origin_city_market_id, origin,
    origin_city_name, origin_state,
    origin_state_fips, origin_state_name,
    origin_wac, dest_airport_id,
    dest_airport_seq_id, dest_city_market_id,
    dest, dest_city_name,
    dest_state, dest_state_fips,
    dest_state_name, dest_wac,
    crs_dep_time, dep_time,
    dep_delay, dep_delay_minutes,
    dep_del_15, departure_delay_groups,
    dep_time_blk, taxi_out,
    wheels_off, wheels_on,
    taxi_in, crs_arr_time,
    arr_time, arr_delay,
    arr_delay_minutes, arr_del_15,
    arrival_delay_groups, arr_time_blk,
    cancelled, cancellation_code,
    diverted, crse_lapsed_time,
    actual_elapsed_time, air_time,
    flights, distance,
    distance_group, carrier_delay,
    weather_delay, nas_delay,
    security_delay, late_aircraft_delay,
    first_dep_time, total_add_g_time,
    longest_add_g_time, div_airport_landings,
    div_reached_dest, div_actual_elapsed_time,
    div_arr_delay, div_distance
FROM 
    AllFlightData
PARTITION BY 
    id
EMIT CHANGES;

CREATE STREAM AllRecordsMainFeaturesWithOriginGeorgiaState
WITH 
(
    KAFKA_TOPIC='AllRecordsMainFeaturesWithOriginGeorgiaState',
    VALUE_FORMAT='AVRO',
    partitions=1
)
AS 
    SELECT
        id,
        flight_year, flight_quarter,
        flight_month, flight_day_of_month,
        flight_day_of_week, flight_date,
        marketing_airline_network, operated_or_branded_code_share_partners,
        dot_id_marketing_airline, iata_code_marketing_airline,
        flight_number_marketing_airline, originally_scheduled_code_share_airline,
        dot_id_originally_scheduled_code_share_airline, iata_code_originally_scheduled_code_share_airline,
        flight_num_originally_scheduled_code_share_airline, operating_airline,
        dot_id_operating_airline, iata_code_operating_airline,
        tail_number, flight_number_operating_airline,
        origin_airport_id, origin_airport_seq_id,
        origin_city_market_id, origin,
        origin_city_name, origin_state,
        origin_state_fips, origin_state_name,
        origin_wac, dest_airport_id,
        dest_airport_seq_id, dest_city_market_id,
        dest, dest_city_name,
        dest_state, dest_state_fips,
        dest_state_name, dest_wac,
        crs_dep_time, dep_time,
        dep_delay, dep_delay_minutes,
        dep_del_15, departure_delay_groups,
        dep_time_blk, taxi_out,
        wheels_off, wheels_on,
        taxi_in, crs_arr_time,
        arr_time, arr_delay,
        arr_delay_minutes, arr_del_15,
        arrival_delay_groups, arr_time_blk,
        cancelled, cancellation_code,
        diverted, crse_lapsed_time,
        actual_elapsed_time, air_time,
        flights, distance,
        distance_group, carrier_delay,
        weather_delay, nas_delay,
        security_delay, late_aircraft_delay,
        first_dep_time, total_add_g_time,
        longest_add_g_time, div_airport_landings,
        div_reached_dest, div_actual_elapsed_time,
        div_arr_delay, div_distance
    FROM
        AllFlightData
    WHERE
        LCASE(origin_state_name) = 'georgia'
    EMIT CHANGES;

SHOW STREAMS;
SHOW TOPICS;

PRINT AllRecordsMainFeatures FROM BEGINNING LIMIT 10;
PRINT AllRecordsMainFeaturesWithOriginGeorgiaState FROM BEGINNING LIMIT 10;

SELECT * FROM AllRecordsMainFeatures EMIT CHANGES;
SELECT * FROM AllRecordsMainFeaturesWithOriginGeorgiaState EMIT CHANGES;

-- CREATE SINK CONNECTOR(s)
CREATE SINK CONNECTOR IF NOT EXISTS flights_data_sink_conn_pg_all_data WITH (
    "name" = 'flights_data_sink_conn_pg_all_data',
    "connector.class" = 'io.confluent.connect.jdbc.JdbcSinkConnector',
    "dialect.name" = 'PostgreSqlDatabaseDialect',
    "connection.url" = 'jdbc:postgresql://postgres:5432/flight_files_target',
    "connection.user" = 'pg',
    "connection.password" = 'pg',
    "output.data.format" = 'avro',
    "auto.create" = 'true',
    "auto.evolve" = 'true',
    "table.name.format" = '${topic}',
    "insert.mode" = 'insert',
    "tasks.max" = '1',
    "topics" = 'AllFlightData',
    "key.converter.schemas.enable" = 'false',
    "value.converter.schemas.enable" = 'false',
    "table.types" = 'TABLE'
);



CREATE SINK CONNECTOR IF NOT EXISTS flights_data_sink_conn_pg_main_features WITH (
    "name" = 'flights_data_sink_conn_pg_main_features',
    "connector.class" = 'io.confluent.connect.jdbc.JdbcSinkConnector',
    "dialect.name" = 'PostgreSqlDatabaseDialect',
    "connection.url" = 'jdbc:postgresql://postgres:5432/flight_files_target',
    "connection.user" = 'pg',
    "connection.password" = 'pg',
    "output.data.format" = 'avro',
    "auto.create" = 'true',
    "auto.evolve" = 'true',
    "table.name.format" = '${topic}',
    "insert.mode" = 'insert',
    "tasks.max" = '1',
    "topics" = 'AllRecordsMainFeatures',
    "key.converter.schemas.enable" = 'false',
    "value.converter.schemas.enable" = 'false',
    "table.types" = 'TABLE'
);

CREATE SINK CONNECTOR IF NOT EXISTS flights_data_sink_conn_pg_all_data_for_georgia WITH (
    "name" = 'flights_data_sink_conn_pg_all_data_for_georgia',
    "topics" = 'AllRecordsMainFeaturesWithOriginGeorgiaState',
    "connector.class" = 'io.confluent.connect.jdbc.JdbcSinkConnector',
    "dialect.name" = 'PostgreSqlDatabaseDialect',
    "connection.url" = 'jdbc:postgresql://postgres:5432/flight_files_target',
    "connection.user" = 'pg',
    "connection.password" = 'pg',
    "output.data.format" = 'avro',
    "auto.create" = 'true',
    "auto.evolve" = 'true',
    "table.name.format" = '${topic}',
    "insert.mode" = 'insert',
    "tasks.max" = '1',
    "key.converter.schemas.enable" = 'false',
    "value.converter.schemas.enable" = 'false',
    "table.types" = 'TABLE'
);


-- Some metadata Commands
SHOW TOPICS;
SHOW STREAMS;
SHOW CONNECTORS;
SHOW QUERIES;

-- Describe SOURCE CONNECTOR(s)
DESCRIBE CONNECTOR flight_data_records_source_conn_ms_ss;

-- Describe SINK CONNECTOR(s)
DESCRIBE CONNECTOR FLIGHTS_DATA_SINK_CONN_PG_ALL_DATA;
DESCRIBE CONNECTOR FLIGHTS_DATA_SINK_CONN_PG_ALL_DATA_FOR_GEORGIA;
DESCRIBE CONNECTOR FLIGHTS_DATA_SINK_CONN_PG_MAIN_FEATURES;

-- Describe STREAM(s)
DESCRIBE AllFlightData EXTENDED;
DESCRIBE AllRecordsMainFeatures EXTENDED;
DESCRIBE AllRecordsMainFeaturesWithOriginGeorgiaState EXTENDED;
 
DESCRIBE FLIGHTS_2022_1 EXTENDED;
DESCRIBE FLIGHTS_2022_2 EXTENDED;
DESCRIBE FLIGHTS_2022_3 EXTENDED;
DESCRIBE FLIGHTS_2022_4 EXTENDED;
DESCRIBE FLIGHTS_2022_5 EXTENDED;
DESCRIBE FLIGHTS_2022_6 EXTENDED;
DESCRIBE FLIGHTS_2022_7 EXTENDED;


-- To check that data made it to Postgres as expected:
-- AllFlightData
echo 'SELECT * FROM "AllFlightData" LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER flight_files_target'
echo 'SELECT COUNT("FLIGHT_YEAR") AS Num_of_Records FROM "AllFlightData";' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER flight_files_target'

-- AllRecordsMainFeatures
echo 'SELECT * FROM "AllRecordsMainFeatures" LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER flight_files_target'
echo 'SELECT COUNT("FLIGHT_YEAR") AS Num_of_Records FROM "AllRecordsMainFeatures";' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER flight_files_target'

-- AllRecordsMainFeaturesWithOriginGeorgiaState
echo 'SELECT * FROM "AllRecordsMainFeaturesWithOriginGeorgiaState" LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER flight_files_target'
echo 'SELECT COUNT("FLIGHT_YEAR") AS Num_of_Records FROM "AllRecordsMainFeaturesWithOriginGeorgiaState";' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER flight_files_target'


/*
#docker compose command to develop interactively:

docker exec -it ksqldb-cli ksql http://ksqldb-server:8088
*/

-- Statements to remove STREAM(s) & CONNECTOR(s)
-- start with the SINK CONNECTOR(s)
DROP CONNECTOR flights_data_sink_conn_pg_all_data_for_georgia;
DROP CONNECTOR FLIGHTS_DATA_SINK_CONN_pg_MAIN_FEATURES;
DROP CONNECTOR FLIGHTS_DATA_SINK_CONN_pg_ALL_DATA;



-- Next, the intermediate &/or output STREAM(s) &/or TABLE(s) [& their associated TOPIC(s)]
DROP STREAM AllRecordsMainFeatures DELETE TOPIC;
DROP STREAM AllRecordsMainFeaturesWithOriginGeorgiaState DELETE TOPIC;

-- need t terminate insert queries prior to removing the AllFlightData topic and stream
TERMINATE INSERTQUERY_17;
TERMINATE INSERTQUERY_19;
TERMINATE INSERTQUERY_21;
TERMINATE INSERTQUERY_23;
TERMINATE INSERTQUERY_25;
TERMINATE INSERTQUERY_27;
TERMINATE INSERTQUERY_29;


DROP STREAM AllFlightData DELETE TOPIC;

-- Next, the input STREAM(s) &/or TABLE(s) [& their associated TOPIC(s)]
DROP STREAM flights_2022_1 DELETE TOPIC;
DROP STREAM flights_2022_2 DELETE TOPIC;
DROP STREAM flights_2022_3 DELETE TOPIC;
DROP STREAM flights_2022_4 DELETE TOPIC;
DROP STREAM flights_2022_5 DELETE TOPIC;
DROP STREAM flights_2022_6 DELETE TOPIC;
DROP STREAM flights_2022_7 DELETE TOPIC;

-- Finally, the SOURCE CONNECTOR(s)
DROP CONNECTOR flight_data_records_source_conn_ms_ss;

-- show that all topics, streams, connectors, and queries were actually removed
SHOW QUERIES;
SHOW CONNECTORS;
SHOW STREAMS;
SHOW TOPICS;
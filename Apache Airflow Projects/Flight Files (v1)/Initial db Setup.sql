-- Create a temporary table to store the file names
CREATE TEMPORARY TABLE temp_file_list (file_name text);

DO $$ 
DECLARE
    file_name text;
    new_table_name text;
    file_path TEXT := '/Users/briandunn/Desktop/Large Data Files/flight_files/data/';
BEGIN
    -- Insert the file names into the temporary table
    EXECUTE format('INSERT INTO temp_file_list SELECT unnest(string_to_array(trim(trailing E''\n'' FROM pg_ls_dir(%L)), E''\n''))', file_path);
	
    -- Loop through files
    FOR file_name IN (SELECT a.file_name FROM temp_file_list AS a)
    LOOP
        -- Extract table name from file name
        new_table_name := split_part(file_name, '.', 1);

		-- DROP Table IF EXISTS
		EXECUTE format('DROP TABLE IF EXISTS %I', new_table_name);

		-- Create the table if it doesn't exist
        EXECUTE format('CREATE TABLE %I (Year INTEGER,
			Quarter INTEGER,
			Month INTEGER,
			DayofMonth INTEGER,
			DayOfWeek INTEGER,
			FlightDate VARCHAR,
			Marketing_Airline_Network VARCHAR,
			Operated_or_Branded_Code_Share_Partners VARCHAR,
			DOT_ID_Marketing_Airline INTEGER,
			IATA_Code_Marketing_Airline VARCHAR,
			Flight_Number_Marketing_Airline INTEGER,
			Originally_Scheduled_Code_Share_Airline VARCHAR,
			DOT_ID_Originally_Scheduled_Code_Share_Airline VARCHAR,
			IATA_Code_Originally_Scheduled_Code_Share_Airline VARCHAR,
			Flight_Num_Originally_Scheduled_Code_Share_Airline VARCHAR,
			Operating_Airline VARCHAR,
			DOT_ID_Operating_Airline INTEGER,
			IATA_Code_Operating_Airline VARCHAR,
			Tail_Number VARCHAR,
			Flight_Number_Operating_Airline INTEGER,
			OriginAirportID INTEGER,
			OriginAirportSeqID INTEGER,
			OriginCityMarketID INTEGER,
			Origin VARCHAR,
			OriginCityName VARCHAR,
			OriginState VARCHAR,
			OriginStateFips FLOAT,
			OriginStateName VARCHAR,
			OriginWac INTEGER,
			DestAirportID INTEGER,
			DestAirportSeqID INTEGER,
			DestCityMarketID INTEGER,
			Dest VARCHAR,
			DestCityName VARCHAR,
			DestState VARCHAR,
			DestStateFips INTEGER,
			DestStateName VARCHAR,
			DestWac INTEGER,
			CRSDepTime INTEGER,
			DepTime INTEGER,
			DepDelay FLOAT,
			DepDelayMinutes FLOAT,
			DepDel15 FLOAT,
			DepartureDelayGroups INTEGER,
			DepTimeBlk VARCHAR,
			TaxiOut FLOAT,
			WheelsOff INTEGER,
			WheelsOn INTEGER,
			TaxiIn FLOAT,
			CRSArrTime INTEGER,
			ArrTime INTEGER,
			ArrDelay FLOAT,
			ArrDelayMinutes FLOAT,
			ArrDel15 FLOAT,
			ArrivalDelayGroups INTEGER,
			ArrTimeBlk VARCHAR,
			Cancelled FLOAT,
			CancellationCode VARCHAR,
			Diverted FLOAT,
			CRSElapsedTime FLOAT,
			ActualElapsedTime FLOAT,
			AirTime FLOAT,
			Flights FLOAT,
			Distance FLOAT,
			DistanceGroup INTEGER,
			CarrierDelay FLOAT,
			WeatherDelay FLOAT,
			NASDelay FLOAT,
			SecurityDelay FLOAT,
			LateAircraftDelay FLOAT,
			FirstDepTime INTEGER,
			TotalAddGTime FLOAT,
			LongestAddGTime FLOAT,
			DivAirportLandings INTEGER,
			DivReachedDest VARCHAR,
			DivActualElapsedTime VARCHAR,
			DivArrDelay VARCHAR,
			DivDistance VARCHAR,
			Div1Airport VARCHAR,
			Div1AirportID VARCHAR,
			Div1AirportSeqID VARCHAR,
			Div1WheelsOn VARCHAR,
			Div1TotalGTime VARCHAR,
			Div1LongestGTime VARCHAR,
			Div1WheelsOff VARCHAR,
			Div1TailNum VARCHAR,
			Div2Airport VARCHAR,
			Div2AirportID VARCHAR,
			Div2AirportSeqID VARCHAR,
			Div2WheelsOn VARCHAR,
			Div2TotalGTime VARCHAR,
			Div2LongestGTime VARCHAR,
			Div2WheelsOff VARCHAR,
			Div2TailNum VARCHAR,
			Div3Airport VARCHAR,
			Div3AirportID VARCHAR,
			Div3AirportSeqID VARCHAR,
			Div3WheelsOn VARCHAR,
			Div3TotalGTime VARCHAR,
			Div3LongestGTime VARCHAR,
			Div3WheelsOff VARCHAR,
			Div3TailNum VARCHAR,
			Div4Airport VARCHAR,
			Div4AirportID VARCHAR,
			Div4AirportSeqID VARCHAR,
			Div4WheelsOn VARCHAR,
			Div4TotalGTime VARCHAR,
			Div4LongestGTime VARCHAR,
			Div4WheelsOff VARCHAR,
			Div4TailNum VARCHAR,
			Div5Airport VARCHAR,
			Div5AirportID VARCHAR,
			Div5AirportSeqID VARCHAR,
			Div5WheelsOn VARCHAR,
			Div5TotalGTime VARCHAR,
			Div5LongestGTime VARCHAR,
			Div5WheelsOff VARCHAR,
			Div5TailNum VARCHAR,
			Duplicate VARCHAR)', 
	   new_table_name);

        -- Copy data into the corresponding table
        EXECUTE format('COPY %I FROM %L WITH CSV HEADER;', new_table_name, file_path || file_name);
    END LOOP;
END $$;
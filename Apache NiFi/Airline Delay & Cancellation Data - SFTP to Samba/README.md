# Airline Delay & Cancellation Data - Apache NiFi Pipeline

This project retrieves data files via an SFTP server/connection, makes transformations and then sends it to a shared directory in Samba. Apache NiFi, SFTP, and Samba are all in their own docker containers.

I have included the Flow Definition Files (both with and without exernal services).

## Notes


- Because the original files were rather large, I used Polars to break each down into 4 (approximately same sized) files.

- Handle Discrete/Categorical Values according to these conversions:
    - OP_CARRIER
        - 'OO' -> 0
        - 'OH' -> 1
        - 'HA' -> 2
        - 'FL' -> 3
        - 'YX' -> 4
        - 'AS' -> 5
        - 'MQ' -> 6
        - 'YV' -> 7
        - 'WN' -> 8
        - 'AA' -> 9
        - 'XE' -> 10
        - 'CO' -> 11
        - 'EV' -> 12
        - 'NW' -> 13
        - 'VX' -> 14
        - 'UA' -> 15
        - 'F9' -> 16
        - '9E' -> 17
        - 'B6' -> 18
        - 'G4' -> 19
        - 'DL' -> 20
        - 'NK' -> 21
        - 'US' -> 22
        - (all other values) -> -1
    - CANCELLATION_CODE
        - 'A' -> 0
        - 'B' -> 1
        - 'C' -> 2
        - 'D' -> 3
        - None -> -1
        - (all other values) -> -1
- Handle missing data (impute data)
    - Remove records that have nulls in these columns as they represent such a small number of the overall records:
        - CRS_DEP_TIME
        - CRS_ARR_TIME
        - CRS_ELAPSED_TIME
    - Assume that these do not have a cancellation code because they was no need to worry about it since the planes were on time:
        - CARRIER_DELAY
        - WEATHER_DELAY
        - NAS_DELAY
        - SECURITY_DELAY
        - LATE_AIRCRAFT_DELAY
    - Impute with -1 for now:
        - DEP_TIME
        - DEP_DELAY
        - TAXI_OUT
        - WHEELS_OFF
        - WHEELS_ON
        - TAXI_IN
        - ARR_TIME 
        - ARR_DELAY
        - CANCELLATION_CODE
        - ACTUAL_ELAPSED_TIME
        - AIR_TIME
- Drop the 'Unnamed: 27' column as all values are null
- Rename columns:
    - Basically, I will convert the text to lowercase text

## Dataset Source
https://www.kaggle.com/datasets/yuanyuwendymu/airline-delay-and-cancellation-data-2009-2018
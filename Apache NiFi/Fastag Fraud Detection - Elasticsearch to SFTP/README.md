# Fastag Fraud Detection - Apache NiFi Pipeline

This project retrieves data from a table in Elasticsearch, makes transformations, converts it to CSV file format, and then sends it to file via SFTP. Apache NiFi, Elasticsearch, and SFTP are all in their own docker containers.

I have included the Flow Definition Files (both with and without exernal services).

## Notes

- Convert string categorical values to integers according to these charts:
    - vehicle_type:
        - 'Bus ' -> 0
        - 'Car' -> 1
        - 'Motorcycle' -> 2
        - 'Sedan' -> 3
        - 'SUV' -> 4
        - 'Truck' -> 5
        - 'Van' -> 6
    - toll_booth_id:
        - 'A-101' -> 0
        - 'B-102' -> 1
        - 'D-104' -> 2
        - 'C-103' -> 3
        - 'D-105' -> 4
        - 'D-106' -> 5
    - lane_type:
        - 'Express' -> 0
        - 'Regular' -> 1
    - vehicle_dims: 
        - 'Small' -> 0
        - 'Medium' -> 1
        - 'Large' -> 2
    - fraud_indicator: 
        - 'Not Fraud' -> 0
        - 'Fraud' -> 1
- The only column/feature with any missing values is: fastag_id. Impute with -1.
- I need to trim leading and trailing whitespace from these columns:
    - transaction_timestamp
    - vehicle_plate_number
- I need to handle these date & time feature(s)/column(s):
    - transaction_timestamp

## Dataset Source
https://www.kaggle.com/datasets/samruddhi4040/online-sales-data?select=Details.csv

# Move Flight Data From SQL Server to Postgres

## Topic Description

This project moves a table of flight data from a Microsoft SQL Server database (in a docker container) to a table in a Postgres database via (Confluent) Kafka Connect.

## Dataset Source

https://www.kaggle.com/datasets/robikscube/flight-delay-dataset-20182022

## Other Notes

- I wrote a bash shell script that  inserts records in batches of 500 records at a time.
- All services are in docker containers.
- I defined all fields/columns as varchar when I was debugging some issues and wanted to rule out other variables.
- In the future, I might change those to more accurate data types now that the project is running smoothly.
- Also, I intend to start including some advanced features such as using both replication and multiple partitions.
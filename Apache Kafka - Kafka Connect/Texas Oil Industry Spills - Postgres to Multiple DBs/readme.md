# Texas Oil Industry Spills - Postgres to Multiple DBs

## Project Description

This project transfers two tables of data from Postgres to MariaDB, MongoDB, and MySQL via Apache Kafka Connect using JDBC and MongoDB Connectors.

## Dataset Source

https://kaggle.com/datasets/sujaykapadnis/texas-oil-and-gas-industry-water-spills-2013-2022

## Other Notes

- The JDBC connector downloads via a startup script. 
- The MariaDB driver should download automatically via the startup script included with the connect container.
- The MySQL driver should download automatically as part of that startup script; if not, you may have to manually download it and insert it into the correct folder (I placed it in the data/connect-jars subdirectory).
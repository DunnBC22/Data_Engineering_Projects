# Transfer Supply Chain Data from Postgres to MongoDB

## Project Description

This project transfers a table of data from Postgres to MongoDB in Apache Kafka Connect using the JDBC Postgres and MongoDB Connectors (respectively).

## Dataset Source

https://www.kaggle.com/datasets/shashwatwork/dataco-smart-supply-chain-for-big-data-analysis?select=DataCoSupplyChainDataset.csv

## Other Notes

- As I have had to do with many of my other projects, I had to trim the size of the 3_inserts.sql file to meet the file size requirement for GitHub. That said, I have included a script to allow you to recreate the full file of INSERT INTO statements rather quickly!
- The source to download the connector jar file: https://www.confluent.io/hub/mongodb/kafka-connect-mongodb.
- Make sure to follow the links from the documentation in the downloaded connector instead of online. There seems to be some conflicting information about the configurations.
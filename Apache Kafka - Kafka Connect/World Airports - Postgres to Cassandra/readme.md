# World Airports - Postgres to Apache Cassandra

## Project Description

In this project, I transferred a Postgres table of data to an Apache Cassandra table using Apache Kafka.

## Dataset Source

https://www.kaggle.com/datasets/mexwell/world-airports

## Other Notes

- For some reason, the script that I put together to convert the csv file of data into INSERT statements struggled with the first column (x_coord). Thus, most (if not all) of them are null values. While I looked past it in this case because I am merely looking to demonstrate my abilities with Apache Kafka and Apache Cassandra, I would normally go back and make sure that that column of data is included. In that case, the treatment of the x_coord column should be identical to the y_coord.
- The instructions for how to download and install the Apache Cassandra connector, visit this site: https://docs.datastax.com/en/kafka/doc/kafka/install/kafkaInstall.html.
- In porder to comply with the maximum file size requirement for GitHub, I had to trim the size of the 3_inserts.sql file. I have included a quick script to generate the insert statements to help with most of the setup. That said, there were some 'illegal characters' that you will have to manually remove/edit/change in the 3_inserts.sql file.
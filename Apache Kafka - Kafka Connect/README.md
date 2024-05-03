# Apache Kafka (Kafka Connect) Projects

## Process Used
1. I manually downloaded and copied the jar (connector) file into data folder.
    + This file was placed in the data/connect-jars subdirectory.
2. Convert the csv data files into insert statements. For this, I wrote a script that does (at least most of the work). 
    + Sometimes, I had to make some minor adjustments to the INSERT INTO statements outside of the script that I wrote.
    + This script was placed in sql-scripts subdirectory.
3. Create the statements to create both the original table(s) and the target database. Additionally, I created the statements that provided correct privileges to allow Kafka to select data from the source tables and the target database.
    + This step includes putting the different startup scripts in the proper order.
    + These scripts were placed in sql-scripts subdirectory.
4. Write & execute 'echo' statements to make sure that the tables were created & contain the data as expected.
    + These statements are in the Main_Statements.sql file.
5. Create the Source connectors.
    + These statements are in the Main_Statements.sql file.
6. Create the input STREAM(s).
    + Admittedly, I borrowed a lot of this work from my previous projects. 
    + These statements are in the Main_Statements.sql file.
7. Create the intermediate & output STREAM(s).
    + By output STREAM(s), I mean the data that the SINK CONNECTOR(s) will send to database tables. This was not the meant to mean the SINK CONNECTOR(s) themselves.
    + These statements are in the Main_Statements.sql file.
8. Create the SINK CONNECTORS.
    + These auto-created tables in the provided database and then inserted the data into those tables.
    + These statements are in the Main_Statements.sql file.
9. Finally, I created & executed some 'echo' statements to run in the bash shell to make sure that the SINK CONNECTORS were sending the correct data to the target database tables.
    + These statements are in the Main_Statements.sql file.

* Sometimes, I dropped the connectors, streams, and tables. I did not always do this, but I should have done this for all of the projects here.

## List of Projects (With Specific Notes About Each)

+ Analyzing the Impact
    + Multiple tables with different schema
+ Car_Spec_Dataset
    + Since the INSERT INTO file was originally over 48 MB, I trimmed it to fit within 25 MB. That said, if you are looking for the full dataset, you will need to go to the URL, download the dataset, and convert the the CSV file to INSERT INTO statements.
+ Chicago Traffic Crashes CPD
    + Single table with over 794,000 records/samples
    + Since the INSERT INTO file was originally over 1 GB, I trimmed it to fit within 25 MB. That said, if you are looking for the full dataset, you will need to go to the URL, download the dataset, and convert the the CSV file to INSERT INTO statements.
+ Cryptocurrencies Prices
    + Multiple tables with the same schema
+ Fuel Prices in Ontario
+ Household Energy Data
+ MAANG Share Prices Thru February 2024
    + Multiple tables with the same schema
+ Mock Marketing Schema
    + Multiple tables with different schema

## Other Notes

+ The dataset source (URL) is located within the `dataset source.txt` file within each project.
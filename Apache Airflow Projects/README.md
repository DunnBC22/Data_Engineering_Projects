# Apache Airflow Projects

## Description

To demonstrate my skill using Apache Airflow, I thought I would complete a plethora of projects! They use Postgres & Python Operators as well as subdags to complete data pipeline operations like imputing & handling missing values, removing outliers, and extracting different parts of time and date values.

## Notes

- The notes file contains the link to the data source
- I preloaded the data into Postgres table(s) to most closely mimic real life/work projects. 
- I created databases and the security access in the PgAdmin4 Graphical User Interface. Then, I ran the code that is located in the `Initial Table Creation & Setup` file in each project folder to create the table(s).
- After each pipeline completed, I ran a quick script on each of the fact tables to show that the transformations worked as expected. The results of those are contained in the `output_descriptive_statistics` subfolder of each project.
- I added a copy of the script that I use to retrieve the descriptive statistics of the output in teh `Assessment Script` subfolder.
- Each project should also have the log files from when I ran them locally.
- I did not normalize the data since there are a plethora of options to do so and they are dependent on which regression or classification algorithm you choose.
- I did not remove class imbalance for any of the classification datasets with class imbalance.

## Project Listings

- Allegheny Co Property Sale Transactions
- CA Housing Data
- Consumer Behavior and Shopping Habits Dataset
- Customer Shopping Trends
- Cyclistic Summary Data (Cyclistic_All_Year_Summary)
- Diamonds
- Different Store Sales
- Electric Vehicle Population
- Healthcare Insurance
- Home Insurance Dataset
- House Price Prediction - Zameen.com Dataset
- Insurance Product Purchase Prediction
- New York Motor Vehicle Collisions
- Online Shopping Dataset
- PPP via FOIA
- Predict Accident Risk Score for Unique postcodes
- Travel Insurance



# Consumer Complaints - KNIME Pipeline

## Description

- This pipeiline:
    - Reads in compressed file from SFTP (including retrieving file from sftp, uncompressing file, & reading CSV file content)
        - The numbers in the comments for each on the relevant nodes signify the order of operations since visually tough to outline
    - Transforms Data:
        - Impute missing values
        - Remove excess whitespace (duplicate values as well as leading and trailing whitespace)
        - Convert dates from String to date data type
        - Extract Date Parts from both date values.
        - Rename column names
    - Sends transformed data to Postgres table (after creating the Postgres table)


## Dataset Source
https://www.kaggle.com/datasets/meetnagadia/consumer-complaint-finance
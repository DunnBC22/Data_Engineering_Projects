# Iowa Liquor Sales - KNIME Pipeline


## Notes

- This pipeline:
    - Retrieves data from zipped CSV file (& decompresses it)
    - Transforms data:
        - Handle/Impute missing data
            - Remove any records with any missing values
        - Fix erroneous values as needed
            - Since the zip codes were made up for this data set, I am going to pick a random number to fix the 712-2 zip code issue.
        - Clean values in string features
        - Convert Features to Proper Data Type(s)
        - Extract date parts from SalesDate
        - Rename features
    - Sends transformed data to Postgres table (that was also created within this pipeline)

## Dataset Source
https://www.kaggle.com/datasets/prattayds/iowa-liquor-sales-full-dataset

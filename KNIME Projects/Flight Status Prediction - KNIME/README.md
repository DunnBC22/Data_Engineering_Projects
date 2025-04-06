# Flight Status Prediction - KNIME Pipeline

## Description

- This pipeline:
    - Retrieves a list of parquet files from an SFTP connection
    - Transforms data, via the following:
        - Remove erroneous feature
        - Impute missing values
        - Rename features
        - Extract Date Parts
        - Convert Date to String data type to prepare it for target database
    - Send transformed data to Postgres Table

## Dataset Source
https://www.kaggle.com/datasets/robikscube/flight-delay-dataset-20182022
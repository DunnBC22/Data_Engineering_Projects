# Comprehensive Supply Chain Analysis - KNIME Pipeline

## Description

- This pipeline:
    - Retrieve data from a MySQL table
    - Transforms the data as follows:
        - Clean currency-related features and convert from String to integer
        - Remove Single Value Feature(s)
        - Reformat dates & extract Date parts
        - Rename Features
    - Sends transformed data to Postgres table

## Dataset Source
https://www.kaggle.com/datasets/dorothyjoel/us-regional-sales
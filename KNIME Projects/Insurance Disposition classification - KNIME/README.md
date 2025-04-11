# Insurance Disposition Classification - KNIME Pipeline

## Notes/Description

- This pipeline:
    - Retrieves data from three individual Postgres tables and joins them into one table (removing duplicate features from those joins)
    - Transforms data, via:
        - Remove City (name) feature
            - Since there is a 1:1 correlation for city and city code. Removing city (name) saves more space.
        - Clean values (mainly in Discrete-valued Features)
            - Append original feature name as well as remove whitespaces and punctuation from:
                - EnterpriseType
                - ProductInsured
                - ClaimType
                - ClaimSite
        - Append original feature name (without whitespace) to CityCode values
        - Rename Features
        - One Hot Encode (OHE) Discrete-Valued Features
        - LabelEncode Disposition (Target Value)
            - These are the unique values for disposition:
                - Deny -> 0
                - Approve in Full -> 1
                - Settle -> 2
            - Since structured data usually does not use neural networks, I decided to go with labelencode approach since it is more likely than not that the analysis done will require that instead of the One Hot Encode approach. The target/result column is Disposition.
    - Sends transformed data to parquet and XML files on SFTP
    - __** Other notes:__
        - There were no missing values in the original data.

## Dataset Source
https://www.kaggle.com/datasets/yetcherlaajay/insurance-disposition-classification?select=Insurance_Date_data.csv
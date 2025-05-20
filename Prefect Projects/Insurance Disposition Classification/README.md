# Insurance Disposition Classification - Prefect Pipeline


## Description

- These are the transformations I applied to this dataset:
    - Individual inputs
        - Main Table
            - Rename Features
                - "Claim Number": "ClaimNumber",
                - "City Code": "CityCode",
                - "City": "CityName",
                - "Enterprise Type": "EnterpriseType",
                - "Claim Type": "ClaimType",
                - "Claim Site": "ClaimSite",
                - "Product Insured": "ProductInsured"
        - Dates Table
            - Rename Features
                - "Claim Number": "ClaimNumber",
                - "Incident Date": "IncidentDate",
                - "Date Received": "DateReceived"
        - Results Table
            - Rename Features
                - "Claim Number": "ClaimNumber",
                - "Claim Amount": "ClaimAmount",
                - "Close Amount": "CloseAmount"
    - Join the inputs based on the ClaimNumber feature
    - Clean Values:
        - Remove leading & trailing whitespace:
            - ClaimNumber
            - CityCode
            - CityName
            - EnterpriseType
            - ClaimType
            - ClaimSite
            - ProductInsured
            - Disposition
        - Remove periods, commas, dashes, as well as both opening and closing parentheses THEN titlecase THEN remove all whitespace
            - EnterpriseType
            - ProductInsured
        - Remove all whitespace
            - Claim Type
            - Claim Site
    - Handle dates & Extract date parts:
        - IncidentDate
        - DateReceived
    - Calculate Duration:
        - DateReceived - IncidentDate
    - __** Other notes:__
        - There were no missing values in the original data.


## Dataset Source
https://www.kaggle.com/datasets/yetcherlaajay/insurance-disposition-classification?select=Insurance_Date_data.csv
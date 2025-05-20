# Comprehensive Supply Chain Analysis - KNIME Pipeline

## Description

- Transformations completed for this dataset:
    - Remove this feature:
        - CurrencyCode (single value feature)

    - Impute Missing Values: NO missing values

    - Clean Erroneous Values:
        - Make sure to fix the year values, also convert '/' to '-' BEFORE converting to date data type
            - ProcuredDate
            - OrderDate
            - ShipDate
            - DeliveryDate
        - Remove $ and , THEN convert from string to numerical data type
            - UnitPrice

    - Convert Data Type to Date & extract date parts:
        - ProcuredDate
        - OrderDate
        - ShipDate
        - DeliveryDate

    - Calculate the duration in days:
        - ProcuredDate to DeliveryDate
        - OrderDate to DeliveryDate
        - ProcuredDate to ShipDate


## Dataset Source
https://www.kaggle.com/datasets/dorothyjoel/us-regional-sales
# Customer Segment Clustering - Apache NiFi Pipeline

This project retrieves data via SFTP, makes transformations and then sends them to Elasticsearch. Apache NiFi, Elasticsearch, and SFTP are all in their own docker containers.

I have included the Flow Definition Files (both with and without exernal services).

## Notes

- The only feature containing null values: Income (there are 24 nulls; 2240 total records in the dataset).
    - Remove the rows that have a null 'Income' value
- Rename columns/features
- Remove single value columns/features:
    - Z_CostContact
    - Z_Revenue
- Handle Discrete/Categorical features by converting them from string to integer values using the following conversions:
    - Education
        - 'Master' -> 3
        - 'Basic' -> 0
        - '2n Cycle' -> 1
        - 'PhD' -> 4
        - 'Graduation' -> 2
        - (any other value) -> -1
    - Marital_Status
        - 'Single' -> 0
        - 'Married' -> 1
        - 'Absurd' -> 2
        - 'Together' -> 3
        - 'Widow' -> 4
        - 'Alone' -> 5
        - 'YOLO' -> 6
        - 'Divorced' -> 7
        - (any other value) -> -1

## Dataset Source
https://www.kaggle.com/datasets/vishakhdapat/customer-segmentation-clustering
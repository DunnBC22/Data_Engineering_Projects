# Car Specifications Dataset - KNIME Pipeline

## Description

- This pipeline:
    - Retrieve data from SFTP connection (then saves it in temp folder in local file system and reads in to a table)
    - Transforms the data, which includes the following:
        - Imputes missing values appropriately
        - Cleans Values in String-valued features
        - One Hot Encodes Discrete-valued features
    - Sends the transformed data to a Postgres table

## Notes

- Drop this features:
    - MpgExtraHigh
- Handle/Impute missing values
- Handle features with discrete values (while there are a few others that I could do this for, it would expand the size of this project far past the scope that I intended upon when I started):
    - Body_style
    - Segment
    - Fuel
    - Drive_Type
    - Power_pack
- Rename features as necessary

__**Note__: Handling discrete-valued features includes both one hot encoding them as well as cleaning up the values in each of the columns (to make the feature names that result from the one hot encoding possible to interpret).

## Dataset Source
https://www.kaggle.com/datasets/usefashrfi/car-specification-dataset
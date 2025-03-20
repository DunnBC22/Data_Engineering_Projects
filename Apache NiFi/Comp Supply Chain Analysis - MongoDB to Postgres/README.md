# Comp Supply Chain Analysis - Apache NiFi Pipeline

This project retrieves data files from a MongoDB collection, makes transformations and then sends it to a Postgres table. Apache NiFi, MongoDB, and Postgres are all in their own docker containers.

I have included the Flow Definition Files (both with and without exernal services).

## Notes
- There are no missing values in any of the features.
- There is one single value column (make sure to remove this feature): currency_code.
- Convert discrete/string/categorical data from strings to integer values according to these charts:
    - sales_channel:
        - 'Online' -> 0
        - 'Distributor' -> 1
        - 'Wholesale' -> 2
        - 'In-Store' -> 3
    - warehouse_code: 
        - 'WARE-UHY1004' -> 0
        - 'WARE-NBV1002' -> 1
        - 'WARE-XYS1001' -> 2
        - 'WARE-PUJ1005' -> 3
        - 'WARE-NMK1003' -> 4
        - 'WARE-MKL1006' -> 5
- Trim leading and trailing whitespace from these feature(s):
    - order_number
- clean these currency values up and rename feature to note currency type (remove '$' and ',', convert to floating-point numerical data type, and rename feature):
    - unit_cost
    - unit_price
- Handle dates, times, & timestamp values*:
    - procured_date
    - order_date
    - ship_date
    - delivery_date


* Steps to take for handling dates:
    - make them into a single dimension table,
    - add date parts to that table only,
    - apply the unique generated value to original table,
    - remove the date fields after inserting id features in the original table

## Dataset Source
https://www.kaggle.com/datasets/dorothyjoel/us-regional-sales
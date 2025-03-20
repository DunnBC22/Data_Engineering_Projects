# ECommerce Data Analysis - Apache NiFi Pipeline

This project retrieves data from a table in MySQL, makes transformations and then sends it to file via SFTP. Apache NiFi, MySQL, and SFTP are all in their own docker containers.

I have included the Flow Definition Files (both with and without exernal services).


## Notes
- Clean dimension tables
    - customer_dim table
        - Rename name to customer_name
        Rename nid to customer_id
        - Title Case 'customer_name' Values
        - Remove leading & trailing whitespace for values in these fields:
            - customer_key
            - customer_name
    - item_dim table
        - Rename name to customer_name
        - Remove 'units' column (it is duplicative)
        - Remove leading & trailing whitespace for values in these fields:
            - item_desc
            - item_key
            - man_country
            - item_name
            - supplier
    - store_dim table
        - Title Case Values in these fields: 
            - district
            - division
            - upazila
        - Remove leading & trailing whitespace for values in these fields:
            - district
            - division
            - store_key
            - upazila
        remove all of the trailing instances of '\r' in the upazilla field/column
    - time_dim table
        - Rename fields according to this (from -> to):
            - trans_day -> transaction_day
            - trans_hour -> transaction_hour
            - trans_month -> transaction_month
            - trans_year -> transaction_year
            - trans_date -> transaction_date
        - Remove leading & trailing whitespace for values in these fields:
            - time_key
            - trans_week
            - trans_quarter
        - Remove extra & unnecessary characters in values:
            - transaction_week -> remove ' Week'
            - transaction_quarter -> remove'Q'
    - trans_dim table
        - Rename 'trans_type' to 'transaction_type'
        - Title Case Values in these fields:
            - bank_name
            - transaction_type
        - Convert sales_datetime to date data type (${sales_datetime:toDate("dd-MM-yyyy HH:mm"):format("yyyy-MM-dd HH:mm:ss")})
        - create two new fields:
            - transaction_quarter -> ${trans_quarter:substring(1,2)}
            - transaction_week -> ${trans_week:substring(0,1)}
        - Remove leading & trailing whitespace for values in these fields:
            - bank_name
            - payment_key
            - trans_type
- Clean fact table data:
    - impute missing values as follows:
        - customer_name -> ${customer_name:ifNull("Unknown Customer Name")
    - Handle Discrete Values, impute missing values & correct odd spellings all at the same time for the 'unit' column:
        - 'ct\.' -> 0
        - 'Ct' -> 0
        - 'ct' -> 0
        - 'Bags'  -> 1
        - 'oz\.' -> 2
        - 'oz' -> 2
        - 'cartons' -> 3
        - 'lb' -> 4
        - 'pack' -> 5
        - 'pk' -> 5
        - 'botlltes' -> 6
        - 'bottles' -> 6
        - any other response -> -1

## Dataset Source
https://www.kaggle.com/datasets/mmohaiminulislam/ecommerce-data-analysis

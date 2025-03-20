# Online Sales Data - Apache NiFi

This project retrieves data from a table in Postgres, makes transformations and then sends it to a collection in MongoDB. Apache NiFi, Postgres, and MongoDB are all in their own docker containers.

I have included the Flow Definition Files (both with and without exernal services).

## Notes

** Before ingesting the data in Apache NiFi, I joined the two tables (Details & Orders) because I am still learning how to do so within Apache NiFi.

- Convert string/categorical/discrete columns to integer values using these conversion charts:
    - state_name: 
        - 'Uttar Pradesh' ->  0
        - 'Delhi' ->  1
        - 'Maharashtra' ->  2
        - 'Madhya Pradesh' ->  3
        - 'Andhra Pradesh' ->  4
        - 'Gujarat' ->  5
        - 'Bihar' ->  6
        - 'Himachal Pradesh' ->  7
        - 'Punjab' ->  8
        - 'Kerala ' ->  9
        - 'Nagaland' ->  10
        - 'Haryana' ->  11
        - 'Rajasthan' ->  12
        - 'Karnataka' ->  13
        - 'Tamil Nadu' ->  14
        - 'West Bengal' ->  15
        - 'Jammu and Kashmir' ->  16
        - 'Goa' ->  17
        - 'Sikkim' ->  18
    - city_name: 
        - 'Mathura' ->  0
        - 'Delhi' ->  1
        - 'Mumbai' ->  2
        - 'Indore' ->  3
        - 'Prayagraj' ->  4
        - 'Pune' ->  5
        - 'Hyderabad' ->  6
        - 'Surat' ->  7
        - 'Ahmedabad' ->  8
        - 'Patna' ->  9
        - 'Simla' ->  10
        - 'Chandigarh' ->  11
        - 'Bhopal' ->  12
        - 'Thiruvananthapuram' ->  13
        - 'Kohima' ->  14
        - 'Udaipur' ->  15
        - 'Bangalore' ->  16
        - 'Lucknow' ->  17
        - 'Chennai' ->  18
        - 'Kolkata' ->  19
        - 'Kashmir' ->  20
        - 'Jaipur' ->  21
        - 'Amritsar' ->  22
        - 'Goa' ->  23
        - 'Gangtok' ->  24
    - Category:
        - 'Electronics' ->  0
        - 'Furniture' ->  1
        - 'Clothing' ->  2
    - Sub-Category: 
        - 'Electronic Games' ->  0
        - 'Chairs' ->  1
        – 'Bookcases' ->  2
        - 'Printers' ->  3
        - 'Phones' ->  4
        - 'Trousers' ->  5
        - 'Saree' ->  6
        - 'Hankerchief' ->  7
        - 'Kurti' ->  8
        - 'Skirt' ->  9
        - 'Tables' ->  10
        - 'Stole' ->  11
        - 'Leggings' ->  12
        - 'Accessories' ->  13
        - 'T-shirt' ->  14
        - 'Furnishings' ->  15
        - 'Shirt' ->  16
    - PaymentMode:
        - 'Credit Card' ->  0
        - 'Debit Card' ->  1
        - 'COD' ->  2
        - 'EMI' ->  3
        - 'UPI' ->  4
- There are no null values in this table.
- I have decided not to handle outlier removal in this project.
- I need to convert the Order Date column from String data type to date data type & extract some date parts from it.
- There are some feature(s)/column(s) that I will rename.


## Dataset Source
https://www.kaggle.com/datasets/samruddhi4040/online-sales-data?select=Details.csv

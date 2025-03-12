# E-Commerce Website Logs - Apache NiFi Pipeline

This project retrieves data from a table in Postgres, makes transformations and then sends it to a collection in MongoDB. Apache NiFi, Postgres, and MongoDB are all in their own docker containers.

I have included the Flow Definition Files (both with and without exernal services).

## Notes About Transformations

- Trim leading & Trailing Whitespace from the following columns:
    - 'accessed_date'
    - 'ip'
- Convert String Categorical/Discrete values to integer values
    - network_protocol:
    	- "ICMP " -> 0
	    - "HTTP" -> 1
    	- "TCP  " -> 2
	    - "HTTP  " -> 3
	    - "UDP  " -> 4
    - accessed_from:
        - "Safari" -> 0
        - "SafFRi" -> 0
        - "Mozilla Firefox" -> 1
        - "IOS App" -> 2
        - "Others" -> 3
        - "Microsoft Edge" -> 3
        - "Chrome" -> 4
        - "Android App" -> 5
    - gender
        - "Unknown" -> 0
        - "Male" -> 1
        - "Female" -> 2
    - country
        - "FR" -> 0
        - "CA" -> 1
        - "DK" -> 2
        - "MX" -> 3
        - "US" -> 4
        - "IE" -> 5
        - "AT" -> 6
        - "FI" -> 7
        - "IT" -> 8
        - "IN" -> 9
        - "CO" -> 10
        - "NO" -> 11
        - "KR" -> 12
        - "PL" -> 13
        - "ZA" -> 14
        - "CN" -> 15
        - "RU" -> 16
        - "DE" -> 17
        - "CH" -> 18
        - "PR" -> 19
        - "AU" -> 20
        - "SE" -> 21
        - "AR" -> 22
        - "JP" -> 23
        - "PE" -> 24
        - "AE" -> 25
        - "GB" -> 26
    - membership
        - "Premium" -> 2
        - "Normal" -> 1
        - "Not Logged In" -> 0
    - language_in_log
	    - "Slovak" -> 0
        - "Russian" -> 1
        - "swahili" -> 2
        - "Spanish" -> 3
        - "polish" -> 4
        - "serbian" -> 5
        - "Italian" -> 6
        - "italian" -> 7
        - "marathi" -> 8
        - "slovene" -> 9
        - "romanian" -> 10
        - "urdu" -> 11
        - "Portuguese" -> 12
        - "Thai" -> 13
        - "mongolian" -> 14
        - "English" -> 15
        - "persian" -> 16
        - "macedonian" -> 17
        - "tegulu" -> 18
        - "swedish" -> 19
        - "norwegian" -> 20
        - "Japanese" -> 21
        - "German" -> 22
        - "Chinese" -> 23
        - "Dutch" -> 24
        - "French" -> 25
        - "Arabic" -> 26
        - "nepali" -> 27
        - "malay" -> 28
        - "malayalam" -> 29
    - returned
    	- "Yes" -> 1
	    - "No" -> 0
    - pay_method
        - "Credit Card" -> 0
        - "Debit Card" -> 1
        - "Others" -> 2
        - "Cash" -> 3
- There is only one column that has any null values in it (the 'age' column has 88,124 null values out of ~172,838 records). Because there are more values missing than there are not missing, I am going to remove this column.
- Handle date, time, and/or timestamp columns:
    - accessed_date


## Dataset Source
https://www.kaggle.com/datasets/kzmontage/e-commerce-website-logs

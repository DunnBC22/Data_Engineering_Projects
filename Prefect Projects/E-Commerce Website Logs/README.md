# E-Commerce Website Logs - Prefect Pipeline

## Description

- These are the transformation I performed on this dataset:
    - Rename Features
        "accessed_date": "AccessedDate",
        "duration_(secs)": "DurationInSeconds",
        "network_protocol": "NetworkProtocol",
        "ip": "IpAddress",
        "bytes": "BytesUsed",
        "accessed_Ffom": "BrowserAccessedFrom",
        "age": "UserAge",
        "gender": "UserGender",
        "country": "UserCountry",
        "membership": "UserMembershipLevel",
        "language": "UserLanguage",
        "sales": "SalesAmount",
        "returned": "ProductReturned",
        "returned_amount": "ReturnedAmount",
        "pay_method": "PaymentMethod"
    - Remove Features
        - $oid
    - Impute Missing Values:
        - UserAge ==> -1
    - Clean Values
        - Clean up the Spelling:
            - BrowserAccessedFrom
                - "SafFRi": "Safari"
            - ProductReturned
                - "No": 0
                - "Yes": 1
        - Remove all leading and trailing whitespace for these features:
            - NetworkProtocol
            - IpAddress
            - UserMembershipLevel
            - UserLanguage
        - Titlecase these features:
            - UserLanguage
            - BrowserAccessedFrom
        - Remove ALL Whitespace from these features:
            - BrowserAccessedFrom
        - PaymentMethod
            - titlecase then remove all whitespace
    - Handle timestamps (convert to date data type & extract parts)
        - accessed_date (example: "2017-03-16 15:52:58.342")
    - Update data types:
        - "UserAge": pl.Int32
        - "ProductReturned": pl.Int32
    - Add a unique identifier feature named LogId

## Dataset Source
https://www.kaggle.com/datasets/kzmontage/e-commerce-website-logs
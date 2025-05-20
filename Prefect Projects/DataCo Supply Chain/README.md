# DataCo Supply Chain


"""
This is what I need to do to this dataset:


- Remove Features:
    - customer_email (single-valued feature)
    - customer_password (single-valued feature)
    - product_desc (single-valued feature)
    - product_status (single-valued feature)

- rename Features
    "id": "Id",
    "transaction_type": "TransactionType",
    "actual_days_to_ship": "ActualDaysToShip",
    "scheduled_days_to_ship": "ScheduledDaysToShip",
    "benefit_per_order": "BenefitPerOrder",
    "sales_per_customer": "SalesPerCustomer",
    "delivery_status": "DeliveryStatus",
    "late_delivery_risk": "LateDeliveryRisk",
    "category_id": "CategoryId",
    "category_name": "CategoryName",
    "customer_city": "CustomerCity",
    "customer_country": "CustomerCountry",
    "customer_fname": "CustomerFirstName",
    "customer_id": "CustomerId",
    "customer_lname": "CustomerLastName",
    "customer_segment": "CustomerSegment",
    "customer_state": "CustomerState",
    "customer_street": "CustomerStreet",
    "customer_zipcode": "CustomerZipCode",
    "department_id": "DepartmentId",
    "department_name": "DepartmentName",
    "latitude": "CustomerLatitude",
    "longitude": "CustomerLongitude",
    "market": "MarketName",
    "order_city": "OrderCity",
    "order_country": "OrderCountry",
    "order_customer_id": "OrderCustomerId",
    "order_date": "OrderDate",
    "order_id": "OrderId",
    "order_item_cardprod_id": "OrderItemCardProdId",
    "order_Item_discount": "OrderItemDiscount",
    "order_item_discount_rate": "OrderItemDiscountRate",
    "order_item_id": "OrderItemId",
    "order_item_product_price": "OrderItemProductPrice",
    "order_item_profit_ratio": "OrderItemProfitRatio",
    "order_item_quantity": "OrderItemQuantity",
    "sales": "SalesAmount",
    "order_item_total": "OrderItemTotal",
    "order_profit_per_order": "OrderProfitPerOrder",
    "order_region": "OrderRegion",
    "order_state": "OrderState",
    "order_status": "OrderStatus",
    "order_zipcode": "OrderZipCode",
    "product_card_id": "ProductCardId",
    "product_category_id": "ProductCategoryId",
    "product_image": "ProductImage",
    "product_name": "ProductName",
    "product_price": "ProductPrice",
    "shipping_date": "ShippingDate",
    "shipping_mode": "ShippingMode"

- Handle nulls and nans for these features:
    "customer_lname" -> remove all records where this feature is null
    "customer_zipcode" -> remove all records where this feature is null
    "order_zipcode"	-> assume that the orderZipCode is the same as the CustomerZipCode

- Create tables for the following:
    - CategoriesDim
        CategoryId
        CategoryName
    - CustomersDim
        CustomerCity
        CustomerCountry
        CustomerFirstName
        CustomerId
        CustomerLastName
        CustomerState
        CustomerStreet
        CustomerZipCode
    - DepartmentsDim
        DepartmentId
        DepartmentName
    - ProductsDim
        ProductCardId
        ProductImage
        ProductName

- Remove these features after creating & saving dimension tables:
    - CategoryName
    - CustomerCity
    - CustomerCountry
    - CustomerFirstName
    - CustomerLastName
    - CustomerState
    - CustomerStreet
    - CustomerZipCode
    - DepartmentName
    - ProductImage
    - ProductName

- Clean String values as such:
    - transaction_type -> titlecase
    - delivery_status -> titlecase then remove all whitespace
    - category_name -> Convert & to And THEN remove all dashes, division signs, and single quotes THEN titlecase THEN remove all leading and trailing whitespace
    - Clean the values in this feature: customer_country
        - "EE. UU." - "USA"
        - "Puerto Rico" -> "PuertoRico"
    - Clean the values in this feature: customer_state
        - "91732" -> "CA"
        - "95758" -> "CA"
    - customer_segment -> remove all whitespace
    - department_name -> titlecase THEN remove all whitespace
    - order_region -> Titlecase then remove all whitespace
    - order_status -> replace underscores with a space, the titlecasevalues followed by removing all whitespace
    - product_name -> replace all + with "Plus" THEN REMOVE all single quotes THEN replace all dashes, periods, division signs with a space THEN Titlecase THEN remove all whitespace (both leading and trailing as well as spaces within the text)
    - shipping_mode -> Remove all whitespace
    - market
        - "LATAM" to "LatinAmerica"
        - "USCA" -> "UnitedStatesOfCentralAmerica"
    - OrderCountry [164]
        "Afganist�n" -> "Afghanistan"
        "Arabia Saud�" -> "SaudiArabia"
        "Azerbaiy�n" -> "Azerbaijan"
        "Banglad�s" -> "Bangladesh"
        "Bar�in" -> "Bahrain"
        "Ben�n" -> "Benin"
        "But�n" -> "Bhutan"
        "B�lgica" -> "Belgium"
        "Camer�n" -> "Cameroon"
        "Emiratos �rabes Unidos" -> "UnitedArabEmirates"
        "Espa�a" -> "Spain"
        "Estados Unidos" -> "UnitedStates"
        "Etiop�a" -> "Ethiopia"
        "Gab�n" -> "Gabon"
        "Hait�" -> "Haiti"
        "Hungr�a" -> "Hungary"
        "Ir�n" -> "Iran"
        "Jap�n" -> "Japan"
        "Kazajist�n" -> "Kazakhstan"
        "Kirguist�n" -> "Kyrgyzstan"
        "L�bano" -> "Lebanon"
        "M�xico" -> "Mexico"
        "N�ger" -> "Niger"
        "Om�n" -> "Oman"
        "Pakist�n" -> "Pakistan"
        "Panam�" -> "Panama"
        "Pap�a Nueva Guinea" -> "PapuaNewGuinea"
        "Pa�ses Bajos" -> "Netherlands"
        "Per�" -> "Peru"
        "Rep�blica Centroafricana" -> "CentralAfricanRepublic"
        "Rep�blica Checa" -> "Czechia"
        "Rep�blica Democr�tica del Congo" -> "DemocraticRepublicOfCongo"
        "Rep�blica Dominicana" -> "Dominican Republic"
        "Rep�blica de Gambia" -> "Gambia"
        "Rep�blica del Congo" -> "Congo"
        "Sud�n" -> "Sudan"
        "Sud�n del Sur" -> "Suriname"
        "S�hara Occidental" -> "Western Sahara"
        "Taiw�n" -> "Taiwan"
        "Tayikist�n", -> "Tajikistan"
        "Turkmenist�n" -> "Turkmenistan"
        "Turqu�a" -> "Turkey"
        "T�nez" -> "Tunisia"
        "Uzbekist�n" -> "Uzbekistan"
        - Also:
            - After cleaning those values, titlecase, then remove all whitespace & remove dashes & white both opening and closing parentheses
    
*** Make note that for each discrete valued feature, in the real world, I would go through each one to clean up all values, but that is a bit outside the scope of this project (seeing as some features have thousands of distinct values)

- Handle dates:
    - OrderDate
    - ShippingDate

- Handle Geographical features:
    - latitude_coord
    - longitude_coord


## Dataset Source
https://www.kaggle.com/datasets/shashwatwork/dataco-smart-supply-chain-for-big-data-analysis?select=DataCoSupplyChainDataset.csv
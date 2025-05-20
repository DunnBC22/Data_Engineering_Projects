# Brazilian E-Commerce Public Dataset By Olist - Prefect Pipeline


## Description

- These are the transformations I applied to this dataset:
	- customers_dataset
		- Remove columns:
			- CustomerUniqueId
		- Rename columns:
			"customer_id": "CustomerId",
			"customer_unique_id": "CustomerUniqueId",
			"customer_zip_code_prefix": "CustomerZipCodePrefix",
			"customer_city": "CustomerCity",
			"customer_state": "CustomerState"
		- Clean values as such:
			- Titlecase 
				- CustomerCity
			- Remove leading and trailing whitespace for:
				- CustomerCity
				- CustomerState
	- geolocation_dataset
		- Remove columns:
			- None until after handling the geo POINT coordinates later
		- Rename columns:
			"geolocation_zip_code_prefix": "GeoZipCodePrefix",
			"geolocation_lat": "GeoLatitude",
			"geolocation_lng": "GeoLongitude",
			"geolocation_city": "GeoCity",
			"geolocation_state": "GeoState"
		- Clean values as such:
			- Titlecase & remove leading and trailing whitespace for:
				- GeoCity
		- Handle geographical features (create single feature & remove old features):
			- "GeoLatitude"
			- "GeoLongitude"
	- order_items_dataset
		- Rename columns:
			"order_id": "OrderId",
			"order_item_id": "OrderItemId",
			"product_id": "ProductId",
			"seller_id": "SellerId",
			"shipping_limit_date": "ShippingLimitDate",
			"price": "OrderItemPrice",
			"freight_value": "FreightValue"
		- Clean values as such:
			- Handle Dates (convert to date/timestamp data type & extract date parts)
				- ShippingLimitDate
	- order_payments_dataset
		- Rename columns:
			"order_id": "OrderId",
			"payment_sequential": "PaymentSequential",
			"payment_type": "PaymentType",
			"payment_installments": "PaymentInstallments",
			"payment_value": "PaymentValue"
		- Clean values as such:
			- Clean the PaymentType values using a dictionary:
				- "boleto": "Ticket",
				- "credit_card": "CreditCard",
				- "debit_card": "DebitCard",
				- "not_defined": "NotDefined",
				- "voucher": "Voucher" 
	- order_reviews_dataset
		- Remove columns:
			- review_id
		- Rename columns:
			"order_id": "OrderId",
			"review_score": "ReviewScore",
			"review_comment_title": "ReviewCommentTitle",
			"review_comment_message": "ReviewCommentMessage",
			"review_creation_date": "ReviewCreationDate",
			"review_answer_timestamp": "ReviewAnswerTimestamp"
		- Clean values as such:
			- Replace all whitespace within text with a single space fot these features
				- ReviewCommentTitle
				- NoReviewCommentMessage
			- Remove all leading & trailing whietspace for these featuers:
				- ReviewCommentTitle
				- NoReviewCommentMessage
			- Handle missing values (& values of 'None') for these features: 
				- ReviewCommentTitle
					- "NoReviewCommentTitle"
				- ReviewCommentMessage
					- "NoReviewCommentMessage"
			- Handle Dates (convert to date/timestamp data type & extract date parts):
				- review_creation_date
				- review_answer_timestamp
	- orders_dataset
		- Rename columns:
			"order_id": "OrderId",
			"customer_id": "CustomerId",
			"order_status": "OrderStatus",
			"order_purchase_timestamp": "OrderPurchaseTimestamp",
			"order_approved_at": "OrderApprovedAt",
			"order_delivered_carrier_date": "OrderDeliveredCarrierDate",
			"order_delivered_customer_date": "OrderDeliveredCustomerDate",
			"order_estimated_delivery_date": "OrderEstimatedDeliveryDate"
		- Clean values as such:
			- Titlecase & remove leading and trailing whitespace for:
				- order_status
			- Handle Dates (convert to date/timestamp data type, deal with missing [and 'None'] values & extract date parts):
				- order_approved_at
				- order_delivered_carrier_date
				- order_delivered_customer_date
				- order_estimated_delivery_date
			- Calculate Durations:
				- "OrderDeliveredCustomerDate" - "OrderDeliveredCarrierDate" AS CarrierDeliveryTurnaround
	- product_category_name_translation
		- Rename columns:
			"product_category_name": "ProductCategoryName",
			"product_category_name_english": "ProductCategoryNameInEnglish"
		- Clean values as such:
			- Replace _ (underscores) with space THEN titlecase:
				- ProductCategoryNameInEnglish
	- products_dataset
		- Rename columns:
			"product_id": "ProductId",
			"product_category_name": "ProductCategoryName",
			"product_name_lenght": "ProductNameLength",
			"product_description_lenght": "ProductDescriptionLength",
			"product_photos_qty": "ProductPhotosQty",
			"product_weight_g": "ProductWeightG",
			"product_length_cm": "ProductLengthCm",
			"product_height_cm": "ProductHeightCm",
			"product_width_cm": "ProductWidthCm"
		- Clean values as such:
			- Join product_category_name_translation based on the ProductCategoryName feature, then remove the ProductCategoryName feature.
		- Handle missing [and 'None'] values:
			"- product_name_lenght": -1,
			- "product_description_lenght": -1,
			- "product_photos_qty": -1,
			- "product_weight_g": -1,
			- "product_length_cm": -1,
			- "product_height_cm": -1,
			- "product_width_cm": -1
	- sellers_dataset
		- Rename columns:
			"seller_id": "SellerId",
			"seller_zip_code_prefix": "SellerZipCodePrefix",
			"seller_city": "SellerCity",
			"seller_state": "SellerState"
		- Clean values as such:
			- Titlecase:
				- SellerCity
			- Remove leading and trailing whitespace for values in the following features:
				- SellerCity
				- SellerState

- Join datasets as such (in this exact order):
	- Join customers to orders dataset on the customer_id feature (to create new df)
	- Join order_items to df on the order_id feature
	- Join order_payments to df on the order_id feature
	- Join order_reviews to df on the order_id feature
	- Join products to df on the product_id feature
	- Join categories to df on the product_category_name feature
	- Join sellers to df on the seller_id feature
		* how="left" for all of the join statements

- After all tables are joined: 
	- Remove ProductCategoryName after all datasets are joined
	- Remove other Id values after all data is joined (such as the CustomerID, OrderId, ProductId, SellerId, Geo)

- For the sake of bandwidth, I am going to send the data over to Apache Spark as two (2) tables: the main table (DataFrame) and the geolocation table (DataFrame). As it is right now, the two DataFrames are less than 0.5 GB. If I join the Geolocation data for both the Seller and the Customer DataFrames, the size of the main DataFrame balloons to over 5 GB!

## Dataset Source
https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
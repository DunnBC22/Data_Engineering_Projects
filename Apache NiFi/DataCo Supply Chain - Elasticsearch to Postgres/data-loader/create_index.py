import requests, time, sys, json

ES_URL = "http://elasticsearch:9200"
INDEX_NAME = "dcsc_transactions"

MAPPINGS = {
    "mappings": {
        "properties": {
            "record_id": { "type": "integer" },
            "transaction_type": { "type": "keyword" },
            "actual_days_to_ship": { "type": "integer" },
            "scheduled_days_to_ship": { "type": "integer" },
            "benefit_per_order": { "type": "float" },
            "sales_per_customer": { "type": "float" },
            "delivery_status": { "type": "keyword" },
            "late_delivery_risk": { "type": "integer" },
            "category_id": { "type": "integer" },
            "category_name": { "type": "keyword" },
            "customer_city": { "type": "keyword" },
            "customer_country": { "type": "keyword" },
            "customer_email": { "type": "keyword" },
            "customer_fname": { "type": "keyword" },
            "customer_id": { "type": "keyword" },
            "customer_lname": { "type": "keyword" },
            "customer_password": { "type": "keyword" },
            "customer_segment": { "type": "keyword" },
            "customer_state": { "type": "keyword" },
            "customer_street": { "type": "keyword" },
            "customer_zipcode": { "type": "keyword" },
            "department_id": { "type": "integer" },
            "department_name": { "type": "keyword" },
            "latitude": { "type": "float" },
            "longitude": { "type": "float" },
            "market": { "type": "keyword" },
            "order_city": { "type": "keyword" },
            "order_country": { "type": "keyword" },
            "order_customer_id": { "type": "keyword" },
            "order_date": { "type": "keyword"},
            "order_id": { "type": "keyword" },
            "order_item_cardprod_id": { "type": "integer" },
            "order_Item_discount": { "type": "float" },
            "order_item_discount_rate": { "type": "float" },
            "order_item_id": { "type": "keyword" },
            "order_item_product_price": { "type": "float" },
            "order_item_profit_ratio": { "type": "float" },
            "order_item_quantity": { "type": "integer" },
            "sales": { "type": "float" },
            "order_item_total": { "type": "float" },
            "order_profit_per_order": { "type": "float" },
            "order_region": { "type": "keyword" },
            "order_state": { "type": "keyword" },
            "order_status": { "type": "keyword" },
            "order_zipcode": { "type": "keyword" },
            "product_card_id": { "type": "keyword" },
            "product_category_id": { "type": "integer" },
            "product_desc": { "type": "text" },
            "product_image": { "type": "keyword" },
            "product_name": { "type": "text" },
            "product_price": { "type": "float" },
            "product_status": { "type": "keyword" },
            "shipping_date": { "type": "keyword"},
            "shipping_mode": { "type": "keyword" }
        }
    }
}

AUTH = ("elastic", "es_nifi_pass")

def wait_for_es():
    print("Waiting for Elasticsearch to become available...")
    for i in range(12):
        try:
            r = requests.get(ES_URL, auth=AUTH)
            if r.status_code == 200:
                print("Elasticsearch is up!")
                return
        except requests.exceptions.RequestException:
            print("Elasticsearch not available yet, retrying...")
        time.sleep(5)
    print("Elasticsearch did not start in time")
    sys.exit(1)

def create_index():
    url = f"{ES_URL}/{INDEX_NAME}"
    # Check if the index exists
    r = requests.head(url, auth=AUTH)
    if r.status_code == 404:
        print(f"Creating index '{INDEX_NAME}'...")
        r = requests.put(url, json=MAPPINGS, auth=AUTH)
        if r.status_code in (200, 201):
            print("Index created successfully!")
        else:
            print("Failed to create index:", r.text)
            sys.exit(1)
    else:
        print(f"Index '{INDEX_NAME}' already exists.")

if __name__ == "__main__":
    wait_for_es()
    create_index()
import requests, time, sys, json

ES_URL = "http://elasticsearch:9200"
INDEX_NAME = "csc_data"

MAPPINGS = {
    "mappings": {
        "properties": {
            "record_id": { "type": "integer" },
            "birth_year": { "type": "integer" },
            "education": { "type": "keyword" },
            "marital_status": { "type": "keyword" },
            "income": { "type": "integer" },
            "num_of_kids_at_home": { "type": "integer" },
            "num_of_teens_at_home": { "type": "integer" },
            "date_customer_enrolled": { "type": "keyword" },
            "day_of_month_customer_enrolled": { "type": "integer" },
            "quarter_customer_enrolled": { "type": "integer" },
            "month_of_year_customer_enrolled": { "type": "integer" },
            "year_customer_enrolled": { "type": "integer" },
            "day_of_week_customer_enrolled": { "type": "integer" },
            "week_of_year_customer_enrolled": { "type": "integer" },
            "num_of_days_since_last_interaction": { "type": "integer" },
            "amt_spent_on_wines": { "type": "integer" },
            "amt_spent_on_fruits": { "type": "integer" },
            "amt_spent_on_meat_products": { "type": "integer" },
            "amt_spent_on_fish_products": { "type": "integer" },
            "amt_spent_on_sweet_products": { "type": "integer" },
            "amt_spent_on_gold_products": { "type": "integer" },
            "num_of_discounted_purchases": { "type": "integer" },
            "num_of_web_purchases": { "type": "integer" },
            "num_of_catalog_purchases": { "type": "integer" },
            "num_of_in_store_purchases": { "type": "integer" },
            "num_web_visits_in_past_month": { "type": "integer" },
            "accepted_campaign_3": { "type": "integer" },
            "accepted_campaign_4": { "type": "integer" },
            "accepted_campaign_5": { "type": "integer" },
            "accepted_campaign_1": { "type": "integer" },
            "accepted_campaign_2": { "type": "integer" },
            "has_customer_complained": { "type": "integer" },
            "response": { "type": "integer" }
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
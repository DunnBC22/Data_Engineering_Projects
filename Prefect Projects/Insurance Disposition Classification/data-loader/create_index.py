import requests, time, sys, json

ES_URL = "http://elasticsearch:9200"
INDEX_NAME = "insurance_disposition_clf"

MAPPINGS = {
    "mappings": {
        "properties": {
            "ClaimNumber": { "type": "keyword" },
            "CityCode": { "type": "keyword" },
            "CityName": { "type": "keyword" },
            "EnterpriseType": { "type": "keyword" },
            "ClaimType": { "type": "keyword" },
            "ClaimSite": { "type": "keyword" },
            "ProductInsured": { "type": "keyword" },
            "id": { "type": "integer" },
            "IncidentDate": { "type": "keyword" },
            "DateReceived": { "type": "keyword" },
            "ClaimAmount": { "type": "float" },
            "CloseAmount": { "type": "float" },
            "Disposition": { "type": "keyword" },
            "IncidentDate_DayOfWeek": { "type": "integer" },
            "IncidentDate_DayOfMonth": { "type": "integer" },
            "IncidentDate_DayOfYear": { "type": "integer" },
            "IncidentDate_Month": { "type": "integer" },
            "IncidentDate_Quarter": { "type": "integer" },
            "IncidentDate_Year": { "type": "integer" },
            "DateReceived_DayOfWeek": { "type": "integer" },
            "DateReceived_DayOfMonth": { "type": "integer" },
            "DateReceived_DayOfYear": { "type": "integer" },
            "DateReceived_Month": { "type": "integer" },
            "DateReceived_Quarter": { "type": "integer" },
            "DateReceived_Year": { "type": "integer" },
            "DaysToReport": { "type": "integer" }
        }
    }
}

AUTH = ("elastic", "es_prefect_pass")

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
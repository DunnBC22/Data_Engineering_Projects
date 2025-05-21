import requests, time, sys, json

ES_URL = "http://elasticsearch:9200"
INDEX_NAME = "top_scientists_researchers"

MAPPINGS = {
    "mappings": {
        "properties": {
            "PersonalProfileLink": { "type": "keyword" },
            "ResearcherName": { "type": "keyword" },
            "Id": { "type": "integer" },
            "Position": { "type": "keyword" },
            "Expertise": { "type": "keyword" },
            "StartYear": { "type": "integer" },
            "DepartmentName": { "type": "keyword" },
            "Qualifications": { "type": "keyword" },
            "WorkLocation": { "type": "keyword" },
            "HonorsAndAwards": { "type": "keyword" },
            "HighestQualification": { "type": "keyword" },
            "UnisersityName": { "type": "keyword" },
            "HasAwards": { "type": "integer" },
            "Experience": { "type": "keyword" }
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
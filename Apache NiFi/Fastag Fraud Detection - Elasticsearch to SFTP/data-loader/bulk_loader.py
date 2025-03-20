import csv
import json
import requests
import sys

ES_URL = "http://elasticsearch:9200"
INDEX_NAME = "transactions"
AUTH = ("elastic", "es_nifi_pass")
DATA_FILE = "/data/data.csv"  # The file path inside the container

def create_bulk_data():
    bulk_lines = []
    try:
        with open(DATA_FILE, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Prepare the bulk action line
                action = {"index": {}}
                bulk_lines.append(json.dumps(action))
                # Append the CSV row as a document
                bulk_lines.append(json.dumps(row))
    except Exception as e:
        print("Error reading data file:", e)
        sys.exit(1)
    # Bulk API payload must end with a newline
    return "\n".join(bulk_lines) + "\n"

def bulk_upload():
    bulk_data = create_bulk_data()
    bulk_url = f"{ES_URL}/{INDEX_NAME}/_bulk"
    headers = {"Content-Type": "application/x-ndjson"}
    print("Uploading bulk data...")
    response = requests.post(bulk_url, data=bulk_data, headers=headers, auth=AUTH)
    if response.status_code == 200:
        print("Bulk upload successful!")
    else:
        print("Bulk upload failed:", response.text)
        sys.exit(1)

if __name__ == "__main__":
    bulk_upload()
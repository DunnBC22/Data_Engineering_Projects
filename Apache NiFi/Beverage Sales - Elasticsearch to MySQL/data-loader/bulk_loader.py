import csv, json, requests, sys

ES_URL = "http://elasticsearch:9200"
INDEX_NAME = "beverage_sales_data"
AUTH = ("elastic", "es_nifi_pass")
DATA_FILE = "/data/data.csv"

def adjust_index_settings(before=True):
    """Adjust index settings before or after bulk upload."""
    settings = {
        "settings": {
            "index.refresh_interval": "-1" if before else "1s",
            "index.translog.durability": "async" if before else "request"
        }
    }
    try:
        response = requests.put(
            f"{ES_URL}/{INDEX_NAME}/_settings",
            headers={"Content-Type": "application/json"},
            json=settings,
            auth=AUTH
        )
        if response.status_code == 200:
            print(f"Index settings adjusted {'before' if before else 'after'} upload.")
        else:
            print(f"Failed to adjust settings: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error adjusting settings: {e}")
        sys.exit(1)

def create_bulk_data():
    try:
        with open(DATA_FILE, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            bulk_lines = []
            for count, row in enumerate(reader, start=1):
                action = {"index": {}}
                bulk_lines.append(json.dumps(action))
                bulk_lines.append(json.dumps(row))

                if count % 10000 == 0:
                    yield "\n".join(bulk_lines) + "\n"
                    bulk_lines = []

            if bulk_lines:
                yield "\n".join(bulk_lines) + "\n"

    except Exception as e:
        print("Error reading data file:", e)
        sys.exit(1)

def bulk_upload():
    adjust_index_settings(before=True)  # Disable refresh_interval before upload
    headers = {"Content-Type": "application/x-ndjson"}

    for batch_num, bulk_data in enumerate(create_bulk_data(), start=1):
        print(f"Uploading batch {batch_num}...")

        try:
            response = requests.post(f"{ES_URL}/{INDEX_NAME}/_bulk", 
                                     data=bulk_data, headers=headers, auth=AUTH)
            
            if response.status_code == 200:
                response_json = response.json()
                failed = [item for item in response_json['items'] if 'error' in item['index']]

                if failed:
                    print(f"Batch {batch_num} had failed records: {failed}")
                    sys.exit(1)
                else:
                    print(f"Batch {batch_num} uploaded successfully!")
            else:
                print(f"Batch {batch_num} failed with status code {response.status_code}: {response.text}")
                sys.exit(1)

        except requests.exceptions.RequestException as e:
            print(f"Error uploading batch {batch_num}: {e}")
            sys.exit(1)

    adjust_index_settings(before=False)

if __name__ == "__main__":
    bulk_upload()

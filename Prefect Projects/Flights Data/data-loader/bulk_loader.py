import csv
import json
import requests
import sys

ES_URL = "http://elasticsearch:9200"
INDEX_NAME = "flights_data"
AUTH = ("elastic", "es_prefect_pass")
DATA_FILE = "/data/flights.txt"
CHUNK_SIZE = 1000  # number of documents per chunk (not lines!)

def generate_bulk_lines():
    try:
        with open(DATA_FILE, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter="|")
            for row in reader:
                action = {"index": {}}
                yield json.dumps(action)
                document = {k.strip(): v.strip() for k, v in row.items()}
                yield json.dumps(document)
    except Exception as e:
        print("Error reading data file:", e)
        sys.exit(1)

def chunked_bulk_upload():
    bulk_url = f"{ES_URL}/{INDEX_NAME}/_bulk"
    headers = {"Content-Type": "application/x-ndjson"}
    buffer = []
    doc_count = 0

    print("Uploading bulk data in chunks...")

    for line in generate_bulk_lines():
        buffer.append(line)
        if len(buffer) >= CHUNK_SIZE * 2:  # 2 lines per doc
            send_chunk(buffer, bulk_url, headers)
            buffer = []
            doc_count += CHUNK_SIZE

    if buffer:
        send_chunk(buffer, bulk_url, headers)
        doc_count += len(buffer) // 2

    print(f"Finished uploading {doc_count} documents.")

def send_chunk(lines, url, headers):
    # Must end with a newline
    payload = "\n".join(lines) + "\n"
    response = requests.post(url, data=payload, headers=headers, auth=AUTH)
    if response.status_code == 200:
        print("Chunk uploaded successfully.")
    else:
        print(f"Bulk upload failed for chunk. Status Code: {response.status_code}")
        print("Response Text:", response.text)
        sys.exit(1)

if __name__ == "__main__":
    chunked_bulk_upload()










# import csv
# import json
# import requests
# import sys

# ES_URL = "http://elasticsearch:9200"
# INDEX_NAME = "flights_data"
# AUTH = ("elastic", "es_prefect_pass")
# DATA_FILE = "/data/flights.txt"  # The file path inside the container

# def create_bulk_data():
#     bulk_lines = []
#     try:
#         with open(DATA_FILE, newline='', encoding='utf-8') as csvfile:
#             reader = csv.DictReader(csvfile, delimiter="|")
#             for row in reader:
#                 # Prepare the bulk action line
#                 action = {"index": {}}
#                 bulk_lines.append(json.dumps(action))
#                 # Append the CSV row as a document
#                 bulk_lines.append(json.dumps(row))
#     except Exception as e:
#         print("Error reading data file:", e)
#         sys.exit(1)
#     # Bulk API payload must end with a newline
#     return "\n".join(bulk_lines) + "\n"

# def bulk_upload():
#     bulk_data = create_bulk_data()
#     bulk_url = f"{ES_URL}/{INDEX_NAME}/_bulk"
#     headers = {"Content-Type": "application/x-ndjson"}
#     print("Uploading bulk data...")
#     response = requests.post(bulk_url, data=bulk_data, headers=headers, auth=AUTH)
#     if response.status_code == 200:
#         print("Bulk upload successful!")
#     else:
#         print("Bulk upload failed:", response.text)
#         sys.exit(1)

# if __name__ == "__main__":
#     bulk_upload()
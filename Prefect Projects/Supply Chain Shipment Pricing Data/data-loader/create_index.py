import requests, time, sys, json

ES_URL = "http://elasticsearch:9200"
INDEX_NAME = "supply_chain_shipment_pricing_data"

MAPPINGS = {
    "mappings": {
        "properties": {
            "Id": { "type": "integer" },
            "ProjectCode": { "type": "keyword" },
            "PqNumber": { "type": "keyword" },
            "PoOrSoNumber": { "type": "keyword" },
            "AsnOrDnNumber": { "type": "keyword" },
            "CountryName": { "type": "keyword" },
            "ManagedBy": { "type": "keyword" },
            "FulfilledVia": { "type": "keyword" },
            "VendorIncoTerm": { "type": "keyword" },
            "ShipmentMode": { "type": "keyword" },
            "PqFirstSentToClientDate": { "type": "keyword" },
            "PoSentToVendorDate": { "type": "keyword" },
            "ScheduledDeliveryDate": { "type": "keyword" },
            "DeliveredToClientDate": { "type": "keyword" },
            "DeliveryRecordedDate": { "type": "keyword" },
            "ProductGroup": { "type": "keyword" },
            "SubClassification": { "type": "keyword" },
            "VendorName": { "type": "keyword" },
            "ItemDescription": { "type": "keyword" },
            "MoleculeOrTestType": { "type": "keyword" },
            "BrandName": { "type": "keyword" },
            "Dosage": { "type": "keyword" },
            "DosageForm": { "type": "keyword" },
            "UnitOfMeasurePerPack": { "type": "integer" },
            "LineItemQuantity": { "type": "integer" },
            "LineItemValue": { "type": "float" },
            "PackPrice": { "type": "float" },
            "UnitPrice": { "type": "float" },
            "ManufacturingSite": { "type": "keyword" },
            "FirstLineDesignation": { "type": "keyword" },
            "WeightInKG": { "type": "keyword" },
            "FreightCostInUSD": { "type": "keyword" },
            "LineItemInsuranceInUSD": { "type": "float" },
            "PoSentToVendorDate_DayOfWeek": { "type": "integer" },
            "PoSentToVendorDate_DayOfMonth": { "type": "integer" },
            "PoSentToVendorDate_DayOfYear": { "type": "integer" },
            "PoSentToVendorDate_Month": { "type": "integer" },
            "PoSentToVendorDate_Quarter": { "type": "integer" },
            "PoSentToVendorDate_Year": { "type": "integer" },
            "ScheduledDeliveryDate_DayOfWeek": { "type": "integer" },
            "ScheduledDeliveryDate_DayOfMonth": { "type": "integer" },
            "ScheduledDeliveryDate_DayOfYear": { "type": "integer" },
            "ScheduledDeliveryDate_Month": { "type": "integer" },
            "ScheduledDeliveryDate_Quarter": { "type": "integer" },
            "ScheduledDeliveryDate_Year": { "type": "integer" },
            "DeliveredToClientDate_DayOfWeek": { "type": "integer" },
            "DeliveredToClientDate_DayOfMonth": { "type": "integer" },
            "DeliveredToClientDate_DayOfYear": { "type": "integer" },
            "DeliveredToClientDate_Month": { "type": "integer" },
            "DeliveredToClientDate_Quarter": { "type": "integer" },
            "DeliveredToClientDate_Year": { "type": "integer" },
            "DeliveryRecordedDate_DayOfWeek": { "type": "integer" },
            "DeliveryRecordedDate_DayOfMonth": { "type": "integer" },
            "DeliveryRecordedDate_DayOfYear": { "type": "integer" },
            "DeliveryRecordedDate_Month": { "type": "integer" },
            "DeliveryRecordedDate_Quarter": { "type": "integer" },
            "DeliveryRecordedDate_Year": { "type": "integer" },
            "DaysLateOrEarly": { "type": "integer" },
            "DaysPoSentToDelivery": { "type": "integer" }
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
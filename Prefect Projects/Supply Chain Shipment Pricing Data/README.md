# Supply Chain Shipment Pricing Data - Prefect Pipeline

## Notes

- Rename features as such:
    - "id": "Id",
    - "project_code": "ProjectCode",
    - "pq_number": "PqNumber",
    - "po_or_so_num": "PoOrSoNumber",
    - "asn_or_dn_num": "AsnOrDnNumber",
    - "country_name": "CountryName",
    - "managed_by": "ManagedBy",
    - "fulfill_via": "FulfilledVia",
    - "vendor_inco_term": "VendorIncoTerm",
    - "shipment_mode": "ShipmentMode",
    - "pq_first_sent_to_client_date": "PqFirstSentToClientDate",
    - "po_sent_to_vendor_date": "PoSentToVendorDate",
    - "scheduled_delivery_date": "ScheduledDeliveryDate",
    - "delivered_to_client_date": "DeliveredToClientDate",
    - "delivery_recorded_date": "DeliveryRecordedDate",
    - "product_group": "ProductGroup",
    - "sub_classification": "SubClassification",
    - "vendor": "VendorName",
    - "item_desc": "ItemDescription",
    - "molecule_or_test_type": "MoleculeOrTestType",
    - "brand": "BrandName",
    - "dosage": "Dosage",
    - "dosage_form": "DosageForm",
    - "unit_of_measure_per_pack": "UnitOfMeasurePerPack",
    - "line_item_quantity": "LineItemQuantity",
    - "line_item_value": "LineItemValue",
    - "pack_price": "PackPrice",
    - "unit_price": "UnitPrice",
    - "manufacturing_site": "ManufacturingSite",
    - "first_line_designation": "FirstLineDesignation",
    - "weight_in_kg": "WeightInKG",
    - "freight_cost_in_usd": "FreightCostInUSD",
    - "line_item_insurance_in_usd": "LineItemInsuranceInUSD"
- Clean the values in these columns up:
    - titlecase, and strip leading and trailing whitespace as well as replace '&' with 'And' for the following features: 
        - CountryName
        - SubClassification
        - ManagedBy
        - VendorName
        - ShipmentMode
        - FulfilledVia
        - DosageForm
        - vendor_inco_term (clean this value: 'N/A - From RDC')
- Handle nulls:
    - line_item_insurance_in_usd -> -1
- Handle dates:
    - Convert 'Date Not Captured' to 01/01/1900 in the following columns:
        - PoSentToVendorDate,
        - ScheduledDeliveryDate,
        - DeliveredToClientDate,
        - DeliveryRecordedDate
    - Then, convert all 4 of the columns from string to date
    - Then, extract date parts for all 4 of the dates
    - Finally, Calculate the number of days between:
        - DeliveredToClientDate - ScheduledDeliveryDate AS DaysLateOrEarly
        - PoSentToVendorDate - DeliveredToClientDate AS DaysPoSentUntilDelivery

## Dataset Source
https://www.kaggle.com/datasets/divyeshardeshana/supply-chain-shipment-pricing-data
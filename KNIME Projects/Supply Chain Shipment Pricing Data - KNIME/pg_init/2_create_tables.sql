\c sc_shipping_prices_pg;

GRANT ALL PRIVILEGES ON DATABASE sc_shipping_prices_pg TO pg;

CREATE TABLE IF NOT EXISTS sc_ship_prices_table (
    id INTEGER,
    project_code VARCHAR(10),
    pq_number VARCHAR(14),
    po_or_so_num VARCHAR(11),
    asn_or_dn_num VARCHAR(9),
    country_name VARCHAR(18),
    managed_by VARCHAR(25),
    fulfill_via VARCHAR(11),
    vendor_inco_term VARCHAR(14),
    shipment_mode VARCHAR(11),
    pq_first_sent_to_client_date VARCHAR(17),
    po_sent_to_vendor_date VARCHAR(17),
    scheduled_delivery_date VARCHAR(9),
    delivered_to_client_date VARCHAR(9),
    delivery_recorded_date VARCHAR(9),
    product_group VARCHAR(4),
    sub_classification VARCHAR(20),
    vendor VARCHAR(65),
    item_desc VARCHAR(113),
    molecule_or_test_type VARCHAR(98),
    brand VARCHAR(15),
    dosage VARCHAR(15),
    dosage_form VARCHAR(34),
    unit_of_measure_per_pack FLOAT,
    line_item_quantity FLOAT,
    line_item_value FLOAT,
    pack_price FLOAT,
    unit_price FLOAT,
    manufacturing_site VARCHAR(72),
    first_line_designation VARCHAR(3),
    weight_in_kg VARCHAR(26),
    freight_cost_in_usd VARCHAR(34),
    line_item_insurance_in_usd FLOAT
);
GRANT SELECT ON supply_chain_shipment_pricing_data_db_mysql.* TO 'mysql'@'%';
FLUSH PRIVILEGES;

-- drop table, if exists, to start from scratch
DROP TABLE IF EXISTS supply_chain_shipment_pricing_data_db_mysql;

-- Create flights_data_table_mysql Table
CREATE TABLE supply_chain_shipment_pricing_data_table_mysql (
    `id` INTEGER PRIMARY KEY,
    `project_code` VARCHAR(12),
    `pq_number` VARCHAR(18),
    `po_or_so_num` VARCHAR(14),
    `asn_or_dn_num` VARCHAR(12),
    `country_name` VARCHAR(24),
    `managed_by` VARCHAR(30),
    `fulfilled_via` VARCHAR(15),
    `vendor_inco_term` VARCHAR(18),
    `shipment_mode` VARCHAR(14),
    `pq_first_sent_to_client_date` VARCHAR(20),
    `po_sent_to_vendor_date` VARCHAR(20),
    `scheduled_delivery_date` VARCHAR(12),
    `delivered_to_client_date` VARCHAR(12),
    `delivery_recorded_date` VARCHAR(12),
    `product_group` VARCHAR(6),
    `sub_classification` VARCHAR(30),
    `vendor` VARCHAR(65),
    `item_desc` VARCHAR(125),
    `molecule_or_test_type` VARCHAR(110),
    `brand` VARCHAR(20),
    `dosage` VARCHAR(20),
    `dosage_form` VARCHAR(40),
    `unit_of_measure_per_pack` INTEGER,
    `line_item_quantity` INTEGER,
    `line_item_value` FLOAT,
    `pack_price` FLOAT,
    `unit_price` FLOAT,
    `manufacturing_site` VARCHAR(80),
    `first_line_designation` VARCHAR(6),
    `weight_in_kg` VARCHAR(40),
    `freight_cost_in_usd` VARCHAR(40),
    `line_item_insurance_in_usd` FLOAT
);
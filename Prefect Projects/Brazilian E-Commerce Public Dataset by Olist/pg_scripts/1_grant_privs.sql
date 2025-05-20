\c brazilian_ecomm_public_dataset_pg_db;

GRANT ALL PRIVILEGES ON DATABASE brazilian_ecomm_public_dataset_pg_db TO pg;

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
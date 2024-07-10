\c dataco_scd_db;

-- Table: dataco_scd_table
CREATE SEQUENCE dataco_sc_seq;

-- 1. Add a new INTEGER column
ALTER TABLE dataco_scd_table ADD COLUMN id INTEGER;

-- 2. Populate the new column with unique values
UPDATE dataco_scd_table SET id = nextval('dataco_sc_seq');

-- 3. Make the new column NOT NULL
ALTER TABLE dataco_scd_table ALTER COLUMN id SET NOT NULL;

-- 4. Set the new column as auto-incrementing
ALTER TABLE dataco_scd_table ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY;
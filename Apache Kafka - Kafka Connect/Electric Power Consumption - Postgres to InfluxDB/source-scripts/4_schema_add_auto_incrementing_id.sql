\c epc_db;

-- Table: epc_table
CREATE SEQUENCE epc_seq;

-- 1. Add a new INTEGER column
ALTER TABLE epc_table ADD COLUMN id INTEGER;

-- 2. Populate the new column with unique values
UPDATE epc_table SET id = nextval('epc_seq');

-- 3. Make the new column NOT NULL
ALTER TABLE epc_table ALTER COLUMN id SET NOT NULL;

-- 4. Set the new column as auto-incrementing
ALTER TABLE epc_table ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY;
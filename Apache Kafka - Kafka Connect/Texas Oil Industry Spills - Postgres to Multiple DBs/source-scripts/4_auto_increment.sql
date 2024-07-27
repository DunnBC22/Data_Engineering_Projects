\c texas_ois;

-- Table: texas_ois_central
CREATE SEQUENCE texas_ois_seq_central;

-- 1. Add a new INTEGER column
ALTER TABLE texas_ois_central ADD COLUMN id INTEGER;

-- 2. Populate the new column with unique values
UPDATE texas_ois_central SET id = nextval('texas_ois_seq_central');

-- 3. Make the new column NOT NULL
ALTER TABLE texas_ois_central ALTER COLUMN id SET NOT NULL;

-- 4. Set the new column as auto-incrementing
ALTER TABLE texas_ois_central ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY;



-- Table: texas_ois_district
CREATE SEQUENCE texas_ois_seq_district;

-- 1. Add a new INTEGER column
ALTER TABLE texas_ois_district ADD COLUMN id INTEGER;

-- 2. Populate the new column with unique values
UPDATE texas_ois_district SET id = nextval('texas_ois_seq_district');

-- 3. Make the new column NOT NULL
ALTER TABLE texas_ois_district ALTER COLUMN id SET NOT NULL;

-- 4. Set the new column as auto-incrementing
ALTER TABLE texas_ois_district ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY;
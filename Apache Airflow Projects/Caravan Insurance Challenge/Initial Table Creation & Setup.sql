-- db name: caravan_insurance_pred_db
-- owner: airflow

CREATE TABLE IF NOT EXISTS caravan_insurance_pred (
    ORIGIN VARCHAR,
    MOSTYPE INTEGER,
    MAANTHUI INTEGER,
    MGEMOMV INTEGER,
    MGEMLEEF INTEGER,
    MOSHOOFD INTEGER,
    MGODRK INTEGER,
    MGODPR INTEGER,
    MGODOV INTEGER,
    MGODGE INTEGER,
    MRELGE INTEGER,
    MRELSA INTEGER,
    MRELOV INTEGER,
    MFALLEEN INTEGER,
    MFGEKIND INTEGER,
    MFWEKIND INTEGER,
    MOPLHOOG INTEGER,
    MOPLMIDD INTEGER,
    MOPLLAAG INTEGER,
    MBERHOOG INTEGER,
    MBERZELF INTEGER,
    MBERBOER INTEGER,
    MBERMIDD INTEGER,
    MBERARBG INTEGER,
    MBERARBO INTEGER,
    MSKA INTEGER,
    MSKB1 INTEGER,
    MSKB2 INTEGER,
    MSKC INTEGER,
    MSKD INTEGER,
    MHHUUR INTEGER,
    MHKOOP INTEGER,
    MAUT1 INTEGER,
    MAUT2 INTEGER,
    MAUT0 INTEGER,
    MZFONDS INTEGER,
    MZPART INTEGER,
    MINKM30 INTEGER,
    MINK3045 INTEGER,
    MINK4575 INTEGER,
    MINK7512 INTEGER,
    MINK123M INTEGER,
    MINKGEM INTEGER,
    MKOOPKLA INTEGER,
    PWAPART INTEGER,
    PWABEDR INTEGER,
    PWALAND INTEGER,
    PPERSAUT INTEGER,
    PBESAUT INTEGER,
    PMOTSCO INTEGER,
    PVRAAUT INTEGER,
    PAANHANG INTEGER,
    PTRACTOR INTEGER,
    PWERKT INTEGER,
    PBROM INTEGER,
    PLEVEN INTEGER,
    PPERSONG INTEGER,
    PGEZONG INTEGER,
    PWAOREG INTEGER,
    PBRAND INTEGER,
    PZEILPL INTEGER,
    PPLEZIER INTEGER,
    PFIETS INTEGER,
    PINBOED INTEGER,
    PBYSTAND INTEGER,
    AWAPART INTEGER,
    AWABEDR INTEGER,
    AWALAND INTEGER,
    APERSAUT INTEGER,
    ABESAUT INTEGER,
    AMOTSCO INTEGER,
    AVRAAUT INTEGER,
    AAANHANG INTEGER,
    ATRACTOR INTEGER,
    AWERKT INTEGER,
    ABROM INTEGER,
    ALEVEN INTEGER,
    APERSONG INTEGER,
    AGEZONG INTEGER,
    AWAOREG INTEGER,
    ABRAND INTEGER,
    AZEILPL INTEGER,
    APLEZIER INTEGER,
    AFIETS INTEGER,
    AINBOED INTEGER,
    ABYSTAND INTEGER,
    CARAVAN INTEGER
);

COPY caravan_insurance_pred(
    ORIGIN,
    MOSTYPE,
    MAANTHUI,
    MGEMOMV,
    MGEMLEEF,
    MOSHOOFD,
    MGODRK,
    MGODPR,
    MGODOV,
    MGODGE,
    MRELGE,
    MRELSA,
    MRELOV,
    MFALLEEN,
    MFGEKIND,
    MFWEKIND,
    MOPLHOOG,
    MOPLMIDD,
    MOPLLAAG,
    MBERHOOG,
    MBERZELF,
    MBERBOER,
    MBERMIDD,
    MBERARBG,
    MBERARBO,
    MSKA,
    MSKB1,
    MSKB2,
    MSKC,
    MSKD,
    MHHUUR,
    MHKOOP,
    MAUT1,
    MAUT2,
    MAUT0,
    MZFONDS,
    MZPART,
    MINKM30,
    MINK3045,
    MINK4575,
    MINK7512,
    MINK123M,
    MINKGEM,
    MKOOPKLA,
    PWAPART,
    PWABEDR,
    PWALAND,
    PPERSAUT,
    PBESAUT,
    PMOTSCO,
    PVRAAUT,
    PAANHANG,
    PTRACTOR,
    PWERKT,
    PBROM,
    PLEVEN,
    PPERSONG,
    PGEZONG,
    PWAOREG,
    PBRAND,
    PZEILPL,
    PPLEZIER,
    PFIETS,
    PINBOED,
    PBYSTAND,
    AWAPART,
    AWABEDR,
    AWALAND,
    APERSAUT,
    ABESAUT,
    AMOTSCO,
    AVRAAUT,
    AAANHANG,
    ATRACTOR,
    AWERKT,
    ABROM,
    ALEVEN,
    APERSONG,
    AGEZONG,
    AWAOREG,
    ABRAND,
    AZEILPL,
    APLEZIER,
    AFIETS,
    AINBOED,
    ABYSTAND,
    CARAVAN
    )
FROM '/Users/briandunn/Desktop/Projects 2/Caravan Insurance Challenge/caravan-insurance-challenge.csv'
DELIMITER ','
CSV HEADER;

/* 
Create the dim tables that were setup by the author of the dataset.
*/

-- create table for customer_subtype_dim
CREATE TABLE IF NOT EXISTS customer_subtype_dim(
    ID INTEGER, 
    customer_subtype VARCHAR
);

-- insert values for customer_subtype_dim
-- insert values for customer_subtype_dim
INSERT INTO customer_subtype_dim(ID, customer_subtype)
VALUES 
    (1, 'High_Income_expensive_child'),
    (2, 'Very_Important_Provincials'),
    (3, 'High_status_seniors'),
    (4, 'Affluent_senior_apartments'),
    (5, 'Mixed_seniors'),
    (6, 'Career_and_childcare'),
    (7, 'dinki'),
    (8, 'Middle_class_families'),
    (9, 'Modern_complete_families'),
    (10, 'Stable_family'),
    (11, 'Family_starters'),
    (12, 'Affluent_young_families'),
    (13, 'Young_all_american_family'),
    (14, 'Junior_cosmopolitan'),
    (15, 'Senior_cosmopolitans'),
    (16, 'Students_in_apartments'),
    (17, 'Fresh_masters_in_the_city'),
    (18, 'Single_youth'),
    (19, 'Suburban_youth'),
    (20, 'Etnically_diverse'),
    (21, 'Young_urban_have_nots'),
    (22, 'Mixed_apartment_dwellers'),
    (23, 'Young_and_rising'),
    (24, 'Young_low_educated'),
    (25, 'Young_seniors_in_the_city'),
    (26, 'Own_home_elderly'),
    (27, 'Seniors_in_apartments'),
    (28, 'Residential_elderly'),
    (29, 'Porchless_seniors_no_front_yard'),
    (30, 'Religious_elderly_singles'),
    (31, 'Low_income_catholics'),
    (32, 'Mixed_seniors'),
    (33, 'Lower_class_large_families'),
    (34, 'Large_family_employed_child'),
    (35, 'Village_families'),
    (36, 'Couples_with_teens_Married_with_children'),
    (37, 'Mixed_small_town_dwellers'),
    (38, 'Traditional_families'),
    (39, 'Large_religous_families'),
    (40, 'Large_family_farms'),
    (41, 'Mixed_rurals');

--create table for avg_age_keys_dim
CREATE TABLE IF NOT EXISTS avg_age_keys_dim(
    ID INTEGER, 
    avg_age_category VARCHAR
);

-- insert values into avg_age_keys_dim
INSERT INTO avg_age_keys_dim(ID, avg_age_category)
VALUES 
(1, '20_30 years'),
(2, '30_40 years'),
(3, '40_50 years'),
(4, '50_60 years'),
(5, '60_70 years'),
(6, '70_80 years');


-- create table for customer_main_type_keys_dim
CREATE TABLE IF NOT EXISTS customer_main_type_keys_dim(
    ID INTEGER, 
    customer_main_type VARCHAR
);

-- insert values into customer_main_type_keys_dim
INSERT INTO customer_main_type_keys_dim (ID, customer_main_type)
VALUES 
    (1, 'Successful_hedonists'),
    (2, 'Driven_Growers'),
    (3, 'Average_Family'),
    (4, 'Career_Loners'),
    (5, 'Living_well'),
    (6, 'Cruising_Seniors'),
    (7, 'Retired_and_Religeous'),
    (8, 'Family_with_grown_ups'),
    (9, 'Conservative_families'),
    (10, 'Farmers');


-- create table for percentage_keys_dim
CREATE TABLE IF NOT EXISTS percentage_keys_dim(
    ID INTEGER, 
    percent_key VARCHAR
);

-- insert values into percentage_keys_dim
INSERT INTO percentage_keys_dim(ID, percent_key)
VALUES 
    (0, '0_percent'),
    (1, '1_10_percent'),
    (2, '11_23_percent'),
    (3, '24_36_percent'),
    (4, '37_49_percent'),
    (5, '50_62_percent'),
    (6, '63_75_percent'),
    (7, '76_88_percent'),
    (8, '89_99_percent'),
    (9, '100_percent');


-- create table for total_num_keys_dim
CREATE TABLE IF NOT EXISTS total_num_keys_dim(
    ID INTEGER,
    num_keys VARCHAR
);

-- insert values into total_num_keys_dim
INSERT INTO total_num_keys_dim (ID, num_keys)
VALUES 
    (0, '0'),
    (1, '1_49'),
    (2, '50_99'),
    (3, '100_199'),
    (4, '200_499'),
    (5, '500_999'),
    (6, '1000_4999'),
    (7, '5000_9999'),
    (8, '10000_19999'),
    (9, '>= 20000');
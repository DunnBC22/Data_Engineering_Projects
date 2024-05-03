\c maang_stock_source;
DROP TABLE IF EXISTS maang_source_amazon;
CREATE TABLE maang_source_amazon (id INTEGER PRIMARY KEY NOT NULL,trading_date DATE,trading_open FLOAT,trading_high FLOAT,trading_low FLOAT,trading_close FLOAT,trading_adj_close FLOAT,trading_volume BIGINT);
GRANT SELECT ON maang_source_amazon TO pg;

DROP TABLE IF EXISTS maang_source_apple;
CREATE TABLE maang_source_apple (id INTEGER PRIMARY KEY NOT NULL,trading_date DATE,trading_open FLOAT,trading_high FLOAT,trading_low FLOAT,trading_close FLOAT,trading_adj_close FLOAT,trading_volume BIGINT);
GRANT SELECT ON maang_source_apple TO pg;

DROP TABLE IF EXISTS maang_source_google;
CREATE TABLE maang_source_google (id INTEGER PRIMARY KEY NOT NULL,trading_date DATE,trading_open FLOAT,trading_high FLOAT,trading_low FLOAT,trading_close FLOAT,trading_adj_close FLOAT,trading_volume BIGINT);
GRANT SELECT ON maang_source_google TO pg;

DROP TABLE IF EXISTS maang_source_meta;
CREATE TABLE maang_source_meta (id INTEGER PRIMARY KEY NOT NULL,trading_date DATE,trading_open FLOAT,trading_high FLOAT,trading_low FLOAT,trading_close FLOAT,trading_adj_close FLOAT,trading_volume BIGINT);
GRANT SELECT ON maang_source_meta TO pg;

DROP TABLE IF EXISTS maang_source_netflix;
CREATE TABLE maang_source_netflix (id INTEGER PRIMARY KEY NOT NULL,trading_date DATE,trading_open FLOAT,trading_high FLOAT,trading_low FLOAT,trading_close FLOAT,trading_adj_close FLOAT,trading_volume BIGINT);
GRANT SELECT ON maang_source_netflix TO pg;
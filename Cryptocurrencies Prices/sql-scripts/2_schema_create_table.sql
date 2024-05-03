\c crypto_prices;

DROP TABLE IF EXISTS crypto_ada_usd;
CREATE TABLE crypto_ada_usd (trading_id INTEGER PRIMARY KEY NOT NULL,trading_date DATE,trading_open FLOAT,trading_high FLOAT,trading_low FLOAT,trading_close FLOAT,trading_adj_close FLOAT,trading_volume BIGINT);
GRANT SELECT ON crypto_ada_usd TO pg;

DROP TABLE IF EXISTS crypto_avax_usd;
CREATE TABLE crypto_avax_usd (trading_id INTEGER PRIMARY KEY NOT NULL,trading_date DATE,trading_open FLOAT,trading_high FLOAT,trading_low FLOAT,trading_close FLOAT,trading_adj_close FLOAT,trading_volume BIGINT);
GRANT SELECT ON crypto_avax_usd TO pg;

DROP TABLE IF EXISTS crypto_bnb_usd;
CREATE TABLE crypto_bnb_usd (trading_id INTEGER PRIMARY KEY NOT NULL,trading_date DATE,trading_open FLOAT,trading_high FLOAT,trading_low FLOAT,trading_close FLOAT,trading_adj_close FLOAT,trading_volume BIGINT);
GRANT SELECT ON crypto_bnb_usd TO pg;

DROP TABLE IF EXISTS crypto_btc_usd;
CREATE TABLE crypto_btc_usd (trading_id INTEGER PRIMARY KEY NOT NULL,trading_date DATE,trading_open FLOAT,trading_high FLOAT,trading_low FLOAT,trading_close FLOAT,trading_adj_close FLOAT,trading_volume BIGINT);
GRANT SELECT ON crypto_btc_usd TO pg;

DROP TABLE IF EXISTS crypto_doge_usd;
CREATE TABLE crypto_doge_usd (trading_id INTEGER PRIMARY KEY NOT NULL,trading_date DATE,trading_open FLOAT,trading_high FLOAT,trading_low FLOAT,trading_close FLOAT,trading_adj_close FLOAT,trading_volume BIGINT);
GRANT SELECT ON crypto_doge_usd TO pg;

DROP TABLE IF EXISTS crypto_eth_usd;
CREATE TABLE crypto_eth_usd (trading_id INTEGER PRIMARY KEY NOT NULL,trading_date DATE,trading_open FLOAT,trading_high FLOAT,trading_low FLOAT,trading_close FLOAT,trading_adj_close FLOAT,trading_volume BIGINT);
GRANT SELECT ON crypto_eth_usd TO pg;

DROP TABLE IF EXISTS crypto_sol_usd;
CREATE TABLE crypto_sol_usd (trading_id INTEGER PRIMARY KEY NOT NULL,trading_date DATE,trading_open FLOAT,trading_high FLOAT,trading_low FLOAT,trading_close FLOAT,trading_adj_close FLOAT,trading_volume BIGINT);
GRANT SELECT ON crypto_sol_usd TO pg;

DROP TABLE IF EXISTS crypto_trx_usd;
CREATE TABLE crypto_trx_usd (trading_id INTEGER PRIMARY KEY NOT NULL,trading_date DATE,trading_open FLOAT,trading_high FLOAT,trading_low FLOAT,trading_close FLOAT,trading_adj_close FLOAT,trading_volume BIGINT);
GRANT SELECT ON crypto_trx_usd TO pg;

DROP TABLE IF EXISTS crypto_usdt_usd;
CREATE TABLE crypto_usdt_usd (trading_id INTEGER PRIMARY KEY NOT NULL,trading_date DATE,trading_open FLOAT,trading_high FLOAT,trading_low FLOAT,trading_close FLOAT,trading_adj_close FLOAT,trading_volume BIGINT);
GRANT SELECT ON crypto_usdt_usd TO pg;

DROP TABLE IF EXISTS crypto_xrp_usd;
CREATE TABLE crypto_xrp_usd (trading_id INTEGER PRIMARY KEY NOT NULL,trading_date DATE,trading_open FLOAT,trading_high FLOAT,trading_low FLOAT,trading_close FLOAT,trading_adj_close FLOAT,trading_volume BIGINT);
GRANT SELECT ON crypto_xrp_usd TO pg;
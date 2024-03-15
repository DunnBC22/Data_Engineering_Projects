/*
ada_usd
avax_usd
bnb_usd
btc_usd
doge_usd
eth_usd
sol_usd
trx_usd
usdt_usd
xrp_usd
*/

CREATE STREAM crypto_ada_usd (
    trading_date DATE,
    trading_open DOUBLE,
    trading_high DOUBLE,
    trading_low DOUBLE,
    trading_close DOUBLE,
    trading_adj_close DOUBLE,
    trading_volume BIGINT
)
WITH 
(
    kafka_topic='crypto_ada_usd',
    value_format='json',
    partitions=2
);

CREATE STREAM crypto_avax_usd (
    trading_date DATE,
    trading_open DOUBLE,
    trading_high DOUBLE,
    trading_low DOUBLE,
    trading_close DOUBLE,
    trading_adj_close DOUBLE,
    trading_volume BIGINT
)
WITH 
(
    kafka_topic='crypto_avax_usd',
    value_format='json',
    partitions=2
);

CREATE STREAM crypto_bnb_usd (
    trading_date DATE,
    trading_open DOUBLE,
    trading_high DOUBLE,
    trading_low DOUBLE,
    trading_close DOUBLE,
    trading_adj_close DOUBLE,
    trading_volume BIGINT
)
WITH 
(
    kafka_topic='crypto_bnb_usd',
    value_format='json',
    partitions=2
);

CREATE STREAM crypto_btc_usd (
    trading_date DATE,
    trading_open DOUBLE,
    trading_high DOUBLE,
    trading_low DOUBLE,
    trading_close DOUBLE,
    trading_adj_close DOUBLE,
    trading_volume BIGINT
)
WITH 
(
    kafka_topic='crypto_btc_usd',
    value_format='json',
    partitions=2
);

CREATE STREAM crypto_doge_usd (
    trading_date DATE,
    trading_open DOUBLE,
    trading_high DOUBLE,
    trading_low DOUBLE,
    trading_close DOUBLE,
    trading_adj_close DOUBLE,
    trading_volume BIGINT
)
WITH 
(
    kafka_topic='crypto_doge_usd',
    value_format='json',
    partitions=2
);

CREATE STREAM crypto_eth_usd (
    trading_date DATE,
    trading_open DOUBLE,
    trading_high DOUBLE,
    trading_low DOUBLE,
    trading_close DOUBLE,
    trading_adj_close DOUBLE,
    trading_volume BIGINT
)
WITH 
(
    kafka_topic='crypto_eth_usd',
    value_format='json',
    partitions=2
);

CREATE STREAM crypto_sol_usd (
    trading_date DATE,
    trading_open DOUBLE,
    trading_high DOUBLE,
    trading_low DOUBLE,
    trading_close DOUBLE,
    trading_adj_close DOUBLE,
    trading_volume BIGINT
)
WITH 
(
    kafka_topic='crypto_sol_usd',
    value_format='json',
    partitions=2
);

CREATE STREAM crypto_trx_usd (
    trading_date DATE,
    trading_open DOUBLE,
    trading_high DOUBLE,
    trading_low DOUBLE,
    trading_close DOUBLE,
    trading_adj_close DOUBLE,
    trading_volume BIGINT
)
WITH 
(
    kafka_topic='crypto_trx_usd',
    value_format='json',
    partitions=2
);

CREATE STREAM crypto_usdt_usd (
    trading_date DATE,
    trading_open DOUBLE,
    trading_high DOUBLE,
    trading_low DOUBLE,
    trading_close DOUBLE,
    trading_adj_close DOUBLE,
    trading_volume BIGINT
)
WITH 
(
    kafka_topic='crypto_usdt_usd',
    value_format='json',
    partitions=2
);

CREATE STREAM crypto_xrp_usd (
    trading_date DATE,
    trading_open DOUBLE,
    trading_high DOUBLE,
    trading_low DOUBLE,
    trading_close DOUBLE,
    trading_adj_close DOUBLE,
    trading_volume BIGINT
)
WITH 
(
    kafka_topic='crypto_xrp_usd',
    value_format='json',
    partitions=2
);



-- Create STREAM for combining all of the stocks into one file

CREATE STREAM all_crypto_stock (
    ticker_symbol VARCHAR,
    trading_date DATE,
    trading_open DOUBLE,
    trading_high DOUBLE,
    trading_low DOUBLE,
    trading_close DOUBLE,
    trading_adj_close DOUBLE,
    trading_volume BIGINT
)
WITH 
(
    kafka_topic='all_crypto',
    value_format='json',
    partitions=2
);
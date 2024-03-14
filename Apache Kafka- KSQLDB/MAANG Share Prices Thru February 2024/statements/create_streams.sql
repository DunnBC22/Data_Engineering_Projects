/*
google_stock
amazon_stock
apple_stock
meta_stock
netflix_stock
*/

CREATE STREAM maang_stock_google_stock (
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
    kafka_topic='maang_stock_google_stock',
    value_format='json',
    partitions=1
);

CREATE STREAM maang_stock_amazon_stock (
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
    kafka_topic='maang_stock_amazon_stock',
    value_format='json',
    partitions=1
);

CREATE STREAM maang_stock_apple_stock (
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
    kafka_topic='maang_stock_apple_stock',
    value_format='json',
    partitions=1
);

CREATE STREAM maang_stock_meta_stock (
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
    kafka_topic='maang_stock_meta_stock',
    value_format='json',
    partitions=1
);

CREATE STREAM maang_stock_netflix_stock (
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
    kafka_topic='maang_stock_netflix_stock',
    value_format='json',
    partitions=1
);

-- Create STREAM for combining all of the stocks into one file

CREATE STREAM all_maang_stock (
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
    kafka_topic='all_maang_stock',
    value_format='json',
    partitions=1
);
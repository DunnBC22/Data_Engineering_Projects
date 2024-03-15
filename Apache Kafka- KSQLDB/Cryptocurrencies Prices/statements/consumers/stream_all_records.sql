CREATE STREAM STREAM_ALL_CRYPTO_DATA AS 
    SELECT
        ticker_symbol,
        CAST(trading_date AS VARCHAR) AS Trading_Date,
        SUBSTRING(CAST(trading_date AS VARCHAR), 1, 4) AS Trading_Year,
        trading_open,
        trading_high,
        trading_low,
        trading_close,
        trading_adj_close,
        trading_volume
    FROM
        all_crypto_stock
    EMIT CHANGES;
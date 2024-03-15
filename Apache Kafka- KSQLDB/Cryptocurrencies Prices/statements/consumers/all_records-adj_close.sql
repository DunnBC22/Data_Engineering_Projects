CREATE STREAM ADJ_CLOSING_PRICE_FOR_ALL_CRYPTO AS
    SELECT
        ticker_symbol,
        CAST(trading_date AS VARCHAR) AS Trading_Date,
        SUBSTRING(CAST(trading_date AS VARCHAR), 1, 4) AS Trading_Year,
        trading_adj_close
    FROM 
        all_crypto_stock
    EMIT CHANGES;
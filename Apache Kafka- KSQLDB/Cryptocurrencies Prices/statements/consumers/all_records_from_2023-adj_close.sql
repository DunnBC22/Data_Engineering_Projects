CREATE STREAM ADJ_CLOSING_PRICE_FOR_ALL_CRYPTO_IN_2023 AS
    SELECT
        ticker_symbol AS Ticker_Symbol,
        CAST(trading_date AS VARCHAR) AS Trading_Date,
        SUBSTRING(CAST(trading_date AS VARCHAR), 1, 4) AS Trading_Year,
        trading_adj_close AS Adjusted_Close
    FROM 
        all_crypto_stock
    WHERE 
        FORMAT_DATE(trading_date, 'yyyy') = '2023'
    EMIT CHANGES;
CREATE STREAM stream_volume_and_adj_close_maang_stock_data AS 
    SELECT
        ticker_symbol,
        trading_date,
        trading_adj_close,
        trading_volume
    FROM 
        all_maang_stock
    EMIT CHANGES;
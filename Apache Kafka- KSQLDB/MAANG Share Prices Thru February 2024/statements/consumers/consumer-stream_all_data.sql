CREATE STREAM stream_all_maang_stock_data AS 
    SELECT
        trading_date,
        trading_open,
        trading_high,
        trading_low,
        trading_close,
        trading_adj_close,
        trading_volume
    FROM 
        all_maang_stock
    EMIT CHANGES;
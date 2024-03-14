CREATE TABLE REVENUE_GEN_AND_QUANTITY_EACH_COMPANY AS 
    SELECT
        c.company_name AS Company_Name,
        SUM(p.quantity) AS Quantity,
        SUM(p.revenue) AS Revenue_Generated,
        ROUND(SUM(p.quantity)/SUM(p.revenue), 2) AS Revenue_Generated_Per_Item
    FROM 
        purchases p
    LEFT JOIN
        companies c
    ON 
        p.company_id=c.company_id
    GROUP BY
        c.company_name
    EMIT CHANGES;
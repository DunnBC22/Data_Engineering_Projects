CREATE STREAM purchases_w_company_info AS 
    SELECT 
        p.purchases_date AS Purchase_Date,
        p.company_id AS Company_ID,
        p.product_category AS Product_Category,
        p.quantity AS Quantity,
        p.revenue AS Revenue_Generated,
        c.company_name AS Company_Name,
        c.company_location AS Company_Location,
        c.company_type AS Company_Type,
        c.employees AS Employee_Count_Category
    FROM 
        purchases p
    LEFT JOIN
        companies c
    ON 
        p.company_id=c.company_id
    EMIT CHANGES;

CREATE STREAM RETIREMENT_PLANNING_MARKETING_DATA AS 
    SELECT
        c.cust_id AS Customer_ID,
        c.first_name AS First_Name,
        c.last_name AS Last_Name,
        c.gender AS Gender,
        c.email AS Email_Address,
        c.birth_year AS Birth_Year,
        c.profession AS Profession,
        c.monthly_net_income AS Monthly_Net_Income,
        c.education_level AS Education_Level,
        c.employment_status AS Employment_Status,
        c.marital_status AS Marital_Status,
        c.age_range AS Age_Range,
        a.acquisition_cost AS Acquisition_Cost,
        a.internet_banking_indicator AS Internet_Banking_Indicator,
        a.primary_advisor_organization_id AS Primary_Advisor_Organization_Id,
        a.primary_branch_proximity AS Primary_Branch_Proximity,
        a.satisfaction_rating_from_survey AS Satisfaction_rating_from_survey,
        a.special_te AS Special_Terms_Indicator,
        c.current_employment_start_date AS Current_Employment_Start_Date,
        c.customer_behavior AS Customer_Behavior,
        c.retirement_age AS Retirement_Age,
        c.customer_status AS Customer_Status,
        c.wallet_share_percentage AS Wallet_Share_Percentage,
        f.monthly_housing_cost AS Monthly_Housing_Cost,
        f.contact_preference AS Contact_Preference,
        f.credit_authority_level AS Credit_Authority_Level,
        f.credit_score AS Credit_Score,
        f.credit_utilization AS Credit_Utilization,
        f.debt_service_coverage_ratio AS Debt_Service_Coverage_Ratio,
        h.household_address AS Household_Address,
        h.household_city AS Household_City,
        h.household_country AS Household_Country,
        h.household_state AS Household_State,
        h.household_zip_code AS Household_Zip_Code,
        h.number_of_dependent_adults AS Number_Of_Dependent_Adults,
        h.number_of_dependent_children AS Number_Of_Dependent_Children,
        h.family_size AS Family_Size,
        h.head_of_household_indicator AS Head_Of_Household_Indicator,
        h.home_owner_indicator AS Home_Owner_Indicator,
        h.urban_code AS Urban_Code,
        m.advertising_indicator AS Advertising_Indicator,
        m.attachment_allowed_indicator AS Attachment_Allowed_Indicator,
        m.preferred_communication_form AS Preferred_Communication_Form,
        m.importance_level_code AS Importance_Level_code,
        m.market_group AS Market_Group
    FROM
        account a
    INNER JOIN
        customer c
    WITHIN
        10 HOURS
    ON
        a.cust_id=c.cust_id
    INNER JOIN
        financials f
    WITHIN
        10 HOURS
    ON
        a.cust_id=f.cust_id
    INNER JOIN
        household h
    WITHIN
        10 HOURS
    ON
        a.cust_id=h.cust_id
    INNER JOIN
        marketing m
    WITHIN
        10 HOURS
    ON 
        a.cust_id=m.cust_id
    WHERE 
        a.pursuit = 'Retirement Planning'
    EMIT CHANGES;
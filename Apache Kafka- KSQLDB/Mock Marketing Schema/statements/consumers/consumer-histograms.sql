CREATE TABLE mock_marketing_schema_histograms AS 
    SELECT
        a.pursuit AS Pursuit,
        histogram(a.internet_banking_indicator) AS Internet_Banking_Indicator,
        histogram(a.satisfaction_rating_from_survey) AS Satisfaction_rating_from_survey,
        histogram(a.special_te) AS Special_Terms_Indicator,
        histogram(c.gender) AS Gender,
        histogram(c.age_range) AS Age_Range,
        histogram(c.customer_behavior) AS Customer_Behavior,
        histogram(c.education_level) AS Education_Level,
        histogram(c.employment_status) AS Employment_Status,
        histogram(c.marital_status) AS Marital_Status,
        histogram(c.profession) AS Profession,
        histogram(c.customer_status) AS Customer_Status,
        histogram(f.contact_preference) AS Contact_Preference,
        histogram(f.credit_authority_level) AS Credit_Authority_Level,
        histogram(h.household_city) AS Household_City,
        histogram(h.household_country) AS Household_Country,
        histogram(h.household_state) AS Household_State,
        histogram(h.head_of_household_indicator) AS Head_Of_Household_Indicator,
        histogram(h.home_owner_indicator) AS Home_Owner_Indicator,
        histogram(h.urban_code) AS Urban_Code,
        histogram(m.advertising_indicator) AS Advertising_Indicator,
        histogram(m.attachment_allowed_indicator) AS Attachment_Allowed_Indicator,
        histogram(m.preferred_communication_form) AS Preferred_Communication_Form,
        histogram(m.importance_level_code) AS Importance_Level_code,
        histogram(m.market_group) AS Market_Group,
        histogram(m.referrals_value_code) AS Referrals_Value_Code
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
    GROUP BY 
        a.pursuit
    EMIT CHANGES;
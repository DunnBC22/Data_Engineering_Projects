\c employee_separation_forecast_pg_db;

DROP TABLE IF EXISTS train_ee_sep_forecast_pg_table;
DROP TABLE IF EXISTS test_wo_results_ee_sep_forecast_pg_table;
DROP TABLE IF EXISTS test_results_ee_sep_forecast_pg_table;

CREATE TABLE train_ee_sep_forecast_pg_table (
    "ID" BIGINT,
    "Age" INTEGER,
    "BusinessTravel" VARCHAR,
    "Department" VARCHAR,
    "DistanceFromHome" INTEGER,
    "Education" INTEGER,
    "EducationField" VARCHAR,
    "EmployeeNumber" BIGINT,
    "EnvironmentSatisfaction" INTEGER,
    "Gender" VARCHAR,
    "JobInvolvement" INTEGER,
    "JobLevel" INTEGER,
    "JobRole" VARCHAR,
    "JobSatisfaction" INTEGER,
    "MaritalStatus" VARCHAR,
    "MonthlyIncome" BIGINT,
    "NumCompaniesWorked" INTEGER,
    "Over18" VARCHAR,
    "OverTime" VARCHAR,
    "PercentSalaryHike" INTEGER,
    "PerformanceRating" INTEGER,
    "RelationshipSatisfaction" INTEGER,
    "StandardHours" INTEGER,
    "StockOptionLevel" INTEGER,
    "TotalWorkingYears" INTEGER,
    "TrainingTimesLastYear" INTEGER,
    "WorkLifeBalance" INTEGER,
    "YearsAtCompany" INTEGER,
    "YearsInCurrentRole" INTEGER,
    "YearsSinceLastPromotion" INTEGER,
    "YearsWithCurrManager" INTEGER,
    "Label" INTEGER
);

CREATE TABLE test_wo_results_ee_sep_forecast_pg_table (
    "ID" BIGINT,
    "Age" INTEGER,
    "BusinessTravel" VARCHAR,
    "Department" VARCHAR,
    "DistanceFromHome" INTEGER,
    "Education" INTEGER,
    "EducationField" VARCHAR,
    "EmployeeNumber" BIGINT,
    "EnvironmentSatisfaction" INTEGER,
    "Gender" VARCHAR,
    "JobInvolvement" INTEGER,
    "JobLevel" INTEGER,
    "JobRole" VARCHAR,
    "JobSatisfaction" INTEGER,
    "MaritalStatus" VARCHAR,
    "MonthlyIncome" BIGINT,
    "NumCompaniesWorked" INTEGER,
    "Over18" VARCHAR,
    "OverTime" VARCHAR,
    "PercentSalaryHike" INTEGER,
    "PerformanceRating" INTEGER,
    "RelationshipSatisfaction" INTEGER,
    "StandardHours" INTEGER,
    "StockOptionLevel" INTEGER,
    "TotalWorkingYears" INTEGER,
    "TrainingTimesLastYear" INTEGER,
    "WorkLifeBalance" INTEGER,
    "YearsAtCompany" INTEGER,
    "YearsInCurrentRole" INTEGER,
    "YearsSinceLastPromotion" INTEGER,
    "YearsWithCurrManager" INTEGER
);

CREATE TABLE test_results_ee_sep_forecast_pg_table (
    "ID" BIGINT,
    "Label" INTEGER
);
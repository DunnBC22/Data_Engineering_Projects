CREATE TABLE IF NOT EXISTS dataco_sc_mariadb_table (
    Id INT PRIMARY KEY,
    TransactionType VARCHAR(12),
    ActualDaysToShip INTEGER,
    ScheduledDaysToShip INTEGER,
    BenefitPerOrder FLOAT,
    SalesPerCustomer FLOAT,
    DeliveryStatus VARCHAR(25),
    LateDeliveryRisk INTEGER,
    CategoryId INTEGER,
    CustomerId BIGINT,
    CustomerSegment VARCHAR(16),
    DepartmentId INTEGER,
    MarketName VARCHAR(36),
    OrderCity VARCHAR(40),
    OrderCountry VARCHAR(40),
    OrderCustomerId BIGINT,
    OrderDate VARCHAR(21),
    OrderId INTEGER,
    OrderItemCardProdId INTEGER,
    OrderItemDiscount FLOAT,
    OrderItemDiscountRate FLOAT,
    OrderItemId INTEGER,
    OrderItemProductPrice FLOAT,
    OrderItemProfitRatio FLOAT,
    OrderItemQuantity FLOAT,
    SalesAmount FLOAT,
    OrderItemTotal FLOAT,
    OrderProfitPerOrder FLOAT,
    OrderRegion VARCHAR(20),
    OrderState VARCHAR(42),
    OrderStatus VARCHAR(21),
    OrderZipCode INTEGER,
    ProductCardId INTEGER,
    ProductCategoryId INTEGER,
    ProductPrice FLOAT,
    ShippingDate VARCHAR(20),
    ShippingMode VARCHAR(20),
    OrderDate_DayOfWeek INTEGER,
    OrderDate_DayOfMonth INTEGER,
    OrderDate_DayOfYear INTEGER,
    OrderDate_Month INTEGER,
    OrderDate_Quarter INTEGER,
    OrderDate_Year INTEGER,
    ShippingDate_DayOfWeek INTEGER,
    ShippingDate_DayOfMonth INTEGER,
    ShippingDate_DayOfYear INTEGER,
    ShippingDate_Month INTEGER,
    ShippingDate_Quarter INTEGER,
    ShippingDate_Year INTEGER,
    geo_point VARCHAR(60)
);

CREATE TABLE IF NOT EXISTS CategoriesDim_mariadb_table (
    CategoryId INTEGER, 
    CategoryName VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS CustomersDim_mariadb_table (
    CustomerId INTEGER,
    CustomerCity VARCHAR(30),
    CustomerCountry VARCHAR(16),
    CustomerFirstName VARCHAR(16),
    CustomerLastName VARCHAR(18),
    CustomerState VARCHAR(8),
    CustomerStreet VARCHAR(40),
    CustomerZipCode INTEGER
);

CREATE TABLE IF NOT EXISTS DepartmentsDim_mariadb_table (
    DepartmentId INTEGER,
    DepartmentName VARCHAR(24)
);

CREATE TABLE IF NOT EXISTS ProductsDim_mariadb_table (
    ProductCardId INTEGER,
    ProductImage VARCHAR(110),
    ProductName VARCHAR(60)
);
CREATE KEYSPACE ecomm_website_logs_keyspace_cassie WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

CREATE TABLE ecomm_website_logs_keyspace_cassie.ecomm_website_logs_table_cassie (
    LogId INT,
	AccessedDate BIGINT,
	DurationInSeconds BIGINT,
	NetworkProtocol VARCHAR,
	IpAddress VARCHAR,
	BytesUsed INT,
	BrowserAccessedFrom VARCHAR,
	UserAge INT,
	UserGender VARCHAR,
	UserCountry VARCHAR,
	UserMembershipLevel VARCHAR,
	UserLanguage VARCHAR,
	SalesAmount FLOAT,
	ProductReturned INT,
	ReturnedAmount FLOAT,
	PaymentMethod VARCHAR,
	AccessedDate_DayOfWeek INT,
	AccessedDate_DayOfMonth INT,
	AccessedDate_DayOfYear INT,
	AccessedDate_Month INT,
	AccessedDate_Quarter INT,
	AccessedDate_Year INT,
    PRIMARY KEY (LogId)
);
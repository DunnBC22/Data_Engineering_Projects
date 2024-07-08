-- Create the login for kafka_user if it does not exist
IF NOT EXISTS (SELECT * FROM sys.server_principals WHERE name = 'kafka_user')
BEGIN
    CREATE LOGIN kafka_user WITH PASSWORD = 'VeryStrong!Passw0rd';
    PRINT 'Login kafka_user created.';
END
GO
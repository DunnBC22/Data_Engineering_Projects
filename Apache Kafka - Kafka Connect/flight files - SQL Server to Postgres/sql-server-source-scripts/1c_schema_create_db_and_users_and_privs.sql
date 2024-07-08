USE flight_files_source_db;
GO

-- Create the user for kafka_user and add to db_owner role
IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'kafka_user')
BEGIN
    CREATE USER kafka_user FOR LOGIN kafka_user;
    ALTER ROLE db_owner ADD MEMBER kafka_user;
    PRINT 'User kafka_user created and added to db_owner role.';
END
GO
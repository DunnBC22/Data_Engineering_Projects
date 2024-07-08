-- Create the database if it does not exist
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'flight_files_source_db')
BEGIN
    CREATE DATABASE flight_files_source_db;
    PRINT 'Database flight_files_source_db created.';
END
GO  
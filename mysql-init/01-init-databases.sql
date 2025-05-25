-- MySQL initialization script for healthcare system
-- This script creates all required databases and sets up user permissions

-- Drop and recreate databases to ensure clean state (only on first run)
-- Note: This only runs when the MySQL data volume is empty
DROP DATABASE IF EXISTS healthcare_sys;
DROP DATABASE IF EXISTS doctor_db;
DROP DATABASE IF EXISTS appointment_db;
DROP DATABASE IF EXISTS patient_db;
DROP DATABASE IF EXISTS chatbot_db;
DROP DATABASE IF EXISTS prescription_db;

-- Create databases with proper character set
CREATE DATABASE healthcare_sys CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE doctor_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE appointment_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE patient_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE chatbot_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE prescription_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user if not exists (MySQL 8.0+ syntax)
CREATE USER IF NOT EXISTS 'namdt25'@'%' IDENTIFIED BY 'namdt25';

-- Grant all privileges on all healthcare databases to the user
GRANT ALL PRIVILEGES ON healthcare_sys.* TO 'namdt25'@'%';
GRANT ALL PRIVILEGES ON doctor_db.* TO 'namdt25'@'%';
GRANT ALL PRIVILEGES ON appointment_db.* TO 'namdt25'@'%';
GRANT ALL PRIVILEGES ON patient_db.* TO 'namdt25'@'%';
GRANT ALL PRIVILEGES ON chatbot_db.* TO 'namdt25'@'%';
GRANT ALL PRIVILEGES ON prescription_db.* TO 'namdt25'@'%';

-- Grant additional privileges for database operations
GRANT CREATE, DROP, ALTER, INDEX, REFERENCES ON *.* TO 'namdt25'@'%';

-- Flush privileges to ensure changes take effect
FLUSH PRIVILEGES;

-- Display created databases for verification
SHOW DATABASES;

-- Display user privileges for verification
SHOW GRANTS FOR 'namdt25'@'%';

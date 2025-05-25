-- PostgreSQL initialization script for healthcare system
-- This script creates all required databases and sets up user permissions

-- Create databases for PostgreSQL services
CREATE DATABASE laboratory_db;
CREATE DATABASE pharmacy_db;

-- Grant all privileges on the databases to the user
GRANT ALL PRIVILEGES ON DATABASE laboratory_db TO namdt25;
GRANT ALL PRIVILEGES ON DATABASE pharmacy_db TO namdt25;

-- Connect to each database and grant schema privileges
\c laboratory_db;
GRANT ALL ON SCHEMA public TO namdt25;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO namdt25;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO namdt25;

\c pharmacy_db;
GRANT ALL ON SCHEMA public TO namdt25;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO namdt25;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO namdt25;

-- Display created databases for verification
\l

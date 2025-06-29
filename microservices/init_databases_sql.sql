-- PostgreSQL Database Initialization Script
-- This script creates separate databases for each microservice

-- Create databases for each microservice
CREATE DATABASE user_service_db;
CREATE DATABASE project_task_service_db;
CREATE DATABASE comment_service_db;
CREATE DATABASE attachment_service_db;
CREATE DATABASE notification_service_db;
CREATE DATABASE activity_log_service_db;
CREATE DATABASE reporting_service_db;

-- Grant privileges to the application user
GRANT ALL PRIVILEGES ON DATABASE user_service_db TO "user";
GRANT ALL PRIVILEGES ON DATABASE project_task_service_db TO "user";
GRANT ALL PRIVILEGES ON DATABASE comment_service_db TO "user";
GRANT ALL PRIVILEGES ON DATABASE attachment_service_db TO "user";
GRANT ALL PRIVILEGES ON DATABASE notification_service_db TO "user";
GRANT ALL PRIVILEGES ON DATABASE activity_log_service_db TO "user";
GRANT ALL PRIVILEGES ON DATABASE reporting_service_db TO "user";

-- Connect to each database and set up extensions if needed
\c user_service_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\c project_task_service_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\c comment_service_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\c attachment_service_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\c notification_service_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\c activity_log_service_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\c reporting_service_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Return to the default database
\c taskapp_db;

-- Log the completion
SELECT 'Database initialization completed' AS status;

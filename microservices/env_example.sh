# =============================================================================
# MICROSERVICES CONFIGURATION
# Copy this file to .env and customize the values for your environment
# =============================================================================

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
# User Service Database
USER_SERVICE_DATABASE_URL=postgresql://user:password@postgres:5432/user_service_db

# Project & Task Service Database
PROJECT_TASK_SERVICE_DATABASE_URL=postgresql://user:password@postgres:5432/project_task_service_db

# Comment Service Database
COMMENT_SERVICE_DATABASE_URL=postgresql://user:password@postgres:5432/comment_service_db

# Attachment Service Database
ATTACHMENT_SERVICE_DATABASE_URL=postgresql://user:password@postgres:5432/attachment_service_db

# Notification Service Database
NOTIFICATION_SERVICE_DATABASE_URL=postgresql://user:password@postgres:5432/notification_service_db

# Activity Log Service Database
ACTIVITY_LOG_SERVICE_DATABASE_URL=postgresql://user:password@postgres:5432/activity_log_service_db

# Reporting Service Database
REPORTING_SERVICE_DATABASE_URL=postgresql://user:password@postgres:5432/reporting_service_db

# =============================================================================
# REDIS CONFIGURATION
# =============================================================================
REDIS_HOST=redis
REDIS_PORT=6379

# Redis URLs for different services (using different databases)
USER_SERVICE_REDIS_URL=redis://redis:6379/0
PROJECT_TASK_SERVICE_REDIS_URL=redis://redis:6379/0
COMMENT_SERVICE_REDIS_URL=redis://redis:6379/0
ATTACHMENT_SERVICE_REDIS_URL=redis://redis:6379/0
NOTIFICATION_SERVICE_REDIS_URL=redis://redis:6379/1
ACTIVITY_LOG_SERVICE_REDIS_URL=redis://redis:6379/2
REPORTING_SERVICE_REDIS_URL=redis://redis:6379/3

# =============================================================================
# CELERY CONFIGURATION
# =============================================================================
# Notification Service Celery
NOTIFICATION_SERVICE_CELERY_BROKER_URL=redis://redis:6379/1
NOTIFICATION_SERVICE_CELERY_RESULT_BACKEND=redis://redis:6379/1

# Activity Log Service Celery
ACTIVITY_LOG_SERVICE_CELERY_BROKER_URL=redis://redis:6379/2
ACTIVITY_LOG_SERVICE_CELERY_RESULT_BACKEND=redis://redis:6379/2

# Reporting Service Celery
REPORTING_SERVICE_CELERY_BROKER_URL=redis://redis:6379/3
REPORTING_SERVICE_CELERY_RESULT_BACKEND=redis://redis:6379/3

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================
# Generate unique secret keys for each service
USER_SERVICE_SECRET_KEY=your_user_service_secret_key_here
PROJECT_TASK_SERVICE_SECRET_KEY=your_project_task_service_secret_key_here
COMMENT_SERVICE_SECRET_KEY=your_comment_service_secret_key_here
ATTACHMENT_SERVICE_SECRET_KEY=your_attachment_service_secret_key_here
NOTIFICATION_SERVICE_SECRET_KEY=your_notification_service_secret_key_here
ACTIVITY_LOG_SERVICE_SECRET_KEY=your_activity_log_service_secret_key_here
REPORTING_SERVICE_SECRET_KEY=your_reporting_service_secret_key_here

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key_here

# =============================================================================
# SERVICE URLS (Internal Communication)
# =============================================================================
USER_SERVICE_URL=http://user-service:5001
PROJECT_TASK_SERVICE_URL=http://project-task-service:5002
COMMENT_SERVICE_URL=http://comment-service:5003
ATTACHMENT_SERVICE_URL=http://attachment-service:5004
NOTIFICATION_SERVICE_URL=http://notification-service:5005
ACTIVITY_LOG_SERVICE_URL=http://activity-log-service:5006
REPORTING_SERVICE_URL=http://reporting-service:5007

# =============================================================================
# EMAIL CONFIGURATION (Notification Service)
# =============================================================================
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_FROM=noreply@taskapp.com

# =============================================================================
# FILE UPLOAD CONFIGURATION (Attachment Service)
# =============================================================================
UPLOAD_FOLDER=/app/uploads
MAX_CONTENT_LENGTH=16777216  # 16MB in bytes

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================
LOG_LEVEL=INFO
DEBUG=false

# =============================================================================
# DATA RETENTION CONFIGURATION
# =============================================================================
LOG_RETENTION_DAYS=90

# =============================================================================
# POSTGRESQL CONFIGURATION
# =============================================================================
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=taskapp_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# =============================================================================
# DEVELOPMENT/PRODUCTION SETTINGS
# =============================================================================
ENVIRONMENT=development
HOST=0.0.0.0

# Service Ports (for development)
USER_SERVICE_PORT=5001
PROJECT_TASK_SERVICE_PORT=5002
COMMENT_SERVICE_PORT=5003
ATTACHMENT_SERVICE_PORT=5004
NOTIFICATION_SERVICE_PORT=5005
ACTIVITY_LOG_SERVICE_PORT=5006
REPORTING_SERVICE_PORT=5007

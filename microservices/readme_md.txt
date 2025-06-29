# Task Management System - Microservices Architecture

A comprehensive task management system built with a microservices architecture, featuring user management, project tracking, task management, file attachments, notifications, activity logging, and reporting capabilities.

## 🏗️ Architecture Overview

The application has been decomposed into 7 specialized microservices:

```
┌─────────────────────────────────────────────────────────────────┐
│                          Nginx (Reverse Proxy)                  │
│                          Port 80/443                           │
└─────────────────────────┬───────────────────────────────────────┘
                          │
           ┌──────────────┼──────────────┐
           │              │              │
    ┌──────▼──────┐ ┌─────▼─────┐ ┌─────▼─────┐
    │User Service │ │Project &  │ │Comment    │
    │Port 5001    │ │Task       │ │Service    │
    │             │ │Service    │ │Port 5003  │
    └─────────────┘ │Port 5002  │ └───────────┘
                    └───────────┘
                          │
    ┌─────────────────────┼─────────────────────┐
    │                     │                     │
┌───▼────┐ ┌─────▼──────┐ ┌──────▼──────┐ ┌────▼─────┐
│Attach  │ │Notification│ │Activity Log │ │Reporting │
│Service │ │Service     │ │Service      │ │Service   │
│Port    │ │Port 5005   │ │Port 5006    │ │Port 5007 │
│5004    │ │            │ │             │ │          │
└────────┘ └────────────┘ └─────────────┘ └──────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                         │
│  ┌──────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ PostgreSQL   │  │   Redis     │  │   Celery Workers        │ │
│  │ (Multiple    │  │ (Cache &    │  │   (Background Tasks)    │ │
│  │  Databases)  │  │  Queue)     │  │                         │ │
│  └──────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Services Overview

### 1. **User Service** (`user_service.py`)
- **Responsibility**: User lifecycle management
- **Features**: Registration, authentication (JWT), authorization, profile management
- **Database**: `user_service_db`
- **Port**: 5001

### 2. **Project & Task Service** (`project_task_service.py`)
- **Responsibility**: Project and task management
- **Features**: CRUD operations for projects and tasks, workflows, status tracking
- **Database**: `project_task_service_db`
- **Port**: 5002

### 3. **Comment Service** (`comment_service.py`)
- **Responsibility**: Task-related discussions
- **Features**: Comment CRUD, collaborative discussions
- **Database**: `comment_service_db`
- **Port**: 5003

### 4. **Attachment Service** (`attachment_service.py`)
- **Responsibility**: File management
- **Features**: File upload/download, metadata management, security
- **Database**: `attachment_service_db`
- **Port**: 5004
- **Storage**: Volume-mounted file system

### 5. **Notification Service** (`notification_service.py`)
- **Responsibility**: Asynchronous communication
- **Features**: Email notifications, templating, webhooks
- **Database**: `notification_service_db`
- **Port**: 5005
- **Background**: Celery workers for email processing

### 6. **Activity Log Service** (`activity_log_service.py`)
- **Responsibility**: Audit trail and logging
- **Features**: Activity tracking, audit logs, data retention
- **Database**: `activity_log_service_db`
- **Port**: 5006
- **Background**: Celery for log cleanup and summaries

### 7. **Reporting Service** (`reporting_service.py`)
- **Responsibility**: Analytics and insights
- **Features**: Report generation, dashboards, metrics aggregation
- **Database**: `reporting_service_db`
- **Port**: 5007
- **Background**: Celery for async report generation

## 📋 Prerequisites

- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Git**
- **At least 4GB RAM** for comfortable development
- **10GB disk space** for containers and data

## 🛠️ Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd task-management-microservices

# Copy environment configuration
cp .env.example .env

# Edit .env file with your specific configuration
nano .env
```

### 2. Configure Environment Variables

Edit the `.env` file with your specific settings:

```bash
# Database credentials
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_secure_password

# JWT and service secrets (generate unique values)
JWT_SECRET_KEY=your_jwt_secret_here
USER_SERVICE_SECRET_KEY=your_user_service_secret
# ... (generate unique secrets for each service)

# Email configuration (for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_FROM=noreply@yourcompany.com

# Other configurations
DEBUG=false
LOG_RETENTION_DAYS=90
```

### 3. Deploy the Stack

```bash
# Build and start all services
docker-compose up -d

# Check service health
docker-compose ps

# View logs
docker-compose logs -f

# Check specific service logs
docker-compose logs -f user-service
```

### 4. Initialize the System

```bash
# The databases will be automatically initialized
# Wait for all services to be healthy (check with docker-compose ps)

# Test the system
curl http://localhost/health
```

### 5. Create Admin User

```bash
# Register an admin user through the API
curl -X POST http://localhost/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "securepassword123",
    "full_name": "System Administrator"
  }'
```

## 📚 API Documentation

### Authentication

All services use JWT tokens for authentication. Obtain a token by logging in:

```bash
# Login to get JWT token
curl -X POST http://localhost/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "securepassword123"
  }'

# Use the token in subsequent requests
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost/api/users/me
```

### Core API Endpoints

#### User Management
```bash
POST /api/register          # Register new user
POST /api/login             # User login
POST /api/logout            # User logout
GET  /api/users/me          # Get current user
PUT  /api/users/me          # Update profile
GET  /api/admin/users       # List all users (admin)
```

#### Project Management
```bash
GET    /api/projects        # List user's projects
POST   /api/projects        # Create new project
GET    /api/projects/{id}   # Get project details
PUT    /api/projects/{id}   # Update project
DELETE /api/projects/{id}   # Delete project
```

#### Task Management
```bash
GET    /api/projects/{id}/tasks    # List project tasks
POST   /api/projects/{id}/tasks    # Create new task
GET    /api/tasks/{id}             # Get task details
PUT    /api/tasks/{id}             # Update task
DELETE /api/tasks/{id}             # Delete task
```

#### Comments
```bash
GET    /api/tasks/{id}/comments    # List task comments
POST   /api/tasks/{id}/comments    # Add comment
PUT    /api/comments/{id}          # Update comment
DELETE /api/comments/{id}          # Delete comment
```

#### File Attachments
```bash
POST /api/tasks/{id}/attachments           # Upload file
GET  /api/tasks/{id}/attachments           # List attachments
GET  /api/attachments/{id}/download        # Download file
DELETE /api/attachments/{id}               # Delete attachment
```

#### Notifications
```bash
POST /api/notifications/send               # Send notification
GET  /api/notifications/user/{id}          # Get user notifications
POST /api/notification-templates           # Create template (admin)
```

#### Reports
```bash
POST /api/reports                          # Generate report
GET  /api/reports                          # List user reports
GET  /api/reports/{id}                     # Get report
GET  /api/reports/quick/dashboard          # Quick dashboard
GET  /api/reports/quick/project-summary/{id} # Project summary
```

## 🔧 Development

### Running Individual Services

For development, you can run services individually:

```bash
# Start infrastructure only
docker-compose up -d postgres redis

# Set environment variables
export DATABASE_URL="postgresql://user:password@localhost:5432/user_service_db"
export JWT_SECRET_KEY="your_jwt_secret"

# Run a service
cd services/
python user_service.py

# Or with auto-reload
flask --app user_service run --debug --port 5001
```

### Adding New Features

1. **Identify the appropriate service** for your feature
2. **Add database models** if needed
3. **Implement API endpoints**
4. **Add service communication** if cross-service data is needed
5. **Update tests** and documentation
6. **Update Docker configuration** if needed

### Service Communication

Services communicate via HTTP APIs. Key patterns:

- **Authentication**: Services verify JWT tokens with User Service
- **Authorization**: Services check permissions via User Service
- **Data Consistency**: Use eventual consistency where appropriate
- **Activity Logging**: All services log activities to Activity Log Service

## 🐳 Production Deployment

### Using Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml taskapp

# Scale services
docker service scale taskapp_user-service=3
docker service scale taskapp_project-task-service=2
```

### Using Kubernetes

Convert the Docker Compose file to Kubernetes manifests:

```bash
# Install kompose
curl -L https://github.com/kubernetes/kompose/releases/download/v1.26.0/kompose-linux-amd64 -o kompose
chmod +x kompose

# Convert to Kubernetes
./kompose convert -f docker-compose.yml

# Deploy to Kubernetes
kubectl apply -f .
```

### Environment-Specific Configurations

Create environment-specific `.env` files:

- `.env.development`
- `.env.staging` 
- `.env.production`

```bash
# Load specific environment
docker-compose --env-file .env.production up -d
```

## 📊 Monitoring and Observability

### Health Checks

Each service provides health endpoints:

```bash
# Overall system health
curl http://localhost/health

# Individual service health
curl http://localhost/health/user
curl http://localhost/health/projects
curl http://localhost/health/comments
# ... etc
```

### Logs

```bash
# View all logs
docker-compose logs -f

# Service-specific logs
docker-compose logs -f user-service
docker-compose logs -f notification-worker

# Follow logs with timestamps
docker-compose logs -f -t

# Limit log output
docker-compose logs --tail=50 user-service
```

### Metrics Collection

For production monitoring, integrate with:

- **Prometheus** for metrics collection
- **Grafana** for visualization  
- **ELK Stack** for centralized logging
- **Jaeger** for distributed tracing

## 🔒 Security Considerations

### JWT Token Security
- Tokens expire after 24 hours
- Use secure secret keys
- Implement token refresh mechanism for production

### Database Security
- Use strong passwords
- Limit database access
- Enable SSL connections in production

### File Upload Security
- File type validation
- Size limits enforced
- Virus scanning recommended for production

### Network Security
- Services communicate over internal Docker network
- Only Nginx exposes ports externally
- Use HTTPS in production

## 🚨 Troubleshooting

### Common Issues

**Services won't start:**
```bash
# Check Docker status
docker-compose ps

# Check logs for errors
docker-compose logs <service-name>

# Restart specific service
docker-compose restart <service-name>
```

**Database connection issues:**
```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Test database connectivity
docker-compose exec postgres psql -U user -d user_service_db -c "SELECT 1;"
```

**Redis connection issues:**
```bash
# Check Redis logs
docker-compose logs redis

# Test Redis connectivity
docker-compose exec redis redis-cli ping
```

**Performance Issues:**
```bash
# Monitor resource usage
docker stats

# Check service response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost/api/users/me
```

### Performance Tuning

- **Database**: Add indexes, optimize queries, use connection pooling
- **Redis**: Configure appropriate memory limits and eviction policies
- **Nginx**: Tune worker processes and connections
- **Services**: Implement caching, optimize database queries

## 📝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Add tests for new features
- Update documentation
- Ensure all services pass health checks
- Test service interactions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

For support and questions:

- Create an issue in the repository
- Check the troubleshooting section
- Review service logs for error details

---

## 📈 Roadmap

Future enhancements planned:

- [ ] GraphQL API gateway
- [ ] Real-time notifications with WebSockets
- [ ] Advanced reporting with charts
- [ ] File preview capabilities
- [ ] Mobile app support
- [ ] Single Sign-On (SSO) integration
- [ ] Advanced workflow management
- [ ] Integration with external tools (Slack, Jira, etc.)

---

**Built with ❤️ using Python, Flask, PostgreSQL, Redis, and Docker**

---
id: service-decomposition-strategies
title: A Closer Look at Each Service
sidebar_label: Service Breakdown
sidebar_position: 3
---

# A Closer Look at Each Service

This section offers a detailed breakdown for each microservice we've identified. You'll find its main purpose, which parts were extracted from the monolith, its API endpoints, how its data is modeled, its dependencies, and the technology stack it uses.

## Service Overview Table

| Service | Data Model | Dependencies | Technology Stack |
| :---- | :---- | :---- | :---- |
| **User Service** | User table (e.g., PostgreSQL) | None (Initial source of truth) | Flask + SQLAlchemy (for its User model and authentication logic), JWT for token management. |
| **Project & Task Service** | Project, Task tables (e.g., PostgreSQL) | User Service (for assignee_id validation), Message Broker (for publishing events like "Task Completed"). | Flask + SQLAlchemy, potentially a task queue like Celery if background processing is introduced. |
| **Comment Service** | Comment table (e.g., PostgreSQL) | Project & Task Service (to ensure task_id exists), User Service (for author_id) | Flask + SQLAlchemy |
| **Attachment Service** | Attachment table (metadata), files stored on a dedicated persistent volume (e.g., S3-compatible storage, NFS, or Kubernetes Persistent Volume). | Project & Task Service (to ensure task_id exists), User Service (for uploaded_by) | Flask + SQLAlchemy, direct file system access for uploads folder (or cloud storage SDK like boto3 for S3). |
| **Notification Service** | Minimal or none (perhaps just email templates or queue data). | Message Broker (Redis/RabbitMQ/Kafka), External SMTP Service (e.g., SendGrid, Mailgun). | Python (e.g., Flask-Restful for internal API, Celery for task consumption), smtplib. |
| **Activity Log Service** | ActivityLog table (e.g., PostgreSQL, NoSQL DB like Cassandra for high write throughput) | Message Broker (Redis/RabbitMQ/Kafka). | Flask + SQLAlchemy (or a more scalable database for logs), potentially a streaming platform like Kafka. |
| **Reporting Service** | Might have its own derived data store (e.g., a data warehouse or materialized views) or fetch data on demand from other services (Project, Task, User, Comment, Attachment Services). | Project & Task Service, User Service, Redis (for caching reports), Message Broker (for async triggers/data ingestion). | Flask (or a micro-framework like FastAPI), potentially a different database for analytical workloads (e.g., PostgreSQL for complex queries, ClickHouse for OLAP), Redis. |

## Detailed Service Descriptions

### User Service
- **Purpose:** Central authentication and user management
- **Responsibilities:** User registration, login, profile management, JWT token generation
- **Database:** Dedicated PostgreSQL instance with User table
- **API Endpoints:** `/register`, `/login`, `/profile`, `/users/{id}`

### Project & Task Service
- **Purpose:** Core business logic for project and task management
- **Responsibilities:** CRUD operations for projects and tasks, status management, assignment logic
- **Database:** PostgreSQL with Project and Task tables
- **Events Published:** Task Created, Task Completed, Project Updated

### Comment Service
- **Purpose:** Manage task-related discussions and comments
- **Responsibilities:** Comment CRUD operations, threaded discussions
- **Database:** PostgreSQL with Comment table
- **Dependencies:** Validates task existence with Project & Task Service

### Attachment Service
- **Purpose:** File upload and management for tasks
- **Responsibilities:** File upload/download, metadata management, storage optimization
- **Storage:** Persistent volumes or cloud storage (S3-compatible)
- **Security:** File type validation, virus scanning, access control

### Notification Service
- **Purpose:** Asynchronous notification delivery
- **Responsibilities:** Email notifications, push notifications, notification templates
- **Architecture:** Event-driven, consumes messages from broker
- **External Dependencies:** SMTP services (SendGrid, Mailgun)

### Activity Log Service
- **Purpose:** Comprehensive audit trail and activity tracking
- **Responsibilities:** Log all user actions, system events, compliance reporting
- **Database:** High-throughput database (PostgreSQL or Cassandra)
- **Characteristics:** Write-heavy, immutable records, analytics-friendly

### Reporting Service
- **Purpose:** Business intelligence and analytics
- **Responsibilities:** Generate reports, dashboards, data aggregation
- **Architecture:** Can use read replicas or materialized views
- **Caching:** Redis for frequently accessed reports

---

**Previous:** [← Understanding the Example](./case-study-example) | **Next:** [Kubernetes Deployment →](./kubernetes-deployment-strategies)

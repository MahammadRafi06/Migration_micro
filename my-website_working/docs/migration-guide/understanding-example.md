---
id: understanding-example
title: Understanding Our Example - The Task Management System
sidebar_label: Understanding the Example
sidebar_position: 2
---

# Understanding Our Example: The Task Management System

To truly grasp the process of moving a monolithic application to a Kubernetes-native environment, we'll use a simplified **Task Management System** as our practical illustration.

## The Monolith Today

Our Task Management System currently lives as a monolithic Python Flask application. In its present form, all its core functionalities— user authentication, comprehensive project and task orchestration, secure file handling, sending notifications, and detailed activity logging—are bundled together within a single codebase and deployment unit.

**What Makes It a Monolith:**

- **One Big Codebase:** Everything lives in a single repository.
- **Shared Database:** All functionalities rely on just one database instance.
- **Tight Coupling:** Components are deeply intertwined, making it tough to develop and scale parts independently.
- **Single Deployment:** The entire application is deployed as one large package.

## Where We're Heading: A Conceptual Microservices View

The driving force behind breaking down this monolith into smaller, independent services is the desire for autonomous development cycles, the ability to scale precisely where needed, streamlined deployments, and ultimately, to fully embrace the advantages of a cloud-native microservices architecture. Our goal is to evolve from a tightly coupled, single-process application into a dynamic, distributed system made up of loosely coupled, independently deployable services.

## Our Approach: The Strangler Fig Pattern

For this architectural transformation, we're going to embrace the "Strangler Fig" pattern. This is a smart, iterative way to gradually pull specific functionalities out into new, independent services, rather than attempting a risky, complete rewrite of the entire application all at once. This phased strategy significantly helps to minimize transitional risks and promotes a smooth, incremental migration, ensuring your operations keep running without interruption throughout the process. New features or refactored parts will be built as shiny new microservices, and we'll progressively direct traffic to them, effectively "strangling" the old monolithic components over time.

## High-Level Steps for Your Transformation

Here's a high-level overview of the journey we'll take to evolve this application towards a robust cloud-native paradigm:

- **Codebase Restructuring:** First, you'll need to decide on your repository strategy: a monorepo (all services in one Git repo) or a poly-repo (each service in its own repo). A monorepo can be simpler to start, but poly-repos often align better with independent teams and continuous delivery. Then, we'll refactor your task-management-app.py into distinct directories and files for each microservice.

- **Containerize Each Service:** This means creating a Dockerfile for every service, ensuring each one can run completely on its own. Once built, these Docker images will be pushed to a container registry.

- **Database Migration & Setup:** For each new service, you'll choose its database strategy. This could involve setting up separate PostgreSQL instances right within Kubernetes or utilizing a managed database service. A crucial step here is migrating existing data from your monolithic database to these new, service-specific databases—a task that can be complex and often requires special data transformation scripts.

- **Kubernetes Manifests (YAML):** You'll write YAML files for each part of your deployment: Deployment.yaml (defining your container images, how many replicas you need, and resource limits), Service.yaml (describing how services are exposed internally or externally), Ingress.yaml (to expose client-facing services like your Flask Web UI or User Service API externally), and PersistentVolumeClaim.yaml for any services needing persistent storage. Don't forget ConfigMap.yaml and Secret.yaml for managing configuration and sensitive data.

- **Deployment to Kubernetes:** Once your manifests are ready, you'll connect to your Kubernetes cluster and apply them using `kubectl apply -f <your-manifests-directory>/`.

- **Monitor Rollout:** After deployment, you'll keep a close eye on the status using commands like `kubectl get pods`, `kubectl get deployments`, `kubectl get services`, and `kubectl get ingress` to ensure everything is running smoothly.

- **Redis & Celery Deployment:** If your application uses background tasks, you'll deploy Redis (perhaps using a Helm chart or a dedicated Redis operator for production, or a simple deployment for development) and then Celery workers as a separate Kubernetes Deployment, configured to connect to your Redis service.

- **External Services Integration:** Finally, you'll configure details for any external services, like your SMTP service for notifications, storing sensitive credentials securely in a Kubernetes Secret.

## Identifying Core Capabilities as Services

After a thorough look at the current structure of our application and its distinct business functions, we've pinpointed the following potential microservices. These are the candidates we believe are ready to be extracted:

1. **User Service:** This service will handle everything related to managing user lifecycles, including registration, authentication, authorization, and profile updates. It's designed to be the definitive source for all user data.

2. **Project & Task Service:** This one will be responsible for creating, retrieving, updating, and deleting projects and their associated tasks. It centralizes all the business logic for project and task workflows, statuses, and priorities.

3. **Comment Service:** Dedicated solely to task-related comments, this service will manage their creation, retrieval, updates, and deletion, making collaborative discussions around specific tasks much smoother.

4. **Attachment Service:** This service will be all about secure storage, retrieval, and management of any files attached to tasks. It'll handle uploads, downloads, and keep track of metadata for each attachment.

5. **Notification Service:** Think of this as your app's communication hub. It will asynchronously manage sending various notifications, like emails for task updates or project changes, by listening to events from other services.

6. **Activity Log Service:** This service provides an unchangeable audit trail of important user and system actions throughout the entire application. It's built to handle a high volume of activity data, giving you comprehensive auditing and analytics capabilities.

7. **Reporting Service:** This service focuses on generating valuable analytical insights. It will be responsible for compiling and delivering comprehensive reports (e.g., project progress, task completion statistics) by pulling data from other services, often in an asynchronous fashion.

## Giving Each Service Its Own Data

A core principle of microservices is "database per service." This means each service should ideally manage its own data store. Why? Because it helps keep things loosely coupled and allows each service to evolve independently. While you might start with some services still sharing a database (a logical separation), the goal is to gradually move towards physical separation, perhaps by using different schemas, separate databases on the same server, or even entirely separate database instances.

| Aspect | Description |
| :---- | :---- |
| **Current State** | All models (User, Project, Task, Comment, Attachment, ActivityLog) share a single database. |
| **Target State** | **User Service:** Owns User data<br/>**Project & Task Service:** Owns Project, Task data<br/>**Comment Service:** Owns Comment data<br/>**Attachment Service:** Owns Attachment data<br/>**Activity Log Service:** Owns ActivityLog data<br/>**Notification Service:** Might not have a persistent data store or a small one for templates/queues<br/>**Reporting Service:** Might cache derived data or generate reports on demand from other services |

## How Our Services Will Talk to Each Other

In a microservices world, how your services communicate is incredibly important for building a coherent distributed system. For our architecture, we'll primarily use two main communication styles:

### RESTful APIs (Synchronous)

For situations where services need immediate responses and direct interaction, we'll use synchronous RESTful APIs. A good example would be the Project & Task Service asking the User Service for details about a task assignee. This method is perfect when one service absolutely depends on an instant result from another.

**Considerations:** While straightforward to set up, remember that synchronous calls can create tighter coupling. You'll want to manage these carefully using things like timeouts and circuit breakers to keep performance and resilience in check.

### Asynchronous Messaging (Event-Driven)

To promote loose coupling and make our system more resilient, we'll also use asynchronous, event-driven communication. This approach allows services to react to events published by others without needing to know who's listening. For instance, when the Project & Task Service marks a "Task Completed," it will publish an event to a message broker. The Notification Service can then pick up this event to send an email, while the Activity Log Service simultaneously records the action. Everyone works independently, with no direct ties. We'll use messaging platforms like Redis (for simpler needs) or more robust queues like RabbitMQ or Apache Kafka to facilitate this decoupled interaction.

**Considerations:** This model does add a bit more complexity around eventual consistency, ensuring messages are processed in order, and handling errors when messages fail. You'll also need a robust message broker infrastructure.

### API Gateway (Centralized Access)

We'll also introduce an API Gateway. Think of this as the single front door for all external client requests. It's smart enough to handle things like routing requests to the right service, load balancing, managing authentication and authorization, setting rate limits, and even caching common responses. This clever setup keeps the underlying microservice architecture neatly hidden from your clients.

---

**Previous:** [← Introduction](./introduction) | **Next:** [Service Breakdown →](./service-breakdown)

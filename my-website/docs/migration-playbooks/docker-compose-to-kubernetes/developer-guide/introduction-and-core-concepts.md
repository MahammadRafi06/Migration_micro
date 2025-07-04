---
id: introduction-and-core-concepts
title: Introduction and Core Concepts
sidebar_label: "Introduction & Concepts"
---

# Converting Docker Compose to Kubernetes YAML

## Introduction

Docker Compose is excellent for local development and orchestrating multi-container applications on a single host. However, when you need to scale, ensure high availability, and manage complex deployments in a production environment, Kubernetes becomes the de-facto standard. This guide will walk you through the process of translating your Docker Compose concepts into their Kubernetes equivalents, providing multiple pathways to achieve your goal.

## Prerequisites

Before you begin, ensure you have:

* **Basic understanding of Docker Compose:** Familiarity with services, volumes, networks, and environment variables.  
* **Basic understanding of Kubernetes concepts:** Familiarity with Pods, Deployments, Services, Volumes, ConfigMaps, and Secrets.  
* **A Docker Compose file:** The application you intend to convert.  
* **kubectl installed and configured:** To interact with a Kubernetes cluster (local like Minikube/Kind, or cloud-based).  
* **Text editor:** For creating and editing YAML files.  
* **Docker Desktop (if using kompose) or Podman (if using podman generate kube)** installed.

## Understanding Docker Compose Structure

A typical docker-compose.yml file defines:

* **services**: Individual application components (e.g., web server, database, API). Each service defines an image, ports, volumes, environment variables, and dependencies.  
* **volumes**: Data persistence mechanisms.  
* **networks**: Custom networks for inter-service communication.

**Example Docker Compose:**

```yaml
# docker-compose.yml
version: '3.8'
services:
  webapp:
    image: my-node-app:1.0
    ports:
      - "80:3000"
    environment:
      - NODE_ENV=production
      - DB_HOST=database
      - API_KEY=mysecretkey
    volumes:
      - ./app-data:/usr/src/app/data
    depends_on:
      - database
    networks:
      - app-net
  database:
    image: postgres:13
    environment:
      - POSTGRES_DB=mydb
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - db-data:/var/lib/postgresql/data
    networks:
      - app-net
volumes:
  db-data:
  app-data: # For host path volume, Kubernetes equivalent is tricky, often requires hostPath or local PV
networks:
  app-net:
```

## Understanding Kubernetes YAML Fundamentals

Kubernetes resources are defined using YAML files. Key resources for conversion include:

* **Pod**: The smallest deployable unit, containing one or more containers.  
* **Deployment**: Manages a set of identical Pods, ensuring a desired number of replicas are running and handling updates.  
* **Service**: An abstract way to expose an application running on a set of Pods as a network service (internal or external).  
* **PersistentVolumeClaim (PVC)**: A request for storage by a user, which then binds to a PersistentVolume (PV) provided by the cluster administrator.  
* **ConfigMap**: Stores non-confidential configuration data in key-value pairs.  
* **Secret**: Stores sensitive data (e.g., passwords, API keys) securely.  
* **Ingress**: Manages external access to services within the cluster, typically HTTP/HTTPS.

:::tip
For a smoother migration, map out how each component in your Docker Compose file translates to Kubernetes resources before you begin the actual conversion.
:::

In the next sections, we'll explore different conversion strategies, from manual conversion (recommended for production) to automated tools and advanced packaging options.
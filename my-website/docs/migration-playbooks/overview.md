---
id: overview
title: Migration Playbooks Overview
sidebar_label: Overview
sidebar_position: 1
---

# Migration Playbooks Overview

This section provides comprehensive, step-by-step guidance for migrating applications to the Edge Platform. Each playbook is designed to address specific migration scenarios with practical examples and best practices.

## Available Migration Paths

### 1. Monolith to Microservices Migration

Transform monolithic applications into microservices architecture for improved scalability, maintainability, and team velocity.

**When to Use:**
- Large, complex applications with multiple business domains
- Teams looking to improve development velocity
- Applications requiring independent scaling of components

**Key Benefits:**
- Independent service deployment
- Technology diversity
- Improved fault isolation
- Enhanced scalability

### 2. Docker Compose to Kubernetes Migration

Migrate multi-container applications from Docker Compose to Kubernetes for production-ready orchestration.

#### Developer Guide
Step-by-step technical instructions for developers converting Docker Compose files to Kubernetes manifests.

#### Operational Runbook
Practical operational procedures for deployment teams managing the migration process.

### 3. Docker Compose to Helm Charts

Package Docker Compose applications as Helm charts for better versioning, templating, and deployment management.

**Benefits:**
- Template-based configuration
- Version management
- Easy rollbacks
- Simplified deployments

### 4. Docker Compose to Virtual Machines

Deploy Docker Compose applications in KubeVirt virtual machines for legacy compatibility while leveraging Kubernetes orchestration.

**Use Cases:**
- Applications with complex system dependencies
- Gradual migration strategies
- Hybrid container-VM architectures

## Choosing the Right Migration Path

Consider these factors when selecting your migration approach:

### Application Complexity
- **Simple applications**: Direct containerization
- **Complex monoliths**: Consider microservices decomposition
- **Legacy dependencies**: VM-based deployment

### Team Readiness
- **Kubernetes experience**: Direct migration to Kubernetes
- **Limited cloud-native experience**: Start with lift-and-shift

### Business Requirements
- **Rapid migration**: Lift-and-shift approach
- **Long-term modernization**: Microservices transformation
- **Incremental changes**: Hybrid approaches

### Risk Tolerance
- **Low risk**: VM-based migration
- **Medium risk**: Containerization
- **Higher risk**: Full microservices transformation

## Migration Process Overview

Each migration playbook follows a structured approach:

1. **Assessment**: Analyze current application architecture
2. **Planning**: Define migration strategy and timeline
3. **Preparation**: Set up tools and environments
4. **Execution**: Implement the migration
5. **Validation**: Test and verify the migrated application
6. **Optimization**: Fine-tune performance and operations

## Getting Started

Choose the migration path that best fits your application and organizational needs:

- **[Monolith to Microservices](./monolith-to-microservices/overview)**: For large application transformations
- **[Docker Compose to Kubernetes](./docker-compose-to-kubernetes/developer-guide/introduction-and-core-concepts)**: For containerized applications
- **[Docker Compose to Helm Charts](./docker-compose-to-helm-charts/introduction-and-prerequisites)**: For better package management
- **[Docker Compose to Virtual Machines](./docker-compose-to-virtual-machines/introduction-and-migration-strategy)**: For legacy compatibility

Each playbook provides detailed guidance, practical examples, and troubleshooting tips to ensure successful migration to the Edge Platform. 
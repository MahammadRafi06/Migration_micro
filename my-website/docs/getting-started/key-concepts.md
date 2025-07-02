---
id: key-concepts
title: Key Concepts
sidebar_label: Key Concepts
sidebar_position: 2
---

# Key Platform Concepts

Understanding these fundamental concepts will help you navigate the Edge Platform effectively.

## Kubernetes Foundation

### Pods and Containers
- **Pods**: The smallest deployable units containing one or more containers
- **Containers**: Lightweight, portable application packaging
- **Container Images**: Immutable snapshots of application code and dependencies

### Workload Management
- **Deployments**: Manage application replicas and rolling updates
- **Services**: Network abstraction for accessing applications
- **ConfigMaps & Secrets**: Configuration and credential management

## Application Patterns

### Microservices Architecture
- **Service Decomposition**: Breaking monoliths into smaller, focused services
- **API-First Design**: Well-defined interfaces between services
- **Independent Deployment**: Services can be updated independently

### Cloud-Native Principles
- **Containerization**: Applications packaged in containers
- **Orchestration**: Automated deployment and scaling
- **Observability**: Comprehensive monitoring and logging

## Migration Strategies

### Lift-and-Shift
- Move existing applications to the platform with minimal changes
- Use virtual machines for legacy applications
- Quick migration with gradual modernization

### Containerization
- Package applications in containers
- Leverage Docker Compose for multi-container applications
- Migrate to Kubernetes for orchestration

### Microservices Transformation
- Decompose monolithic applications
- Implement domain-driven design
- Adopt cloud-native patterns

## Platform Services

### Container Orchestration
- Kubernetes for container management
- Helm for package management
- Service mesh for advanced networking

### Virtual Machine Support
- KubeVirt for VM management
- Hybrid container-VM deployments
- Legacy application support

### Development Tools
- CI/CD pipelines
- Container registries
- Development environments

## Next Steps

Now that you understand the key concepts, explore the [Application Modernization](../application-modernization/microservice-fundamentals) section to learn about microservices patterns and best practices. 
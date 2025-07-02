---
id: platform-overview
title: Platform Overview
sidebar_label: Platform Overview
sidebar_position: 1
---

# Edge Platform Overview

Welcome to the documentation for the Armada Edge Platform (AEP)! This section provides a high-level overview of AEP, its purpose, and how it empowers Independent Software Vendors (ISVs) like you to deploy and manage your applications at the remote edge.

## What is the Armada Edge Platform?

The Armada Edge Platform is a powerful, modular infrastructure designed to solve the most challenging problems of deploying and operating applications in remote, disconnected, or resource-constrained environments. It brings the capabilities of cloud computing directly to where your data is generated, ensuring seamless, scalable performance where it matters most.

AEP is built on a foundation of robust, secure, and highly resilient components, enabling you to extend your application's reach beyond traditional data centers and central clouds.

## Why the Edge? Why Armada?

Traditional cloud infrastructure, while powerful, often faces limitations when dealing with data generated at the extreme edge.

### Challenges of Traditional Cloud Infrastructure

#### High Latency
Sending data back to a central cloud for processing introduces delays that are unacceptable for real-time applications (e.g., industrial automation, autonomous vehicles, real-time analytics).

#### Limited Bandwidth
Remote locations often have intermittent or low-bandwidth connectivity, making it impractical to constantly stream large volumes of data to the cloud.

#### Security Concerns
Data in transit or stored in centralized locations can be vulnerable. Edge processing keeps sensitive data local.

#### Operational Resilience
Many edge environments require applications to function autonomously even when disconnected from the central network.

### Armada's Solutions

The Armada Edge Platform addresses these challenges by providing:

#### Real-time Processing
Process data directly at the source, enabling immediate insights and actions.

#### Bandwidth Optimization
Reduce data egress costs and improve efficiency by only sending mission-critical insights back to the cloud.

#### Enhanced Security
Keep sensitive data localized and leverage robust security features designed for distributed environments.

#### Unmatched Resilience
Ensure application continuity even in challenging or disconnected scenarios.

#### Simplified Deployment
Deploy complex applications with ease using a turnkey solution.

## Core Components of the Armada Edge Platform

The Armada Edge Platform comprises three primary components that work together to deliver comprehensive edge capabilities:

### Galleon

Our ruggedized modular data centers. These are the physical compute units that bring powerful processing and storage capabilities directly to your edge locations. Galleons are designed in multiple form factors to tackle diverse environmental challenges.

### Atlas

Our operational insights product for all your connected assets. Atlas provides a single pane of glass for seamlessly monitoring and managing your IoT devices and edge infrastructure.

### Marketplace

Your hub for all the hardware and software you need to operate at the remote edge. This is where you can discover, deploy, and manage a wide array of applications and services optimized for the AEP.

## Platform Capabilities

By leveraging these components, ISVs can unlock new possibilities for their applications, extending their reach and impact to the farthest corners of the globe.

### Cloud-Native Foundation
Built on Kubernetes with support for containers and virtual machines

### Edge Computing Optimization
Optimized for edge deployments with reduced latency and improved performance

### Application Modernization
Tools and frameworks for migrating legacy applications to cloud-native architectures

### Scalable Infrastructure
Auto-scaling, load balancing, and resource optimization

### Operational Excellence
Comprehensive monitoring, logging, and observability

## Platform Architecture

The platform supports multiple deployment patterns:

### Container-Based Workloads
- Native Kubernetes deployments
- Helm chart packaging
- Microservices architectures

### Virtual Machine Workloads
- KubeVirt integration for VM management
- Support for legacy applications
- Hybrid container-VM deployments

### Application Migration Paths
- Lift-and-shift VM deployments
- Containerization strategies
- Microservices decomposition

## Getting Started

This documentation will guide you through:

### 1. Platform Fundamentals
Understanding core concepts and capabilities

### 2. Application Modernization
Strategies for moving to microservices

### 3. Migration Playbooks
Step-by-step guides for different migration scenarios

Begin with the [Key Concepts](./key-concepts) to understand the foundational elements of the platform. 
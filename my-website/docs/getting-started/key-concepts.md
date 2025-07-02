---
id: key-concepts
title: Key Concepts
sidebar_label: Key Concepts
sidebar_position: 2
---

# Key Concepts: Understanding the Armada Edge Platform

To effectively utilize the Armada Edge Platform (AEP), it's important to grasp some fundamental concepts that underpin its architecture and operation. This section clarifies key terminology and principles.

## Edge Computing

Edge computing is a distributed computing paradigm that brings computation and data storage closer to the sources of data. Instead of sending all data to a centralized cloud or data center for processing, edge computing processes data locally at or near the "edge" of the network.

### Why it matters for ISVs

#### Reduced Latency
Critical for applications requiring immediate responses (e.g., real-time analytics, industrial control).

#### Bandwidth Efficiency
Minimizes the need to transmit large volumes of raw data over potentially limited or expensive network connections.

#### Improved Reliability
Operations can continue even with intermittent or no connectivity to a central cloud.

#### Enhanced Security
Data can be processed and stored locally, reducing exposure during transit.

## Galleon: The Modular Edge Data Center

Galleon is the physical manifestation of our edge computing infrastructure. It is a ruggedized, modular data center designed for deployment in challenging environments. Think of it as a mini-cloud environment that can be deployed wherever your operations are.

### Key Characteristics

#### Containerized
Often housed in standard or custom container-like structures for easy transport and deployment.

#### Self-contained
Includes compute (CPUs, GPUs), storage, networking, and environmental controls (cooling, heating).

#### Scalable
Multiple Galleons can be deployed and managed as a distributed fleet.

#### Resilient
Engineered to withstand harsh physical and environmental conditions.

### Value for ISVs

For ISVs, Galleons provide the localized compute power necessary to run your applications, including demanding AI/ML workloads, directly at the point of data generation.

## Atlas: Operational Insights & Management

Atlas is Armada's operational insights platform, providing a single pane of glass for comprehensive visibility and control over your distributed edge assets. It's designed to simplify the management of a fleet of Galleons and connected IoT devices.

### Key Capabilities

#### Centralized Monitoring
Track the health, performance, and status of your Galleons and deployed applications.

#### IoT Device Management
Seamlessly integrate and manage various IoT devices.

#### Connectivity Optimization
Tools for managing network connections, including Starlink integration.

#### Predictive Analytics
Leverage AI to provide insights for proactive maintenance and operational efficiency.

### ISV Benefits

Atlas empowers ISVs to remotely manage, monitor, and update their applications across a vast, geographically dispersed edge infrastructure.

## Marketplace: Your Edge Ecosystem

The Marketplace is an integral part of the Armada Edge Platform, serving as a curated hub for hardware and software solutions optimized for the edge.

### Benefits for ISVs

#### Discoverability
Showcase and distribute your edge-native applications to other AEP users.

#### Accelerated Deployment
Access pre-validated hardware and software components that are guaranteed to work seamlessly with Galleons.

#### Ecosystem Leverage
Benefit from a growing ecosystem of solutions tailored for remote and edge environments.

## Kubernetes at the Edge

While Galleon provides the physical infrastructure, Kubernetes serves as the orchestration layer for containerized applications running on the Armada Edge Platform. It allows ISVs to deploy, scale, and manage their microservices-based applications consistently across edge locations, leveraging familiar cloud-native tools and practices.

### Key Benefits of Kubernetes on AEP

#### Portability
Run your containerized applications consistently from the cloud to the edge.

#### Scalability
Automatically scale your applications up or down based on demand and available resources.

#### Resilience
Kubernetes' self-healing capabilities ensure your applications remain available even if individual components fail.

#### Declarative Management
Define your desired application state, and Kubernetes works to maintain it.

## Foundation for Success

Understanding these core concepts will provide a strong foundation as you explore the more detailed migration guides and advanced features of the Armada Edge Platform.

## Next Steps

Now that you understand the key concepts, explore the [Application Modernization](../application-modernization/microservice-fundamentals) section to learn about microservices patterns and best practices. 
---
id: glossary
title: Glossary
sidebar_label: Glossary
sidebar_position: 999
---

# Glossary

This glossary provides definitions for technical terms and concepts used throughout the Armada Edge Platform documentation.

## A

**API (Application Programming Interface)**
A set of protocols, routines, and tools for building software applications. APIs specify how software components should interact.

**Atlas**
Armada's operational insights product for connected assets. Provides monitoring and management capabilities for IoT devices and edge infrastructure through a unified interface.

**Auto-scaling**
The ability to automatically adjust computing resources (up or down) based on demand to maintain performance and optimize costs.

## B

**Blue-Green Deployment**
A deployment strategy that reduces downtime by running two identical production environments (blue and green). Traffic is switched from one to the other during deployments.

## C

**Canary Deployment**
A deployment strategy where a new version is gradually rolled out to a small subset of users before full deployment, allowing for testing in production with minimal risk.

**CI/CD (Continuous Integration/Continuous Deployment)**
A practice of automating the integration of code changes and deployment to production environments, enabling faster and more reliable software delivery.

**Container**
A lightweight, standalone package that includes everything needed to run an application: code, runtime, system tools, libraries, and settings.

**Container Registry**
A repository for storing and distributing container images, such as Docker Hub or private registries.

## D

**Docker**
A platform for developing, shipping, and running applications using containerization technology.

**Docker Compose**
A tool for defining and running multi-container Docker applications using YAML files.

## E

**Edge Computing**
A distributed computing paradigm that brings computation and data storage closer to the sources of data to improve response times and save bandwidth.

**Egress**
Network traffic that leaves a network or system, often referring to data flowing from internal systems to external networks.

## F

**Failover**
The ability to automatically switch to a backup system or component when the primary system fails.

## G

**Galleon**
Armada's ruggedized modular data centers designed for edge deployments. Available in multiple form factors to address diverse environmental challenges.

**GitOps**
An operational framework that takes DevOps best practices used for application development and applies them to infrastructure automation.

## H

**Helm**
A package manager for Kubernetes that helps define, install, and upgrade complex Kubernetes applications using charts.

**Helm Chart**
A collection of files that describe a related set of Kubernetes resources, packaged together for easy deployment and management.

**Horizontal Pod Autoscaler (HPA)**
A Kubernetes feature that automatically scales the number of pods in a deployment based on observed CPU utilization or other metrics.

## I

**Ingress**
Network traffic that enters a network or system, often referring to external traffic flowing into internal systems.

**IoT (Internet of Things)**
A network of physical devices embedded with sensors, software, and connectivity to collect and exchange data.

## J

**JSON (JavaScript Object Notation)**
A lightweight data interchange format that is easy for humans to read and write, commonly used for APIs and configuration files.

## K

**Kubernetes (K8s)**
An open-source container orchestration platform for automating deployment, scaling, and management of containerized applications.

**KubeVirt**
A Kubernetes add-on that enables running virtual machines alongside containers in a Kubernetes cluster.

**kubectl**
The command-line tool for interacting with Kubernetes clusters.

## L

**Load Balancer**
A device or software that distributes network traffic across multiple servers to ensure no single server becomes overwhelmed.

**Latency**
The delay between a request and response in a network communication, typically measured in milliseconds.

## M

**Marketplace**
Armada's hub for hardware and software resources needed for edge operations. Provides discovery, deployment, and management of edge-optimized applications and services.

**Microservices**
An architectural approach where applications are built as a collection of small, independent services that communicate over well-defined APIs.

**Monolith**
A traditional software architecture where all components of an application are interconnected and deployed as a single unit.

## N

**Namespace**
A way to divide cluster resources between multiple users or projects in Kubernetes, providing scope for names and resource isolation.

**Node**
A worker machine in Kubernetes, which can be either a physical or virtual machine, where pods are scheduled to run.

## O

**Observability**
The ability to measure the internal states of a system by examining its outputs, including logs, metrics, and traces.

**Orchestration**
The automated configuration, coordination, and management of computer systems and services.

## P

**Pod**
The smallest deployable unit in Kubernetes, consisting of one or more containers that share storage and network.

**Persistent Volume (PV)**
A piece of storage in a Kubernetes cluster that has been provisioned by an administrator or dynamically using Storage Classes.

## R

**Replica Set**
A Kubernetes controller that ensures a specified number of pod replicas are running at any given time.

**Rolling Update**
A deployment strategy that gradually replaces old versions of an application with new ones, ensuring zero downtime.

**Rollback**
The process of reverting to a previous version of an application or configuration when issues are detected.

## S

**Service Mesh**
A dedicated infrastructure layer for handling service-to-service communication, providing features like traffic management, security, and observability.

**StatefulSet**
A Kubernetes workload API object used to manage stateful applications, providing guarantees about ordering and uniqueness of pods.

## T

**Telemetry**
The automatic collection and transmission of data from remote sources for monitoring and analysis purposes.

## V

**Virtual Machine (VM)**
A software-based emulation of a physical computer that runs an operating system and applications as if it were a physical machine.

**Vertical Pod Autoscaler (VPA)**
A Kubernetes feature that automatically adjusts CPU and memory resource requests for containers based on usage patterns.

## W

**Workload**
An application or service running on Kubernetes, typically consisting of pods, deployments, services, and other resources.

## Y

**YAML (YAML Ain't Markup Language)**
A human-readable data serialization standard commonly used for configuration files and data exchange between applications.

---

:::tip Need More Information?
If you can't find a term you're looking for, please [open an issue on GitHub](https://github.com/armada-platform/aep-docs/issues/new) or [contribute to this glossary](https://github.com/armada-platform/aep-docs/edit/main/docs/glossary.md).
:::

:::info Related Resources
- [Platform Overview](./getting-started/platform-overview.md).
- [Key Concepts](./getting-started/key-concepts.md).
- [Developer Resources](./developer-resources/overview.md).
::: 
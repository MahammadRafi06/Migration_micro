---
id: faq
title: Frequently Asked Questions
sidebar_label: FAQ
sidebar_position: 998
---

import FeedbackWidget from '@site/src/components/FeedbackWidget';

# Frequently Asked Questions (FAQ)

Find answers to the most commonly asked questions about the Armada Edge Platform.

## General Platform Questions

### What is the Armada Edge Platform?

The Armada Edge Platform (AEP) is a comprehensive edge computing solution that brings cloud-native capabilities to remote, disconnected, or resource-constrained environments. It consists of three main components:

- **Galleon**: Ruggedized modular data centers
- **Atlas**: Operational insights and monitoring
- **Marketplace**: Hub for edge-optimized software and hardware

### Who is the target audience for AEP?

AEP is designed for:
- **Independent Software Vendors (ISVs)** looking to extend their applications to the edge
- **Enterprise customers** with remote operations requiring local computing
- **Developers** building edge-native applications
- **Operations teams** managing distributed infrastructure

### How does AEP differ from traditional cloud platforms?

:::note Key Differences
| Traditional Cloud | Armada Edge Platform |
|-------------------|---------------------|
| Centralized data centers | Distributed edge locations |
| High latency for remote operations | Ultra-low latency processing |
| Requires constant connectivity | Autonomous operation capability |
| Generic infrastructure | Purpose-built for edge environments |
| Standard security models | Enhanced edge security features |
:::

## Technical Questions

### What container orchestration does AEP use?

AEP is built on **Kubernetes**, providing:
- Industry-standard container orchestration
- Support for both containers and virtual machines (via KubeVirt)
- Helm chart compatibility
- GitOps workflows

### Can I run virtual machines on AEP?

Yes! AEP supports virtual machines through **KubeVirt integration**, allowing you to:
- Run legacy applications without modification
- Manage VMs alongside containers
- Migrate existing VM workloads to the edge

### What programming languages and frameworks are supported?

AEP supports any language or framework that can run in containers or VMs, including:
- **Web frameworks**: React, Angular, Vue.js, Django, Flask, Express.js
- **Languages**: Python, Java, C#, Go, Node.js, Ruby, PHP
- **Databases**: PostgreSQL, MySQL, MongoDB, Redis
- **Message queues**: RabbitMQ, Apache Kafka, NATS

## Deployment and Migration

### How do I migrate my existing application to AEP?

We provide several migration paths:

1. **Lift-and-shift**: Move existing VMs to edge locations
2. **Containerization**: Package applications as containers
3. **Microservices decomposition**: Break monoliths into microservices

:::tip Migration Resources
Check our [Migration Playbooks](./migration-playbooks/overview) for step-by-step guides tailored to your specific scenario.
:::

### Can I use Docker Compose files with AEP?

Yes! We provide tools to convert Docker Compose files to Kubernetes manifests:
- **Kompose**: Automated conversion tool
- **Manual conversion**: Step-by-step process with optimization
- **Helm charts**: Advanced packaging for complex applications

### How long does a typical migration take?

Migration timelines vary based on application complexity:

- **Simple applications**: 1-2 weeks
- **Medium complexity**: 4-8 weeks  
- **Enterprise applications**: 3-6 months
- **Legacy monoliths**: 6-12 months

### What if my application requires specific hardware?

Galleon data centers come in multiple form factors and can be customized with:
- Specialized GPU cards for AI/ML workloads
- Industrial-grade networking equipment
- Custom storage solutions
- Environmental sensors and controls

## Operations and Management

### How do I monitor my applications on AEP?

Atlas provides comprehensive monitoring including:
- **Real-time metrics** and alerting
- **Log aggregation** across all edge locations
- **Distributed tracing** for microservices
- **Performance dashboards** and reports

### Can I integrate with my existing monitoring tools?

Yes! Atlas supports integration with popular monitoring platforms:
- Prometheus and Grafana
- Datadog, New Relic, Splunk
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Custom integrations via APIs

### How do I handle updates and deployments?

AEP supports multiple deployment strategies:
- **Rolling updates**: Gradual replacement with zero downtime
- **Blue-green deployments**: Switch between two identical environments
- **Canary deployments**: Test with a subset of traffic
- **GitOps workflows**: Automated deployments from Git repositories

### What happens if connectivity to the cloud is lost?

AEP is designed for autonomous operation:
- Applications continue running locally
- Local data processing and storage continue
- Automatic synchronization when connectivity resumes
- Emergency fallback procedures for critical operations

## Security and Compliance

### How secure is data on AEP?

AEP implements multiple security layers:
- **Encryption**: Data at rest and in transit
- **Network security**: Micro-segmentation and policies
- **Identity management**: RBAC and service authentication
- **Compliance**: SOC 2, ISO 27001, and industry standards

### Can I use my existing identity provider?

Yes! AEP integrates with:
- Active Directory and LDAP
- SAML and OAuth providers
- Cloud identity services (Azure AD, AWS IAM)
- Custom authentication systems

### How do I ensure compliance in regulated industries?

AEP supports compliance requirements for:
- **Healthcare**: HIPAA compliance features
- **Financial services**: PCI DSS requirements
- **Government**: FedRAMP and other standards
- **Manufacturing**: Industry-specific regulations

## Troubleshooting

### My application is running slowly. How do I troubleshoot?

Follow this troubleshooting checklist:

1. **Check resource utilization** in Atlas dashboards
2. **Review application logs** for errors or warnings
3. **Analyze network latency** between components
4. **Verify storage performance** and availability
5. **Check for resource constraints** (CPU, memory, storage)

:::tip Performance Optimization
Visit our [Performance Tuning Guide](./platform-deep-dive/scaling-performance/performance-tuning) for detailed optimization strategies.
:::

### I'm getting deployment errors. What should I check?

Common deployment issues and solutions:

- **Image pull errors**: Verify container registry access and credentials
- **Resource limits**: Check CPU, memory, and storage quotas
- **Network policies**: Ensure required ports and protocols are allowed
- **Configuration errors**: Validate YAML syntax and required fields
- **Dependency issues**: Verify all required services are running

### How do I get support?

Multiple support channels are available:

- **Community forums**: Connect with other users and experts
- **Documentation**: Comprehensive guides and troubleshooting
- **GitHub issues**: Report bugs and request features
- **Professional support**: Enterprise support options available

:::info Support Resources
- [Community Resources](./developer-resources/support/community-resources)
- [Support Channels](./developer-resources/support/support-channels)
- [Troubleshooting Guides](./developer-resources/troubleshooting/debugging-guides)
:::

## Billing and Pricing

### How is AEP pricing structured?

Our pricing model includes:
- **Hardware costs**: Galleon data center lease/purchase
- **Software licensing**: Platform and feature licenses
- **Support services**: Optional professional support
- **Usage-based**: Computing and storage consumption

See our [Pricing Model](./cost-management/pricing-model) for detailed information.

### Can I start with a proof of concept?

Yes! We offer several options for getting started:
- **Free trial**: Limited-time access to platform features
- **Pilot programs**: Small-scale deployments for evaluation
- **Developer sandbox**: Testing environment for application development
- **POC support**: Technical assistance for proof of concepts

## Integration and APIs

### Does AEP provide APIs for integration?

Yes! AEP offers comprehensive APIs for:
- **Deployment management**: Deploy and manage applications
- **Monitoring and metrics**: Access operational data
- **Resource management**: Control computing resources
- **User management**: Manage access and permissions

See our [API Reference](./developer-resources/cli-apis/api-reference) for complete documentation.

### Can I integrate with CI/CD pipelines?

Absolutely! AEP supports integration with:
- **GitHub Actions, GitLab CI, Jenkins**
- **ArgoCD, Flux for GitOps**
- **Docker registries and Helm repositories**
- **Custom CI/CD tools via APIs**

Check our [CI/CD Integration Guide](./application-lifecycle/ci-cd/integrating-popular-tools) for setup instructions.

---

## Still Have Questions?

:::tip Get Help
If you can't find the answer you're looking for:

1. **Search our documentation** using the search bar
2. **Check the [Glossary](./glossary)** for technical definitions
3. **Browse [Community Resources](./developer-resources/support/community-resources)** for user discussions
4. **Contact [Support](./developer-resources/support/support-channels)** for direct assistance
5. **[Open a GitHub issue](https://github.com/armada-platform/aep-docs/issues/new)** to suggest improvements
:::

<FeedbackWidget /> 
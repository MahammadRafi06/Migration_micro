---
id: platform-specific-clis
title: Platform-Specific CLI Tools
sidebar_label: Platform-Specific CLIs
description: Command-line tools for managing edge platform resources
draft: true
---

# Platform-Specific CLI Tools (Archived)

> **⚠️ Archived:** This page is no longer maintained and may contain outdated information. Please refer to the latest documentation or team resources for up-to-date guidance.

<!--
# Platform-Specific CLI Tools: A Practical Guide

Managing edge platforms and Kubernetes clusters efficiently often requires more than just the standard tools. Platform-specific CLI tools provide powerful, streamlined ways to interact with your infrastructure, automate deployments, and manage resources. This guide introduces the essential CLI tools for your edge platform, explains their use cases, and provides actionable steps for getting started.

---

## What Are Platform-Specific CLI Tools?

Platform-specific CLI tools are command-line applications tailored to your edge platform or cloud provider. They offer:
- Simplified authentication and access management
- One-stop commands for cluster, app, and resource management
- Integrations with Kubernetes, Helm, Kustomize, and more
- Automation capabilities for CI/CD and scripting

---

## Getting Started: Installing the Edge Platform CLI

Before you can manage your edge resources, install the official CLI tool:

```bash
# Download and install the Edge CLI (Linux example)
curl -L https://releases.edge-platform.com/cli/latest/edge-cli-linux-amd64 -o edge
chmod +x edge
sudo mv edge /usr/local/bin/
```

- **Tip:** For Windows or Mac, download the appropriate binary from the [official releases page](https://releases.edge-platform.com/cli/).
- **Verify installation:**
  ```bash
  edge version
  ```

---

## Core Features & Usage

### 1. **Authentication & Access**
- **Login securely:**
  ```bash
  edge auth login
  ```
  - Opens a browser for SSO or prompts for credentials.
- **Why:** Ensures all actions are securely tracked and authorized.

---

### 2. **Cluster Management**
- **List all clusters:**
  ```bash
  edge cluster list
  ```
- **Set default cluster:**
  ```bash
  edge config set-cluster edge-west-1
  ```
- **Switch contexts/environments:**
  ```bash
  edge config use-context production
  ```
- **View current config:**
  ```bash
  edge config view
  ```
- **Use case:**
  > You manage multiple edge locations and need to quickly switch between them for deployments or troubleshooting.

---

### 3. **Application Deployment**
- **Deploy an application:**
  ```bash
  edge app deploy --file app.yaml --cluster edge-west-1
  ```
- **Check deployment status:**
  ```bash
  edge app status myapp
  ```
- **Use case:**
  > You want to roll out a new version of your app to a specific edge cluster and monitor its rollout.

---

### 4. **Configuration Management**
- **Maintain separate configs for each environment (dev, staging, prod).**
- **Automate config changes in CI/CD pipelines.**
- **Example:**
  ```bash
  edge config set-cluster staging
  edge app deploy --file app-staging.yaml
  ```

---

## Kubernetes CLI Extensions

Platform CLIs often integrate with Kubernetes tools for advanced workflows:

### 1. **Kustomize Integration**
- **Deploy with Kustomize overlays:**
  ```bash
  edge deploy --kustomize overlays/production/
  ```
- **Preview changes before applying:**
  ```bash
  edge deploy --dry-run --kustomize overlays/production/
  ```
- **Use case:**
  > You want to test your production configuration before making changes live.

---

### 2. **Helm Integration**
- **Install a Helm chart:**
  ```bash
  edge helm install myapp ./chart --cluster edge-east-1
  ```
- **Upgrade a release:**
  ```bash
  edge helm upgrade myapp ./chart --cluster edge-east-1
  ```
- **Use case:**
  > You manage complex applications with Helm and want to deploy or upgrade them across multiple edge clusters.

---

## Best Practices for CLI Usage

- **Authentication:** Always use secure login methods (SSO, tokens).
- **Configuration:** Keep separate configs for each environment and document them.
- **Automation:** Integrate CLI commands into your CI/CD pipelines for repeatable, reliable deployments.
- **Documentation:** Maintain up-to-date CLI usage docs for your team.
- **Security:** Regularly update your CLI tool to get the latest security patches.

---

## Troubleshooting

- **Command Not Found:** Ensure the CLI binary is in your PATH and executable.
- **Authentication Errors:** Re-run `edge auth login` or check your credentials.
- **Permission Denied:** Make sure you have the right role or access level for the action.
- **Deployment Fails:** Use `edge app status <app>` and check logs for details.
- **Version Mismatch:** Run `edge version` and update if needed.

---

## Further Reading & Resources

- [Edge Platform CLI Documentation](https://releases.edge-platform.com/docs/cli/)
- [Kubernetes Official Documentation](https://kubernetes.io/docs/)
- [API Reference](./api-reference.md)
- [Recommended kubectl Plugins](./recommended-kubectl-plugins.md)

---

With these tools and best practices, you'll be able to manage your edge platform and Kubernetes resources efficiently, securely, and with confidence. Happy automating!
--> 
---
id: introduction-and-prerequisites
title: Introduction & Prerequisites
sidebar_label: Introduction & Prerequisites
---

# Converting Docker Compose to Helm Charts

## Introduction

This guide provides a comprehensive walkthrough for converting Docker Compose files into Kubernetes Helm Charts. Helm Charts are a powerful way to package and deploy applications on Kubernetes, offering templating, versioning, and easier management compared to raw Kubernetes manifests.

We'll explore multiple approaches including:
- Using open-source tools like Kompose and Katenary for direct conversion.
- Using Score as an alternative, platform-agnostic approach.
- Manually refining and optimizing the generated charts.

:::tip Key Insight
While automated tools can assist with the conversion process, understanding the underlying concepts and manual refinement steps is crucial for production-ready deployments.
:::

## Prerequisites

Ensure you have the following essential tools installed on your development machine. Each tool plays a vital role in the conversion and deployment workflow.

### Git

```bash
# Check installation
git --version
```

### Docker (with Docker Compose)

```bash
# Check Docker installation
docker --version

# Check Docker Compose installation
docker compose version
```

### Minikube

A tool that runs a single-node Kubernetes cluster inside a virtual machine (VM) on your local machine. It's ideal for local development and testing Kubernetes deployments.

```bash
# Linux installation example
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube_latest_amd64.deb
sudo dpkg -i minikube_latest_amd64.deb

# Check installation
minikube version
```

### kubectl

The Kubernetes command-line tool for running commands against Kubernetes clusters. Minikube typically installs and configures kubectl automatically.

```bash
# Check installation
kubectl version --client
```

### Helm (latest version)

The package manager for Kubernetes, used to manage Helm Charts.

```bash
# Linux installation example
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Check installation
helm version
```

### Kompose (latest version)

A conversion tool that transforms Docker Compose files into Kubernetes resources and can generate basic Helm charts.

```bash
# Linux installation example
curl -L https://github.com/kubernetes/kompose/releases/download/v1.36.0/kompose-linux-amd64 -o kompose
chmod +x kompose
sudo mv ./kompose /usr/local/bin/kompose

# Check installation
kompose version
```

### Katenary (latest version)

A tool specifically designed to convert Docker Compose files to configurable Helm charts.

```bash
# Linux installation example
sh <(curl -sSL https://raw.githubusercontent.com/metal3d/katenary/master/install.sh)

# Check installation
katenary version
```

### Score CLI & Score-Helm (latest versions)

For the alternative Score approach.

```bash
# macOS installation example using Homebrew
brew install score-spec/tap/score
brew install score-spec/tap/score-helm

# Check installation
score --version
score-helm --version
```

:::note
Follow the official documentation for each tool to get the latest installation methods for your operating system.
:::

## Setup and Initial Verification

This section guides you through setting up the example application and verifying its functionality in a Docker Compose environment before transitioning to Kubernetes with Helm.

### Clone the Repository

Begin by cloning the provided example application repository. This repository contains the Docker Compose file and application code necessary for this guide.

```bash
git clone https://github.com/MahammadRafi06/examples.git
cd compose2k8
```

Review the file structure to understand the project layout. This helps in mapping Docker Compose services to Kubernetes components.

```
compose2k8/
├── app/                  # Contains the Python application code and Dockerfile
│   ├── app.py            # The main Python Flask application
│   ├── Dockerfile        # Defines how to build the Docker image for the 'app'
│   └── requirements.txt  # Python dependencies for the 'app'
├── templates/            # HTML templates used by the Flask application
│   └── index.html        # The main HTML page served by the application
├── docker-compose.yaml   # Docker Compose definition file
└── init.sql              # SQL script for initializing the PostgreSQL database
```

### Verify Docker Compose Application

It is crucial to ensure the application functions correctly in its native Docker Compose environment before attempting to migrate it to Kubernetes. This step establishes a working baseline.

```bash
docker compose up --build
```

This builds the Docker images (if not already built) and starts all services defined in the 'docker-compose.yaml' file. The '--build' flag ensures images are rebuilt if changes are detected.

Verify that the Docker containers are running as expected:

```bash
docker ps
```

Access the application from your browser (typically http://localhost:5000 or the port specified in your docker-compose.yaml) to confirm full functionality. This ensures the application logic and database connectivity are working correctly.

### Start Minikube Cluster

Minikube provides a local Kubernetes environment, allowing you to test your Kubernetes manifests and Helm charts without needing a full-fledged cloud cluster.

```bash
minikube start armadalocal
```

This initializes and starts a new Minikube cluster named 'armadalocal'. This process involves setting up a VM (or Docker container, depending on your driver) and deploying the necessary Kubernetes components.

Example output during Minikube startup:

```
minikube v1.36.0 on Ubuntu 24.04
Automatically selected the docker driver. Other choices: none, ssh
Starting "minikube" primary control-plane node in "minikube" cluster
Done! kubectl is now configured to use "minikube" cluster and "default" namespace by default
```

Verify the Minikube node status to ensure the cluster is ready:

```bash
kubectl get nodes
```

Example output:

```
NAME       STATUS   ROLES           AGE     VERSION
minikube   Ready    control-plane   7m25s   v1.33.1
```

:::important
Make sure your Minikube node is in the "Ready" state before proceeding to the next steps. This indicates that the Kubernetes control plane is fully operational.
:::

## Next Steps

Now that we have our environment set up and verified, we can proceed to the conversion process. In the next section, we'll explore how to use Kompose to automatically convert our Docker Compose configuration to a Helm chart, followed by using Katenary for a more refined conversion.

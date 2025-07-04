---
id: prerequisites-and-setup
title: "Setup & Prerequisites"
sidebar_label: "Setup & Prerequisites"
---

# Setup & Prerequisites

## Introduction

This guide provides a detailed walkthrough for converting your existing Docker Compose configurations into Kubernetes YAML manifests. We'll explore various tools and strategies, including manual conversion, automated tools like kompose and podman generate kube, and advanced packaging with Helm charts and Kubernetes Operators. 

:::tip Key Insight
While tools can automate parts of this process, understanding the underlying concepts and manual refinement steps is crucial for robust, production-ready deployments.
:::

## Prerequisites

Ensure you have the following essential tools installed on your development machine:

### Git

```bash
git --version
```

### Docker (with Docker Compose)

```bash
docker --version
docker compose version
```

### Kompose (Linux Installation)

```bash
curl -L https://github.com/kubernetes/kompose/releases/download/v1.36.0/kompose-linux-amd64 -o kompose
chmod +x kompose
sudo mv ./kompose /usr/local/bin/kompose
kompose version
```

### Minikube (Linux Installation)

```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube_latest_amd64.deb
sudo dpkg -i minikube_latest_amd64.deb
minikube version
```

### kubectl (usually installed via Minikube)

```bash
kubectl version --client
```

## Setup and Initial Verification

### Clone the Repository

```bash
git clone https://github.com/MahammadRafi06/examples.git
cd compose2k8
```

Project structure:
```
compose2k8/
├── app/                  # Python application code and Dockerfile
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── templates/
│   └── index.html
├── docker-compose.yaml   # Defines services
└── init.sql              # SQL for initializing PostgreSQL
```

### Verify Docker Compose Application

Start the application with:

```bash
docker compose up --build
```

Check running containers:

```bash
docker ps
```

Open your browser to [http://localhost:5000](http://localhost:5000) or the configured port to verify the app runs as expected.

### Start Minikube Cluster

Start a new Minikube cluster:

```bash
minikube start armadalocal
```

Example output:
```
minikube v1.36.0 on Ubuntu 24.04
Using Docker driver with root privileges
Starting control-plane node...
Done! kubectl is now configured...
```

Check node status:

```bash
kubectl get nodes
```

Expected output:
```
NAME       STATUS   ROLES           AGE     VERSION
minikube   Ready    control-plane   7m25s   v1.33.1
```

:::note
Make sure your Minikube node is in the "Ready" state before proceeding to the next steps. This indicates that the Kubernetes control plane is fully operational.
:::

## Next Steps

In the next section, we'll use Kompose to automatically convert our Docker Compose configuration to Kubernetes manifests, and learn how to review and adjust the generated files.

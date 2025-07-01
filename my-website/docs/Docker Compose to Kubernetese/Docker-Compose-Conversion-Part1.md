# Part 1: Setup & Prerequisites

## Navigation
- **Part 1: Setup & Prerequisites** (Current)
- [Part 2: Converting with Kompose](#part2)
- [Part 3: Deployment & Manual Creation](#part3)
- [Part 4: Advanced Considerations & Cleanup](#part4)

---

## **1. Introduction**

This runbook provides a comprehensive guide for developers to convert Docker Compose files into Kubernetes manifests. It covers both the use of Kompose, a tool designed to simplify this conversion process, and manual manifest creation for a deeper understanding. Understanding these steps is crucial for migrating containerized applications from a local Docker environment to a Kubernetes cluster.

---

## **2. Prerequisites**

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

---

## **3. Setup and Initial Verification**

### **3.1. Clone the Repository**

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

---

### **3.2. Verify Docker Compose Application**

Start the application with:
```bash
docker compose up --build
```

Check running containers:
```bash
docker ps
```

Open your browser to [http://localhost:5000](http://localhost:5000) or the configured port to verify the app runs as expected.

---

### **3.3. Start Minikube Cluster**

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

---

## Navigation
- **Part 1: Setup & Prerequisites** (Current)
- [Part 2: Converting with Kompose](#part2)
- [Part 3: Deployment & Manual Creation](#part3)
- [Part 4: Advanced Considerations & Cleanup](#part4)
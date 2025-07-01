# **Converting Docker Compose to Kubernetes YAML - Part 1: Setup & Prerequisites**

## Navigation
- **Part 1: Setup & Prerequisites** (Current)
- [Part 2: Converting with Kompose](#part2)
- [Part 3: Deployment & Manual Creation](#part3)
- [Part 4: Advanced Considerations & Cleanup](#part4)

---

## **1. Introduction**

This runbook provides a comprehensive guide for developers to convert Docker Compose files into Kubernetes manifests. It covers both the use of Kompose, a tool designed to simplify this conversion process, and manual manifest creation for a deeper understanding. Understanding these steps is crucial for migrating containerized applications from a local Docker environment to a Kubernetes cluster.

## **2. Prerequisites**

Ensure you have the following essential tools installed on your development machine. Each tool plays a vital role in the conversion and deployment workflow.

* Git: A version control system used for cloning the example application repository.
  * Installation Check: git \--version
* Docker (with Docker Compose): The platform for building, shipping, and running containerized applications. Docker Compose is used for defining and running multi-container Docker applications.
  * Installation Check: docker \--**version**, docker compose **version**
* Kompose (latest version): A conversion tool that transforms Docker Compose files into Kubernetes resources (Deployments, Services, etc.).
  * Installation Steps for Linux:

| curl \-L https://github.com/kubernetes/kompose/releases/download/v1.36.0/kompose-linux-amd64 \-o kompose\# Explanation: Downloads the Kompose executable for Linux AMD64 architecture.chmod \+x kompose\# Explanation: Makes the downloaded file executable.sudo mv ./kompose /usr/local/bin/kompose\# Explanation: Moves the executable to a directory in your system's PATH, making it globally accessible. |
| :---- |

  * Installation Check: kompose version
* Minikube: A tool that runs a single-node Kubernetes cluster inside a virtual machine (VM) on your local machine. It's ideal for local development and testing Kubernetes deployments.
  * Installation Steps for Linux:

| curl \-LO https://storage.googleapis.com/minikube/releases/latest/minikube\_latest\_amd64.deb\# Explanation: Downloads the latest Minikube Debian package.sudo dpkg \-i minikube\_latest\_amd64.deb\# Explanation: Installs the Minikube package on your system. |
| :---- |

  * 
  * Installation Check: minikube version
* kubectl: The Kubernetes command-line tool for running commands against Kubernetes clusters. Minikube typically installs and configures kubectl automatically.
  * Installation Check: kubectl version \--client

## **3. Setup and Initial Verification**

This section guides you through setting up the example application and verifying its functionality in a Docker Compose environment before transitioning to Kubernetes.

### **3.1. Clone the Repository**

Begin by cloning the provided example application repository. This repository contains the Docker Compose file and application code necessary for this runbook.

| git clone https://github.com/MahammadRafi06/examples.git\# Explanation: Downloads the 'examples' repository from GitHub to your local machine.cd compose2k8\# Explanation: Changes your current directory to the 'compose2k8' subdirectory within the cloned repository, where the Docker Compose file is located. |
| :---- |

Review the file structure. Understanding the project layout helps in mapping Docker Compose services to Kubernetes components. You should see a structure similar to this:

| compose2k8/├── app/                  \# Contains the Python application code and Dockerfile for the 'app' service.│   ├── app.py            \# The main Python Flask application.│   ├── Dockerfile        \# Defines how to build the Docker image for the 'app'.│   └── requirements.txt  \# Python dependencies for the 'app'.├── templates/            \# HTML templates used by the Flask application.│   └── index.html        \# The main HTML page served by the application.├── docker-compose.yaml   \# The Docker Compose definition file, describing the multi-service application.└── init.sql              \# SQL script for initializing the PostgreSQL database. |
| :---- |

### **3.2. Verify Docker Compose Application**

It is crucial to ensure the application functions correctly in its native Docker Compose environment before attempting to migrate it to Kubernetes. This step establishes a working baseline.

| docker compose up \--build\# Explanation: Builds the Docker images (if not already built) and starts all services defined in the 'docker\-compose.yaml' file. The '\--build' flag ensures images are rebuilt if changes are detected. |
| :---- |

Verify that the Docker containers are running as expected:

| docker ps\# Explanation: Lists all currently running Docker containers, allowing you to confirm that both the 'app' and 'db' services are active. |
| :---- |

Access the application from your browser (typically http://localhost:5000 or the port specified in your **docker-compose**.yaml) to confirm full functionality. This ensures the application logic and database connectivity are working correctly.

### **3.3. Start Minikube Cluster**

Minikube provides a local Kubernetes environment, allowing you to test your Kubernetes manifests without needing a full-fledged cloud cluster.

| minikube start armadalocal\# Explanation: Initializes and starts a new Minikube cluster named 'armadalocal'. This process involves setting up a VM (or Docker container, depending on your driver) and deploying the necessary Kubernetes components. |
| :---- |

Example output during Minikube startup:

| minikube v1.36.0 on Ubuntu 24.04Automatically selected the docker driver. Other choices: none, sshUsing Docker driver with root privilegesStarting "minikube" primary control-plane node in "minikube" cluster...Done\! kubectl is now configured to use "minikube" cluster and "default"namespace by default\# Explanation: This message confirms that Minikube has successfully started and configured your \`kubectl\` command-line tool to interact with this new cluster. |
| :---- |

Verify the Minikube node status to ensure the cluster is ready:

| kubectl get nodes\# Explanation: Lists the nodes in your Kubernetes cluster. In Minikube, you should see a single 'minikube' node with a 'Ready' status. |
| :---- |

Example output:

| NAME       STATUS   ROLES           AGE     VERSIONminikube   Ready    control\-plane   7m25s   v1.33.1 |
| :---- |

---

## Navigation
- **Part 1: Setup & Prerequisites** (Current)
- [Part 2: Converting with Kompose](#part2)
- [Part 3: Deployment & Manual Creation](#part3)
- [Part 4: Advanced Considerations & Cleanup](#part4)
---
id: preparing-golden-images
title: Prepare Docker Compose & Golden Image
sidebar_label: Prepare Application & VM Image
---

# Preparing Your Docker Compose Application and VM Image

Before we can deploy our Docker Compose application to KubeVirt VMs, we need to prepare both the application and create a "golden image" that will serve as the base for our virtual machines.

## Phase 1: Prepare Your Docker Compose Application

### Ensure Docker Images are Accessible

Your Docker Compose application will run inside a VM, which means it needs to pull Docker images from a registry.

- **For locally built images**: If your docker-compose.yml builds images locally (e.g., `build: .`), you must build these images and push them to a container registry (Docker Hub, Quay.io, a private registry) that your KubeVirt VMs can access. Your docker-compose.yml should then reference these pre-built images (e.g., `image: your-registry/your-app:tag`).

- **For pre-built images**: If your docker-compose.yml already pulls images from public or private registries, you're good to go.

:::warning
VMs inside KubeVirt won't have access to locally built Docker images unless they're pushed to a registry. Make sure all images are accessible from within the VM.
:::

### Review Docker Compose for External Access

Identify which services in your docker-compose.yml expose ports that need to be accessible from outside the VM:

- Look for port mappings like `ports: "80:3000"`, where 3000 is the internal container port, and 80 is the port exposed on the VM's host.
- You will map this host port (80 in this example) in your KubeVirt VM definition and then in a Kubernetes Service.

**Example docker-compose.yml:**

```yaml
# docker-compose.yml
version: '3.8'
services:
  webapp:
    image: your-registry/my-node-app:1.0
    ports:
      - "80:3000" # VM port 80 maps to container port 3000
    environment:
      NODE_ENV: production
      DB_HOST: database # This will be resolvable within the VM's Docker network
    volumes:
      - ./app-data:/usr/src/app/data # Relative path within the VM
    depends_on:
      - database
  database:
    image: postgres:13
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - db-data:/var/lib/postgresql/data
volumes:
  db-data:
  app-data:
```

### Handle Persistent Volumes

For data persistence, you have two options:

- **Docker-managed volumes**: Named volumes in your docker-compose.yml (e.g., `db-data`, `app-data`) will be managed by Docker within the KubeVirt VM. This is the simpler approach but may not be suitable for all production workloads.

- **Kubernetes-managed volumes**: For external persistence that survives the VM's deletion, you'll need to define additional PersistentVolumeClaims (PVCs) in Kubernetes and attach them to your KubeVirt VM. This is more complex but provides more robust persistence.

:::note
For simplicity, this guide assumes Docker's internal volume management within the VM is sufficient, or that data persistence is handled by a separate, dedicated database service outside this VM.
:::

## Phase 2: Create a Base VM Disk Image (Golden Image)

This is the most crucial step. You need a QCOW2 disk image that will serve as the base for your KubeVirt VMs.

### Obtain a Base OS Image

Download a minimal cloud-ready QCOW2 image for a Linux distribution:

```bash
# Example for Ubuntu 22.04
wget https://cloud-images.ubuntu.com/releases/jammy/release/ubuntu-22.04-server-cloudimg-amd64.img
```

### Prepare the Golden Image

You have two main approaches to create your golden image:

#### Method A: Using virt-builder (Recommended for Automation)

virt-builder allows you to create and customize VM disk images programmatically:

```bash
# Install libguestfs-tools if you don't have it (e.g., on Ubuntu/Debian)
sudo apt-get install libguestfs-tools

# Customize the image:
virt-builder --output my-golden-vm.qcow2 \
  --size 20G \
  --format qcow2 \
  ubuntu-22.04 \
  --hostname my-docker-host \
  --user dockeruser --password password:your_secure_password \
  --run-command "apt update && apt install -y docker.io docker-compose" \
  --run-command "systemctl enable docker && systemctl start docker" \
  --upload docker-compose.yml:/home/dockeruser/my-app/docker-compose.yml \
  --upload ./your-app-code:/home/dockeruser/my-app/your-app-code \
  --run-command "chown -R dockeruser:dockeruser /home/dockeruser/my-app" \
  --run-command "chmod +x /home/dockeruser/my-app/start-app.sh" # If you have a startup script
```

:::important
Replace `your_secure_password`, `your-app-code`, and `start-app.sh` with your actual values.
:::

#### Method B: Manual VM Setup (Less Automated)

If you prefer a more manual approach or can't use virt-builder:

1. **Spin up a temporary VM** using your base OS image (e.g., in VirtualBox, VMware, or even a temporary KubeVirt VM).

2. **Inside this temporary VM**:
   - Install Docker and Docker Compose:
     ```bash
     # For Ubuntu/Debian
     sudo apt update
     sudo apt install -y docker.io docker-compose
     ```
   
   - Configure Docker to start on boot:
     ```bash
     sudo systemctl enable docker
     ```
   
   - Copy your docker-compose.yml file and any necessary application code into a directory:
     ```bash
     mkdir -p /opt/my-app
     # Copy your files to this directory
     ```
   
   - (Optional but recommended) Install cloud-init if it's not already present:
     ```bash
     sudo apt install -y cloud-init
     ```
   
   - Clean up any unnecessary files, history, or temporary data:
     ```bash
     sudo apt clean
     sudo rm -rf /var/lib/apt/lists/*
     history -c
     ```

3. **Shut down the temporary VM.**

4. **Convert or copy its virtual disk to a QCOW2 format** if it's not already:
   ```bash
   qemu-img convert -f <source-format> -O qcow2 <source-disk> my-golden-vm.qcow2
   ```

### Create a Startup Script (Optional)

For convenience, you might want to create a startup script that will run your Docker Compose application automatically when the VM boots. Save this as `start-app.sh` in your application directory:

```bash
#!/bin/bash
cd /opt/my-app
docker-compose up -d
```

Make it executable:

```bash
chmod +x start-app.sh
```

### Host Your Golden Image

To make your golden image accessible to CDI, you need to host it on a web server (HTTP/HTTPS) or an S3-compatible storage. Options include:

- **Local development**: Use a simple web server within your development environment:
  ```bash
  # Example using Python's built-in HTTP server
  python3 -m http.server 8000
  ```

- **Cloud storage**: Upload to S3, Google Cloud Storage, or similar services

- **Container registry**: Some container registries can also store VM images

:::tip
For production environments, ensure your VM image is stored securely and is accessible only to authorized systems.
:::

## Next Steps

Now that we have prepared our Docker Compose application and created a golden VM image, in the next section we'll define the KubeVirt VirtualMachine resource and import our golden image into the Kubernetes cluster.

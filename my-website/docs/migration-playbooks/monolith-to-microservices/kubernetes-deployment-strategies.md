---
id: kubernetes-deployment-strategies
title: Getting Your Services Ready for Kubernetes
sidebar_label: Kubernetes Deployment
sidebar_position: 4
---

# Getting Your Services Ready for Kubernetes

This next phase is all about preparing your individual services and then deploying them onto a Kubernetes cluster. This is a fundamental step towards achieving a true cloud-native architecture, allowing your services to run independently, consistently, and with excellent scalability across various environments.

## Containerizing with Docker

Once you've logically broken down your monolithic application into distinct services, the next crucial step is to wrap each service within its own isolated Docker container. This is how we ensure portability and consistent execution no matter where your application runs. You'll create a dedicated Dockerfile for each service (e.g., `Dockerfile.user-service`, `Dockerfile.project-task-service`). A Dockerfile is essentially a recipe – a text-based script that tells Docker exactly how to build your image, defining the service's environment, installing dependencies, copying code, and specifying the command to launch the service.

### Your Container Image Registry

After successfully creating your images, you'll need to store them in a remote container registry. This central, accessible location is where your Kubernetes cluster will pull the service containers from for deployment. You have several great options for container registries, including private ones, or public services like Docker Hub, Google Container Registry (GCR), AWS Elastic Container Registry (ECR), or Azure Container Registry (ACR). For this example, we'll use Docker Hub.

**Action:** Go ahead and sign in or sign up for a Docker Hub account, then create a public or private container repository as needed. Don't forget to authenticate your local Docker client with the registry using `docker login`.

### Building Your Dockerfile: The User Service Example

Here's a Dockerfile example for our User Service (`Dockerfile.user`). When you're ready for production, consider using multi-stage builds for even smaller image sizes and improved security.

```docker
# Stage 1: Build environment
FROM python:3.9-slim-buster as builder

# Set the working directory within the container
WORKDIR /app

# Copy the Python dependency requirements file
COPY requirements.txt .

# Install necessary Python packages. Use --no-cache-dir for smaller image size.
# Consider using a virtual environment within the Dockerfile for better isolation.
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final image
FROM python:3.9-slim-buster

# Set the working directory within the container
WORKDIR /app

# Copy installed packages from builder stage (if using multi-stage build)
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the remaining application code into the container
COPY . .

# Expose port 5001, which the Flask application listens on (Flask default is 5000)
# Ensure your Flask app listens on 0.0.0.0 to be accessible within the container.
EXPOSE 5001

# Define environment variables for the database path and other settings.
# These will be overridden by Kubernetes Secrets/ConfigMaps in production.
ENV DATABASE_PATH=/app/data/database.db
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5001

# Create a directory for persistent data, such as an SQLite database file (for local dev/testing).
# In Kubernetes, persistent storage will be mounted.
RUN mkdir -p /app/data

# Command to execute when the container starts.
# Use a production-ready WSGI server like Gunicorn instead of `flask run` for production.
# Example: CMD ["gunicorn", "-b", "0.0.0.0:5001", "app:app"]
CMD ["python", "app.py"]
```

**A quick tip on .dockerignore:** Always create a `.dockerignore` file right in the root of your service directory. This helps you exclude unnecessary files (like `.git` folders, `__pycache__`, `.env` files, or `node_modules/`) from being copied into your Docker image. It's a simple step that significantly reduces image size and speeds up your builds.

### How to Build Your Docker Images

To build a Docker image for a specific service, you'll run the following command from the root of that service's directory (where your Dockerfile and application code live):

```bash
docker build -f Dockerfile.<service-name> -t <your-dockerhub-username>/<service-name>:<tag> .
```

**For example:** To build the Docker image for the User Service with a tag of 1.2.0, you'd use:

```bash
docker build -f Dockerfile.user -t your_dockerhub_username/user-service:1.2.0 .
```

### Testing Your Containers Locally

Before you push your image to the registry, it's always a good idea to test it out right on your local machine:

```bash
docker run -p 5001:5001 your_dockerhub_username/user-service:1.2.0
```

You should then be able to access your running application locally at http://localhost:5001. Just make sure your Flask application inside the container is set to listen on 0.0.0.0 (not 127.0.0.1 or localhost) so it's accessible from your host machine.

### Pushing Images to Your Registry

Once you've tested your image and you're happy with it, it's time to push it to your configured container registry:

```bash
docker push your_dockerhub_username/user-service:1.2.0
```

## Deploying to Kubernetes: The User Service Walkthrough

With your container images now safely stored in the registry, the next exciting step is to define and deploy your Kubernetes manifests. These manifests are the blueprints that will orchestrate your application components within the cluster.

### Before You Begin: Prerequisites

Before diving into deployment, make sure you have a few things in place:

- **Kubectl CLI Installation:** Confirm that kubectl is installed and correctly configured to communicate with your target Kubernetes cluster. If you're working with a cloud provider like AWS EKS, Azure AKS, or Google GKE, you'll typically use their specific CLIs (aws cli, az cli, gcloud cli) to set up your kubectl context.
- **Local Development Cluster (Optional but Recommended):** For a smooth development and testing experience, we highly recommend setting up a lightweight Kubernetes cluster on your local machine. Tools like Minikube, Kind, Kubeadm, or k3d are excellent choices for this.
- **Kubernetes Cluster Access:** Double-check that you have admin or at least developer level access permissions to deploy resources within your target Kubernetes namespace.

### Identifying Your Kubernetes Objects

For the User Service (and you'll follow a similar pattern for your other services), we'll define and deploy the following Kubernetes objects:

- **Secrets:** These are for securely storing sensitive environment variables, like database credentials or application-specific secret keys.
- **PersistentVolumeClaim (PVC):** This is how you'll request persistent storage for your PostgreSQL database, ensuring your data sticks around even if a pod restarts.
- **Deployment (PostgreSQL):** This object will manage and scale your PostgreSQL database instances.
- **Service (PostgreSQL):** This will expose your PostgreSQL database internally within the cluster, allowing other services to connect to it seamlessly.
- **Deployment (User Service):** This will manage and scale your Flask User Service application instances.
- **Service (User Service):** This will expose your Flask User Service to other internal services or, if needed, externally (though for production, LoadBalancer or Ingress are usually preferred).
- **Ingress (Optional/Recommended for External Access):** If you want to expose your User Service externally via a friendly, publicly accessible URL, you'll use an Ingress resource with an Ingress controller (like Nginx Ingress).

### Crafting Your Kubernetes Manifests

Here are the YAML manifests that define the Kubernetes objects for our User Service and its necessary dependencies. It's a great practice to organize these in a dedicated directory, perhaps something like `kubernetes/user-service/`.

#### Secrets for Database & App

This Secret object is where we'll securely store all your sensitive configuration data, including database credentials and application-specific secret keys. **Seriously, remember to replace these placeholder values with strong, randomly generated secrets when you go to production!**

```yaml
# user-service-secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: user-service-secrets
  labels:
    app: user-service
type: Opaque # Use Opaque for generic key-value secrets
stringData:
  # Application secrets (replace with strong, random values for production)
  SECRET_KEY: "your_flask_app_secret_key_here_e.g._os.urandom(24).hex()" # Used by Flask for session management
  JWT_SECRET_KEY: "your_jwt_secret_key_here_e.g._os.urandom(24).hex()"  # Used for signing JWT tokens
  # PostgreSQL database credentials (replace with strong values for production)
  POSTGRES_DB: "user_db"
  POSTGRES_USER: "user_service_user"
  POSTGRES_PASSWORD: "user_service_password"
```

#### Persistent Storage for PostgreSQL

This PersistentVolumeClaim (PVC) is your request for 1 Gigabyte of storage specifically for your PostgreSQL database. Keep in mind that your cluster might require you to specify a StorageClass.

```yaml
# user-service-db-pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: user-service-db-pvc
  labels:
    app: user-service-db
spec:
  accessModes:
    - ReadWriteOnce # Volume can be mounted as read-write by a single node
  resources:
    requests:
      storage: 1Gi # Request 1 Gigabyte of storage
  # storageClassName: standard # Uncomment and specify a StorageClass if required by your cluster
```

#### Deploying Your PostgreSQL Database

This Deployment sets up a single PostgreSQL database instance. For high availability in a production environment, you'd typically want to use StatefulSets and a dedicated database operator (like Crunchy Data PostgreSQL Operator or Zalando Postgres Operator) which expertly handle database-specific tasks such as backups, replication, and upgrades.

```yaml
# user-service-db-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service-db
  labels:
    app: user-service-db
spec:
  replicas: 1 # Single instance for simplicity; consider StatefulSets for high availability and operators for managed DB
  selector:
    matchLabels:
      app: user-service-db
  template:
    metadata:
      labels:
        app: user-service-db
    spec:
      containers:
      - name: postgres
        image: postgres:13 # Using a stable PostgreSQL version
        ports:
        - containerPort: 5432 # Default PostgreSQL port
        env:
        - name: POSTGRES_DB
          valueFrom:
            secretKeyRef:
              name: user-service-secrets
              key: POSTGRES_DB
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: user-service-secrets
              key: POSTGRES_USER
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: user-service-secrets
              key: POSTGRES_PASSWORD
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data # Path where PostgreSQL stores its data
        resources: # Define resource requests and limits for production environments
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
      volumes:
      - name: postgres-data
        persistentVolumeClaim:
          claimName: user-service-db-pvc
```

#### Exposing Your PostgreSQL Database

This Service is designed to expose your PostgreSQL database internally within your cluster. This means other services can easily connect to it using its internal DNS name, `user-service-db`.

```yaml
# user-service-db-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: user-service-db # Internal DNS name for the database service
  labels:
    app: user-service-db
spec:
  selector:
    app: user-service-db
  ports:
  - protocol: TCP
    port: 5432 # Service port (inside cluster)
    targetPort: 5432 # Container port
  type: ClusterIP # Only accessible within the cluster
```

#### Deploying Your User Service Application

This Deployment sets up your User Service with two replicas, providing some basic scalability. Remember to update the image field with your actual Docker image path and tag.

```yaml
# user-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
  labels:
    app: user-service
spec:
  replicas: 2 # Adjust the number of replicas for desired scalability in production
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
      - name: user-service
        image: your_dockerhub_username/user-service:1.2.0 # Replace with your actual Docker image path and tag
        ports:
        - containerPort: 5001 # The port your Flask application listens on
        env:
        # PostgreSQL database connection details assembled from secrets
        # Note: A more robust approach for DATABASE_URL in production might involve
        # an init container or templating. For this example, direct assembly is shown.
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: user-service-secrets
              key: POSTGRES_USER
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: user-service-secrets
              key: POSTGRES_PASSWORD
        - name: POSTGRES_DB
          valueFrom:
            secretKeyRef:
              name: user-service-secrets
              key: POSTGRES_DB
        - name: DATABASE_URL
          # Construct the connection string using secret values and internal service DNS name
          value: "postgresql://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@user-service-db:5432/$(POSTGRES_DB)"
        # Application-specific secrets
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: user-service-secrets
              key: SECRET_KEY
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: user-service-secrets
              key: JWT_SECRET_KEY
        # Other environment variables
        - name: JWT_ACCESS_TOKEN_EXPIRES
          value: "86400" # 24 hours in seconds
        - name: ACTIVITY_LOG_SERVICE_URL
          value: "http://activity-log-service:5006" # Assumes 'activity-log-service' is in the same namespace
        - name: SQLALCHEMY_TRACK_MODIFICATIONS
          value: "False"
        - name: DEBUG
          value: "False" # Set to False for production
        resources: # Define resource requests and limits for stable performance
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        # Health checks (recommended for production deployments)
        livenessProbe:
          httpGet:
            path: /health # Your service should implement a /health endpoint
            port: 5001
          initialDelaySeconds: 15 # Initial delay before liveness probes start
          periodSeconds: 20       # How often (in seconds) to perform the probe
          timeoutSeconds: 5       # How long to wait for a response
          failureThreshold: 3     # Number of consecutive failures before marking as unhealthy
        readinessProbe:
          httpGet:
            path: /health
            port: 5001
          initialDelaySeconds: 5  # Initial delay before readiness probes start
          periodSeconds: 10       # How often (in seconds) to perform the probe
          timeoutSeconds: 5
          failureThreshold: 3
```

#### Exposing Your User Service

This Service makes your User Service accessible internally within the cluster, allowing other services or an Ingress controller to connect using the DNS name `user-service`. For external access in production, LoadBalancer or Ingress are much preferred over NodePort.

```yaml
# user-service-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: user-service # Internal DNS name for the user service
  labels:
    app: user-service
spec:
  selector:
    app: user-service
  ports:
  - protocol: TCP
    port: 5001 # Service port (internal cluster communication)
    targetPort: 5001 # Container port
  type: NodePort # Exposes the service on a port on each Node in the cluster.
                  # For external access, LoadBalancer (for direct external IP)
                  # or Ingress (for HTTP/HTTPS routing) is preferred in production.
```

#### Optional: Ingress for External Access

If you've got an Ingress Controller up and running in your Kubernetes cluster (like Nginx Ingress, Traefik, or GCE Ingress), you can expose your user-service via a more friendly domain name.

```yaml
# user-service-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: user-service-ingress
  labels:
    app: user-service
  annotations:
    # Add any Ingress controller specific annotations here (e.g., for SSL, rewrites)
    # kubernetes.io/ingress.class: nginx
    # cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  rules:
  - host: user.yourdomain.com # Replace with your actual domain
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: user-service # Name of your Service
            port:
              number: 5001 # Port of your Service
  # tls: # Uncomment for HTTPS with cert-manager
  # - hosts:
  #   - user.yourdomain.com
  #   secretName: user-service-tls # Kubernetes Secret that will hold your TLS certificate
```

## Bringing Your User Service to Life on Kubernetes

With all your necessary container images built and pushed to the registry, and your Kubernetes manifests clearly defined, we're now ready for the exciting part: deploying the User Service and its dependencies to your Kubernetes cluster!

### First, Check Your Cluster Connection

Before you deploy anything, make sure your kubectl is properly configured and connected to your local Kubernetes cluster. Just run this command in your terminal:

```bash
kubectl get nodes
```

**What you should see:** This command should list the nodes within your Kubernetes cluster, confirming that you're successfully connected.

### Applying Your Kubernetes Manifests

Now, navigate to the directory where you've stored all the Kubernetes YAML manifest files for your User Service (for instance, `kubernetes/user-service/`). This directory should contain all the `.yaml` files we outlined in the previous section.

Then, apply these manifests to your cluster using this simple command:

```bash
cd kubernetes/user-service/ # Assuming 'kubernetes/user-service/' is the directory containing your manifests
kubectl apply -f .
```

**What's happening here:**
- `kubectl apply -f .`: This command tells kubectl to either create new Kubernetes resources or update existing ones based on all the `.yaml` files found in your current directory. This will include your Secret, PersistentVolumeClaim, PostgreSQL Deployment and Service, and your User Service Deployment and Service.

### Keeping an Eye on Your Pods

After you've applied the manifests, it's a good idea to watch the status of your deployed pods to ensure they successfully transition to a Running state. This might take a few moments as images are pulled and containers start up.

```bash
kubectl get pods -l app=user-service-db
kubectl get pods -l app=user-service
```

**What you should see:** Keep running these commands until all the pods for `user-service-db` and `user-service` show a Running status. You're looking for a READY status that looks like `1/1` or `2/2`.

### Finding Your User Service Access Details

Once all your pods are up and running, you'll want to get the IP address and port number for your user-service so you can actually access the application.

```bash
kubectl get svc -o wide
```

**What's happening here:**
- `kubectl get svc`: This command gives you a list of all the services in your cluster.
- `-o wide`: This handy flag provides extra details, including the external IP (if applicable) and port mappings.

Look for the `user-service` entry in the output. If you're using NodePort for your service, you'll see a PORT(S) column that looks something like `5001:3xxxx/TCP`. The `3xxxx` number is the NodePort that Kubernetes has assigned.

**If you're using Minikube:** The easiest way to get the direct access URL for your user-service is to use:

```bash
minikube service user-service --url
```

### Accessing Your User Application

Now for the moment of truth! Using the IP address and port number you just retrieved, open your web browser or use a tool like curl to access your User Service application.

**For example (specifically for Minikube Clusters):** If `kubectl get svc -o wide` shows your user-service with TYPE: NodePort and PORT(S): `5001:3xxxx/TCP`, and your Minikube IP is `192.168.49.2`, you would access it via `http://192.168.49.2:3xxxx`.

You've done it! You've successfully deployed your first application service to Kubernetes. Now, you can follow these same steps for all the other services in your monolithic application to complete your migration to a microservices architecture on Kubernetes.

---

**Previous:** [← Service Breakdown](./service-decomposition-strategies) | **Next:** [Migration Considerations →](./key-migration-considerations)

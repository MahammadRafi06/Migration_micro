---
id: manual-conversion-process
title: Manual Conversion Process
sidebar_label: Manual Conversion
---

# Manual Conversion Process

## Manual Conversion (Recommended for Production)

This is the most robust method as it gives you full control and understanding of each Kubernetes resource. It's highly recommended even if you use automated tools as a starting point, as they often generate basic configurations that need significant refinement for production.

:::important
The manual conversion process is considered the best approach for production-ready Kubernetes manifests, as it allows you to incorporate best practices and ensure all aspects of your application are properly configured.
:::

### Steps for Manual Conversion

#### 1. Analyze Your Docker Compose File

Go through each service, volume, and network defined in your docker-compose.yml. Identify:  
* **Services:** What are the application components?  
* **Images:** Which Docker images are used?  
* **Ports:** Which ports are exposed and mapped?  
* **Environment Variables:** What configuration is passed via environment variables?  
* **Volumes:** What data needs to be persisted? Are they named volumes or host-path mounts?  
* **Dependencies:** Which services depend on others? (Kubernetes handles this differently, often via readiness probes).  
* **Networks:** How do services communicate?

#### 2. Convert Services to Deployments

Each service in Docker Compose typically translates to a Deployment in Kubernetes. A Deployment manages the lifecycle of your application's Pods.  
* **image**: Directly maps to spec.template.spec.containers[].image.  
* **container_name**: Not directly mapped; Kubernetes uses auto-generated Pod names. You can use labels for identification.  
* **restart**: Kubernetes Deployments inherently handle restarts. Always is the default restart policy for Pods managed by a Deployment.

**Kubernetes Deployment Example (webapp-deployment.yaml):**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp-deployment
  labels:
    app: webapp
spec:
  replicas: 1 # Start with 1 replica, scale as needed
  selector:
    matchLabels:
      app: webapp
  template:
    metadata:
      labels:
        app: webapp
    spec:
      containers:
        - name: webapp
          image: my-node-app:1.0 # From Docker Compose 'image'
          ports:
            - containerPort: 3000 # The internal port the app listens on
          envFrom: # Referencing ConfigMap and Secret for environment variables
            - configMapRef:
                name: webapp-config
            - secretRef:
                name: webapp-secret
          volumeMounts:
            - name: app-data-storage
              mountPath: /usr/src/app/data # From Docker Compose 'volumes'
      volumes:
        - name: app-data-storage
          persistentVolumeClaim:
            claimName: app-data-pvc # Link to PVC for persistent storage
```

#### 3. Convert Ports to Services

Docker Compose's ports mapping ("80:3000") exposes a container port to the host. In Kubernetes, this is handled by a Service. A Service provides a stable IP address and DNS name for a set of Pods.  
* **targetPort**: The port on the Pod/container that the service sends traffic to (e.g., 3000 for webapp).  
* **port**: The port on the Service itself (e.g., 80).  
* **protocol**: TCP (default) or UDP.  
* **type**:  
  * ClusterIP (default): Internal only, accessible within the cluster.  
  * NodePort: Exposes the service on a static port on each Node's IP. Good for testing.  
  * LoadBalancer: Exposes the service externally using a cloud provider's load balancer.  
  * ExternalName: Maps the service to a DNS name.

**Kubernetes Service Example (webapp-service.yaml):**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: webapp-service
spec:
  selector:
    app: webapp # Selects Pods with label 'app: webapp'
  ports:
    - protocol: TCP
      port: 80 # Service port
      targetPort: 3000 # Container port
  type: ClusterIP # Or NodePort/LoadBalancer for external access
```

**Kubernetes Service Example (database-service.yaml):**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: database # This name becomes the DNS name for the database
spec:
  selector:
    app: database
  ports:
    - protocol: TCP
      port: 5432 # Default PostgreSQL port
      targetPort: 5432
  type: ClusterIP # Database typically only needs internal access
```

#### 4. Handle Volumes (PersistentVolumeClaim)

Docker Compose volumes can be named volumes or host-path mounts. In Kubernetes, you'll typically use PersistentVolumeClaims (PVCs) for persistent storage.  
* **Named Volumes (e.g., db-data):** Translate to PersistentVolumeClaim (PVC) and a corresponding PersistentVolume (PV) if dynamic provisioning is not configured. PVCs request storage, and the cluster provisions it (e.g., from a StorageClass).  
* **Host-Path Mounts (e.g., ./app-data):** These are generally discouraged in production Kubernetes as they tie Pods to specific nodes. For development, hostPath volumes can be used, but for production, consider redesigning your application to use proper persistent storage or object storage.

**Kubernetes PersistentVolumeClaim Example (db-data-pvc.yaml):**

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: db-data-pvc
spec:
  accessModes:
    - ReadWriteOnce # Can be mounted as read-write by a single node
  resources:
    requests:
      storage: 1Gi # Request 1 Gigabyte of storage
  # storageClassName: standard # Optional: if you have a specific StorageClass
```

**Kubernetes PersistentVolumeClaim Example (app-data-pvc.yaml):**

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: app-data-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Mi # Request 100 Megabytes for app data
```

Then, link the PVCs to your Deployment's Pods using volumes and volumeMounts (as shown in Step 2 of the Deployment example).

#### 5. Handle Environment Variables (ConfigMaps & Secrets)

Docker Compose environment variables can be converted to ConfigMaps for non-sensitive data and Secrets for sensitive data.  
* **ConfigMap**: For NODE_ENV, DB_HOST, POSTGRES_DB, POSTGRES_USER.  
* **Secret**: For API_KEY, POSTGRES_PASSWORD.

**Kubernetes ConfigMap Example (webapp-config.yaml):**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: webapp-config
data:
  NODE_ENV: production
  DB_HOST: database # Use the Kubernetes Service name for inter-service communication
```

**Kubernetes Secret Example (webapp-secret.yaml):**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: webapp-secret
type: Opaque
data:
  # Base64 encoded values: echo -n "mysecretkey" | base64
  API_KEY: bXlzZWNyZXRrZXk=
```

**Kubernetes Secret Example (database-secret.yaml):**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: database-secret
type: Opaque
data:
  # Base64 encoded values: echo -n "password" | base64
  POSTGRES_PASSWORD: cGFzc3dvcmQ=
```

Then, reference these ConfigMaps and Secrets in your Deployment using envFrom (as shown in Step 2 of the Deployment example).

#### 6. Networking

Docker Compose networks are handled by Kubernetes' internal DNS and Service discovery. When a Service is created, it gets a DNS name (e.g., database for the database service). Containers in other Pods can simply use this DNS name to communicate.  
* **depends_on**: In Docker Compose, this ensures services start in order. In Kubernetes, this is generally not needed for service-to-service communication. Instead, use readinessProbes (see Step 8) to ensure a service is ready before traffic is routed to it.  

#### 7. Ingress (Optional but Recommended for External Access)

If your Docker Compose application was exposed directly on host ports (e.g., 80:3000), and you want to expose it externally in Kubernetes, an Ingress resource is the standard way. An Ingress acts as a layer 7 load balancer, routing external HTTP/HTTPS traffic to internal Services.  
You'll need an Ingress Controller (e.g., Nginx Ingress Controller, Traefik) deployed in your cluster for Ingress resources to work.  

**Kubernetes Ingress Example (webapp-ingress.yaml):**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: webapp-ingress
  annotations:
    # Example annotation for Nginx Ingress Controller
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
    - host: myapp.example.com # Your domain name
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: webapp-service # Name of your webapp Service
                port:
                  number: 80 # Port of the webapp Service
```

#### 8. Liveness and Readiness Probes

Kubernetes can automatically check the health of your containers.  
* **livenessProbe**: Determines if a container is still running. If it fails, Kubernetes restarts the container.  
* **readinessProbe**: Determines if a container is ready to serve traffic. If it fails, the Pod is removed from Service endpoints until it becomes ready.

Add these to your Deployment's container specification.

**Example Liveness/Readiness Probes (in webapp-deployment.yaml):**

```yaml
# ... inside containers: - name: webapp
          livenessProbe:
            httpGet:
              path: /healthz # An endpoint in your app that returns 200 OK
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready # An endpoint in your app that returns 200 OK when ready
              port: 3000
            initialDelaySeconds: 10
            periodSeconds: 15
            timeoutSeconds: 5
```

#### 9. Resource Limits and Requests

Define resource requests and limits for your containers to ensure fair resource allocation and prevent resource exhaustion.  
* **requests**: The minimum resources a container needs. Kubernetes schedules Pods based on requests.  
* **limits**: The maximum resources a container can consume. If a container exceeds its limit, it might be throttled or killed.

**Example Resource Limits/Requests (in webapp-deployment.yaml):**

```yaml
# ... inside containers: - name: webapp
          resources:
            requests:
              memory: "64Mi"
              cpu: "250m" # 0.25 CPU core
            limits:
              memory: "128Mi"
              cpu: "500m" # 0.5 CPU core
```

#### 10. Testing and Debugging

1. **Apply YAMLs:** Apply your Kubernetes YAML files in the correct order (Secrets, ConfigMaps, PVCs, Deployments, Services, Ingress).

```bash
kubectl apply -f webapp-config.yaml
kubectl apply -f webapp-secret.yaml
kubectl apply -f database-config.yaml
kubectl apply -f database-secret.yaml
kubectl apply -f db-data-pvc.yaml
kubectl apply -f app-data-pvc.yaml
kubectl apply -f database-deployment.yaml
kubectl apply -f webapp-deployment.yaml
kubectl apply -f database-service.yaml
kubectl apply -f webapp-service.yaml
kubectl apply -f webapp-ingress.yaml # If using Ingress
```

2. **Check Status:**

```bash
kubectl get pods
kubectl get deployments
kubectl get services
kubectl get pvc
kubectl get ingress # If using Ingress
```

3. **Inspect Logs:**

```bash
kubectl logs <pod-name>
```

4. **Describe Resources:** Get detailed information about a resource.

```bash
kubectl describe pod <pod-name>
kubectl describe deployment <deployment-name>
kubectl describe service <service-name>
```

5. **Port Forward (for local testing):**

```bash
kubectl port-forward service/webapp-service 8080:80 # For ClusterIP service
```

:::tip
Create a shell script to automate the application of Kubernetes resources in the correct order to simplify the deployment process.
:::
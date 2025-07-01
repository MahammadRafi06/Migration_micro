# Part 3: Deployment & Manual Creation

## Navigation

- [Part 1: Setup & Prerequisites](#part1)
- [Part 2: Converting with Kompose](#part2)
- **Part 3: Deployment & Manual Creation** (Current)
- [Part 4: Advanced Considerations & Cleanup](#part4)

---

## **5. Deploy to Minikube**

Once your Kubernetes manifests are ready and reviewed, you can deploy them to your Minikube cluster.

### **5.1. Apply Kubernetes Manifests**

Deploy all the generated (or manually created) Kubernetes artifacts to your Minikube cluster:

```bash
# Apply all YAML manifests in the current directory
kubectl apply -f .
```

You will see output indicating that each resource has been created or configured.

### **5.2. Verify Services**

After applying the manifests, verify that your Kubernetes services and pods are running correctly:

```bash
# List all services
kubectl get svc

# List all pods
kubectl get pods

# List all deployments
kubectl get deployments
```

Example service output:

```
NAME         TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)          AGE
app          NodePort    10.111.5.104   <none>        5000:31380/TCP   95s
db           ClusterIP   10.96.144.49   <none>        5432/TCP         95s
kubernetes   ClusterIP   10.96.0.1      <none>        443/TCP          3h3m
```

Note the NodePort assigned to your app service (e.g., 31380). This is the port on the Minikube VM that will forward traffic to your application.

### **5.3. Access the Application**

Since Minikube runs in a VM (or Docker container), you need to identify the Minikube VM's IP address to access the application from your host machine:

```bash
# Get Minikube IP
minikube ip
```

Example output:

```
192.168.49.2
```

Access the application using the Minikube IP and the NodePort identified earlier:

```bash
curl 192.168.49.2:31380
```

You should see the HTML content of your application, indicating successful deployment and external access.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>User List</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      max-width: 800px;
      margin: 0 auto;
      padding: 20px;
    }
    h1 {
      color: #333;
      border-bottom: 2px solid #eee;
      padding-bottom: 10px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 20px;
    }
    /* ... more styles ... */
  </style>
</head>
<body>
  <!-- ... application content ... -->
</body>
</html>
```

## **6. Manual Kubernetes Manifest Creation**

Understanding the underlying Kubernetes objects is fundamental, even when using automation tools like Kompose. This section details how to manually construct the necessary Kubernetes manifests.

### **6.1. Identify Required Kubernetes Objects**

When migrating a Docker Compose application to Kubernetes, each service and its dependencies (like volumes and environment variables) need to be translated into specific Kubernetes API objects:

- **Deployments**: Define and manage application pods.
- **Services**: Enable networking and service discovery.
- **Secrets**: Store sensitive configuration data.
- **ConfigMaps**: Store non-sensitive config data.
- **PersistentVolumeClaim (PVC)**: Request for storage.
- **PersistentVolume (PV)**: The actual backing storage.

### **6.2. Example Manifests**

Below are examples of the Kubernetes manifest files. Each should be saved as a separate `.yaml` file (e.g., `userapp-deployment.yaml`, `postgres-secret.yaml`).

#### **6.2.1. User Application Deployment (userapp-deployment.yaml)**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: userapp-deployment
  labels:
    app: userapp
spec:
  replicas: 2
  selector:
    matchLabels:
      app: userapp
  template:
    metadata:
      labels:
        app: userapp
    spec:
      containers:
        - name: userapp
          image: userapp:1.1.2
          ports:
            - containerPort: 5000
          env:
            - name: POSTGRES_DB
              value: mydatabase
            - name: POSTGRES_USER
              value: myuser
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: POSTGRES_PASSWORD
```

#### **6.2.2. PostgreSQL Secret (postgres-secret.yaml)**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
type: Opaque
stringData:
  POSTGRES_PASSWORD: your_strong_password
```

#### **6.2.3. PostgreSQL ConfigMap (postgres-config.yaml)**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: postgres-config
data:
  postgresql.conf: |
    max_connections = 100
    shared_buffers = 128MB
    # Add more PostgreSQL settings here
```

#### **6.2.4. PostgreSQL PersistentVolumeClaims (PVC)**

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-data-0
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-data-1
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
```

#### **6.2.5. PostgreSQL Deployment (postgres-deployment.yaml)**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres-deployment
  labels:
    app: postgres
spec:
  replicas: 2
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:16
          ports:
            - containerPort: 5432
          env:
            - name: POSTGRES_DB
              value: mydatabase
            - name: POSTGRES_USER
              value: myuser
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: POSTGRES_PASSWORD
          volumeMounts:
            - name: postgres-persistent-storage-0
              mountPath: /var/lib/postgresql/data
              subPath: data
            - name: postgres-config-volume
              mountPath: /etc/postgresql/postgresql.conf
              subPath: postgresql.conf
          resources:
            requests:
              cpu: "250m"
              memory: "512Mi"
            limits:
              cpu: "500m"
              memory: "1Gi"
      volumes:
        - name: postgres-persistent-storage-0
          persistentVolumeClaim:
            claimName: postgres-data-0
        - name: postgres-config-volume
          configMap:
            name: postgres-config
```

#### **6.2.6. PostgreSQL Service (postgres-service.yaml)**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
spec:
  selector:
    app: postgres
  ports:
    - protocol: TCP
      port: 5432
      targetPort: 5432
  type: ClusterIP
```

---

## Navigation

- [Part 1: Setup & Prerequisites](#part1)
- [Part 2: Converting with Kompose](#part2)
- **Part 3: Deployment & Manual Creation** (Current)
- [Part 4: Advanced Considerations & Cleanup](#part4)

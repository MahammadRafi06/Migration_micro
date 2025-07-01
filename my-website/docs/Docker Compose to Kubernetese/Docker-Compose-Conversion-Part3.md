# **Converting Docker Compose to Kubernetes YAML - Part 3: Deployment & Manual Creation**

## Navigation
- [Part 1: Setup & Prerequisites](#part1)
- [Part 2: Converting with Kompose](#part2)
- **Part 3: Deployment & Manual Creation** (Current)
- [Part 4: Advanced Considerations & Cleanup](#part4)

---

## **5. Deploy to Minikube**

Once your Kubernetes manifests are ready and reviewed, you can deploy them to your Minikube cluster.

### **5.1. Apply Kubernetes Manifests**

Deploy all the generated (or manually created) Kubernetes artifacts to your Minikube cluster.

| kubectl apply \-f .\# Explanation: This command reads all YAML files in the current directory and applies them to the Kubernetes cluster. 'kubectl' communicates with the Kubernetes API server to create or update the defined resources (Deployments, Services, etc.). |
| :---- |

You will see output indicating that each resource has been created or configured.

### **5.2. Verify Services**

After applying the manifests, verify that your Kubernetes services and pods are running correctly.

| kubectl get svc\# Explanation: Lists all services running in the current Kubernetes namespace. This allows you to see the names, types, cluster IPs, and ports of your deployed services. |
| :---- |

Example output:

| NAME         TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)          AGEapp          NodePort    10.111.5.104   \<none\>        5000:31380/TCP   95sdb           ClusterIP   10.96.144.49   \<none\>        5432/TCP         95skubernetes   ClusterIP   10.96.0.1      \<none\>        443/TCP          3h3m |
| :---- |

Note the NodePort assigned to your app service (e.g., 31380). This is the port on the Minikube VM that will forward traffic to your application.

Additionally, check the status of your pods and deployments:

| kubectl get pods\# Explanation: Lists all pods and their current status (e.g., Running, Pending, Error).kubectl get deployments\# Explanation: Lists all deployments and their status (e.g., desired vs. current replicas). |
| :---- |

### **5.3. Access the Application**

Since Minikube runs in a VM (or Docker container), you need to identify the Minikube VM's IP address to access the application from your host machine.

| minikube ip\# Explanation: Retrieves the IP address of the Minikube virtual machine or Docker container. This IP is required to access services exposed via NodePort. |
| :---- |

Example output:

| 192.168.49.2 |
| :---- |

Access the application using the Minikube IP and the NodePort identified earlier (e.g., 31380):

| curl 192.168.49.2:31380\# Explanation: Uses the 'curl' command-line tool to make an HTTP request to your application's service running on Minikube. |
| :---- |

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

## **6. Manual Kubernetes Manifest Creation**

Understanding the underlying Kubernetes objects is fundamental, even when using automation tools like Kompose. This section details how to manually construct the necessary Kubernetes manifests.

### **6.1. Identify Required Kubernetes Objects**

When migrating a Docker Compose application to Kubernetes, each service and its dependencies (like volumes and environment variables) need to be translated into specific Kubernetes API objects. For an application with a web service and a PostgreSQL database, the following Kubernetes objects are typically needed:

* Deployments:
  * Purpose: Manages a set of identical pods, ensuring a specified number of replicas are running at all times. It handles rolling updates, rollbacks, and self-healing.
  * Relation to Docker Compose: Corresponds to the services defined in your docker-compose.yaml (e.g., app and db). Each service will typically become a Deployment.
  * Objects Needed:
    * One for the application (e.g., userapp-deployment).
    * One for PostgreSQL (e.g., postgres-deployment).
* Services:
  * Purpose: An abstract way to expose an application running on a set of pods as a network service. Services enable communication between different parts of your application and expose your application to external users.
  * Relation to Docker Compose: Maps to the exposed ports and network configurations of your Docker Compose services.
  * Objects Needed:
    * One for the application (to expose it to users).
    * One for PostgreSQL (to allow the application to connect to the database internally).
* Secrets:
  * Purpose: Used to store sensitive information, such as passwords, OAuth tokens, and SSH keys. Secrets are base64 encoded by default but are not encrypted at rest without additional configuration.
  * Relation to Docker Compose: Replaces environment variables used for sensitive data in **docker-compose**.yaml.
  * Objects Needed:
    * One for PostgreSQL secrets (e.g., postgres-secret) to store the database password.
* ConfigMaps:
  * Purpose: Used to store non-sensitive configuration data in key-value pairs. They allow you to decouple configuration from your application code.
  * Relation to Docker Compose: Can replace environment variables or mounted configuration files for non-sensitive data.
  * Objects Needed:
    * One for PostgreSQL configuration (e.g., postgres-config) for database-specific settings.
* PersistentVolumeClaim (PVC):
  * Purpose: A request for storage by a user. It's a way for users to consume abstract storage resources provided by administrators.
  * Relation to Docker Compose: Corresponds to named volumes used for data persistence (e.g., for the database).
  * Objects Needed:
    * One or more for PostgreSQL data (e.g., **postgres**\-**data**\-0, postgres-**data**\-1) to ensure data persists even if the database pod restarts or is rescheduled.
* PersistentVolume (PV):
  * Purpose: A piece of storage in the cluster that has been provisioned by an administrator or dynamically provisioned using Storage Classes. It's a cluster resource, not tied to any specific namespace.
  * Relation to Docker Compose: The actual storage backend for the named volumes. While not explicitly created manually here, a PV is required to provision the storage claimed by the PVC. Minikube often handles dynamic provisioning of PVs (e.g., using its default storage class).

### **6.2. Example Manifests**

Below are examples of the Kubernetes manifest files. Each should be saved as a separate .yaml file (e.g., **userapp-deployment**.yaml, **postgres-secret**.yaml, etc.) in your project directory.

#### **6.2.1. User Application Deployment (userapp-deployment.yaml)**

This manifest defines how your application's pods will be deployed and managed.

| apiVersion: apps/v1kind: Deploymentmetadata:  name: userapp-deployment \# Unique name for this deployment  labels:    app: userapp          \# Labels used for selecting pods and servicesspec:  replicas: 2             \# Desired number of application replicas for high availability  selector:    matchLabels:      app: userapp        \# Selector to identify pods managed by this deployment  template:    metadata:      labels:        app: userapp      \# Labels applied to the pods created by this deployment    spec:      containers:      \- name: userapp     \# Name of the container within the pod        image: userapp:1.1.2 \# Replace with your actual application image and tag. Ensure this image is available in your Minikube environment or a configured registry.        ports:        \- containerPort: 5000 \# The port your Flask application listens on inside the container        env:        \- name: POSTGRES\_DB          value: mydatabase        \- name: POSTGRES\_USER          value: myuser        \- name: POSTGRES\_PASSWORD          valueFrom:            secretKeyRef:              name: postgres-secret \# Refers to the Secret object named 'postgres-secret'              key: POSTGRES\_PASSWORD \# Specifies the key within the Secret to use for the password |
| :---- |

#### **6.2.2. PostgreSQL Secret (postgres-secret.yaml)**

This manifest securely stores the PostgreSQL database password.

| apiVersion: v1kind: Secretmetadata:  name: postgres-secret \# Unique name for the secrettype: Opaque \# Indicates the secret data is opaque (arbitrary user-defined data)stringData:  POSTGRES\_PASSWORD: your\_strong\_password \# CHANGE THIS TO A SECURE, UNIQUE PASSWORD\! This field allows you to specify string values directly, which Kubernetes will then base64 encode. |
| :---- |

#### **6.2.3. PostgreSQL ConfigMap (postgres-config.yaml) (Optional)**

This manifest stores non-sensitive configuration for PostgreSQL.

| apiVersion: v1kind: ConfigMapmetadata:  name: postgres-config \# Unique name for the ConfigMapdata:  \# Example configuration, customize as needed. This data will be mounted as a file or exposed as environment variables.  postgresql.conf: |    max\_connections \= 100    shared\_buffers \= 128MB    \# Add more PostgreSQL settings here, formatted as a multi-line string. |
| :---- |

#### **6.2.4. PostgreSQL PersistentVolumeClaim (PVC) (postgres-pvc.yaml)**

These manifests request persistent storage for the PostgreSQL database, ensuring data is not lost if pods are restarted or moved.

| apiVersion: v1kind: PersistentVolumeClaimmetadata:  name: postgres-data-0 \# Unique name for the first PVCspec:  accessModes:    \- ReadWriteOnce \# Specifies that the volume can be mounted as read-write by a single node  resources:    requests:      storage: 5Gi \# Requests 5 Gigabytes of storage. Adjust size as needed.\---apiVersion: v1kind: PersistentVolumeClaimmetadata:  name: postgres-data-1 \# Unique name for the second PVC (if multiple replicas need separate storage)spec:  accessModes:    \- ReadWriteOnce  resources:    requests:      storage: 5Gi \# Requests 5 Gigabytes of storage. |
| :---- |

#### **6.2.5. PostgreSQL Deployment (postgres-deployment.yaml)**

This manifest defines how your PostgreSQL database pods will be deployed and managed.

| apiVersion: apps/v1kind: Deploymentmetadata:  name: postgres-deployment \# Unique name for this deployment  labels:    app: postgres          \# Labels for selecting podsspec:  replicas: 2              \# Desired number of PostgreSQL replicas for high availability (requires separate PVCs for each replica if ReadWriteOnce)  selector:    matchLabels:      app: postgres        \# Selector to identify pods managed by this deployment  template:    metadata:      labels:        app: postgres      \# Labels applied to the pods    spec:      containers:      \- name: postgres     \# Name of the container        image: postgres:16 \# Use a specific, stable version of PostgreSQL (e.g., postgres:16)        ports:        \- containerPort: 5432 \# Default PostgreSQL port        env:        \- name: POSTGRES\_DB          value: mydatabase        \- name: POSTGRES\_USER          value: myuser        \- name: POSTGRES\_PASSWORD          valueFrom:            secretKeyRef:              name: postgres-secret \# Refers to the Secret for the password              key: POSTGRES\_PASSWORD        volumeMounts:        \- name: postgres-persistent-storage-0 \# Name of the volume mount, matching a volume defined below          mountPath: /var/lib/postgresql/data \# Default PostgreSQL data directory inside the container          subPath: data \# Specifies a subdirectory within the volume to mount        \- name: postgres-config-volume \# Mount for the ConfigMap          mountPath: /etc/postgresql/postgresql.conf \# Path where the config file will be mounted          subPath: postgresql.conf \# Specifies the key from the ConfigMap to mount as a file        resources: \# Resource limits are crucial for production environments to prevent resource exhaustion          requests:            cpu: "250m" \# Requests 250 milli-cores (0.25 CPU core)            memory: "512Mi" \# Requests 512 MiB of memory          limits:            cpu: "500m" \# Limits CPU usage to 500 milli-cores (0.5 CPU core)            memory: "1Gi" \# Limits memory usage to 1 GiB      volumes:      \- name: postgres-persistent-storage-0 \# Defines a volume named 'postgres-persistent-storage-0'        persistentVolumeClaim:          claimName: postgres-data-0 \# Links this volume to the PVC named 'postgres-data-0'      \- name: postgres-config-volume \# Defines a volume for the ConfigMap        configMap:          name: postgres-config \# Links this volume to the ConfigMap named 'postgres-config' |
| :---- |

#### **6.2.6. PostgreSQL Service (postgres-service.yaml)**

This manifest exposes the PostgreSQL database internally within the cluster, allowing your application to connect to it.

| apiVersion: v1kind: Servicemetadata:  name: postgres-service \# Unique name for the servicespec:  selector:    app: postgres \# Selects pods with the label 'app: postgres' to route traffic to  ports:    \- protocol: TCP      port: 5432 \# The port on which the service will listen      targetPort: 5432 \# The port on the pods to which the service will forward traffic  type: ClusterIP \# Use ClusterIP for internal cluster access only. This service is not exposed outside the cluster. |
| :---- |

---

## Navigation
- [Part 1: Setup & Prerequisites](#part1)
- [Part 2: Converting with Kompose](#part2)
- **Part 3: Deployment & Manual Creation** (Current)
- [Part 4: Advanced Considerations & Cleanup](#part4)
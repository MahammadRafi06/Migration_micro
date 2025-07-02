---
id: practical-examples-and-best-practices
title: Example Conversion and Best Practices
sidebar_label: "Example & Best Practices"
---

# Example Conversion and Best Practices

## Example Conversion: Docker Compose to Kubernetes

Let's convert the initial Docker Compose example fully using the manual approach, which forms the basis for any further packaging with Helm.

### Original docker-compose.yml

```yaml
# docker-compose.yml
version: '3.8'
services:
  webapp:
    image: my-node-app:1.0
    ports:
      - "80:3000"
    environment:
      - NODE_ENV=production
      - DB_HOST=database
      - API_KEY=mysecretkey
    volumes:
      - ./app-data:/usr/src/app/data
    depends_on:
      - database
    networks:
      - app-net
  database:
    image: postgres:13
    environment:
      - POSTGRES_DB=mydb
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - db-data:/var/lib/postgresql/data
    networks:
      - app-net
volumes:
  db-data:
  app-data:
networks:
  app-net:
```

### Corresponding Kubernetes YAML Files (Manual Conversion)

#### 1. webapp-config.yaml

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: webapp-config
data:
  NODE_ENV: production
  DB_HOST: database # Kubernetes service name for the database
```

#### 2. webapp-secret.yaml

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: webapp-secret
type: Opaque
data:
  API_KEY: bXlzZWNyZXRrZXk= # base64 encoded "mysecretkey"
```

#### 3. database-config.yaml

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: database-config
data:
  POSTGRES_DB: mydb
  POSTGRES_USER: user
```

#### 4. database-secret.yaml

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: database-secret
type: Opaque
data:
  POSTGRES_PASSWORD: cGFzc3dvcmQ= # base64 encoded "password"
```

#### 5. db-data-pvc.yaml

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: db-data-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

#### 6. app-data-pvc.yaml

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
      storage: 100Mi
```

#### 7. database-deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: database-deployment
  labels:
    app: database
spec:
  replicas: 1
  selector:
    matchLabels:
      app: database
  template:
    metadata:
      labels:
        app: database
    spec:
      containers:
        - name: postgres
          image: postgres:13
          ports:
            - containerPort: 5432
          envFrom:
            - configMapRef:
                name: database-config
            - secretRef:
                name: database-secret
          volumeMounts:
            - name: db-data-storage
              mountPath: /var/lib/postgresql/data
          livenessProbe: # Basic probe for database
            tcpSocket:
              port: 5432
            initialDelaySeconds: 15
            periodSeconds: 20
          readinessProbe: # Basic probe for database
            tcpSocket:
              port: 5432
            initialDelaySeconds: 20
            periodSeconds: 20
      volumes:
        - name: db-data-storage
          persistentVolumeClaim:
            claimName: db-data-pvc
```

#### 8. webapp-deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp-deployment
  labels:
    app: webapp
spec:
  replicas: 1
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
          image: my-node-app:1.0
          ports:
            - containerPort: 3000
          envFrom:
            - configMapRef:
                name: webapp-config
            - secretRef:
                name: webapp-secret
          volumeMounts:
            - name: app-data-storage
              mountPath: /usr/src/app/data
          livenessProbe:
            httpGet:
              path: /healthz
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 3000
            initialDelaySeconds: 10
            periodSeconds: 15
            timeoutSeconds: 5
          resources:
            requests:
              memory: "64Mi"
              cpu: "250m"
            limits:
              memory: "128Mi"
              cpu: "500m"
      volumes:
        - name: app-data-storage
          persistentVolumeClaim:
            claimName: app-data-pvc
```

#### 9. database-service.yaml

```yaml
apiVersion: v1
kind: Service
metadata:
  name: database # This name is used by webapp to connect
spec:
  selector:
    app: database
  ports:
    - protocol: TCP
      port: 5432
      targetPort: 5432
  type: ClusterIP
```

#### 10. webapp-service.yaml

```yaml
apiVersion: v1
kind: Service
metadata:
  name: webapp-service
spec:
  selector:
    app: webapp
  ports:
    - protocol: TCP
      port: 80
      targetPort: 3000
  type: ClusterIP # Or NodePort/LoadBalancer for external access
```

## Best Practices and Considerations

### Organization and Maintenance

* **Separate YAML Files:** Keep related resources in separate files (e.g., deployment.yaml, service.yaml, pvc.yaml). This improves readability and manageability.  
* **Namespace:** Consider using Kubernetes Namespaces to logically isolate your application's resources within the cluster.
* **Kustomize:** Use Kustomize (built into kubectl) for environment-specific customizations without duplicating YAMLs.
* **CI/CD Integration:** Integrate your Kubernetes deployments into your CI/CD pipeline for automated testing and deployment.

:::tip
Consider organizing your Kubernetes manifests in a Git repository with separate directories for different components or environments.
```
kubernetes/
├── base/            # Common configurations
├── overlays/        # Environment-specific overlays (for Kustomize)
│   ├── development/
│   ├── staging/
│   └── production/
└── charts/          # Helm charts (if using Helm)
```
:::

### Resource Management

* **Resource Requests and Limits:** Always define resource requests and limits for your containers to ensure fair resource allocation and prevent resource exhaustion.
* **Horizontal Pod Autoscaler (HPA):** Configure HPA to automatically scale your deployments based on CPU utilization or other metrics.
* **Vertical Pod Autoscaler (VPA):** For automatically setting resource requests and limits.
* **StatefulSets:** For stateful applications (like databases) that require stable network identities and persistent storage across restarts, consider using StatefulSets instead of Deployments.

```yaml
# Example HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: webapp-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: webapp-deployment
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
```

### Reliability and Availability

* **Pod Disruption Budgets (PDB):** Define PDBs to ensure high availability during voluntary disruptions.
* **Anti-Affinity Rules:** Distribute Pods across nodes to improve fault tolerance.
* **Topology Spread Constraints:** Ensure Pods are distributed across failure domains.

```yaml
# Example Pod Disruption Budget
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: webapp-pdb
spec:
  minAvailable: 1  # Or use maxUnavailable
  selector:
    matchLabels:
      app: webapp
```

### Security

* **Use Secrets for sensitive data** and avoid hardcoding credentials.
* **Implement Role-Based Access Control (RBAC)** to restrict access to Kubernetes resources.
* **Scan your Docker images for vulnerabilities** using tools like Trivy, Clair, or Snyk.
* **Consider Pod Security Standards (PSS)** or Network Policies for enhanced security.
* **Limit container capabilities** and run as non-root when possible.

```yaml
# Example Network Policy to restrict database access
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: db-network-policy
spec:
  podSelector:
    matchLabels:
      app: database
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: webapp
    ports:
    - protocol: TCP
      port: 5432
```

### Monitoring and Logging

* **Implement robust monitoring** (e.g., Prometheus, Grafana) for your Kubernetes applications.
* **Set up centralized logging** (e.g., ELK stack, Fluentd) to collect and analyze logs.
* **Add ServiceMonitors** (if using Prometheus Operator) to automatically discover and scrape metrics.
* **Create dashboards and alerts** for key application metrics.

### Advanced Deployment Strategies

* **Rolling Updates:** The default Kubernetes deployment strategy.
* **Blue/Green Deployments:** Run two identical environments and switch traffic.
* **Canary Deployments:** Gradually route traffic to a new version.
* **Feature Flags:** Use application-level feature flags for safer deployments.

```yaml
# Example Deployment with Rolling Update Strategy
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp-deployment
spec:
  # ... other fields
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
```

## Conclusion

Converting Docker Compose configurations to Kubernetes manifests is a crucial step for deploying applications at scale. While tools like kompose and podman generate kube can provide a quick start, manual refinement and adherence to Kubernetes best practices are essential for production-grade deployments. 

Furthermore, leveraging Helm for packaging and, in advanced scenarios, Kubernetes Operators for complex application management, can significantly enhance your Kubernetes adoption journey. By understanding these various strategies, you can choose the right approach for your application's needs and effectively migrate to a Kubernetes-native environment.

Remember that this process often involves an iterative approach:

1. Start with a basic conversion
2. Test in a non-production environment
3. Refine based on testing results
4. Add advanced features (probes, resource limits, etc.)
5. Implement best practices (security, monitoring, etc.)
6. Consider packaging options (Helm, Operators) for more complex deployments

With careful planning and following the guidelines in this documentation, you can successfully migrate your Docker Compose applications to Kubernetes while ensuring they are robust, scalable, and maintainable.
# Kubernetes Manifests for AEP

Learn how to create effective Kubernetes manifests specifically optimized for Armada Edge Platform deployments.

## Overview

Kubernetes manifests define how your applications run on the AEP infrastructure. This guide covers best practices for creating manifests that work efficiently in edge environments.

## Deployment Manifests

### Basic Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  namespace: production
  labels:
    app: myapp
    version: v1.0.0
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
        version: v1.0.0
    spec:
      containers:
      - name: myapp
        image: myregistry/myapp:v1.0.0
        ports:
        - containerPort: 3000
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Edge-Optimized Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: edge-app
  labels:
    app: edge-app
    tier: edge
spec:
  replicas: 2
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  selector:
    matchLabels:
      app: edge-app
  template:
    metadata:
      labels:
        app: edge-app
        tier: edge
    spec:
      # Node selection for edge locations
      nodeSelector:
        node-type: edge
      # Tolerate edge-specific taints
      tolerations:
      - key: "edge-node"
        operator: "Equal"
        value: "true"
        effect: "NoSchedule"
      containers:
      - name: edge-app
        image: myregistry/edge-app:latest
        imagePullPolicy: IfNotPresent
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "100m"
        # Edge-specific environment variables
        env:
        - name: EDGE_LOCATION
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName
        - name: DEPLOYMENT_MODE
          value: "edge"
```

## Service Manifests

### ClusterIP Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-service
  labels:
    app: myapp
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 3000
    protocol: TCP
  selector:
    app: myapp
```

### LoadBalancer for Edge Exposure

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-external
  annotations:
    # AEP-specific load balancer configuration
    service.beta.kubernetes.io/do-loadbalancer-protocol: "http"
    service.beta.kubernetes.io/do-loadbalancer-healthcheck-path: "/health"
spec:
  type: LoadBalancer
  ports:
  - port: 443
    targetPort: 3000
    protocol: TCP
  selector:
    app: myapp
```

## ConfigMap and Secrets

### ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: myapp-config
data:
  app.properties: |
    debug=false
    max_connections=100
    timeout=30s
  nginx.conf: |
    server {
        listen 80;
        location / {
            proxy_pass http://localhost:3000;
        }
    }
```

### Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: myapp-secrets
type: Opaque
data:
  # Base64 encoded values
  database-url: bW9uZ29kYjovL2xvY2FsaG9zdDoyNzAxNy9teWRi
  api-key: YWJjZGVmZ2hpams=
```

## Health Checks and Probes

### Comprehensive Health Checks

```yaml
spec:
  containers:
  - name: myapp
    image: myapp:latest
    # Liveness probe - restart if unhealthy
    livenessProbe:
      httpGet:
        path: /health/live
        port: 3000
      initialDelaySeconds: 60
      periodSeconds: 30
      timeoutSeconds: 5
      failureThreshold: 3
    # Readiness probe - remove from service if not ready
    readinessProbe:
      httpGet:
        path: /health/ready
        port: 3000
      initialDelaySeconds: 10
      periodSeconds: 10
      timeoutSeconds: 3
      failureThreshold: 3
    # Startup probe - for slow-starting applications
    startupProbe:
      httpGet:
        path: /health/startup
        port: 3000
      initialDelaySeconds: 10
      periodSeconds: 10
      timeoutSeconds: 3
      failureThreshold: 30
```

## Resource Management

### Resource Quotas

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: edge-quota
  namespace: production
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    persistentvolumeclaims: "4"
```

### Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## Security Configurations

### Pod Security Context

```yaml
spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
        runAsGroup: 1001
        fsGroup: 1001
      containers:
      - name: myapp
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
        volumeMounts:
        - name: tmp
          mountPath: /tmp
      volumes:
      - name: tmp
        emptyDir: {}
```

### Network Policy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: myapp-netpol
spec:
  podSelector:
    matchLabels:
      app: myapp
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          role: frontend
    ports:
    - protocol: TCP
      port: 3000
  egress:
  - to:
    - podSelector:
        matchLabels:
          role: database
    ports:
    - protocol: TCP
      port: 5432
```

## Edge-Specific Configurations

### Node Affinity for Edge Deployment

```yaml
spec:
  template:
    spec:
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: node-type
                operator: In
                values:
                - edge
                - edge-premium
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            preference:
              matchExpressions:
              - key: location
                operator: In
                values:
                - west-coast
                - east-coast
```

### Pod Disruption Budget

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: myapp-pdb
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: myapp
```

## Manifest Validation

### Using kubeval

```bash
# Install kubeval
curl -L https://github.com/instrumenta/kubeval/releases/latest/download/kubeval-linux-amd64.tar.gz | tar xz
sudo cp kubeval /usr/local/bin

# Validate manifests
kubeval deployment.yaml
```

### Using kubectl dry-run

```bash
# Validate without applying
kubectl apply -f deployment.yaml --dry-run=client -o yaml
```

## Testing Manifests

### Local Testing with kind

```bash
# Create local cluster
kind create cluster --name test

# Apply manifests
kubectl apply -f .

# Test functionality
kubectl port-forward svc/myapp-service 8080:80
```

## Complete Example

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  labels:
    app: web-app
    tier: frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
        tier: frontend
    spec:
      containers:
      - name: web-app
        image: nginx:1.21-alpine
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "100m"
        volumeMounts:
        - name: config
          mountPath: /etc/nginx/conf.d
      volumes:
      - name: config
        configMap:
          name: nginx-config
---
apiVersion: v1
kind: Service
metadata:
  name: web-app-service
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 80
  selector:
    app: web-app
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
data:
  default.conf: |
    server {
        listen 80;
        location / {
            return 200 'Hello from AEP!';
            add_header Content-Type text/plain;
        }
    }
```

## Next Steps

- [Helm Charts](./helm-charts.md) - Package your manifests for easy deployment
- [Configuration Management](./configuration-management.md) - Advanced configuration strategies
- [Security Considerations](./security-considerations.md) - Enhance security posture

---

:::tip Manifest Organization
Organize your manifests in a logical directory structure:
```
manifests/
├── base/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── configmap.yaml
├── overlays/
│   ├── staging/
│   └── production/
└── kustomization.yaml
```
::: 
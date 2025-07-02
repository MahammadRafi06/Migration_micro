---
id: blue-green-deployments
title: Blue-Green Deployment Strategies
sidebar_label: Blue-Green Deployments
description: Implement blue-green deployments for zero-downtime application updates
draft: true
---

# Blue-Green Deployment Strategies

Implement blue-green deployments to achieve zero-downtime application updates with instant rollback capabilities.

## Overview

Blue-green deployment is a strategy where you maintain two identical production environments (blue and green). At any time, only one serves live production traffic while the other is idle or serves as staging.

## Key Benefits

- **Zero Downtime**: Instant traffic switching.
- **Quick Rollback**: Immediate fallback to previous version.
- **Risk Reduction**: Test in production-like environment.
- **Complete Validation**: Full testing before traffic switch.

## Implementation Approaches

### 1. Service-Level Blue-Green

```yaml
# Blue deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-blue
  labels:
    app: myapp
    version: blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: blue
  template:
    metadata:
      labels:
        app: myapp
        version: blue
    spec:
      containers:
      - name: myapp
        image: myapp:v1.0.0
        ports:
        - containerPort: 8080
```

```yaml
# Green deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-green
  labels:
    app: myapp
    version: green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: green
  template:
    metadata:
      labels:
        app: myapp
        version: green
    spec:
      containers:
      - name: myapp
        image: myapp:v2.0.0
        ports:
        - containerPort: 8080
```

### 2. Traffic Switching Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-service
spec:
  selector:
    app: myapp
    version: blue  # Switch to 'green' for deployment
  ports:
  - port: 80
    targetPort: 8080
  type: LoadBalancer
```

### 3. Ingress-Based Blue-Green

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp-ingress
  annotations:
    nginx.ingress.kubernetes.io/canary: "false"
spec:
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: myapp-blue-service
            port:
              number: 80
```

## Automated Blue-Green with ArgoCD

### Application Definition
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp-blue-green
spec:
  source:
    repoURL: https://github.com/myorg/myapp-config
    path: blue-green
    targetRevision: HEAD
  destination:
    server: https://kubernetes.default.svc
    namespace: myapp
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

### Rollout Configuration
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: myapp-rollout
spec:
  replicas: 5
  strategy:
    blueGreen:
      activeService: myapp-active
      previewService: myapp-preview
      autoPromotionEnabled: false
      scaleDownDelaySeconds: 30
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myapp:latest
        ports:
        - containerPort: 8080
```

## Health Checks and Validation

### Readiness Probes
```yaml
readinessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 1
  successThreshold: 1
  failureThreshold: 3
```

### Pre-Production Testing
```bash
#!/bin/bash
# Test script for green environment

GREEN_URL="http://myapp-green-service/health"

# Health check
if curl -f $GREEN_URL; then
  echo "Health check passed"
else
  echo "Health check failed"
  exit 1
fi

# Load testing
hey -n 1000 -c 10 $GREEN_URL

# Integration tests
kubectl run test-pod --image=test-runner:latest --rm -it -- \
  pytest tests/integration/ --url=$GREEN_URL
```

## Traffic Switching Strategies

### Manual Switch
```bash
# Switch from blue to green
kubectl patch service myapp-service -p '{"spec":{"selector":{"version":"green"}}}'

# Verify traffic
kubectl get endpoints myapp-service
```

### Automated Switch with Flagger
```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: myapp
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  progressDeadlineSeconds: 60
  service:
    port: 80
    targetPort: 8080
  analysis:
    interval: 1m
    threshold: 5
    maxWeight: 100
    stepWeight: 100
    metrics:
    - name: request-success-rate
      threshold: 99
      interval: 1m
```

## Database Considerations

### Schema Compatibility
- Ensure backward compatibility during deployment.
- Use database migration strategies.
- Implement feature flags for breaking changes.

### Connection Management
```yaml
# Separate database connections for blue/green
apiVersion: v1
kind: ConfigMap
metadata:
  name: myapp-blue-config
data:
  database_url: "postgresql://blue-db:5432/myapp"
  
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: myapp-green-config
data:
  database_url: "postgresql://green-db:5432/myapp"
```

## Monitoring and Observability

### Metrics Collection
```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-blue-metrics
  labels:
    app: myapp
    version: blue
spec:
  selector:
    app: myapp
    version: blue
  ports:
  - port: 9090
    name: metrics
```

### Alert Configuration
```yaml
groups:
- name: blue-green-deployment
  rules:
  - alert: BlueGreenSwitchFailed
    expr: up{job="myapp-green"} == 0
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Green environment is down during blue-green switch"
```

## Best Practices

1. **Resource Planning**: Ensure sufficient resources for both environments.
2. **Data Synchronization**: Plan for data consistency between environments.
3. **Testing Automation**: Implement comprehensive automated testing.
4. **Monitoring**: Monitor both environments during switches.
5. **Rollback Planning**: Have clear rollback procedures.

## Troubleshooting

### Common Issues
- **Resource Constraints**: Insufficient cluster resources for both environments.
- **Service Discovery**: DNS caching causing traffic routing issues.
- **Data Inconsistency**: Database synchronization problems.

### Debug Commands
```bash
# Check deployment status
kubectl get deployments -l app=myapp
kubectl describe deployment myapp-blue
kubectl describe deployment myapp-green

# Verify service endpoints
kubectl get endpoints myapp-service
kubectl describe service myapp-service

# Check pod health
kubectl get pods -l app=myapp
kubectl logs -l app=myapp,version=green
```

## Next Steps

- [Canary Deployments](./canary-deployments.md).
- [Rolling Updates](./rolling-updates.md).
- [Rollback Procedures](./rollback-procedures.md). 
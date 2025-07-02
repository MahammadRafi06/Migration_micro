---
id: rolling-updates
title: Rolling Update Strategies
sidebar_label: Rolling Updates
description: Implement rolling updates for seamless application deployments with minimal downtime
draft: true
---

# Rolling Update Strategies

Implement rolling updates to deploy new application versions with minimal downtime and controlled risk through gradual pod replacement.

## Overview

Rolling updates gradually replace old application instances with new ones, ensuring continuous availability during deployments. This is the default deployment strategy in Kubernetes and provides a balance between risk mitigation and resource efficiency.

## Configuration Examples

### Basic Rolling Update
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 6
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
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
        image: myapp:v2.0.0
        ports:
        - containerPort: 8080
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
```

### Advanced Configuration
```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 25%
      maxSurge: 25%
  minReadySeconds: 30
  progressDeadlineSeconds: 300
```

## Best Practices

1. **Proper Health Checks**: Implement readiness and liveness probes
2. **Resource Planning**: Set appropriate maxSurge and maxUnavailable
3. **Testing**: Validate deployments in staging environments
4. **Monitoring**: Track deployment progress and application health

## Troubleshooting

### Common Issues
- **Pods Not Ready**: Check readiness probe configuration
- **Deployment Stuck**: Verify resource availability and image accessibility
- **Service Disruption**: Ensure proper load balancer configuration

## Next Steps

- [Blue-Green Deployments](./blue-green-deployments.md)
- [Canary Deployments](./canary-deployments.md)
- [Rollback Procedures](./rollback-procedures.md) 
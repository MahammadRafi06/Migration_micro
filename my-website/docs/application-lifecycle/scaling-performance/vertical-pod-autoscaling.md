---
id: vertical-pod-autoscaling
title: Vertical Pod Autoscaling (VPA)
sidebar_label: Vertical Pod Autoscaling
description: Configure vertical pod autoscaling to optimize resource allocation
draft: true
---

# Vertical Pod Autoscaling (VPA)

Configure vertical pod autoscaling to automatically adjust resource requests and limits based on actual usage patterns.

## Basic VPA Configuration

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: myapp-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: myapp
      maxAllowed:
        cpu: 1
        memory: 500Mi
      minAllowed:
        cpu: 100m
        memory: 50Mi
```

## Best Practices

1. **Monitor Resource Usage**: Track actual vs requested resources.
2. **Set Boundaries**: Configure min/max resource limits.
3. **Test Thoroughly**: Validate VPA behavior in non-production first.
4. **Combine Wisely**: Use with HPA carefully to avoid conflicts.

## Next Steps

- [Horizontal Pod Autoscaling](./horizontal-pod-autoscaling.md).
- [Performance Tuning](./performance-tuning.md). 
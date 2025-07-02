---
id: horizontal-pod-autoscaling
title: Horizontal Pod Autoscaling (HPA)
sidebar_label: Horizontal Pod Autoscaling
description: Configure horizontal pod autoscaling to automatically scale applications based on demand
draft: true
---

# Horizontal Pod Autoscaling (HPA)

Configure horizontal pod autoscaling to automatically scale your applications based on CPU, memory, or custom metrics.

## Basic HPA Configuration

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

## Custom Metrics Scaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp-custom-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 1
  maxReplicas: 20
  metrics:
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "100"
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
```

## Best Practices

1. **Set Appropriate Limits**: Configure realistic min/max replicas
2. **Monitor Performance**: Track scaling behavior and adjust thresholds
3. **Resource Requests**: Ensure pods have proper resource requests
4. **Stabilization**: Configure scaling behavior to prevent flapping

## Troubleshooting

### Common Issues
- **No Scaling**: Check metrics server and resource requests
- **Thrashing**: Adjust stabilization windows and thresholds
- **Resource Limits**: Verify cluster has sufficient resources

## Next Steps

- [Vertical Pod Autoscaling](./vertical-pod-autoscaling.md)
- [Performance Tuning](./performance-tuning.md)
- [Edge-Specific Challenges](./edge-specific-scaling-challenges.md) 
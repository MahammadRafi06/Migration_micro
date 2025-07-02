---
id: canary-deployments
title: Canary Deployment Strategies
sidebar_label: Canary Deployments
description: Implement canary deployments for gradual rollouts with risk mitigation
draft: true
---

# Canary Deployment Strategies

Implement canary deployments to gradually roll out new versions while monitoring performance and minimizing risk through controlled traffic splitting.

## Overview

Canary deployment is a progressive delivery strategy where you release a new version to a small subset of users before rolling it out to the entire infrastructure. This approach allows you to test in production with real traffic while limiting the blast radius of potential issues.

## Key Benefits

- **Risk Mitigation**: Limited exposure to potential issues.
- **Real-world Testing**: Validation with actual production traffic.
- **Gradual Rollout**: Controlled progression of deployment.
- **Quick Detection**: Early identification of problems.

## Implementation Approaches

### 1. Traffic-Based Canary

```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: myapp-canary
  namespace: production
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  progressDeadlineSeconds: 60
  service:
    port: 80
    targetPort: 8080
    gateways:
    - public-gateway.istio-system.svc.cluster.local
    hosts:
    - myapp.example.com
  analysis:
    interval: 1m
    threshold: 5
    maxWeight: 50
    stepWeight: 5
    metrics:
    - name: request-success-rate
      thresholdRange:
        min: 99
      interval: 1m
    - name: request-duration
      thresholdRange:
        max: 500
      interval: 1m
```

### 2. Header-Based Canary

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: myapp-canary
spec:
  hosts:
  - myapp.example.com
  http:
  - match:
    - headers:
        canary-user:
          exact: "true"
    route:
    - destination:
        host: myapp-canary
        port:
          number: 80
  - route:
    - destination:
        host: myapp-stable
        port:
          number: 80
```

### 3. Geographic Canary

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: myapp-geo-canary
spec:
  hosts:
  - myapp.example.com
  http:
  - match:
    - headers:
        x-region:
          exact: "us-west"
    route:
    - destination:
        host: myapp-canary
        port:
          number: 80
  - route:
    - destination:
        host: myapp-stable
        port:
          number: 80
```

## Automated Canary with ArgoCD and Flagger

### Canary Configuration
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: myapp-rollout
spec:
  replicas: 10
  strategy:
    canary:
      steps:
      - setWeight: 10
      - pause: {duration: 1m}
      - setWeight: 20
      - pause: {duration: 1m}
      - setWeight: 50
      - pause: {duration: 1m}
      - setWeight: 100
      canaryService: myapp-canary
      stableService: myapp-stable
      trafficRouting:
        istio:
          virtualService:
            name: myapp-vsvc
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

### Analysis Templates
```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
spec:
  args:
  - name: service-name
  metrics:
  - name: success-rate
    interval: 2m
    count: 3
    successCondition: result[0] >= 0.95
    provider:
      prometheus:
        address: http://prometheus.istio-system:9090
        query: |
          sum(irate(
            istio_requests_total{reporter="destination",destination_service_name="{{args.service-name}}",response_code!~"5.*"}[2m]
          )) / 
          sum(irate(
            istio_requests_total{reporter="destination",destination_service_name="{{args.service-name}}"}[2m]
          ))
```

## Monitoring and Metrics

### Key Metrics to Monitor

#### Success Rate
```promql
sum(rate(http_requests_total{status!~"5.."}[5m])) / sum(rate(http_requests_total[5m]))
```

#### Response Time
```promql
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
```

#### Error Rate
```promql
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))
```

### Custom Metrics Dashboard
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: canary-dashboard
data:
  dashboard.json: |
    {
      "dashboard": {
        "title": "Canary Deployment Metrics",
        "panels": [
          {
            "title": "Success Rate",
            "type": "graph",
            "targets": [
              {
                "expr": "sum(rate(http_requests_total{status!~\"5..\"}[5m])) by (version) / sum(rate(http_requests_total[5m])) by (version)"
              }
            ]
          }
        ]
      }
    }
```

## Advanced Canary Patterns

### Feature Flag Integration
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: feature-flags
data:
  flags.yaml: |
    canary_enabled: true
    new_feature_rollout: 10  # Percentage of traffic
    experimental_api: false
```

### A/B Testing Canary
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: myapp-ab-test
spec:
  hosts:
  - myapp.example.com
  http:
  - match:
    - headers:
        x-user-id:
          regex: ".*[02468]$"  # Even user IDs
    route:
    - destination:
        host: myapp-canary
        port:
          number: 80
  - route:
    - destination:
        host: myapp-stable
        port:
          number: 80
```

### Canary with Custom Validation
```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisRun
metadata:
  name: myapp-canary-analysis
spec:
  args:
  - name: canary-hash
    value: "abc123"
  metrics:
  - name: custom-validation
    provider:
      job:
        spec:
          template:
            spec:
              containers:
              - name: validator
                image: validator:latest
                command: ["/bin/sh"]
                args: ["-c", "curl -f http://myapp-canary/validate || exit 1"]
              restartPolicy: Never
```

## Rollback Strategies

### Automatic Rollback
```yaml
spec:
  analysis:
    interval: 1m
    threshold: 3  # Number of failed checks before rollback
    maxWeight: 50
    stepWeight: 10
    metrics:
    - name: success-rate
      thresholdRange:
        min: 95
      interval: 1m
      failureLimit: 3
```

### Manual Rollback
```bash
# Rollback canary deployment
kubectl argo rollouts abort myapp-rollout

# Promote stable version
kubectl argo rollouts promote myapp-rollout

# Check rollout status
kubectl argo rollouts get rollout myapp-rollout
```

## Edge-Specific Considerations

### Bandwidth Optimization
```yaml
spec:
  template:
    spec:
      containers:
      - name: myapp
        image: myapp:canary
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "100m"
```

### Regional Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-canary-west
spec:
  replicas: 1
  selector:
    matchLabels:
      app: myapp
      version: canary
      region: west
  template:
    spec:
      nodeSelector:
        topology.kubernetes.io/region: us-west-1
```

## Best Practices

1. **Start Small**: Begin with minimal traffic percentage.
2. **Monitor Closely**: Watch key metrics during rollout.
3. **Define Clear Criteria**: Set specific success/failure thresholds.
4. **Automated Validation**: Use automated testing and monitoring.
5. **Quick Rollback**: Have rapid rollback mechanisms ready.

## Troubleshooting

### Common Issues
- **Traffic Split Not Working**: Check service mesh configuration.
- **Metrics Collection**: Verify monitoring stack is properly configured.
- **Rollback Failures**: Ensure stable version is available.

### Debug Commands
```bash
# Check canary status
kubectl argo rollouts get rollout myapp-rollout

# View traffic distribution
kubectl get virtualservice myapp-vsvc -o yaml

# Check metrics
kubectl get analysisrun -l rollout=myapp-rollout

# Manual promotion
kubectl argo rollouts promote myapp-rollout

# Abort canary
kubectl argo rollouts abort myapp-rollout
```

## Integration Examples

### GitHub Actions Integration
```yaml
- name: Deploy Canary
  run: |
    kubectl argo rollouts set image myapp-rollout myapp=${{ github.sha }}
    kubectl argo rollouts status myapp-rollout --timeout=600s
```

### Slack Notifications
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: notification-config
data:
  config.yaml: |
    templates:
      canary-success: |
        Canary deployment successful for {{.app.metadata.name}}
      canary-failed: |
        Canary deployment failed for {{.app.metadata.name}}
```

## Next Steps

- [Blue-Green Deployments](./blue-green-deployments.md).
- [Rolling Updates](./rolling-updates.md).
- [Rollback Procedures](./rollback-procedures.md). 
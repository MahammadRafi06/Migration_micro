---
id: network-policies
title: Network Policies
sidebar_label: Network Policies
sidebar_position: 3
---

# Network Policies

Implement fine-grained network security controls using Kubernetes Network Policies.

## Overview

Network policies provide network-level security by controlling traffic flow between pods, namespaces, and external endpoints.

## Network Policy Fundamentals

### Basic Concepts
- **Pod Selectors**: Target specific pods.
- **Namespace Selectors**: Target entire namespaces.
- **Policy Types**: Ingress, Egress, or both.
- **Rules**: Allow or deny specific traffic.

### Default Behavior
```yaml
# Deny all ingress traffic
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
```

## Ingress Policies

### Allow Specific Sources

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
```

### Namespace-based Access Control

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-namespace-access
spec:
  podSelector:
    matchLabels:
      app: api-server
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          environment: production
    - namespaceSelector:
        matchLabels:
          environment: staging
```

## Egress Policies

### Restrict External Access

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: restrict-external-egress
spec:
  podSelector:
    matchLabels:
      app: web-app
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector: {}
  - to: []
    ports:
    - protocol: TCP
      port: 443  # Allow HTTPS only
    - protocol: TCP
      port: 53   # Allow DNS
    - protocol: UDP
      port: 53   # Allow DNS
```

### Database Access Control

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: database-access
spec:
  podSelector:
    matchLabels:
      tier: database
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          tier: backend
    ports:
    - protocol: TCP
      port: 5432
```

## Advanced Patterns

### Multi-tier Application

```yaml
# Frontend can only access backend
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: frontend-policy
spec:
  podSelector:
    matchLabels:
      tier: frontend
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector:
        matchLabels:
          tier: backend
    ports:
    - protocol: TCP
      port: 8080
  - to: []  # Allow DNS
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
```

### Cross-Namespace Communication

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: cross-namespace-access
  namespace: app-namespace
spec:
  podSelector:
    matchLabels:
      app: api-gateway
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: frontend-namespace
      podSelector:
        matchLabels:
          app: frontend
```

## Edge-Specific Considerations

### Regional Isolation

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: regional-isolation
spec:
  podSelector:
    matchLabels:
      region: us-east
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          region: us-east
  egress:
  - to:
    - podSelector:
        matchLabels:
          region: us-east
  - to: []  # External access
    ports:
    - protocol: TCP
      port: 443
```

### Edge Node Security

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: edge-node-policy
spec:
  podSelector:
    matchLabels:
      deployment: edge-workload
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - ipBlock:
        cidr: 10.0.0.0/8  # Internal network only
        except:
        - 10.0.1.0/24    # Except management subnet
```

## CNI Compatibility

### Supported CNIs
- **Calico**: Full NetworkPolicy support.
- **Cilium**: Extended eBPF-based policies.
- **Weave Net**: Basic NetworkPolicy support.
- **Flannel**: Requires additional plugins.

### CNI-Specific Features

#### Calico Global Network Policies
```yaml
apiVersion: projectcalico.org/v3
kind: GlobalNetworkPolicy
metadata:
  name: global-deny-all
spec:
  order: 1000
  types:
  - Ingress
  - Egress
```

#### Cilium Layer 7 Policies
```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: l7-policy
spec:
  endpointSelector:
    matchLabels:
      app: api-server
  ingress:
  - fromEndpoints:
    - matchLabels:
        app: frontend
    toPorts:
    - ports:
      - port: "8080"
        protocol: TCP
      rules:
        http:
        - method: "GET"
          path: "/api/v1/.*"
```

## Testing and Validation

### Policy Testing

```bash
# Test connectivity between pods
kubectl exec -it frontend-pod -- curl backend-service:8080

# Check policy application
kubectl describe networkpolicy <policy-name>

# Verify pod labels
kubectl get pods --show-labels
```

### Troubleshooting Tools

```bash
# Check CNI status
kubectl get nodes -o wide

# Verify network plugin
kubectl get daemonset -n kube-system

# Debug network connectivity
kubectl run test-pod --image=busybox --rm -it -- sh
```

## Best Practices

### Policy Design
- Start with default deny policies.
- Use specific selectors and ports.
- Document policy intentions.
- Regular policy reviews.

### Security
- Implement defense in depth.
- Use least privilege principle.
- Regular security audits.
- Monitor policy violations.

### Performance
- Minimize policy complexity.
- Use efficient selectors.
- Monitor resource usage.
- Regular performance testing.

## Monitoring and Alerting

### Policy Violations
- Log denied connections.
- Alert on policy changes.
- Monitor compliance.

### Performance Impact
- Track CNI performance.
- Monitor policy evaluation time.
- Optimize policy rules.

## Next Steps

Continue to [Edge Network Considerations](./edge-network-considerations) to learn about networking challenges specific to edge deployments. 
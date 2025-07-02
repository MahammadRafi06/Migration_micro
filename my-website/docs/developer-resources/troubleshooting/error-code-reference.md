---
id: error-code-reference
title: Error Code Reference
sidebar_label: Error Code Reference
description: Reference guide for error codes and their solutions
draft: true
---

# Error Code Reference

Quick reference for understanding and resolving platform error codes.

## HTTP Error Codes

### 400 - Bad Request
**Meaning**: The request could not be understood by the server
**Common Causes**:
- Invalid JSON payload
- Missing required fields
- Malformed resource definitions

**Solutions**:
```bash
# Validate YAML/JSON syntax
kubectl apply --dry-run=client -f deployment.yaml
yamllint deployment.yaml
```

### 401 - Unauthorized
**Meaning**: Authentication credentials are missing or invalid
**Solutions**:
```bash
# Check authentication
kubectl auth whoami
kubectl config view --minify

# Refresh credentials
kubectl auth refresh
```

### 403 - Forbidden
**Meaning**: Insufficient permissions for the requested operation
**Solutions**:
```bash
# Check RBAC permissions
kubectl auth can-i create pods
kubectl auth can-i create deployments --namespace production

# View current permissions
kubectl describe clusterrolebinding
```

### 404 - Not Found
**Meaning**: Requested resource does not exist
**Solutions**:
```bash
# List available resources
kubectl get all --all-namespaces
kubectl api-resources
```

## Kubernetes Error Codes

### ImagePullBackOff
**Meaning**: Unable to pull container image
**Solutions**:
```bash
# Check image exists
docker pull <image-name>

# Verify registry access
kubectl get secrets
kubectl describe secret <registry-secret>
```

### CrashLoopBackOff
**Meaning**: Container keeps crashing and restarting
**Solutions**:
```bash
# Check container logs
kubectl logs <pod-name> --previous
kubectl describe pod <pod-name>

# Check resource limits
kubectl get pods <pod-name> -o yaml | grep -A 10 resources
```

### Pending
**Meaning**: Pod cannot be scheduled to any node
**Common Causes**:
- Insufficient resources
- Node selector constraints
- Taints and tolerations

**Solutions**:
```bash
# Check node resources
kubectl describe nodes
kubectl top nodes

# Check pod events
kubectl describe pod <pod-name>
```

## Platform-Specific Error Codes

### EDGE-001: Node Connectivity Lost
**Meaning**: Edge node lost connection to control plane
**Solutions**:
```bash
# Check node status
kubectl get nodes
kubectl describe node <edge-node>

# Verify network connectivity
ping <control-plane-ip>
```

### EDGE-002: Resource Quota Exceeded
**Meaning**: Edge node resources exceeded limits
**Solutions**:
```bash
# Check resource usage
kubectl top nodes <edge-node>
kubectl describe node <edge-node>

# Scale down non-critical workloads
kubectl scale deployment <deployment-name> --replicas=1
```

### EDGE-003: Storage Limit Reached
**Meaning**: Edge node storage capacity exceeded
**Solutions**:
```bash
# Check disk usage
kubectl exec -it <pod-name> -- df -h
kubectl get pv,pvc

# Clean up unused resources
kubectl delete pods --field-selector=status.phase=Succeeded
```

## Debugging Commands

```bash
# Get detailed error information
kubectl get events --sort-by='.lastTimestamp'
kubectl describe <resource-type> <resource-name>

# Check logs with timestamps
kubectl logs <pod-name> --timestamps=true

# Debug with verbose output
kubectl apply -f deployment.yaml --v=6
```

## Next Steps

- [Common Issues & Solutions](./common-issues-solutions.md).
- [Debugging Guides](./debugging-guides.md). 
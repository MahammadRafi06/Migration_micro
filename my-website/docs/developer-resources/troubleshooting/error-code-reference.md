---
id: error-code-reference
title: Error Code Reference
sidebar_label: Error Code Reference
description: Comprehensive reference guide for error codes, their meanings, and step-by-step solutions
draft: false
---

# Error Code Reference

Comprehensive reference guide for understanding and resolving platform error codes in edge Kubernetes deployments. This guide provides detailed explanations, root cause analysis, and step-by-step solutions for common error scenarios.

## How to Use This Reference

Each error code entry includes:
- **Meaning**: Clear explanation of what the error indicates
- **Root Causes**: Common underlying issues that trigger this error
- **Immediate Actions**: Quick steps to take when encountering the error
- **Detailed Solutions**: Step-by-step troubleshooting procedures
- **Prevention**: Best practices to avoid the error in the future

## HTTP Error Codes

### 400 - Bad Request

**Meaning**: The server cannot process the request due to client-side errors in the request syntax, format, or content.

**Root Causes**:
- Malformed YAML or JSON in Kubernetes manifests
- Invalid resource specifications or field values
- Missing required fields in API requests
- Incompatible API versions
- Invalid resource names or labels

**Immediate Actions**:
```bash
# Validate manifest syntax before applying
kubectl apply --dry-run=client -f your-manifest.yaml

# Check for YAML syntax errors
yamllint your-manifest.yaml

# Validate against Kubernetes schema
kubectl apply --validate=true --dry-run=client -f your-manifest.yaml
```

**Detailed Solutions**:

1. **Validate Manifest Structure**:
   ```bash
   # Use kubeval for schema validation
   kubeval your-manifest.yaml
   
   # Check API version compatibility
   kubectl api-versions | grep apps
   ```

2. **Common Field Validation Issues**:
   ```bash
   # Verify resource names follow DNS conventions
   # Names must be lowercase, contain only alphanumeric characters and hyphens
   
   # Check label and annotation syntax
   kubectl explain pod.metadata.labels
   ```

3. **Debug Specific Field Errors**:
   ```bash
   # Get detailed field explanations
   kubectl explain deployment.spec.template.spec.containers
   
   # Validate resource requirements format
   kubectl explain pod.spec.containers.resources
   ```

**Prevention**:
- Use IDE plugins with Kubernetes schema validation
- Implement CI/CD pipeline validation steps
- Use `kubectl --dry-run=client` before applying changes
- Maintain consistent naming conventions

### 401 - Unauthorized

**Meaning**: The request lacks valid authentication credentials or the provided credentials are invalid.

**Root Causes**:
- Expired authentication tokens or certificates
- Missing or incorrect kubeconfig configuration
- Invalid service account tokens
- Clock skew between client and server
- Revoked or disabled user credentials

**Immediate Actions**:
```bash
# Check current authentication status
kubectl auth whoami

# View current context and credentials
kubectl config current-context
kubectl config view --minify
```

**Detailed Solutions**:

1. **Token Refresh and Validation**:
   ```bash
   # Refresh authentication token
   kubectl auth refresh
   
   # For OIDC providers, re-authenticate
   kubectl oidc-login
   
   # Check token expiration
   kubectl config view --raw -o jsonpath='{.users[0].user.auth-provider.config.id-token}' | base64 -d
   ```

2. **Service Account Authentication**:
   ```bash
   # Check service account token
   kubectl get serviceaccount <sa-name> -o yaml
   
   # Verify token mounting in pods
   kubectl describe pod <pod-name> | grep -A 5 "Mounts:"
   
   # Create new service account token if needed
   kubectl create token <sa-name>
   ```

3. **Certificate-Based Authentication**:
   ```bash
   # Check client certificate validity
   openssl x509 -in ~/.kube/client.crt -text -noout
   
   # Verify certificate against CA
   openssl verify -CAfile ~/.kube/ca.crt ~/.kube/client.crt
   ```

**Prevention**:
- Set up automatic token renewal
- Monitor certificate expiration dates
- Use short-lived tokens with refresh mechanisms
- Implement proper RBAC policies

### 403 - Forbidden

**Meaning**: The server understood the request but refuses to authorize it due to insufficient permissions.

**Root Causes**:
- Inadequate RBAC permissions for the requested operation
- Missing role bindings or cluster role bindings
- Incorrect service account assignments
- Namespace-level permission restrictions
- Resource quota or limit range violations

**Immediate Actions**:
```bash
# Check specific permission
kubectl auth can-i <verb> <resource> --namespace <namespace>

# List all permissions for current user
kubectl auth can-i --list --namespace <namespace>
```

**Detailed Solutions**:

1. **RBAC Permission Analysis**:
   ```bash
   # Check current user's role bindings
   kubectl get rolebinding,clusterrolebinding -A | grep $(kubectl config view --minify -o jsonpath='{.contexts[0].context.user}')
   
   # Examine specific role permissions
   kubectl describe role <role-name> -n <namespace>
   kubectl describe clusterrole <clusterrole-name>
   ```

2. **Service Account Permission Debugging**:
   ```bash
   # Check service account's role bindings
   kubectl get rolebinding,clusterrolebinding -A | grep <service-account-name>
   
   # Test permissions as service account
   kubectl auth can-i create pods --as=system:serviceaccount:<namespace>:<sa-name>
   ```

3. **Resource Quota and Limits**:
   ```bash
   # Check namespace resource quotas
   kubectl describe quota -n <namespace>
   
   # Check limit ranges
   kubectl describe limitrange -n <namespace>
   ```

**Prevention**:
- Follow principle of least privilege
- Regularly audit RBAC permissions
- Use namespace-specific service accounts
- Document required permissions for applications

### 404 - Not Found

**Meaning**: The requested resource does not exist on the server.

**Root Causes**:
- Resource was deleted or never created
- Incorrect resource name or namespace
- API version mismatch
- Custom Resource Definition (CRD) not installed
- Typos in resource references

**Immediate Actions**:
```bash
# List all resources in namespace
kubectl get all -n <namespace>

# Search across all namespaces
kubectl get <resource-type> -A | grep <resource-name>
```

**Detailed Solutions**:

1. **Resource Discovery**:
   ```bash
   # List all available resource types
   kubectl api-resources
   
   # Check specific resource type availability
   kubectl api-resources | grep <resource-type>
   
   # Verify CRD installation
   kubectl get crd | grep <custom-resource>
   ```

2. **Namespace and Name Verification**:
   ```bash
   # Check current namespace context
   kubectl config view --minify | grep namespace
   
   # List resources with labels
   kubectl get <resource-type> --show-labels -A
   ```

3. **API Version Compatibility**:
   ```bash
   # Check deprecated API versions
   kubectl api-versions | sort
   
   # Convert deprecated resources
   kubectl convert -f old-manifest.yaml --output-version <new-api-version>
   ```

**Prevention**:
- Use consistent naming conventions
- Implement resource tagging strategies
- Version control for resource manifests
- Regular cluster resource auditing

## Kubernetes Pod Error States

### ImagePullBackOff / ErrImagePull

**Meaning**: Kubernetes cannot pull the specified container image from the registry.

**Root Causes**:
- Image does not exist in the specified registry
- Incorrect image name, tag, or registry URL
- Authentication issues with private registries
- Network connectivity problems to registry
- Registry service unavailable
- Image architecture mismatch (e.g., ARM vs x86)

**Immediate Actions**:
```bash
# Check pod events for specific error details
kubectl describe pod <pod-name>

# Verify image exists manually
docker pull <image-name>:<tag>
```

**Detailed Solutions**:

1. **Image and Registry Verification**:
   ```bash
   # Test direct image pull
   docker pull <registry>/<image>:<tag>
   
   # Check image manifest
   docker manifest inspect <image>:<tag>
   
   # Verify image architecture
   docker image inspect <image>:<tag> | grep Architecture
   ```

2. **Registry Authentication**:
   ```bash
   # Check existing image pull secrets
   kubectl get secrets | grep docker
   
   # Describe image pull secret
   kubectl get secret <secret-name> -o yaml
   
   # Create new registry secret
   kubectl create secret docker-registry <secret-name> \
     --docker-server=<registry-url> \
     --docker-username=<username> \
     --docker-password=<password>
   
   # Link secret to service account
   kubectl patch serviceaccount default -p '{"imagePullSecrets": [{"name": "<secret-name>"}]}'
   ```

3. **Network and Connectivity**:
   ```bash
   # Test registry connectivity from node
   kubectl debug node/<node-name> -it --image=nicolaka/netshoot -- curl -v https://<registry-url>
   
   # Check DNS resolution
   kubectl exec -it <debug-pod> -- nslookup <registry-domain>
   
   # Verify proxy settings if applicable
   kubectl get nodes -o yaml | grep -i proxy
   ```

**Prevention**:
- Use specific image tags instead of 'latest'
- Implement image scanning and validation
- Use private registries with proper authentication
- Test image pulls in CI/CD pipeline

### CrashLoopBackOff

**Meaning**: The container repeatedly crashes and Kubernetes keeps restarting it with increasing delays.

**Root Causes**:
- Application startup failures due to misconfigurations
- Missing dependencies or environment variables
- Resource constraints (memory/CPU limits too low)
- Port binding conflicts
- Database or external service connectivity issues
- Invalid command or entrypoint specifications

**Immediate Actions**:
```bash
# Check current and previous container logs
kubectl logs <pod-name> --previous
kubectl logs <pod-name> --tail=50

# Get detailed pod information
kubectl describe pod <pod-name>
```

**Detailed Solutions**:

1. **Application Log Analysis**:
   ```bash
   # Follow logs in real-time
   kubectl logs <pod-name> -f
   
   # Check logs from all containers in pod
   kubectl logs <pod-name> --all-containers=true
   
   # Get logs with timestamps
   kubectl logs <pod-name> --timestamps=true --since=10m
   ```

2. **Resource and Configuration Review**:
   ```bash
   # Check resource limits and requests
   kubectl get pod <pod-name> -o yaml | grep -A 10 resources
   
   # Verify environment variables
   kubectl get pod <pod-name> -o yaml | grep -A 20 env
   
   # Check mounted volumes and secrets
   kubectl describe pod <pod-name> | grep -A 10 "Mounts:"
   ```

3. **Interactive Debugging**:
   ```bash
   # Run debug container with same image
   kubectl run debug-container --image=<same-image> -it --rm -- /bin/sh
   
   # Execute commands in running container (if available)
   kubectl exec -it <pod-name> -- /bin/sh
   
   # Debug with different entrypoint
   kubectl run debug-pod --image=<image> -it --rm --command -- /bin/sh
   ```

**Prevention**:
- Implement proper health checks and readiness probes
- Use init containers for dependency checks
- Set appropriate resource requests and limits
- Test containerized applications locally first

### Pending

**Meaning**: The pod has been accepted by Kubernetes but cannot be scheduled to run on any node.

**Root Causes**:
- Insufficient CPU or memory resources on available nodes
- Node selector constraints cannot be satisfied
- Pod anti-affinity rules preventing scheduling
- Taints on nodes without corresponding tolerations
- Persistent volume availability issues
- Resource quotas preventing pod creation

**Immediate Actions**:
```bash
# Check pod scheduling events
kubectl describe pod <pod-name>

# Review node resource availability
kubectl top nodes
kubectl describe nodes
```

**Detailed Solutions**:

1. **Resource Availability Analysis**:
   ```bash
   # Check detailed node capacity
   kubectl describe node <node-name> | grep -A 10 "Allocated resources"
   
   # View all node allocatable resources
   kubectl get nodes -o custom-columns=NAME:.metadata.name,CPU-ALLOCATABLE:.status.allocatable.cpu,MEMORY-ALLOCATABLE:.status.allocatable.memory
   
   # Check resource quotas
   kubectl describe quota -n <namespace>
   ```

2. **Scheduling Constraints Review**:
   ```bash
   # Check node labels for selector matching
   kubectl get nodes --show-labels
   
   # Review pod node selector and affinity rules
   kubectl get pod <pod-name> -o yaml | grep -A 10 nodeSelector
   kubectl get pod <pod-name> -o yaml | grep -A 20 affinity
   
   # Check node taints
   kubectl describe node <node-name> | grep Taints
   ```

3. **Storage and Volume Issues**:
   ```bash
   # Check persistent volume claims
   kubectl get pvc -n <namespace>
   
   # Verify storage class availability
   kubectl get storageclass
   
   # Check persistent volume status
   kubectl get pv | grep Available
   ```

**Prevention**:
- Monitor cluster resource utilization
- Implement cluster autoscaling
- Use resource requests appropriately
- Plan for node maintenance and capacity

## Edge-Specific Error Codes

### EDGE-001: Node Connectivity Lost

**Meaning**: An edge node has lost network connectivity to the Kubernetes control plane.

**Root Causes**:
- Network infrastructure failures or instability
- Firewall or security group configuration changes
- DNS resolution issues
- Control plane endpoint changes
- Certificate expiration or rotation issues
- Power or hardware failures at edge location

**Immediate Actions**:
```bash
# Check node status from control plane
kubectl get nodes

# Verify node-specific details
kubectl describe node <edge-node-name>
```

**Detailed Solutions**:

1. **Network Connectivity Testing**:
   ```bash
   # Test connectivity from edge node to control plane
   # (Run these commands on the edge node if accessible)
   ping <control-plane-ip>
   telnet <control-plane-ip> 6443
   
   # Check DNS resolution
   nslookup <control-plane-hostname>
   
   # Verify routing
   traceroute <control-plane-ip>
   ```

2. **Certificate and Authentication Verification**:
   ```bash
   # Check kubelet certificate status
   openssl x509 -in /var/lib/kubelet/pki/kubelet-client-current.pem -text -noout
   
   # Verify kubelet configuration
   systemctl status kubelet
   journalctl -u kubelet --since "1 hour ago"
   ```

3. **Recovery Procedures**:
   ```bash
   # Restart kubelet service
   systemctl restart kubelet
   
   # Reset node if necessary (from node)
   kubeadm reset
   kubeadm join <control-plane-endpoint> --token <token> --discovery-token-ca-cert-hash <hash>
   
   # Drain and cordon node for maintenance (from control plane)
   kubectl drain <node-name> --ignore-daemonsets
   kubectl cordon <node-name>
   ```

**Prevention**:
- Implement redundant network paths
- Monitor network connectivity continuously
- Set up automated certificate renewal
- Use node health monitoring and alerting

### EDGE-002: Resource Quota Exceeded

**Meaning**: The edge node has exceeded its allocated resource limits, preventing new workload scheduling.

**Root Causes**:
- Insufficient resource planning for edge node capacity
- Memory leaks in running applications
- Unexpected workload spikes or scaling events
- Background processes consuming resources
- Storage space exhaustion

**Immediate Actions**:
```bash
# Check node resource usage
kubectl top node <edge-node-name>

# List resource-intensive pods
kubectl top pods --sort-by=memory -n <namespace>
kubectl top pods --sort-by=cpu -n <namespace>
```

**Detailed Solutions**:

1. **Resource Usage Analysis**:
   ```bash
   # Get detailed node resource allocation
   kubectl describe node <edge-node-name> | grep -A 20 "Allocated resources"
   
   # Check for resource-intensive pods
   kubectl get pods -o custom-columns=NAME:.metadata.name,CPU-REQUEST:.spec.containers[0].resources.requests.cpu,MEMORY-REQUEST:.spec.containers[0].resources.requests.memory --sort-by=.spec.containers[0].resources.requests.memory
   
   # Monitor resource usage over time
   watch kubectl top pods -n <namespace>
   ```

2. **Workload Optimization**:
   ```bash
   # Scale down non-critical workloads
   kubectl scale deployment <deployment-name> --replicas=1
   
   # Update resource limits for problematic pods
   kubectl patch deployment <deployment-name> -p '{"spec":{"template":{"spec":{"containers":[{"name":"<container-name>","resources":{"limits":{"memory":"512Mi","cpu":"500m"}}}]}}}}'
   
   # Remove completed or failed pods
   kubectl delete pods --field-selector=status.phase=Succeeded
   kubectl delete pods --field-selector=status.phase=Failed
   ```

3. **Storage Management**:
   ```bash
   # Check disk usage on node
   kubectl debug node/<node-name> -it --image=nicolaka/netshoot -- df -h
   
   # Clean up unused volumes
   kubectl delete pvc <unused-pvc-name>
   
   # Remove unused images (on node)
   docker system prune -a
   ```

**Prevention**:
- Implement resource monitoring and alerting
- Set appropriate resource requests and limits
- Use horizontal pod autoscaling
- Regular cleanup of unused resources

### EDGE-003: Storage Limit Reached

**Meaning**: The edge node has reached its storage capacity limit, affecting application operation and new deployments.

**Root Causes**:
- Log files growing without rotation or cleanup
- Application data accumulation without management
- Container image buildup without cleanup
- Temporary file accumulation
- Persistent volume space exhaustion

**Immediate Actions**:
```bash
# Check storage usage on node
kubectl debug node/<node-name> -it --image=nicolaka/netshoot -- df -h

# Check persistent volume status
kubectl get pv,pvc -A
```

**Detailed Solutions**:

1. **Storage Analysis and Cleanup**:
   ```bash
   # Analyze disk usage by directory
   kubectl debug node/<node-name> -it --image=nicolaka/netshoot -- du -sh /var/lib/docker/*
   
   # Clean up Docker resources
   kubectl debug node/<node-name> -it --image=nicolaka/netshoot -- docker system prune -a
   
   # Remove unused container images
   kubectl debug node/<node-name> -it --image=nicolaka/netshoot -- docker image prune -a
   ```

2. **Log Management**:
   ```bash
   # Check log sizes
   kubectl debug node/<node-name> -it --image=nicolaka/netshoot -- du -sh /var/log/*
   
   # Rotate logs manually if needed
   kubectl debug node/<node-name> -it --image=nicolaka/netshoot -- logrotate -f /etc/logrotate.conf
   
   # Clear old journal logs
   kubectl debug node/<node-name> -it --image=nicolaka/netshoot -- journalctl --vacuum-time=7d
   ```

3. **Persistent Volume Management**:
   ```bash
   # Check PV usage
   kubectl exec -it <pod-using-pv> -- df -h /mount/path
   
   # Resize persistent volumes if supported
   kubectl patch pvc <pvc-name> -p '{"spec":{"resources":{"requests":{"storage":"20Gi"}}}}'
   
   # Backup and clean old data
   kubectl exec -it <pod-name> -- tar -czf /backup/data.tar.gz /data/old/
   kubectl exec -it <pod-name> -- rm -rf /data/old/*
   ```

**Prevention**:
- Implement log rotation and retention policies
- Set up storage monitoring and alerting
- Use ephemeral storage for temporary data
- Regular maintenance and cleanup schedules

## Debugging Commands Quick Reference

### Essential Diagnostic Commands

```bash
# Get cluster overview
kubectl cluster-info
kubectl get nodes -o wide
kubectl get events --sort-by='.lastTimestamp' -A

# Pod debugging
kubectl get pods -A -o wide
kubectl describe pod <pod-name>
kubectl logs <pod-name> --previous --timestamps

# Resource monitoring
kubectl top nodes
kubectl top pods -A --sort-by=memory
kubectl get events --field-selector type=Warning

# Network debugging
kubectl get svc,ep -A
kubectl exec -it <pod-name> -- netstat -tulpn
kubectl run netshoot --image=nicolaka/netshoot -it --rm

# Storage debugging
kubectl get pv,pvc,sc -A
kubectl describe pvc <pvc-name>

# RBAC debugging
kubectl auth can-i --list
kubectl get rolebinding,clusterrolebinding -A
```

### Advanced Debugging Techniques

```bash
# Enable verbose output
kubectl apply -f manifest.yaml --v=8

# Use debug containers
kubectl debug <pod-name> -it --image=nicolaka/netshoot
kubectl debug node/<node-name> -it --image=nicolaka/netshoot

# Simulate pod scheduling
kubectl apply --dry-run=server -f pod.yaml

# Force delete stuck resources
kubectl delete pod <pod-name> --force --grace-period=0

# Export resources for analysis
kubectl get pod <pod-name> -o yaml > pod-debug.yaml
kubectl describe pod <pod-name> > pod-description.txt
```

## Next Steps

For additional troubleshooting resources:

- [Common Issues & Solutions](./common-issues-solutions.md) - Quick fixes for frequent problems
- [Debugging Guides](./debugging-guides.md) - Step-by-step troubleshooting workflows
- [Platform Deep Dive](../../platform-deep-dive/) - Understanding underlying platform components 
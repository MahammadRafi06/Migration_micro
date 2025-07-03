---
id: debugging-guides
title: Debugging Guides
sidebar_label: Debugging Guides
description: Comprehensive step-by-step debugging guides for complex issues in edge deployments
draft: false
---

# Debugging Guides

Comprehensive step-by-step guides for debugging complex issues in edge deployments. This guide provides systematic approaches to identify, diagnose, and resolve common problems in Kubernetes-based edge environments.

## General Debugging Methodology

Before diving into specific scenarios, follow this general approach:

1. **Identify the Problem**: Clearly define symptoms and expected vs. actual behavior
2. **Gather Information**: Collect logs, metrics, and configuration details
3. **Isolate Components**: Determine which layer is causing the issue (application, platform, infrastructure)
4. **Test Hypotheses**: Make changes incrementally and validate results
5. **Document Solutions**: Record findings for future reference

## Application Not Starting

When applications fail to start or remain in pending/error states, follow this systematic approach.

### Step 1: Check Pod Status and Events

Start by understanding the current state of your application pods:

```bash
# Get overall pod status
kubectl get pods -l app=myapp -o wide

# Get detailed pod information and events
kubectl describe pod <pod-name>
```

**What to look for:**
- **Pending**: Usually indicates resource constraints or scheduling issues
- **CrashLoopBackOff**: Application is starting but immediately crashing
- **ImagePullBackOff**: Cannot pull the container image
- **Error/Failed**: General failure state

**Common Events and Their Meanings:**
- `FailedScheduling`: No nodes available with required resources
- `FailedMount`: Issues mounting volumes or secrets
- `Failed to pull image`: Registry connectivity or authentication issues

### Step 2: Examine Application Logs

Logs provide crucial insights into why applications fail to start:

```bash
# Get current logs
kubectl logs <pod-name>

# Get logs from previous container instance (if crashed)
kubectl logs <pod-name> --previous

# Follow logs in real-time
kubectl logs <pod-name> -f

# Get logs from specific container in multi-container pod
kubectl logs <pod-name> -c <container-name>
```

**Log Analysis Tips:**
- Look for startup errors, missing dependencies, or configuration issues
- Check for port binding conflicts or permission denied errors
- Identify any stack traces or error codes
- Note any environment variable or secret-related errors

### Step 3: Verify Resource Availability

Ensure the cluster has sufficient resources for your application:

```bash
# Check node resource usage
kubectl top nodes

# Get detailed node information
kubectl describe node <node-name>

# Check resource quotas (if applicable)
kubectl get resourcequota

# Verify persistent volume claims
kubectl get pvc
```

**Resource Troubleshooting:**
- Compare requested resources in your deployment with available node capacity
- Check if resource quotas are preventing pod scheduling
- Verify that persistent volumes are available and properly bound

### Step 4: Validate Configuration

Configuration issues are common causes of startup failures:

```bash
# Check ConfigMaps
kubectl get configmap <config-name> -o yaml

# Verify Secrets
kubectl get secret <secret-name> -o yaml

# Validate deployment configuration
kubectl get deployment <deployment-name> -o yaml

# Check service account permissions
kubectl get serviceaccount <sa-name> -o yaml
```

**Configuration Checklist:**
- Ensure all required environment variables are set
- Verify secret and configmap references are correct
- Check that image tags exist and are accessible
- Validate service account has necessary permissions

### Step 5: Network and DNS Resolution

For applications that depend on external services:

```bash
# Test DNS resolution from within a pod
kubectl exec -it <pod-name> -- nslookup kubernetes.default

# Check if external services are reachable
kubectl exec -it <pod-name> -- curl -v http://external-service.com

# Verify internal service connectivity
kubectl exec -it <pod-name> -- telnet <service-name> <port>
```

## Performance Issues

When applications are running but experiencing poor performance, use this systematic approach.

### Step 1: Monitor Resource Usage

Start by understanding current resource consumption:

```bash
# Check pod resource usage
kubectl top pods --sort-by=memory
kubectl top pods --sort-by=cpu

# Monitor specific pod over time
watch kubectl top pod <pod-name>

# Get detailed resource information
kubectl describe pod <pod-name> | grep -A 20 "Containers:"
```

**Performance Indicators:**
- **High CPU**: May indicate inefficient algorithms, infinite loops, or insufficient resources
- **High Memory**: Could suggest memory leaks, large datasets, or inadequate limits
- **Resource Throttling**: Check if pods are hitting their limits

### Step 2: Analyze Application Metrics

Access application-specific metrics to understand internal performance:

```bash
# Port-forward to access metrics endpoint
kubectl port-forward <pod-name> 9090:9090

# Query Prometheus-style metrics
curl http://localhost:9090/metrics

# For custom applications, check health endpoints
curl http://localhost:8080/health
curl http://localhost:8080/ready
```

**Metrics to Focus On:**
- Request latency and throughput
- Database connection pool utilization
- Cache hit/miss ratios
- Queue depths and processing times

### Step 3: Deep Dive into Logs

Analyze log patterns to identify performance bottlenecks:

```bash
# Look for error patterns
kubectl logs <pod-name> | grep ERROR | tail -20

# Search for performance-related issues
kubectl logs <pod-name> | grep -i "timeout\|slow\|performance"

# Check for memory issues
kubectl logs <pod-name> | grep -i "out of memory\|oom"

# Analyze request patterns (for web applications)
kubectl logs <pod-name> | grep "response_time" | tail -50
```

### Step 4: Check Downstream Dependencies

Performance issues often originate from dependencies:

```bash
# Test database connectivity and performance
kubectl exec -it <pod-name> -- pg_isready -h <db-host>

# Check external API response times
kubectl exec -it <pod-name> -- time curl -s http://api.example.com/health

# Verify internal service response times
kubectl exec -it <pod-name> -- time curl -s http://internal-service/health
```

### Step 5: Resource Optimization

Based on findings, optimize resource allocation:

```bash
# Update resource requests and limits
kubectl patch deployment <deployment-name> -p '{"spec":{"template":{"spec":{"containers":[{"name":"<container-name>","resources":{"requests":{"memory":"512Mi","cpu":"500m"},"limits":{"memory":"1Gi","cpu":"1000m"}}}]}}}}'

# Scale horizontally if needed
kubectl scale deployment <deployment-name> --replicas=3

# Check if horizontal pod autoscaler would help
kubectl get hpa
```

## Networking Issues

Network connectivity problems can be complex to diagnose in edge environments.

### Step 1: Test Basic Connectivity

Start with fundamental network connectivity tests:

```bash
# Test pod-to-pod communication
kubectl exec -it <source-pod> -- ping <target-pod-ip>

# Test service connectivity
kubectl exec -it <pod-name> -- telnet <service-name> <port>

# Check DNS resolution
kubectl exec -it <pod-name> -- nslookup <service-name>

# Test external connectivity
kubectl exec -it <pod-name> -- curl -v http://google.com
```

**Common Connectivity Issues:**
- DNS resolution failures
- Service discovery problems
- Network policy restrictions
- Firewall or security group blocks

### Step 2: Verify Service Configuration

Ensure services are properly configured and have valid endpoints:

```bash
# Check service configuration
kubectl get svc <service-name> -o yaml

# Verify service endpoints
kubectl get endpoints <service-name>

# Check if service selector matches pod labels
kubectl get pods --show-labels -l <service-selector>

# Test service from within cluster
kubectl run test-pod --image=nicolaka/netshoot -it --rm -- curl http://<service-name>:<port>
```

**Service Troubleshooting:**
- Ensure service selector matches pod labels exactly
- Verify target ports match container ports
- Check that endpoints list shows healthy pods

### Step 3: Analyze Network Policies

Network policies can restrict traffic flow:

```bash
# List all network policies
kubectl get networkpolicy -A

# Check specific policy details
kubectl describe networkpolicy <policy-name>

# Test connectivity before and after policy application
kubectl exec -it <pod-name> -- curl -v http://<target-service>
```

**Network Policy Debugging:**
- Verify ingress/egress rules match your traffic patterns
- Check namespace and pod selectors
- Test connectivity from allowed and denied sources

### Step 4: Ingress and Load Balancer Issues

For external traffic routing problems:

```bash
# Check ingress configuration
kubectl get ingress <ingress-name> -o yaml

# Verify ingress controller logs
kubectl logs -n ingress-nginx <ingress-controller-pod>

# Test load balancer health
kubectl get svc <loadbalancer-service> -o wide

# Check external DNS resolution
nslookup <your-domain.com>
```

### Step 5: Edge-Specific Network Considerations

Edge environments often have unique networking challenges:

```bash
# Check node network configuration
kubectl get nodes -o wide

# Verify cluster networking components
kubectl get pods -n kube-system | grep -E "(calico|flannel|weave)"

# Check for network interface issues on nodes
kubectl debug node/<node-name> -it --image=nicolaka/netshoot
```

## Edge-Specific Debugging Scenarios

### Intermittent Connectivity

Edge deployments often experience network instability:

```bash
# Monitor connectivity over time
kubectl exec -it <pod-name> -- ping -c 100 <target-host> | grep -E "(loss|min/avg/max)"

# Check for network interface flapping
kubectl exec -it <pod-name> -- ip link show

# Monitor DNS resolution stability
for i in {1..10}; do kubectl exec -it <pod-name> -- nslookup google.com; sleep 5; done
```

### Resource Constraints in Edge Environments

Edge nodes often have limited resources:

```bash
# Monitor node resources over time
watch kubectl top nodes

# Check for evicted pods
kubectl get pods -A | grep Evicted

# Verify resource quotas and limits
kubectl describe resourcequota
kubectl describe limitrange
```

### Geographic Distribution Issues

For multi-site edge deployments:

```bash
# Check pod distribution across nodes/zones
kubectl get pods -o wide | sort -k 7

# Verify node affinity rules
kubectl get deployment <deployment-name> -o yaml | grep -A 10 affinity

# Test cross-zone connectivity
kubectl exec -it <pod-in-zone-a> -- ping <pod-in-zone-b>
```

## Debugging Best Practices

### 1. Systematic Approach
- Always start with the most basic checks before diving into complex analysis
- Document your debugging steps and findings
- Use a consistent methodology across different types of issues

### 2. Comprehensive Logging
```bash
# Enable verbose logging for troubleshooting
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  LOG_LEVEL: "DEBUG"
  ENABLE_TRACING: "true"
EOF
```

### 3. Use Debugging Tools
```bash
# Deploy debugging utilities
kubectl run debug-pod --image=nicolaka/netshoot -it --rm

# Use kubectl debug for node-level issues
kubectl debug node/<node-name> -it --image=nicolaka/netshoot

# Employ port-forwarding for direct access
kubectl port-forward <pod-name> 8080:8080
```

### 4. Monitor Continuously
- Set up alerts for common failure patterns
- Use observability tools to track trends
- Implement health checks and readiness probes

### 5. Document and Share
- Maintain a knowledge base of common issues and solutions
- Create runbooks for recurring problems
- Share findings with team members

## Advanced Debugging Techniques

### Container Runtime Debugging
```bash
# Check container runtime status
kubectl get nodes -o wide

# Debug container creation issues
kubectl describe pod <pod-name> | grep -A 10 "Events:"

# Access node-level container information
kubectl debug node/<node-name> -it --image=nicolaka/netshoot -- crictl ps
```

### Storage and Volume Issues
```bash
# Check persistent volume status
kubectl get pv,pvc -A

# Debug volume mount issues
kubectl describe pod <pod-name> | grep -A 10 "Mounts:"

# Verify storage class configuration
kubectl get storageclass -o yaml
```

### Security and RBAC Debugging
```bash
# Check service account permissions
kubectl auth can-i <verb> <resource> --as=system:serviceaccount:<namespace>:<serviceaccount>

# Verify RBAC bindings
kubectl get rolebinding,clusterrolebinding -A | grep <serviceaccount>

# Debug security context issues
kubectl get pod <pod-name> -o yaml | grep -A 10 securityContext
```

## Escalation Guidelines

When to escalate issues:

1. **Infrastructure-level failures** affecting multiple applications
2. **Security incidents** or suspected breaches
3. **Resource exhaustion** at the cluster level
4. **Persistent issues** that don't respond to standard troubleshooting
5. **Performance degradation** affecting SLA compliance

## Next Steps

For additional troubleshooting resources:

- [Common Issues & Solutions](./common-issues-solutions.md) - Quick reference for frequent problems
- [Error Code Reference](./error-code-reference.md) - Detailed error code explanations
- [Observability Tools](../observability/) - Monitoring and alerting setup guides 
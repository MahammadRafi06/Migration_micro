---
id: troubleshooting
title: Troubleshooting Common Hurdles
sidebar_label: Troubleshooting
sidebar_position: 6
---

# Troubleshooting Common Hurdles

Migrating and operating microservices on Kubernetes means you'll definitely encounter issues along the way. That's normal! Here are some common hurdles and practical ways to approach them:

## Pod CrashLoopBackOff

**The problem:** A container inside one of your Pods starts up, immediately crashes, and then Kubernetes tries to restart it over and over again.

**How to troubleshoot:**

1. **Check Logs:** Your first stop should always be the logs. Run `kubectl logs <pod-name> -c <container-name>` (or just `kubectl logs <pod-name>` if there's only one container in the pod). Look for any error messages, stack traces, or exceptions that tell you why the application crashed.

2. **Check Events:** Get a broader picture by running `kubectl describe pod <pod-name>`. Take a close look at the "Events" section; it often holds clues like OOMKilled (out of memory) or Liveness probe failed.

3. **Inspect Container State:** For a deeper dive into the container's last state, use `kubectl get pod <pod-name> -o yaml` or json. Check the containerStatuses for lastState and reason.

4. **Verify Configuration:** Double-check that all your environment variables, mounted secrets, configmaps, and the container's startup commands are exactly as they should be.

5. **Resource Limits:** If you see OOMKilled in the events, it means your container ran out of memory. Try increasing the memory limits in your Deployment YAML.

## Service Not Reachable

**The problem:** You're trying to reach your service, but it's not responding, whether from another Pod internally or from outside the cluster.

**How to troubleshoot:**

1. **Check Service Status:** Run `kubectl get svc`. Make sure your service is listed and has a CLUSTER-IP (if it's a ClusterIP type) or an EXTERNAL-IP (if it's a LoadBalancer type).

2. **Check Endpoints:** Use `kubectl get ep <service-name>`. This command shows you which Pods are actually connected to and backing your service. If you see no endpoints, it usually means the selector in your Service YAML doesn't match the labels on any currently running Pods.

3. **Check Pod Labels:** Confirm that the labels on your Pods truly match the selector in your Service YAML by running `kubectl get pods -l <label-key>=<label-value>`.

4. **Network Policies:** If you have Kubernetes Network Policies enabled, ensure they're configured to allow traffic to your service. Sometimes, these can block legitimate communication.

5. **Firewall/Security Groups:** For LoadBalancer or NodePort services, make sure your external firewalls or cloud provider security groups are configured to allow traffic on the exposed ports.

6. **Ingress Controller:** If you're using an Ingress, verify that your Ingress controller is healthy and running, your Ingress resource is set up correctly, and its routing rules match your service.

## Container Image Pull Errors

**The problem:** Kubernetes just can't seem to download the Docker image for your container.

**How to troubleshoot:**

1. **Check Image Name:** Carefully double-check the image name and tag in your Deployment YAML for any typos. Even a small mistake can prevent the pull.

2. **Verify Registry Access:** If you're using a private image registry, ensure your Kubernetes cluster has the necessary credentials (e.g., imagePullSecrets) configured to pull images from it.

3. **Registry Availability:** Confirm that the image registry (like Docker Hub, GCR, etc.) is actually accessible and not experiencing any outages from your cluster nodes.

4. **Image Exists:** It sounds basic, but verify that the image genuinely exists in the specified registry with the exact tag you've provided. You can try running `docker pull <image-name>` locally to confirm its presence.

## Persistent Volume Claim Pending

**The problem:** Your PersistentVolumeClaim (PVC) is stuck in a Pending state and can't find a PersistentVolume (PV) to bind to.

**How to troubleshoot:**

1. **Check PVC Status:** Start by running `kubectl get pvc`. Look specifically for any PVCs that are showing a Pending status.

2. **Check Events:** Get more details by running `kubectl describe pvc <pvc-name>`. The events section will often clearly state why it's pending (e.g., "no PersistentVolumes available for this claim and no StorageClass is set").

3. **StorageClass:** Make sure a StorageClass is defined and available in your cluster. Also, check that your PVC either explicitly requests that StorageClass (`storageClassName: <name>`) or that a default StorageClass is set up.

4. **PV Availability:** If you're using manually provisioned PVs, ensure there are enough PVs available that perfectly match your PVC's requirements (this includes access modes like ReadWriteOnce and the requested storage size).

## Networking Issues

**The problem:** Your Pods or services just aren't able to communicate with each other.

**How to troubleshoot:**

1. **DNS Resolution:** If services can't find each other by name, test DNS resolution directly from inside a Pod. You can do this by running `kubectl exec -it <pod-name> -- nslookup <service-name>`.

2. **Network Policy Conflicts:** If you've implemented Kubernetes Network Policies, they might be inadvertently blocking traffic. In a development environment, you could temporarily disable them for testing, or more safely, carefully review their rules to ensure they permit the necessary communication.

3. **CNI Plugin:** Ensure your Container Network Interface (CNI) plugin (like Calico, Flannel, or Cilium) is healthy and actively running on all your nodes. Check its logs for any errors.

4. **Container Port vs. Service Port vs. Target Port:** These port definitions need to be perfectly aligned. Double-check that they are consistent across your Dockerfile, your Deployment YAML, and your Service YAML. A mismatch here is a very common cause of connectivity issues.

## Common kubectl Commands for Troubleshooting

Here are some essential commands that will help you diagnose issues:

### Basic Status Commands
```bash
# Check cluster status
kubectl get nodes
kubectl cluster-info

# Check all resources in current namespace
kubectl get all

# Check resources across all namespaces
kubectl get all --all-namespaces
```

### Pod Debugging
```bash
# Get detailed pod information
kubectl describe pod <pod-name>

# View pod logs
kubectl logs <pod-name>
kubectl logs <pod-name> -c <container-name>  # for multi-container pods

# Follow logs in real-time
kubectl logs -f <pod-name>

# Execute commands inside a pod
kubectl exec -it <pod-name> -- /bin/bash
kubectl exec -it <pod-name> -- /bin/sh
```

### Service and Network Debugging
```bash
# Check services and their endpoints
kubectl get svc
kubectl get endpoints

# Test service connectivity from within cluster
kubectl run test-pod --image=busybox --restart=Never -- sleep 3600
kubectl exec -it test-pod -- nslookup <service-name>
kubectl exec -it test-pod -- wget -qO- <service-name>:<port>
```

### Resource Monitoring
```bash
# Check resource usage
kubectl top nodes
kubectl top pods

# Watch resource changes
kubectl get pods -w
kubectl get events -w
```

---

**Previous:** [← Migration Considerations](./migration-considerations) | **Next:** [Conclusion →](./conclusion)

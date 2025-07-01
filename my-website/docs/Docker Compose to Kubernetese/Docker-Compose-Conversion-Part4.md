# Part 4: Advanced Considerations & Cleanup

## Navigation
- [Part 1: Setup & Prerequisites](#part1)
- [Part 2: Converting with Kompose](#part2)
- [Part 3: Deployment & Manual Creation](#part3)
- **Part 4: Advanced Considerations & Cleanup** (Current)

---

## **7. Advanced Considerations and Troubleshooting**

This section provides additional steps for a more robust deployment and guidance on resolving common issues.

### **7.1. Image Management for Production**

For production deployments, simply relying on local Docker images is insufficient. You need an image registry.

**Build Docker Image**:
```bash
docker build -t your-registry/your-image-name:tag .
```
> Builds your Docker image and tags it with your registry's address, image name, and a specific tag (e.g., version number).

**Push to Container Registry**:
```bash
docker push your-registry/your-image-name:tag
```
> Uploads your tagged Docker image to the specified container registry.

**Update Kubernetes Manifests**:
- Set the `image` field in your `Deployment` YAML to:
  ```yaml
  image: your-registry/your-image-name:tag
  ```

**If using a private registry**:
- Configure `imagePullSecrets` in your deployment to authenticate.

---

### **7.2. Kubernetes Dashboard**

The Kubernetes Dashboard provides a web-based UI for managing and monitoring your cluster.

**Start the Dashboard**:
```bash
minikube dashboard
```
> Opens the dashboard in your default browser. Minikube sets up the proxy automatically.

Use this interface to inspect deployments, pods, services, and events visually.

---

### **7.3. Troubleshooting Common Issues**

####  Pod Stuck in `Pending`
- **Cause**: Insufficient resources or unbound PVCs.
- **Debug**:
  ```bash
  kubectl describe pod <pod-name>
  kubectl get events
  ```

####  Pod in `ImagePullBackOff`
- **Cause**: Bad image name/tag or private registry auth failure.
- **Debug**:
  ```bash
  kubectl describe pod <pod-name>
  ```

####  Application Not Accessible
- **Cause**: Wrong service type or port issue.
- **Debug**:
  ```bash
  kubectl get svc
  kubectl describe svc <service-name>
  kubectl logs <pod-name>
  ```

####  Application Errors in Container
- **Cause**: Code bugs, env issues, or DB connection failure.
- **Debug**:
  ```bash
  kubectl logs <pod-name>
  kubectl exec -it <pod-name> -- /bin/bash
  ```

---

### **7.4. Security Best Practices**

- **Secrets Management**: Use Kubernetes `Secrets`, or tools like Vault, AWS Secrets Manager.
- **Network Policies**: Use `NetworkPolicy` to control pod communication.
- **Resource Limits**: Define `resources.requests` and `resources.limits` for every container.
- **Least Privilege**: Enforce minimal access with Kubernetes RBAC.

---

## **8. Cleanup (Optional)**

To remove all deployed Kubernetes resources and shut down the Minikube cluster:

```bash
# Delete all resources created from local YAML files
kubectl delete -f .

# Stop the Minikube VM
minikube stop armadalocal

# Delete the Minikube cluster and all its data
minikube delete armadalocal
```

---

## Navigation
- [Part 1: Setup & Prerequisites](#part1)
- [Part 2: Converting with Kompose](#part2)
- [Part 3: Deployment & Manual Creation](#part3)
- **Part 4: Advanced Considerations & Cleanup** (Current)
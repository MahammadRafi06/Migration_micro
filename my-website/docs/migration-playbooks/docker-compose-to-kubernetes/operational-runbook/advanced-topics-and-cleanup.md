---
id: advanced-topics-and-cleanup
title: Advanced Considerations & Cleanup
sidebar_label: Advanced Considerations & Cleanup
---

# Advanced Considerations & Cleanup

This section provides additional steps for a more robust deployment and guidance on resolving common issues.

## Advanced Considerations and Troubleshooting

### Image Management for Production

For production deployments, simply relying on local Docker images is insufficient. You need an image registry.

**Build Docker Image**:
```bash
docker build -t your-registry/your-image-name:tag .
```

:::tip
Builds your Docker image and tags it with your registry's address, image name, and a specific tag (e.g., version number).
:::

**Push to Container Registry**:
```bash
docker push your-registry/your-image-name:tag
```

:::tip
Uploads your tagged Docker image to the specified container registry.
:::

**Update Kubernetes Manifests**:
- Set the `image` field in your `Deployment` YAML to:
  ```yaml
  image: your-registry/your-image-name:tag
  ```

**If using a private registry**:
- Configure `imagePullSecrets` in your deployment to authenticate:

```yaml
spec:
  template:
    spec:
      imagePullSecrets:
      - name: regcred
      containers:
      # ...
```

To create the registry credentials secret:

```bash
kubectl create secret docker-registry regcred \
  --docker-server=<your-registry-server> \
  --docker-username=<your-name> \
  --docker-password=<your-password> \
  --docker-email=<your-email>
```

### Kubernetes Dashboard

The Kubernetes Dashboard provides a web-based UI for managing and monitoring your cluster.

**Start the Dashboard**:
```bash
minikube dashboard
```

:::tip
Opens the dashboard in your default browser. Minikube sets up the proxy automatically.
:::

Use this interface to inspect deployments, pods, services, and events visually.

### Troubleshooting Common Issues

#### Pod Stuck in `Pending`
- **Cause**: Insufficient resources or unbound PVCs.
- **Debug**:
  ```bash
  kubectl describe pod <pod-name>
  kubectl get events
  ```

#### Pod in `ImagePullBackOff`
- **Cause**: Bad image name/tag or private registry auth failure.
- **Debug**:
  ```bash
  kubectl describe pod <pod-name>
  ```

#### Application Not Accessible
- **Cause**: Wrong service type or port issue.
- **Debug**:
  ```bash
  kubectl get svc
  kubectl describe svc <service-name>
  kubectl logs <pod-name>
  ```

#### Application Errors in Container
- **Cause**: Code bugs, env issues, or DB connection failure.
- **Debug**:
  ```bash
  kubectl logs <pod-name>
  kubectl exec -it <pod-name> -- /bin/bash
  ```

:::note Troubleshooting Chart
When troubleshooting Kubernetes issues, follow this general workflow:
1. Check the pod status: `kubectl get pods`
2. Examine the detailed description: `kubectl describe pod <pod-name>`
3. Check logs: `kubectl logs <pod-name>`
4. Look at recent events: `kubectl get events`
5. If possible, exec into the container: `kubectl exec -it <pod-name> -- /bin/bash`
:::

### Security Best Practices

- **Secrets Management**: Use Kubernetes `Secrets`, or tools like Vault, AWS Secrets Manager.
- **Network Policies**: Use `NetworkPolicy` to control pod communication.
- **Resource Limits**: Define `resources.requests` and `resources.limits` for every container.
- **Least Privilege**: Enforce minimal access with Kubernetes RBAC.

Example NetworkPolicy to restrict database access:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: db-network-policy
spec:
  podSelector:
    matchLabels:
      app: postgres
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: userapp
    ports:
    - protocol: TCP
      port: 5432
```

### RBAC Configuration

For proper security, set up Role-Based Access Control:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: app-role
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list", "watch"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: app-role-binding
  namespace: default
subjects:
- kind: ServiceAccount
  name: app-service-account
  namespace: default
roleRef:
  kind: Role
  name: app-role
  apiGroup: rbac.authorization.k8s.io
```

## Cleanup (Optional)

To remove all deployed Kubernetes resources and shut down the Minikube cluster:

```bash
# Delete all resources created from local YAML files
kubectl delete -f .

# Stop the Minikube VM
minikube stop armadalocal

# Delete the Minikube cluster and all its data
minikube delete armadalocal
```

:::caution
This will permanently delete all data in your Minikube cluster. Make sure to back up any important data before running these commands.
:::

## Conclusion

In this guide, we've covered:

1. **Setup & Prerequisites**: Installing necessary tools and verifying the environment
2. **Converting with Kompose**: Automatically generating Kubernetes manifests from Docker Compose
3. **Deployment & Manual Creation**: Deploying to Minikube and manually creating Kubernetes resources
4. **Advanced Considerations & Cleanup**: Managing images, troubleshooting, and implementing security best practices

By following these steps, you've successfully converted a Docker Compose application to Kubernetes and deployed it in a Minikube cluster. This process provides a foundation for deploying containerized applications in more complex Kubernetes environments.

### Next Learning Steps

To further enhance your Kubernetes skills, consider exploring:

- Helm for packaging applications
- Kubernetes Operators for complex, stateful applications
- CI/CD pipelines for Kubernetes deployments
- Monitoring and logging solutions (Prometheus, Grafana, ELK)
- Advanced networking and service mesh (Istio, Linkerd)
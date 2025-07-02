---
id: helm-repositories-and-advanced-charting
title: Helm Repositories and Advanced Topics
sidebar_label: Repositories & Advanced Topics
---

# Helm Repositories and Advanced Topics

In this final section, we'll cover how to share your Helm charts through repositories, explore advanced considerations for production deployments, and learn about proper cleanup procedures.

## Pushing Helm Charts to a Remote Repository

To share your Helm charts or deploy them from a centralized location, you'll need to push them to a remote Helm repository. Common types of Helm repositories include:

* **ChartMuseum:** An open-source Helm Chart Repository server.
* **Cloud-specific repositories:** Such as Google Cloud Artifact Registry, AWS Elastic Container Registry (ECR) Public/Private, Azure Container Registry.
* **GitHub Pages:** A simple way to host static Helm charts.
* **OCI Registries:** Using Docker registries (like Docker Hub, GCR, ACR) to store Helm charts as OCI artifacts.

Here's a general process for pushing to a remote repository, focusing on OCI registries as a modern and common approach:

### Package the Helm Chart

First, package your Helm chart into a .tgz archive.

```bash
helm package ./my-app-chart
```

This creates a compressed archive (e.g., my-app-chart-0.1.0.tgz) of your Helm chart, ready for distribution or pushing to a repository.

This will create a file like my-app-chart-0.1.0.tgz in your current directory.

### Authenticate to the OCI Registry

Before pushing, you need to authenticate your Helm client with the target OCI registry. The exact command depends on your registry.

**For Docker Hub (or any OCI registry that uses Docker CLI for auth):**

```bash
docker login your-registry.example.com
# Example: docker login ghcr.io (for GitHub Container Registry)
```

**For Google Cloud Artifact Registry:**

```bash
gcloud auth configure-docker your-region-docker.pkg.dev
# Example: gcloud auth configure-docker us-central1-docker.pkg.dev
```

**For AWS ECR:**

```bash
aws ecr get-login-password --region your-region | docker login --username AWS --password-stdin your-aws-account-id.dkr.ecr.your-region.amazonaws.com
```

### Push the Chart to the OCI Registry

Once authenticated, use the `helm push` command with the OCI prefix.

```bash
helm push my-app-chart-0.1.0.tgz oci://your-registry.example.com/charts
# Example: helm push my-app-chart-0.1.0.tgz oci://ghcr.io/my-org/charts
# Example: helm push my-app-chart-0.1.0.tgz oci://us-central1-docker.pkg.dev/my-project/my-repo
```

### Verify the Pushed Chart

You can verify that the chart has been pushed by listing charts in the remote repository (if the registry supports it) or by attempting to pull it.

```bash
helm pull oci://your-registry.example.com/charts/my-app-chart --version 0.1.0
```

This downloads the specified Helm chart from the OCI registry to your local machine, verifying its availability.

:::tip
For organizations with multiple teams, consider setting up a centralized Helm chart repository that follows consistent standards for chart structure, naming conventions, and version management.
:::

## Advanced Considerations and Troubleshooting

This section provides additional steps for a more robust deployment and guidance on resolving common issues, specifically in the context of Helm.

### Image Management for Production

For production deployments, simply relying on local Docker images is insufficient. You need an image registry.

**Build Docker Images:**

```bash
docker build -t your-registry/your-image-name:tag .
```

This builds your Docker image and tags it with your registry's address, image name, and a specific tag (e.g., version number).

**Push to a Container Registry:**

```bash
docker push your-registry/your-image-name:tag
```

This uploads your tagged Docker image to the specified container registry, making it accessible to your Kubernetes cluster.

**Update Helm values.yaml:**

Change the `image.repository` and `image.tag` fields in your Helm chart's values.yaml to point to the registry path:

```yaml
app:
  image:
    repository: your-registry/your-image-name
    tag: tag
```

**For private registries**, configure imagePullSecrets in your Helm chart:

```yaml
# In values.yaml
imagePullSecrets:
  - name: regcred

# In templates/deployment.yaml
spec:
  template:
    spec:
      imagePullSecrets:
        {{- toYaml .Values.imagePullSecrets | nindent 8 }}
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

**Enable Dashboard (Minikube):**

```bash
minikube dashboard
```

This opens the Kubernetes Dashboard in your default web browser. Minikube automatically handles proxying the dashboard service.

Use this interface to visually inspect your deployments, pods, services, and other resources.

### Security Best Practices

#### Secrets Management

Always use Kubernetes Secrets for sensitive data. In Helm, ensure secrets are either created separately or managed via a robust secret management solution (e.g., Vault, AWS Secrets Manager) rather than directly embedding sensitive data in values.yaml.

Example of creating a Secret outside of Helm:

```bash
kubectl create secret generic app-secrets \
  --from-literal=postgres-password=your-password \
  --from-literal=api-key=your-api-key
```

Then reference it in your Helm templates:

```yaml
env:
  - name: POSTGRES_PASSWORD
    valueFrom:
      secretKeyRef:
        name: app-secrets
        key: postgres-password
```

#### Network Policies

Implement Kubernetes NetworkPolicies to control traffic flow between pods and external services, enhancing security.

Example NetworkPolicy in your Helm chart:

```yaml
# templates/network-policy.yaml
{{- if .Values.networkPolicy.enabled }}
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: {{ include "my-app.fullname" . }}-db-policy
spec:
  podSelector:
    matchLabels:
      {{- include "my-app.selectorLabels" . | nindent 6 }}
      component: db
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          {{- include "my-app.selectorLabels" . | nindent 10 }}
          component: app
    ports:
    - protocol: TCP
      port: 5432
{{- end }}
```

#### Resource Limits

Define `resources.requests` and `resources.limits` for all containers in your Helm chart's deployments to prevent resource exhaustion and ensure stable performance.

```yaml
# In values.yaml
app:
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 200m
      memory: 256Mi

# In templates/deployment.yaml
resources:
  {{- toYaml .Values.app.resources | nindent 12 }}
```

#### Least Privilege

Configure Kubernetes RBAC (Role-Based Access Control) to grant only the necessary permissions to users and service accounts.

Example RBAC configuration in your Helm chart:

```yaml
# templates/rbac.yaml
{{- if .Values.rbac.create }}
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: {{ include "my-app.fullname" . }}
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list", "watch"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: {{ include "my-app.fullname" . }}
subjects:
- kind: ServiceAccount
  name: {{ include "my-app.serviceAccountName" . }}
roleRef:
  kind: Role
  name: {{ include "my-app.fullname" . }}
  apiGroup: rbac.authorization.k8s.io
{{- end }}
```

### Common Troubleshooting Scenarios

#### Chart Installation Fails

If your Helm chart installation fails, use the following commands to diagnose the issue:

```bash
# Check the Helm release status
helm status my-app

# Enable debug output during installation
helm install my-app ./my-app-chart --debug

# Check Kubernetes events
kubectl get events --sort-by='.lastTimestamp'
```

#### Pod Stuck in Pending or CrashLoopBackOff

If pods are not starting properly after deployment:

```bash
# Get details about the pod
kubectl describe pod <pod-name>

# Check pod logs
kubectl logs <pod-name>

# For init container issues
kubectl logs <pod-name> -c <init-container-name>
```

#### Database Connection Issues

If your application can't connect to the database:

```bash
# Check if the database service exists
kubectl get svc

# Verify the database pod is running
kubectl get pods -l component=db

# Test connectivity from another pod
kubectl run -it --rm debug --image=alpine -- sh
# Then inside the container:
# apk add --no-cache postgresql-client
# psql -h db-service -U myuser -d mydatabase
```

#### Ingress Not Working

If your application is not accessible via Ingress:

```bash
# Check Ingress resource
kubectl get ingress

# Verify Ingress controller is running
kubectl get pods -n ingress-nginx

# Check Ingress logs
kubectl logs -n ingress-nginx <ingress-controller-pod>
```

:::note Debugging Workflow
When troubleshooting Helm and Kubernetes issues, follow this general workflow:
1. Check release status: `helm status my-app`.
2. Examine rendered templates: `helm get manifest my-app`.
3. Inspect Kubernetes resources: `kubectl describe` relevant resources.
4. Check pod logs: `kubectl logs <pod-name>`.
5. Look at events: `kubectl get events`.
:::

## Cleanup (Optional)

To remove all deployed Kubernetes resources managed by Helm and stop/delete your Minikube cluster, follow these steps:

### Uninstall Helm Release

```bash
helm uninstall my-app
```

This uninstalls the Helm release named 'my-app', which deletes all Kubernetes resources (Deployments, Services, PVCs, etc.) that were created by this Helm chart.

### Stop/Delete Minikube Cluster

```bash
minikube stop armadalocal
```

This stops the Minikube cluster VM, freeing up system resources. The cluster state is preserved.

```bash
minikube delete armadalocal
```

This permanently deletes the Minikube cluster VM and all associated data. Use this when you no longer need the cluster.

:::caution
The `minikube delete` command will permanently delete all resources in your cluster. Make sure you have backed up any important data before running this command.
:::

## Conclusion and Next Steps

In this guide, we've explored multiple approaches to converting Docker Compose files to Helm charts:

1. **Using Kompose** for a basic automated conversion.
2. **Using Katenary** for a more refined conversion with better templating.
3. **Using Score** for a platform-agnostic workload definition.

We've also covered important aspects of working with Helm charts:

- Deploying charts to a Kubernetes cluster.
- Verifying and testing charts locally.
- Sharing charts through repositories.
- Implementing security best practices.
- Troubleshooting common issues.

### Where to Go from Here

As you continue your Kubernetes and Helm journey, consider exploring:

1. **CI/CD Integration**: Automate your Helm chart deployment using CI/CD pipelines with tools like Jenkins, GitHub Actions, or GitLab CI.
2. **Infrastructure as Code**: Combine Helm with tools like Terraform or Pulumi to manage both your Kubernetes clusters and applications.
3. **Advanced Helm Features**:
   - Subchart dependencies.
   - Custom hook integration.
   - Post-rendering with Kustomize.
4. **Kubernetes Operators**: For complex, stateful applications, consider developing Kubernetes Operators that extend Kubernetes' capabilities with application-specific logic.
5. **Monitoring and Observability**: Integrate tools like Prometheus, Grafana, and Jaeger into your Helm deployments for comprehensive monitoring.

Remember that while automated tools can help with the initial conversion from Docker Compose to Helm, understanding the underlying Kubernetes concepts and Helm templating is essential for creating production-ready, maintainable charts.

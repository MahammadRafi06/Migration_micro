# Security Considerations for the Armada Edge Platform

Learn essential security practices and considerations when packaging applications for deployment on the Armada Edge Platform.

## Overview

Security in edge computing environments requires special attention due to distributed infrastructure and potential exposure to diverse threat vectors. This guide covers critical security measures for application packaging and deployment.

## Container Security

### Secure Base Images

```dockerfile
# Avoid using latest or unknown base images
FROM ubuntu:latest

# Use specific, minimal, and trusted base images
FROM alpine:3.18.4
# or
FROM gcr.io/distroless/java:11-debian11

# Use official images with security patches
FROM nginx:1.25.3-alpine
```

### Non-Root User Implementation

```dockerfile
# Create dedicated user and group
RUN addgroup -g 1001 -S appgroup && \
    adduser -S appuser -u 1001 -G appgroup

# Set proper ownership
COPY --chown=appuser:appgroup . /app

# Switch to non-root user
USER appuser
```

### Image Vulnerability Scanning

```bash
# Using Trivy for vulnerability scanning
trivy image myapp:latest

# Using Docker Scout
docker scout cves myapp:latest

# CI/CD integration example
docker build -t myapp:latest .
trivy image --exit-code 1 --severity HIGH,CRITICAL myapp:latest
```

## Secrets Management

### Kubernetes Secrets Best Practices

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: production
  annotations:
    # Rotation metadata
    security.armada.io/rotation-schedule: "90d"
    security.armada.io/last-rotated: "2024-01-01"
type: Opaque
data:
  # Always use base64 encoded values
  database-password: <base64-encoded-password>
  api-key: <base64-encoded-key>
  jwt-signing-key: <base64-encoded-jwt-key>
```

### External Secret Management

```yaml
# Using External Secrets Operator with HashiCorp Vault
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-backend
spec:
  provider:
    vault:
      server: "https://vault.example.com"
      path: "secret"
      version: "v2"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "myapp-role"
          serviceAccountRef:
            name: vault-auth

---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: app-external-secret
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: app-secrets
    creationPolicy: Owner
  data:
  - secretKey: database-password
    remoteRef:
      key: myapp/database
      property: password
```

### Secret Rotation

```yaml
# Automated secret rotation job
apiVersion: batch/v1
kind: CronJob
metadata:
  name: secret-rotation
spec:
  schedule: "0 2 1 * *"  # Monthly at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: secret-rotator
          containers:
          - name: rotator
            image: secret-rotator:latest
            env:
            - name: TARGET_SECRETS
              value: "app-secrets,database-secrets"
            - name: VAULT_ADDR
              value: "https://vault.example.com"
          restartPolicy: OnFailure
```

## Pod Security Standards

### Pod Security Context

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: secure-app
spec:
  template:
    spec:
      securityContext:
        # Run as non-root user
        runAsNonRoot: true
        runAsUser: 1001
        runAsGroup: 1001
        fsGroup: 1001
        # Prevent privilege escalation
        seccompProfile:
          type: RuntimeDefault
      containers:
      - name: app
        image: myapp:latest
        securityContext:
          # Container-level security
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
            add:
            - NET_BIND_SERVICE  # Only if needed
        # Temporary filesystem for writes
        volumeMounts:
        - name: tmp
          mountPath: /tmp
        - name: var-cache
          mountPath: /var/cache
      volumes:
      - name: tmp
        emptyDir: {}
      - name: var-cache
        emptyDir: {}
```

### Pod Security Policies/Standards

```yaml
# Pod Security Standards enforcement
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

## Network Security

### Network Policies

```yaml
# Default deny all traffic
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress

---
# Allow specific traffic to app
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: app-network-policy
spec:
  podSelector:
    matchLabels:
      app: myapp
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          role: frontend
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          role: database
    ports:
    - protocol: TCP
      port: 5432
  - to: []  # Allow DNS
    ports:
    - protocol: UDP
      port: 53
```

### Service Mesh Security

```yaml
# Istio security policies
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: STRICT

---
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: app-authz
  namespace: production
spec:
  selector:
    matchLabels:
      app: myapp
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/frontend/sa/frontend-service"]
  - to:
    - operation:
        methods: ["GET", "POST"]
```

## RBAC and Service Accounts

### Service Account Configuration

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: myapp-service-account
  namespace: production
automountServiceAccountToken: false  # Disable auto-mounting

---
# Mount token only when needed
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  template:
    spec:
      serviceAccountName: myapp-service-account
      automountServiceAccountToken: true  # Enable only if needed
```

### RBAC Configuration

```yaml
# Role for application-specific permissions
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: myapp-role
  namespace: production
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get", "list"]
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get"]
  resourceNames: ["app-secrets"]  # Specific secret only

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: myapp-rolebinding
  namespace: production
subjects:
- kind: ServiceAccount
  name: myapp-service-account
  namespace: production
roleRef:
  kind: Role
  name: myapp-role
  apiGroup: rbac.authorization.k8s.io
```

## Security Monitoring

### Security Audit Logging

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: audit-policy
data:
  audit-policy.yaml: |
    apiVersion: audit.k8s.io/v1
    kind: Policy
    rules:
    # Log security-related events
    - level: Metadata
      namespaces: ["production"]
      resources:
      - group: ""
        resources: ["secrets", "serviceaccounts"]
    - level: Request
      namespaces: ["production"]
      resources:
      - group: "rbac.authorization.k8s.io"
        resources: ["roles", "rolebindings"]
```

### Runtime Security Monitoring

```yaml
# Falco security monitoring
apiVersion: v1
kind: ConfigMap
metadata:
  name: falco-config
data:
  falco.yaml: |
    rules_file:
      - /etc/falco/falco_rules.yaml
      - /etc/falco/falco_rules.local.yaml
    json_output: true
    log_level: info
    priority: warning
    
  falco_rules.local.yaml: |
    - rule: Detect shell in container
      desc: Notice shell activity within a container
      condition: >
        spawned_process and container and
        proc.name in (shell_binaries)
      output: >
        Shell spawned in container (user=%user.name container=%container.name
        proc=%proc.name parent=%proc.pname cmdline=%proc.cmdline)
      priority: WARNING
```

## Edge-Specific Security

### Certificate Management

```yaml
# cert-manager for automatic certificate provisioning
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: app-tls
  namespace: production
spec:
  secretName: app-tls-secret
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
  - myapp.example.com
  - api.myapp.example.com

---
# Using certificate in ingress
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - myapp.example.com
    secretName: app-tls-secret
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: myapp-service
            port:
              number: 80
```

### Edge Node Security

```yaml
# Node security constraints
apiVersion: apps/v1
kind: Deployment
metadata:
  name: edge-secure-app
spec:
  template:
    spec:
      # Ensure deployment on trusted edge nodes
      nodeSelector:
        security-tier: "trusted"
        compliance: "certified"
      
      # Tolerate security-focused taints
      tolerations:
      - key: "security-hardened"
        operator: "Equal"
        value: "true"
        effect: "NoSchedule"
      
      # Security-focused affinity
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: "security-compliance"
                operator: In
                values: ["fips-140", "common-criteria"]
```

## Security Testing

### Container Security Scanning

```bash
#!/bin/bash
# Comprehensive security scanning pipeline

# Build image
docker build -t myapp:latest .

# Vulnerability scanning
echo "Running vulnerability scan..."
trivy image --exit-code 1 --severity HIGH,CRITICAL myapp:latest

# Configuration scanning
echo "Running configuration scan..."
docker run --rm -v $(pwd):/workspace \
  aquasec/trivy config /workspace

# Secret scanning
echo "Running secret scan..."
docker run --rm -v $(pwd):/workspace \
  trufflesecurity/trufflehog:latest filesystem /workspace

echo "Security scans completed successfully"
```

### Penetration Testing

```yaml
# Security testing job
apiVersion: batch/v1
kind: Job
metadata:
  name: security-test
spec:
  template:
    spec:
      containers:
      - name: security-test
        image: owasp/zap2docker-stable:latest
        command:
        - /bin/bash
        - -c
        - |
          zap-baseline.py -t http://myapp-service:80 \
            -J security-report.json \
            -r security-report.html
        volumeMounts:
        - name: reports
          mountPath: /zap/wrk
      volumes:
      - name: reports
        emptyDir: {}
      restartPolicy: Never
```

## Security Checklist

Before deploying your application, use this checklist to ensure all critical security measures are in place.

### Container Security

- [ ] **Base Images** - Using minimal, trusted base images.
- [ ] **Non-Root User** - Running as non-privileged user.
- [ ] **Vulnerability Scanning** - No critical vulnerabilities.
- [ ] **Read-Only Filesystem** - Using read-only root filesystem.
- [ ] **Dropped Capabilities** - Minimal required capabilities only.
- [ ] **Image Signing** - Container images digitally signed.

### Kubernetes Security

- [ ] **Pod Security Standards** - Restricted PSS enforced.
- [ ] **Network Policies** - Traffic properly restricted.
- [ ] **RBAC** - Least privilege access controls.
- [ ] **Service Accounts** - Dedicated service accounts.
- [ ] **Secrets Management** - Proper secret handling.
- [ ] **Security Contexts** - Appropriate security contexts.

### Edge Security

- [ ] **Certificate Management** - Automated cert provisioning.
- [ ] **Node Security** - Trusted edge node deployment.
- [ ] **Data Encryption** - Data encrypted in transit/rest.
- [ ] **Audit Logging** - Security events logged.
- [ ] **Runtime Monitoring** - Security monitoring enabled.

## Next Steps

- [Application Lifecycle Management](../application-lifecycle/overview.md) - Secure deployment and updates.
- [Platform Security](../platform-deep-dive/security/overview.md) - Platform-level security features.
- [Compliance and Certifications](../platform-deep-dive/security/compliance-certifications.md) - Regulatory compliance.

---

:::warning Security is a Journey
Security is not a one-time configuration but an ongoing process. Regularly update dependencies, rotate secrets, monitor for threats, and stay informed about new security best practices.
::: 
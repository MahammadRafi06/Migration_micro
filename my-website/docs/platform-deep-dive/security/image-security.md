---
id: image-security
title: Image Security
sidebar_label: Image Security
sidebar_position: 3
---

# Image Security

Container image security scanning, vulnerability management, and secure image pipeline practices.

## Overview

Image security is crucial for edge deployments where containers run with varying levels of network connectivity and may be deployed across numerous edge locations.

## Image Scanning

### Vulnerability Scanning with Trivy

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: image-security-scan
  namespace: security
spec:
  template:
    spec:
      containers:
      - name: trivy-scanner
        image: aquasec/trivy:latest
        command:
        - trivy
        - image
        - --format
        - json
        - --output
        - /tmp/scan-results.json
        - myapp:latest
        volumeMounts:
        - name: scan-results
          mountPath: /tmp
      volumes:
      - name: scan-results
        emptyDir: {}
      restartPolicy: Never
```

### Admission Controller for Image Scanning

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: image-policy
  namespace: security
data:
  policy.yaml: |
    images:
      policies:
      - pattern: "*"
        requirements:
          max_severity: "MEDIUM"
          trusted_registries:
            - "registry.edge.example.com"
            - "docker.io/library"
        exceptions:
          - image: "utility/debug:latest"
            reason: "debugging tool"
```

## Secure Image Registries

### Private Registry Configuration

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: registry-credentials
  namespace: default
type: kubernetes.io/dockerconfigjson
data:
  .dockerconfigjson: <base64-encoded-docker-config>
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: registry-service-account
  namespace: default
imagePullSecrets:
- name: registry-credentials
```

### Registry Mirror for Edge

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: registry-mirror-config
  namespace: kube-system
data:
  daemon.json: |
    {
      "registry-mirrors": [
        "https://mirror.edge.example.com"
      ],
      "insecure-registries": [
        "local-registry.edge.local:5000"
      ]
    }
```

## Image Signing and Verification

### Cosign Integration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cosign-policy
  namespace: security
data:
  policy.yaml: |
    apiVersion: v1alpha1
    kind: ClusterImagePolicy
    metadata:
      name: signed-images-policy
    spec:
      images:
      - glob: "registry.edge.example.com/**"
      authorities:
      - keyless:
          url: "https://fulcio.sigstore.dev"
          identities:
          - issuer: "https://github.com/login/oauth"
            subject: "https://github.com/edge-platform/*"
```

## Runtime Security

### Pod Security Standards

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### Security Context Configuration

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: secure-app
spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 2000
        seccompProfile:
          type: RuntimeDefault
      containers:
      - name: app
        image: secure-app:latest
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          capabilities:
            drop:
            - ALL
            add:
            - NET_BIND_SERVICE
```

## Best Practices

### Image Hardening
- Use minimal base images.
- Regular security updates.
- Remove unnecessary packages.
- Non-root user execution.

### Supply Chain Security
- Image signing and verification.
- Trusted registries.
- Build-time security scanning.
- Software Bill of Materials (SBOM).

## Next Steps

Continue to [Network Security](./network-security) to learn about network-level security controls and monitoring. 
---
id: secrets-management
title: Secrets Management
sidebar_label: Secrets Management
sidebar_position: 2
---

# Secrets Management

Comprehensive strategies for secure handling of sensitive data across edge deployments.

## Overview

Secrets management is critical for edge environments where sensitive data like API keys, certificates, and passwords must be securely stored, distributed, and rotated across geographically distributed locations.

## Kubernetes Native Secrets

### Basic Secret Creation

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-credentials
  namespace: production
type: Opaque
data:
  username: <base64-encoded-username>
  password: <base64-encoded-password>
  api-key: <base64-encoded-api-key>
---
apiVersion: v1
kind: Secret
metadata:
  name: tls-certificate
  namespace: production
type: kubernetes.io/tls
data:
  tls.crt: <base64-encoded-certificate>
  tls.key: <base64-encoded-private-key>
```

### Secret Consumption Patterns

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: secure-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: secure-app
  template:
    metadata:
      labels:
        app: secure-app
    spec:
      containers:
      - name: app
        image: secure-app:latest
        env:
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: app-credentials
              key: password
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: app-credentials
              key: api-key
        volumeMounts:
        - name: tls-certs
          mountPath: /etc/ssl/certs
          readOnly: true
      volumes:
      - name: tls-certs
        secret:
          secretName: tls-certificate
```

## External Secret Management

### HashiCorp Vault Integration

```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-secret-store
  namespace: production
spec:
  provider:
    vault:
      server: "https://vault.edge.example.com:8200"
      path: "secret"
      version: "v2"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "edge-platform"
          serviceAccountRef:
            name: vault-auth-sa
---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: vault-secret
  namespace: production
spec:
  refreshInterval: 15s
  secretStoreRef:
    name: vault-secret-store
    kind: SecretStore
  target:
    name: app-vault-secret
    creationPolicy: Owner
  data:
  - secretKey: password
    remoteRef:
      key: database
      property: password
  - secretKey: api-key
    remoteRef:
      key: external-api
      property: key
```

### AWS Secrets Manager

```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secret-store
  namespace: production
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
      auth:
        secretRef:
          accessKeyIDSecretRef:
            name: aws-credentials
            key: access-key-id
          secretAccessKeySecretRef:
            name: aws-credentials
            key: secret-access-key
---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: aws-secret
  namespace: production
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secret-store
    kind: SecretStore
  target:
    name: aws-app-secret
    creationPolicy: Owner
  data:
  - secretKey: database-url
    remoteRef:
      key: "prod/database"
      property: "url"
```

### Azure Key Vault

```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: azure-secret-store
  namespace: production
spec:
  provider:
    azurekv:
      vaultUrl: "https://edge-vault.vault.azure.net"
      authType: ManagedIdentity
      identityId: "abc123-def456-ghi789"
---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: azure-secret
  namespace: production
spec:
  refreshInterval: 30m
  secretStoreRef:
    name: azure-secret-store
    kind: SecretStore
  target:
    name: azure-app-secret
  data:
  - secretKey: connection-string
    remoteRef:
      key: "database-connection"
```

## Secret Encryption at Rest

### Encryption Configuration

```yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
- resources:
  - secrets
  providers:
  - aescbc:
      keys:
      - name: key1
        secret: <32-byte-base64-encoded-key>
  - identity: {}
- resources:
  - configmaps
  providers:
  - aescbc:
      keys:
      - name: key1
        secret: <32-byte-base64-encoded-key>
  - identity: {}
```

### Key Rotation

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: encryption-key-rotation
  namespace: kube-system
spec:
  schedule: "0 2 1 * *"  # Monthly on the 1st at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: key-rotator
            image: key-management:latest
            command:
            - /bin/sh
            - -c
            - |
              # Generate new encryption key
              NEW_KEY=$(openssl rand -base64 32)
              
              # Update encryption configuration
              kubectl patch encryptionconfig default \
                --type='json' \
                -p='[{"op": "add", "path": "/resources/0/providers/0/aescbc/keys/0", "value": {"name": "key2", "secret": "'$NEW_KEY'"}}]'
              
              # Restart API server to pick up new config
              kubectl rollout restart deployment/kube-apiserver -n kube-system
          restartPolicy: OnFailure
```

## Secret Lifecycle Management

### Automated Secret Rotation

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: secret-rotation-config
  namespace: secret-management
data:
  rotation-schedule.yaml: |
    secrets:
      - name: database-credentials
        namespace: production
        rotation-interval: "30d"
        type: "database"
        provider: "vault"
      - name: api-keys
        namespace: production
        rotation-interval: "7d"
        type: "api-key"
        provider: "aws-secrets-manager"
      - name: tls-certificates
        namespace: production
        rotation-interval: "90d"
        type: "certificate"
        provider: "cert-manager"
```

### Secret Versioning

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: versioned-secret
  namespace: production
  annotations:
    external-secrets.io/force-refresh: "true"
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-secret-store
    kind: SecretStore
  target:
    name: app-secret-v2
    creationPolicy: Owner
    template:
      metadata:
        annotations:
          secret-version: "{{ .version }}"
          last-updated: "{{ .timestamp }}"
  data:
  - secretKey: current-password
    remoteRef:
      key: database
      property: password
      version: "latest"
  - secretKey: previous-password
    remoteRef:
      key: database
      property: password
      version: "previous"
```

## Certificate Management

### Cert-Manager Integration

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: edge-ca-issuer
spec:
  ca:
    secretName: edge-ca-key-pair
---
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: edge-app-tls
  namespace: production
spec:
  secretName: edge-app-tls-secret
  issuerRef:
    name: edge-ca-issuer
    kind: ClusterIssuer
  commonName: app.edge.example.com
  dnsNames:
  - app.edge.example.com
  - api.edge.example.com
  duration: 2160h  # 90 days
  renewBefore: 360h  # 15 days
```

### Automatic Certificate Rotation

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: auto-renew-cert
  namespace: production
  annotations:
    cert-manager.io/revision-history-limit: "3"
spec:
  secretName: auto-renew-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  commonName: auto.edge.example.com
  dnsNames:
  - auto.edge.example.com
  duration: 2160h
  renewBefore: 720h  # Renew 30 days before expiry
  subject:
    organizationalUnits:
    - "Edge Platform"
  privateKey:
    algorithm: RSA
    size: 2048
    rotationPolicy: Always
```

## Edge-Specific Secret Patterns

### Regional Secret Distribution

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: regional-secret-config
  namespace: secret-management
data:
  distribution-policy.yaml: |
    regions:
      us-east:
        secrets:
          - database-credentials
          - api-keys
        encryption-key: "us-east-key"
      us-west:
        secrets:
          - database-credentials
          - api-keys
        encryption-key: "us-west-key"
      eu-central:
        secrets:
          - database-credentials
          - api-keys
          - gdpr-compliance-key
        encryption-key: "eu-central-key"
```

### Offline Secret Caching

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: secret-cache
  namespace: edge-system
spec:
  selector:
    matchLabels:
      app: secret-cache
  template:
    metadata:
      labels:
        app: secret-cache
    spec:
      containers:
      - name: secret-cache
        image: secret-cache:latest
        env:
        - name: CACHE_DURATION
          value: "24h"
        - name: SYNC_INTERVAL
          value: "1h"
        - name: ENCRYPTION_KEY
          valueFrom:
            secretKeyRef:
              name: cache-encryption-key
              key: key
        volumeMounts:
        - name: cache-storage
          mountPath: /var/cache/secrets
      volumes:
      - name: cache-storage
        hostPath:
          path: /opt/edge/secret-cache
          type: DirectoryOrCreate
```

## Security Best Practices

### Secret Access Control

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: production
  name: secret-reader
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "list"]
  resourceNames: ["app-credentials", "tls-certificate"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: secret-reader-binding
  namespace: production
subjects:
- kind: ServiceAccount
  name: app-service-account
  namespace: production
roleRef:
  kind: Role
  name: secret-reader
  apiGroup: rbac.authorization.k8s.io
```

### Secret Scanning

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: secret-scanner
  namespace: security
spec:
  schedule: "0 3 * * *"  # Daily at 3 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: scanner
            image: secret-scanner:latest
            command:
            - /bin/sh
            - -c
            - |
              # Scan for exposed secrets in logs
              kubectl logs --all-namespaces --since=24h | \
                grep -E "(password|secret|key|token)" | \
                grep -v "redacted" > /tmp/exposed-secrets.log
              
              # Check for hardcoded secrets in configurations
              kubectl get configmaps --all-namespaces -o yaml | \
                grep -E "(password|secret|key|token)" > /tmp/config-secrets.log
              
              # Generate security report
              if [ -s /tmp/exposed-secrets.log ] || [ -s /tmp/config-secrets.log ]; then
                echo "Potential secret exposure detected"
                # Send alert
              fi
          restartPolicy: OnFailure
```

## Monitoring and Alerting

### Secret Usage Monitoring

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: secret-monitoring
  namespace: monitoring
data:
  prometheus-rules.yaml: |
    groups:
    - name: secret-monitoring
      rules:
      - alert: SecretExpiringSoon
        expr: (cert_manager_certificate_expiration_timestamp_seconds - time()) < 7*24*3600
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "Certificate expiring soon"
          description: "Certificate {{ $labels.name }} expires in less than 7 days"
      
      - alert: SecretAccessFailure
        expr: increase(kubernetes_audit_total{verb="get",objectRef_resource="secrets",objectRef_name!=""}[5m]) > 10
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High number of secret access failures"
          description: "Unusual number of failed secret access attempts detected"
```

### Audit Logging

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: secret-audit-policy
  namespace: kube-system
data:
  audit-policy.yaml: |
    apiVersion: audit.k8s.io/v1
    kind: Policy
    rules:
    - level: Metadata
      resources:
      - group: ""
        resources: ["secrets"]
      verbs: ["get", "create", "update", "patch", "delete"]
    - level: Request
      resources:
      - group: "external-secrets.io"
        resources: ["externalsecrets"]
      verbs: ["create", "update", "patch", "delete"]
```

## Troubleshooting

### Common Issues

```bash
# Check secret existence
kubectl get secrets -n production

# Describe secret (without exposing data)
kubectl describe secret app-credentials -n production

# Verify secret data structure
kubectl get secret app-credentials -n production -o yaml

# Check external secret status
kubectl describe externalsecret vault-secret -n production

# Debug secret store connection
kubectl logs -n external-secrets-system deployment/external-secrets
```

### Certificate Issues

```bash
# Check certificate status
kubectl describe certificate edge-app-tls -n production

# View cert-manager logs
kubectl logs -n cert-manager deployment/cert-manager

# Check certificate expiration
kubectl get certificate -A --sort-by=.status.notAfter

# Test certificate validation
openssl x509 -in cert.pem -text -noout
```

## Best Practices

### Security Hardening
- Use external secret management systems
- Implement proper RBAC for secret access
- Regular secret rotation
- Encryption at rest and in transit

### Monitoring and Alerting
- Secret usage tracking
- Certificate expiration monitoring
- Access failure alerts
- Compliance auditing

## Next Steps

Continue to [Image Security](./image-security) to learn about container image security scanning and management practices. 
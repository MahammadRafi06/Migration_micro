# Helm Charts for AEP Applications

Learn how to create and manage Helm charts for efficient application deployment on the Armada Edge Platform.

## Overview

Helm charts provide a powerful way to package, configure, and deploy applications on Kubernetes. This guide covers best practices for creating Helm charts optimized for edge deployments on AEP.

## Chart Structure

### Basic Chart Layout

```
myapp-chart/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   ├── ingress.yaml
│   ├── serviceaccount.yaml
│   ├── NOTES.txt
│   └── _helpers.tpl
├── charts/
└── README.md
```

### Chart.yaml

```yaml
apiVersion: v2
name: myapp
description: A Helm chart for MyApp on AEP
type: application
version: 0.1.0
appVersion: "1.0.0"
keywords:
  - edge
  - microservice
  - web
home: https://github.com/myorg/myapp
sources:
  - https://github.com/myorg/myapp
maintainers:
  - name: Platform Team
    email: platform@myorg.com
dependencies:
  - name: postgresql
    version: "11.6.12"
    repository: "https://charts.bitnami.com/bitnami"
    condition: postgresql.enabled
annotations:
  category: Application
```

## Values Configuration

### values.yaml

```yaml
# Default values for myapp
replicaCount: 3

image:
  repository: myregistry/myapp
  pullPolicy: IfNotPresent
  tag: ""

imagePullSecrets: []
nameOverride: ""
fullnameOverride: ""

serviceAccount:
  create: true
  annotations: {}
  name: ""

podAnnotations: {}

podSecurityContext:
  fsGroup: 2000
  runAsNonRoot: true
  runAsUser: 1000

securityContext:
  allowPrivilegeEscalation: false
  capabilities:
    drop:
    - ALL
  readOnlyRootFilesystem: true

service:
  type: ClusterIP
  port: 80
  targetPort: 3000

ingress:
  enabled: false
  className: ""
  annotations: {}
  hosts:
    - host: myapp.local
      paths:
        - path: /
          pathType: Prefix
  tls: []

resources:
  limits:
    cpu: 200m
    memory: 256Mi
  requests:
    cpu: 100m
    memory: 128Mi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

nodeSelector:
  node-type: edge

tolerations:
  - key: "edge-node"
    operator: "Equal"
    value: "true"
    effect: "NoSchedule"

affinity: {}

# Edge-specific configurations
edge:
  enabled: true
  location: "auto"
  bandwidth: "limited"
  
# Application configuration
config:
  debug: false
  logLevel: "info"
  maxConnections: 100
  timeout: "30s"

# Database configuration
postgresql:
  enabled: false
  auth:
    postgresPassword: "changeMe"
    database: "myapp"

# Monitoring
monitoring:
  enabled: true
  serviceMonitor:
    enabled: true
    interval: 30s
```

## Template Examples

### deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "myapp.fullname" . }}
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "myapp.selectorLabels" . | nindent 6 }}
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  template:
    metadata:
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
        {{- with .Values.podAnnotations }}
        {{- toYaml . | nindent 8 }}
        {{- end }}
      labels:
        {{- include "myapp.selectorLabels" . | nindent 8 }}
    spec:
      {{- with .Values.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      serviceAccountName: {{ include "myapp.serviceAccountName" . }}
      securityContext:
        {{- toYaml .Values.podSecurityContext | nindent 8 }}
      containers:
        - name: {{ .Chart.Name }}
          securityContext:
            {{- toYaml .Values.securityContext | nindent 12 }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ .Values.service.targetPort }}
              protocol: TCP
          livenessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
          env:
            - name: NODE_ENV
              value: {{ .Values.environment | default "production" }}
            {{- if .Values.edge.enabled }}
            - name: EDGE_LOCATION
              valueFrom:
                fieldRef:
                  fieldPath: spec.nodeName
            - name: DEPLOYMENT_MODE
              value: "edge"
            {{- end }}
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
          volumeMounts:
            - name: config
              mountPath: /app/config
              readOnly: true
            - name: tmp
              mountPath: /tmp
      volumes:
        - name: config
          configMap:
            name: {{ include "myapp.fullname" . }}-config
        - name: tmp
          emptyDir: {}
      {{- with .Values.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.affinity }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.tolerations }}
      tolerations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
```

### _helpers.tpl

```yaml
{{/*
Expand the name of the chart.
*/}}
{{- define "myapp.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "myapp.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "myapp.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "myapp.labels" -}}
helm.sh/chart: {{ include "myapp.chart" . }}
{{ include "myapp.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "myapp.selectorLabels" -}}
app.kubernetes.io/name: {{ include "myapp.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "myapp.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "myapp.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Edge configuration helper
*/}}
{{- define "myapp.edgeConfig" -}}
{{- if .Values.edge.enabled }}
edge.enabled: "true"
edge.location: {{ .Values.edge.location | quote }}
edge.bandwidth: {{ .Values.edge.bandwidth | quote }}
{{- end }}
{{- end }}
```

## Environment-Specific Values

### values-staging.yaml

```yaml
replicaCount: 2

image:
  tag: staging

ingress:
  enabled: true
  hosts:
    - host: myapp-staging.example.com
      paths:
        - path: /
          pathType: Prefix

resources:
  limits:
    cpu: 100m
    memory: 128Mi
  requests:
    cpu: 50m
    memory: 64Mi

config:
  debug: true
  logLevel: "debug"

edge:
  location: "staging-cluster"
```

### values-production.yaml

```yaml
replicaCount: 5

image:
  tag: v1.0.0

ingress:
  enabled: true
  hosts:
    - host: myapp.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: myapp-tls
      hosts:
        - myapp.example.com

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20

monitoring:
  enabled: true
  serviceMonitor:
    enabled: true

postgresql:
  enabled: true
  auth:
    database: "myapp_prod"
```

## Testing Charts

### Helm Template Testing

```bash
# Render templates locally
helm template myapp ./myapp-chart

# Test with specific values
helm template myapp ./myapp-chart -f values-staging.yaml

# Validate chart
helm lint ./myapp-chart
```

### Chart Testing with helm-unittest

```yaml
# tests/deployment_test.yaml
suite: test deployment
templates:
  - deployment.yaml
tests:
  - it: should create deployment with correct name
    asserts:
      - isKind:
          of: Deployment
      - equal:
          path: metadata.name
          value: RELEASE-NAME-myapp
  
  - it: should set correct image
    set:
      image.repository: custom/myapp
      image.tag: v2.0.0
    asserts:
      - equal:
          path: spec.template.spec.containers[0].image
          value: custom/myapp:v2.0.0
```

## Chart Dependencies

### Chart.yaml Dependencies

```yaml
dependencies:
  - name: postgresql
    version: "11.6.12"
    repository: "https://charts.bitnami.com/bitnami"
    condition: postgresql.enabled
  - name: redis
    version: "16.4.0"
    repository: "https://charts.bitnami.com/bitnami"
    condition: redis.enabled
```

### Managing Dependencies

```bash
# Update dependencies
helm dependency update

# Build dependencies
helm dependency build
```

## Deployment Commands

### Installing the Chart

```bash
# Install with default values
helm install myapp ./myapp-chart

# Install with custom values
helm install myapp ./myapp-chart -f values-production.yaml

# Install in specific namespace
helm install myapp ./myapp-chart -n production --create-namespace

# Dry run installation
helm install myapp ./myapp-chart --dry-run --debug
```

### Upgrading and Managing

```bash
# Upgrade release
helm upgrade myapp ./myapp-chart -f values-production.yaml

# Rollback to previous version
helm rollback myapp 1

# Uninstall release
helm uninstall myapp
```

## Chart Best Practices

### Security

- ✅ Use non-root containers
- ✅ Implement proper RBAC
- ✅ Set resource limits
- ✅ Use read-only filesystems
- ✅ Validate inputs with JSON Schema

### Maintainability

- ✅ Clear documentation in NOTES.txt
- ✅ Comprehensive default values
- ✅ Proper versioning strategy
- ✅ Consistent naming conventions
- ✅ Thorough testing

### Edge Optimization

- ✅ Efficient resource allocation
- ✅ Edge-specific configurations
- ✅ Bandwidth-aware image management
- ✅ Local caching strategies

## Chart Validation Schema

### values.schema.json

```json
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "replicaCount": {
      "type": "integer",
      "minimum": 1,
      "maximum": 100
    },
    "image": {
      "type": "object",
      "properties": {
        "repository": {
          "type": "string"
        },
        "tag": {
          "type": "string"
        },
        "pullPolicy": {
          "type": "string",
          "enum": ["Always", "IfNotPresent", "Never"]
        }
      },
      "required": ["repository"]
    }
  },
  "required": ["replicaCount", "image"]
}
```

## Next Steps

- [Configuration Management](./configuration-management.md) - Advanced configuration strategies
- [Resource Requirements](./resource-requirements.md) - Optimize resource allocation
- [Security Considerations](./security-considerations.md) - Implement security best practices

---

:::tip Chart Repository
Consider publishing your charts to a Helm repository for easy sharing and version management:
```bash
# Package chart
helm package ./myapp-chart

# Publish to repository
helm repo index . --url https://charts.example.com
```
::: 
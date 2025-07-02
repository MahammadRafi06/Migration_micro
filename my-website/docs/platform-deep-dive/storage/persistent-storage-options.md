---
id: persistent-storage-options
title: Persistent Storage Options
sidebar_label: Persistent Storage Options
sidebar_position: 1
---

# Persistent Storage Options

Comprehensive guide to storage solutions and persistent data management for edge deployments.

## Overview

Edge environments require robust storage solutions that can handle intermittent connectivity, limited resources, and distributed data requirements while maintaining high availability and performance.

## Storage Classes

### Local Storage

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: local-storage
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: false
```

### NFS Storage

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nfs-storage
provisioner: example.com/nfs
parameters:
  server: nfs-server.edge.local
  path: /shared/storage
  readOnly: "false"
allowVolumeExpansion: true
volumeBindingMode: Immediate
```

### Cloud Storage Integration

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: cloud-storage
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  encrypted: "true"
  fsType: ext4
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
```

## Persistent Volume Claims

### Database Storage

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: database-storage
  namespace: production
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
  storageClassName: local-storage
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: database
  namespace: production
spec:
  serviceName: database
  replicas: 1
  selector:
    matchLabels:
      app: database
  template:
    metadata:
      labels:
        app: database
    spec:
      containers:
      - name: postgres
        image: postgres:14
        env:
        - name: POSTGRES_DB
          value: "edgedb"
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: username
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: password
        volumeMounts:
        - name: database-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: database-storage
        persistentVolumeClaim:
          claimName: database-storage
```

## Edge-Specific Storage Patterns

### Distributed Storage with Longhorn

```yaml
apiVersion: longhorn.io/v1beta1
kind: Volume
metadata:
  name: edge-distributed-volume
  namespace: longhorn-system
spec:
  size: "50Gi"
  numberOfReplicas: 2
  staleReplicaTimeout: 30
  nodeSelector:
    - "edge.platform.io/region=us-east"
  diskSelector:
    - "node.longhorn.io/create-default-disk=true"
  dataLocality: "best-effort"
```

### Regional Data Replication

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: replication-policy
  namespace: storage-system
data:
  policy.yaml: |
    replication:
      primary_region: "us-east"
      replica_regions:
        - "us-west"
        - "eu-central"
      sync_mode: "async"
      backup_schedule: "0 2 * * *"
      retention_policy: "30d"
```

## Data Synchronization

### Multi-Site Data Sync

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: data-sync
  namespace: storage-system
spec:
  schedule: "*/15 * * * *"  # Every 15 minutes
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: sync-agent
            image: rsync:latest
            command:
            - /bin/sh
            - -c
            - |
              # Sync data between edge sites
              rsync -avz --delete \
                /data/local/ \
                sync-user@remote-site.edge.local:/data/remote/
            volumeMounts:
            - name: local-data
              mountPath: /data/local
            - name: sync-credentials
              mountPath: /etc/ssh
              readOnly: true
          volumes:
          - name: local-data
            persistentVolumeClaim:
              claimName: local-data-pvc
          - name: sync-credentials
            secret:
              secretName: sync-ssh-keys
          restartPolicy: OnFailure
```

## Backup and Recovery

### Automated Backup

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: storage-backup
  namespace: backup-system
spec:
  schedule: "0 3 * * *"  # Daily at 3 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup-agent
            image: backup-tools:latest
            command:
            - /bin/sh
            - -c
            - |
              # Create timestamped backup
              BACKUP_NAME="backup-$(date +%Y%m%d-%H%M%S)"
              
              # Backup persistent volumes
              kubectl get pv -o json > /backups/${BACKUP_NAME}-pvs.json
              
              # Backup application data
              tar -czf /backups/${BACKUP_NAME}-data.tar.gz /data/
              
              # Upload to remote storage
              aws s3 cp /backups/${BACKUP_NAME}-* s3://edge-backups/
            env:
            - name: AWS_ACCESS_KEY_ID
              valueFrom:
                secretKeyRef:
                  name: backup-credentials
                  key: access-key
            - name: AWS_SECRET_ACCESS_KEY
              valueFrom:
                secretKeyRef:
                  name: backup-credentials
                  key: secret-key
            volumeMounts:
            - name: backup-storage
              mountPath: /backups
            - name: data-to-backup
              mountPath: /data
              readOnly: true
          volumes:
          - name: backup-storage
            emptyDir: {}
          - name: data-to-backup
            persistentVolumeClaim:
              claimName: application-data
          restartPolicy: OnFailure
```

## Performance Optimization

### Storage Performance Monitoring

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: storage-monitoring
  namespace: monitoring
data:
  prometheus-rules.yaml: |
    groups:
    - name: storage-performance
      rules:
      - alert: HighDiskUsage
        expr: (node_filesystem_size_bytes - node_filesystem_free_bytes) / node_filesystem_size_bytes > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High disk usage detected"
          description: "Disk usage is above 80% on {{ $labels.device }}"
      
      - alert: StorageIOLatency
        expr: rate(node_disk_io_time_seconds_total[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High storage I/O latency"
          description: "Storage I/O latency is high on {{ $labels.device }}"
```

### Caching Strategies

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: storage-cache
  namespace: storage-system
spec:
  selector:
    matchLabels:
      app: storage-cache
  template:
    metadata:
      labels:
        app: storage-cache
    spec:
      containers:
      - name: redis-cache
        image: redis:7-alpine
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        volumeMounts:
        - name: cache-storage
          mountPath: /data
      volumes:
      - name: cache-storage
        hostPath:
          path: /opt/edge/cache
          type: DirectoryOrCreate
```

## Best Practices

### Storage Design Principles
- Plan for data locality.
- Implement proper backup strategies.
- Monitor storage performance.
- Use appropriate storage classes.

### Edge Considerations
- Handle intermittent connectivity.
- Optimize for limited resources.
- Implement data synchronization.
- Plan for disaster recovery.

## Next Steps

Continue to [Database Services](./database-services) to learn about database deployment and management patterns. 
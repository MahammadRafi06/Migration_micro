---
id: database-services
title: Database Services
sidebar_label: Database Services
sidebar_position: 2
---

# Database Services

Database deployment, management, and optimization patterns for edge environments.

## Overview

Database services at the edge require careful consideration of connectivity constraints, data locality, synchronization needs, and resource limitations while maintaining data consistency and availability.

## Relational Databases

### PostgreSQL Deployment

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgresql
  namespace: databases
spec:
  serviceName: postgresql
  replicas: 1
  selector:
    matchLabels:
      app: postgresql
  template:
    metadata:
      labels:
        app: postgresql
    spec:
      containers:
      - name: postgresql
        image: postgres:14
        env:
        - name: POSTGRES_DB
          value: "edgedb"
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: username
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: password
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata
        ports:
        - containerPort: 5432
          name: postgres
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
        - name: postgres-config
          mountPath: /etc/postgresql/postgresql.conf
          subPath: postgresql.conf
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
      volumes:
      - name: postgres-config
        configMap:
          name: postgres-config
  volumeClaimTemplates:
  - metadata:
      name: postgres-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 50Gi
      storageClassName: local-storage
```

### MySQL with Replication

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mysql-config
  namespace: databases
data:
  master.cnf: |
    [mysqld]
    log-bin=mysql-bin
    server-id=1
    binlog-format=ROW
    binlog-do-db=edgeapp
  slave.cnf: |
    [mysqld]
    server-id=2
    relay-log=mysql-relay
    read-only=1
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql-master
  namespace: databases
spec:
  serviceName: mysql-master
  replicas: 1
  selector:
    matchLabels:
      app: mysql
      role: master
  template:
    metadata:
      labels:
        app: mysql
        role: master
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-credentials
              key: root-password
        - name: MYSQL_DATABASE
          value: "edgeapp"
        - name: MYSQL_USER
          valueFrom:
            secretKeyRef:
              name: mysql-credentials
              key: username
        - name: MYSQL_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-credentials
              key: password
        ports:
        - containerPort: 3306
          name: mysql
        volumeMounts:
        - name: mysql-data
          mountPath: /var/lib/mysql
        - name: mysql-config
          mountPath: /etc/mysql/conf.d/master.cnf
          subPath: master.cnf
      volumes:
      - name: mysql-config
        configMap:
          name: mysql-config
  volumeClaimTemplates:
  - metadata:
      name: mysql-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 30Gi
```

## NoSQL Databases

### MongoDB Replica Set

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mongodb
  namespace: databases
spec:
  serviceName: mongodb
  replicas: 3
  selector:
    matchLabels:
      app: mongodb
  template:
    metadata:
      labels:
        app: mongodb
    spec:
      containers:
      - name: mongodb
        image: mongo:6.0
        command:
        - mongod
        - --replSet
        - rs0
        - --bind_ip_all
        - --auth
        - --keyFile
        - /etc/mongodb/keyfile
        env:
        - name: MONGO_INITDB_ROOT_USERNAME
          valueFrom:
            secretKeyRef:
              name: mongodb-credentials
              key: username
        - name: MONGO_INITDB_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mongodb-credentials
              key: password
        ports:
        - containerPort: 27017
          name: mongodb
        volumeMounts:
        - name: mongodb-data
          mountPath: /data/db
        - name: mongodb-keyfile
          mountPath: /etc/mongodb/keyfile
          subPath: keyfile
          readOnly: true
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
      volumes:
      - name: mongodb-keyfile
        secret:
          secretName: mongodb-keyfile
          defaultMode: 0400
  volumeClaimTemplates:
  - metadata:
      name: mongodb-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 40Gi
```

### Redis Cache Cluster

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis-cluster
  namespace: databases
spec:
  serviceName: redis-cluster
  replicas: 6
  selector:
    matchLabels:
      app: redis-cluster
  template:
    metadata:
      labels:
        app: redis-cluster
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        command:
        - redis-server
        - /etc/redis/redis.conf
        - --cluster-enabled
        - "yes"
        - --cluster-config-file
        - nodes.conf
        - --cluster-node-timeout
        - "5000"
        - --appendonly
        - "yes"
        - --protected-mode
        - "no"
        - --port
        - "6379"
        ports:
        - containerPort: 6379
          name: redis
        - containerPort: 16379
          name: cluster
        volumeMounts:
        - name: redis-data
          mountPath: /data
        - name: redis-config
          mountPath: /etc/redis/redis.conf
          subPath: redis.conf
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
      volumes:
      - name: redis-config
        configMap:
          name: redis-config
  volumeClaimTemplates:
  - metadata:
      name: redis-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
```

## Database Operators

### PostgreSQL Operator

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: postgres-cluster
  namespace: databases
spec:
  instances: 3
  primaryUpdateStrategy: unsupervised
  
  postgresql:
    parameters:
      max_connections: "200"
      shared_buffers: "256MB"
      effective_cache_size: "1GB"
      wal_level: "replica"
      max_wal_senders: "3"
      
  bootstrap:
    initdb:
      database: edgeapp
      owner: appuser
      secret:
        name: postgres-credentials
        
  storage:
    size: 50Gi
    storageClass: local-storage
    
  monitoring:
    enabled: true
    
  backup:
    retentionPolicy: "30d"
    barmanObjectStore:
      destinationPath: "s3://postgres-backups"
      s3Credentials:
        accessKeyId:
          name: backup-credentials
          key: access-key
        secretAccessKey:
          name: backup-credentials
          key: secret-key
      wal:
        retention: "7d"
      data:
        retention: "30d"
```

## Edge-Specific Database Patterns

### Regional Database Deployment

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: database-topology
  namespace: databases
data:
  topology.yaml: |
    regions:
      us-east:
        primary: true
        databases:
          - postgresql-primary
          - redis-cache
        replicas:
          - postgresql-read-replica
      us-west:
        primary: false
        databases:
          - postgresql-read-replica
          - redis-cache
        sync_source: "us-east"
      eu-central:
        primary: false
        databases:
          - postgresql-read-replica
          - redis-cache
        sync_source: "us-east"
```

### Data Synchronization

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: database-sync
  namespace: databases
spec:
  schedule: "*/10 * * * *"  # Every 10 minutes
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: sync-agent
            image: postgres:14
            command:
            - /bin/bash
            - -c
            - |
              # Sync data between regions
              pg_dump -h $PRIMARY_HOST -U $DB_USER $DB_NAME | \
              psql -h $REPLICA_HOST -U $DB_USER $DB_NAME
            env:
            - name: PRIMARY_HOST
              value: "postgresql-primary.us-east.edge.local"
            - name: REPLICA_HOST
              value: "postgresql-replica.us-west.edge.local"
            - name: DB_USER
              valueFrom:
                secretKeyRef:
                  name: postgres-credentials
                  key: username
            - name: DB_NAME
              value: "edgeapp"
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgres-credentials
                  key: password
          restartPolicy: OnFailure
```

## Database Monitoring

### Performance Metrics

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: database-monitoring
  namespace: monitoring
data:
  prometheus-rules.yaml: |
    groups:
    - name: database-performance
      rules:
      - alert: DatabaseConnectionsHigh
        expr: pg_stat_database_numbackends / pg_settings_max_connections > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High database connections"
          description: "Database connections are above 80% of maximum"
      
      - alert: DatabaseReplicationLag
        expr: pg_replication_lag_seconds > 300
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Database replication lag"
          description: "Replication lag is over 5 minutes"
      
      - alert: DatabaseDiskSpaceLow
        expr: pg_database_size_bytes / (1024^3) > 40
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "Database disk space low"
          description: "Database size is approaching storage limit"
```

## Best Practices

### Database Design
- Choose appropriate database types for use cases
- Implement proper indexing strategies
- Plan for data growth and scaling
- Design for eventual consistency when needed

### Edge Considerations
- Minimize data synchronization overhead
- Implement local caching strategies
- Plan for network partitions
- Optimize for resource constraints

### Security
- Use strong authentication
- Encrypt data at rest and in transit
- Implement proper access controls
- Regular security updates

## Next Steps

Continue to [Data Synchronization & Consistency](./data-synchronization-consistency) to learn about maintaining data consistency across distributed edge locations. 
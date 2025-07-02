# Container Best Practices for AEP

Learn how to create optimized Docker containers for successful deployment on the Armada Edge Platform.

## Overview

Containers deployed to edge environments have unique requirements compared to traditional cloud deployments. This guide covers best practices for creating efficient, secure, and edge-optimized containers.

## Image Optimization

### Use Minimal Base Images

```dockerfile
# ❌ Avoid heavy base images
FROM ubuntu:latest

# ✅ Use minimal base images
FROM alpine:3.18
# or
FROM gcr.io/distroless/java:11
```

### Multi-Stage Builds

```dockerfile
# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Production stage
FROM node:18-alpine AS production
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

## Security Practices

### Non-Root User

```dockerfile
# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# Switch to non-root user
USER nextjs
```

### Image Scanning

```bash
# Scan for vulnerabilities
docker scan myapp:latest

# Use tools like Trivy
trivy image myapp:latest
```

## Performance Optimization

### Layer Optimization

```dockerfile
# ❌ Each RUN creates a new layer
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y wget

# ✅ Combine commands to reduce layers
RUN apt-get update && \
    apt-get install -y curl wget && \
    rm -rf /var/lib/apt/lists/*
```

### .dockerignore

```dockerignore
node_modules
*.log
.git
.gitignore
README.md
Dockerfile
.dockerignore
```

## Resource Management

### Health Checks

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1
```

### Resource Limits in Code

```javascript
// Example: Node.js memory management
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  server.close(() => {
    process.exit(0);
  });
});
```

## Edge-Specific Considerations

### Image Size Optimization

:::warning Edge Bandwidth Constraints
Edge locations may have limited bandwidth. Keep images as small as possible:
- Target < 100MB for optimal performance
- Use compression and optimization tools
- Consider image layering strategies
:::

### Offline Capabilities

```dockerfile
# Include necessary dependencies for offline operation
COPY ./offline-assets /app/assets
```

## Example Dockerfile

```dockerfile
# Multi-stage build for Node.js application
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && npm cache clean --force

# Production stage
FROM node:18-alpine AS production

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Set working directory
WORKDIR /app

# Copy dependencies and application
COPY --from=builder --chown=nextjs:nodejs /app/node_modules ./node_modules
COPY --chown=nextjs:nodejs . .

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

# Start application with dumb-init
ENTRYPOINT ["dumb-init", "--"]
CMD ["npm", "start"]
```

## Testing Your Containers

### Local Testing

```bash
# Build the image
docker build -t myapp:latest .

# Run locally
docker run -p 3000:3000 myapp:latest

# Test health check
docker inspect --format='{{.State.Health.Status}}' <container_id>
```

### Security Testing

```bash
# Run security scan
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image myapp:latest
```

## Container Checklist

Before deploying to AEP:

- [ ] **Base Image** - Using minimal, secure base image
- [ ] **Multi-stage Build** - Optimized build process
- [ ] **Non-root User** - Running as non-privileged user
- [ ] **Security Scan** - No critical vulnerabilities
- [ ] **Health Checks** - Proper liveness/readiness checks
- [ ] **Signal Handling** - Graceful shutdown implemented
- [ ] **Resource Limits** - Appropriate memory/CPU settings
- [ ] **Image Size** - Optimized for edge deployment
- [ ] **Documentation** - Clear build and run instructions

## Next Steps

- [Kubernetes Manifests](./kubernetes-manifests.md) - Create deployment configurations
- [Helm Charts](./helm-charts.md) - Package your containerized application
- [Security Considerations](./security-considerations.md) - Implement additional security measures

---

:::tip Container Registry
Ensure your container images are pushed to a registry accessible from your edge locations. AEP supports various registry types including private registries with authentication.
::: 
---
id: platform-specific-clis
title: Platform-Specific CLI Tools
sidebar_label: Platform-Specific CLIs
description: Command-line tools for managing edge platform resources
draft: true
---

# Platform-Specific CLI Tools

Learn about the command-line tools available for managing your edge platform resources and deployments.

## Edge Platform CLI

### Installation
```bash
# Download and install edge CLI
curl -L https://releases.edge-platform.com/cli/latest/edge-cli-linux-amd64 -o edge
chmod +x edge
sudo mv edge /usr/local/bin/
```

### Basic Commands
```bash
# Login to platform
edge auth login

# List clusters
edge cluster list

# Deploy application
edge app deploy --file app.yaml --cluster edge-west-1

# Check deployment status
edge app status myapp
```

### Configuration Management
```bash
# Set default cluster
edge config set-cluster edge-west-1

# View current configuration
edge config view

# Switch contexts
edge config use-context production
```

## Kubernetes CLI Extensions

### Kustomize Integration
```bash
# Deploy with kustomize
edge deploy --kustomize overlays/production/

# Preview changes
edge deploy --dry-run --kustomize overlays/production/
```

### Helm Integration
```bash
# Deploy Helm chart
edge helm install myapp ./chart --cluster edge-east-1

# Upgrade release
edge helm upgrade myapp ./chart --cluster edge-east-1
```

## Best Practices

1. **Authentication**: Use secure authentication methods
2. **Configuration**: Maintain separate configs for environments
3. **Automation**: Integrate CLI commands into CI/CD pipelines
4. **Documentation**: Keep CLI usage documented for team members

## Next Steps

- [API Reference](./api-reference.md)
- [Recommended kubectl Plugins](./recommended-kubectl-plugins.md) 
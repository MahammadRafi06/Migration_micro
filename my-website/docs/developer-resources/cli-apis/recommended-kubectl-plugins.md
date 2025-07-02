---
id: recommended-kubectl-plugins
title: Recommended kubectl Plugins
sidebar_label: Recommended kubectl Plugins
description: Essential kubectl plugins for enhanced productivity
draft: true
---

# Recommended kubectl Plugins

Essential kubectl plugins that enhance productivity when working with edge platforms.

## Essential Plugins

### krew (Plugin Manager)
```bash
# Install krew
(
  set -x; cd "$(mktemp -d)" &&
  OS="$(uname | tr '[:upper:]' '[:lower:]')" &&
  ARCH="$(uname -m | sed -e 's/x86_64/amd64/' -e 's/\(arm\)\(64\)\?.*/\1\2/' -e 's/aarch64$/arm64/')" &&
  KREW="krew-${OS}_${ARCH}" &&
  curl -fsSLO "https://github.com/kubernetes-sigs/krew/releases/latest/download/${KREW}.tar.gz" &&
  tar zxvf "${KREW}.tar.gz" &&
  ./"${KREW}" install krew
)
```

### ctx (Context Switching)
```bash
# Install kubectx
kubectl krew install ctx

# Switch contexts quickly
kubectl ctx edge-west-1
kubectl ctx edge-east-1
```

### ns (Namespace Switching)
```bash
# Install kubens
kubectl krew install ns

# Switch namespaces
kubectl ns production
kubectl ns staging
```

## Debugging Plugins

### stern (Multi-pod Logs)
```bash
# Install stern
kubectl krew install stern

# Tail logs from multiple pods
kubectl stern myapp
kubectl stern myapp --namespace production
```

### debug-shell
```bash
# Install debug-shell
kubectl krew install debug-shell

# Debug pod with shell
kubectl debug-shell myapp-pod-12345
```

## Resource Management

### resource-capacity
```bash
# Install resource-capacity
kubectl krew install resource-capacity

# View cluster resource usage
kubectl resource-capacity
kubectl resource-capacity --pods --util
```

### tree
```bash
# Install tree
kubectl krew install tree

# View resource hierarchies
kubectl tree deployment myapp
```

## Productivity Plugins

### neat
```bash
# Install neat
kubectl krew install neat

# Clean output
kubectl get pods -o yaml | kubectl neat
```

### whoami
```bash
# Install whoami
kubectl krew install whoami

# Check current user
kubectl whoami
```

## Best Practices

1. **Regular Updates**: Keep plugins updated with `kubectl krew upgrade`.
2. **Essential Set**: Install core productivity plugins on all development machines.
3. **Team Standards**: Standardize plugin usage across development teams.
4. **Documentation**: Document custom plugin usage in team guides.

## Next Steps

- [Platform-Specific CLIs](./platform-specific-clis.md).
- [API Reference](./api-reference.md). 
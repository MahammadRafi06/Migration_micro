---
id: kubevirt-deployment-and-best-practices
title: Deployment Process & Best Practices
sidebar_label: Deployment & Best Practices
---

# Deployment Process Summary & Best Practices

Now that we've covered all the steps for deploying Docker Compose applications to KubeVirt VMs, let's summarize the entire process and explore best practices, considerations, and advanced scenarios.

## Deployment Process Summary

Here's a complete summary of the steps we've covered for deploying Docker Compose applications to KubeVirt VMs:

1. **Prepare your Docker Compose application**:
   - Ensure images are pushed to a registry
   - Identify exposed ports
   - Consider volume and persistence requirements

2. **Create your Golden VM Image**:
   - Download a base OS QCOW2 image
   - Install Docker, Docker Compose, and copy your docker-compose.yml and application code into it
   - Save this as your `my-golden-vm.qcow2` image

3. **Host your Golden Image**:
   - Make `my-golden-vm.qcow2` accessible via HTTP/HTTPS or S3-compatible storage

4. **Apply DataVolume (01-datavolume.yaml)**:
   - This imports your golden image into a Kubernetes PVC
   - Wait for the import to complete successfully

5. **Apply VirtualMachine (02-virtualmachine.yaml)**:
   - This creates your KubeVirt VM, using the imported disk
   - A cloud-init script starts Docker and Docker Compose on boot

6. **Apply Service (03-service.yaml)**:
   - This exposes the necessary ports of your KubeVirt VM
   - Makes your application accessible within the Kubernetes cluster or externally

7. **Monitor and Verify**:
   - Check all resources with `kubectl get vm,vmi,pod,pvc,svc -l app=my-docker-compose-app`
   - Connect to the VM with `virtctl console my-docker-compose-vm`
   - Verify your application is accessible at the service endpoint

:::tip
Create a deployment script that executes all these steps in sequence, with proper error handling and validation checks between steps.
:::

## Considerations and Best Practices

### Resource Overhead

Running an entire VM for a Docker Compose application introduces more overhead (CPU, RAM) compared to running containers directly in Kubernetes Pods.

**Best Practices**:
- Allocate sufficient resources to your VM based on the requirements of all containers in your Docker Compose application, plus overhead for the VM's OS and Docker itself
- Consider using resource quotas and limits at the namespace level to prevent VMs from consuming excessive resources
- Monitor resource usage to optimize allocations over time

### Networking

Ensure your network configuration allows communication between the Kubernetes Service and the KubeVirt VM.

**Best Practices**:
- Use the VM's pod network interface (`bridge`) for better integration with Kubernetes networking
- Configure network policies to control traffic to and from your VM
- Consider using a service mesh (e.g., Istio) if you need advanced traffic management, though this adds complexity

### Persistent Storage for VM Data

If your Docker Compose application generates data that needs to persist even if the VM disk is recreated, you'll need additional storage configurations.

**Best Practices**:
- For truly critical data, mount additional Kubernetes PVCs to your KubeVirt VM:

```yaml
# In your VirtualMachine spec
volumes:
  - name: app-disk
    persistentVolumeClaim:
      claimName: my-docker-compose-vm-disk
  - name: data-disk
    persistentVolumeClaim:
      claimName: my-data-pvc  # Separate PVC for persistent data

# In your VM domain.devices
disks:
  - name: app-disk
    disk:
      bus: virtio
  - name: data-disk
    disk:
      bus: virtio
```

- Inside the VM, mount this additional disk to a specific path and configure your Docker Compose volumes to use it
- Consider backup strategies for your PVCs, such as using Velero or other Kubernetes-native backup solutions

### Updates and Maintenance

Managing updates requires careful planning to maintain availability and data integrity.

#### Docker Image Updates

To update the running containers in the VM:

```bash
# SSH or connect to your VM
virtctl ssh my-docker-compose-vm

# Navigate to your Docker Compose directory
cd /path/to/docker-compose

# Pull the latest images
docker-compose pull

# Update the running containers
docker-compose up -d
```

Consider automating this process with a Kubernetes Job or CronJob.

#### Base VM Image Updates (OS, Docker/Docker Compose versions)

This requires rebuilding your golden image, updating the DataVolume, and then updating your VirtualMachine:

1. Create a new golden image with updated OS, Docker, etc.
2. Host this new image
3. Create a new DataVolume pointing to the new image
4. Update your VirtualMachine to use the new PVC
5. Restart the VM

:::caution
This process will destroy the VM and recreate it, which may lead to data loss if you haven't properly configured persistent storage.
:::

### Security

Security should be a top priority for any production deployment.

**Best Practices**:
- Harden your golden image:
  - Remove unnecessary software
  - Configure a firewall
  - Apply security patches
  - Disable unnecessary services
- Manage SSH keys for VM access carefully:
  - Use a secure method to distribute and rotate SSH keys
  - Consider using a secrets management solution
- Ensure your docker-compose.yml does not expose sensitive information:
  - Use Kubernetes Secrets or ConfigMaps and mount them into the VM
  - Consider using external secret management solutions like HashiCorp Vault
- Apply the principle of least privilege:
  - For the VM itself
  - For containers within the VM
  - For users accessing the VM

### Scalability

If you need to scale your application, you have several options:

1. **Vertical Scaling**: Increase the CPU and memory allocated to your VM:

```yaml
domain:
  cpu:
    cores: 4  # Increased from 2
  memory:
    guest: 8Gi  # Increased from 4Gi
```

2. **Horizontal Scaling**: Create multiple KubeVirt VirtualMachine instances, each running an instance of your Docker Compose application. Your Kubernetes Service would then load-balance traffic across these VMs:

```yaml
# Create multiple VMs with different names
metadata:
  name: my-docker-compose-vm-1
  # ...

# Ensure all VMs have the same label for the service selector
metadata:
  labels:
    app: my-docker-compose-app
```

### Monitoring and Logging

Standard Kubernetes monitoring and logging tools might not directly see inside your VM. You'll need additional configuration.

**Best Practices**:
- Install monitoring agents inside the VM:
  - Prometheus Node Exporter for VM metrics
  - cAdvisor for container metrics
  - Fluentd or Fluent Bit for log collection
- Configure these agents to forward metrics and logs to your Kubernetes monitoring stack
- Set up alerts for VM-level issues (e.g., high CPU, memory, disk usage)
- Consider using a dedicated monitoring solution for VMs, such as Telegraf with InfluxDB

### Example Monitoring Setup in cloud-init

You can add monitoring agent installation to your cloud-init script:

```yaml
cloudInitNoCloud:
  userData: |
    #cloud-config
    runcmd:
      # Start Docker and your application
      - sudo systemctl enable docker
      - sudo systemctl start docker
      - cd /home/dockeruser/my-app
      - docker-compose up -d
      
      # Install Prometheus Node Exporter
      - wget https://github.com/prometheus/node_exporter/releases/download/v1.3.1/node_exporter-1.3.1.linux-amd64.tar.gz
      - tar xvfz node_exporter-1.3.1.linux-amd64.tar.gz
      - cd node_exporter-1.3.1.linux-amd64
      - sudo cp node_exporter /usr/local/bin/
      - sudo useradd -rs /bin/false node_exporter
      - echo '[Unit]
        Description=Node Exporter
        After=network.target
        
        [Service]
        User=node_exporter
        Group=node_exporter
        Type=simple
        ExecStart=/usr/local/bin/node_exporter
        
        [Install]
        WantedBy=multi-user.target' | sudo tee /etc/systemd/system/node_exporter.service
      - sudo systemctl daemon-reload
      - sudo systemctl enable node_exporter
      - sudo systemctl start node_exporter
```

## Alternative Approaches

While this guide focuses on running Docker Compose inside a VM, there are alternative approaches you might consider:

### Kompose / Native Kubernetes

For most containerized applications, the more "Kubernetes-native" approach is to convert your docker-compose.yml into Kubernetes Deployments, Services, ConfigMaps, and Secrets. Tools like `kompose` can help with this initial conversion.

**Advantages**:
- Better resource utilization
- Finer-grained control
- More seamless integration with Kubernetes features like horizontal pod autoscaling
- Direct access to Kubernetes' monitoring, logging, and security features

**When to consider**:
- Your Docker Compose application is already container-based and doesn't rely on VM-specific features
- You need better scalability and resource efficiency
- You're comfortable with Kubernetes concepts and resources
- You want to leverage Kubernetes' native features more directly

### Combination Approach

A hybrid approach is to run some services in KubeVirt VMs and others as native Kubernetes resources:

- Use KubeVirt VMs for services that are hard to containerize or have specific OS requirements
- Use native Kubernetes Deployments for services that are already well-containerized
- Connect them using Kubernetes Services and networking

## Conclusion

Deploying Docker Compose applications to KubeVirt VMs provides a practical path for migrating to Kubernetes without having to immediately refactor your applications. While this approach introduces some overhead and complexity compared to native Kubernetes deployments, it offers a valuable transition strategy.

As you become more comfortable with Kubernetes, you might gradually migrate services from the VM to native Kubernetes resources, eventually adopting a fully Kubernetes-native architecture if that better suits your needs.

Remember to adapt the resource requests, paths, and image names in this guide to your specific application. Each application will have unique requirements that may necessitate adjustments to these general patterns.

### Next Steps

Now that you've successfully deployed your Docker Compose application to KubeVirt VMs, consider exploring:

1. **Automation**: Use GitOps tools like ArgoCD or Flux to automate the deployment process
2. **Monitoring**: Set up comprehensive monitoring for your VMs and the applications running inside them
3. **Backup and Disaster Recovery**: Implement strategies for backing up your VM data and configurations
4. **CI/CD Integration**: Integrate VM image building and deployment into your CI/CD pipeline
5. **Security Hardening**: Apply additional security measures to protect your VMs and applications

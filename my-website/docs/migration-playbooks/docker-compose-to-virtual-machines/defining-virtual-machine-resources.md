---
id: defining-virtual-machine-resources
title: Define KubeVirt VM Resources
sidebar_label: Define VM Resources
---

# Define Your KubeVirt VM Resources

Now that we have our Docker Compose application ready and a golden VM image created, we need to define the Kubernetes resources for our KubeVirt VM and import our VM image into the cluster.

## Phase 3: Define Your KubeVirt VirtualMachine Resource

### Upload Your Golden Image to a PVC using CDI

You need to make your `my-golden-vm.qcow2` image accessible to KubeVirt. Containerized Data Importer (CDI) is the standard way to import disk images into Kubernetes PersistentVolumeClaims (PVCs).

#### 1. Create a DataVolume Resource

Create a file named `01-datavolume.yaml`:

```yaml
apiVersion: cdi.kubevirt.io/v1beta1
kind: DataVolume
metadata:
  name: my-docker-compose-vm-disk
  namespace: default # Or your desired namespace
spec:
  source:
    http:
      url: "http://your-webserver.com/path/to/my-golden-vm.qcow2" # <--- REPLACE THIS URL
  pvc:
    accessModes:
      - ReadWriteOnce # Can be mounted as read-write by a single node
    resources:
      requests:
        storage: 20Gi # Ensure this is large enough for your OS + Docker + App
    storageClassName: standard # Use your cluster's default or a specific StorageClass
```

:::important
Replace the URL with the actual location where you've hosted your golden VM image.
:::

#### 2. Apply the DataVolume Resource

```bash
kubectl apply -f 01-datavolume.yaml
```

#### 3. Monitor the Import Process

Wait for the DataVolume to be in the `Succeeded` phase and a PVC named `my-docker-compose-vm-disk` to be created:

```bash
kubectl get dv my-docker-compose-vm-disk -o wide
kubectl get pvc my-docker-compose-vm-disk
```

Example output when complete:

```
NAME                        PHASE     PROGRESS   RESTARTS   AGE
my-docker-compose-vm-disk   Succeeded   100.0%              5m
```

:::note
The import process can take several minutes depending on the size of your VM image and your network connection.
:::

### Create Your VirtualMachine Manifest

This manifest tells KubeVirt how to create and manage your VM. The `cloudInitNoCloud` section is crucial for running docker-compose up on VM startup.

Create a file named `02-virtualmachine.yaml`:

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: my-docker-compose-vm
  namespace: default # Or your desired namespace
  labels:
    app: my-docker-compose-app # Label for the Kubernetes Service selector
spec:
  runStrategy: Always # Ensures the VM is always running
  template:
    metadata:
      labels:
        app: my-docker-compose-app # Label for the Kubernetes Service selector
    spec:
      domain:
        cpu:
          cores: 2 # Adjust CPU cores as needed for your application
        memory:
          guest: 4Gi # Adjust RAM as needed for your application
        devices:
          disks:
            - name: app-disk
              disk:
                bus: virtio # Recommended for performance
          interfaces:
            - name: default
              bridge: {} # Connects to the Kubernetes pod network
        # You might need to adjust CPU and memory based on your Docker Compose app's requirements
      volumes:
        - name: app-disk
          persistentVolumeClaim:
            claimName: my-docker-compose-vm-disk # Links to the PVC created by CDI
      networks:
        - name: default
          pod: {} # Uses the default pod network
      cloudInitNoCloud: # Cloud-init script for initial setup inside the VM
        userData: |
          #cloud-config
          # This script runs on first boot of the VM
          runcmd:
            - echo "Starting Docker daemon..."
            - sudo systemctl enable docker
            - sudo systemctl start docker
            - echo "Navigating to application directory..."
            - cd /home/dockeruser/my-app # <--- REPLACE with the actual path where your docker-compose.yml is
            - echo "Running docker-compose up -d..."
            - docker-compose up -d # Start your Docker Compose application in detached mode
            - echo "Docker Compose application started."
          # Optional: Inject SSH keys for easier access to the VM
          # ssh_authorized_keys:
          #   - ssh-rsa AAAAB3NzaC... your_public_ssh_key_here
```

:::tip Customization Points
- Adjust the CPU cores and memory based on your application's requirements
- Update the path to your docker-compose.yml file
- Consider adding SSH keys for remote access to the VM
- For production, you might want to add more robust startup checks and error handling
:::

### Apply the VirtualMachine Resource

```bash
kubectl apply -f 02-virtualmachine.yaml
```

### Monitor the VM Status

```bash
kubectl get vm my-docker-compose-vm -o wide
kubectl get vmi my-docker-compose-vm -o wide
```

The VM should eventually transition to `Running` state:

```
NAME                   AGE   STATUS    READY
my-docker-compose-vm   3m    Running   True
```

### Troubleshooting VM Startup

If your VM doesn't start properly, you can check its status and logs:

```bash
# Check detailed VM status
kubectl describe vm my-docker-compose-vm

# Check VM instance status
kubectl describe vmi my-docker-compose-vm

# Check events related to your VM
kubectl get events --field-selector involvedObject.name=my-docker-compose-vm
```

You can also connect to the VM's console to see boot logs and debug issues:

```bash
virtctl console my-docker-compose-vm
```

## Phase 4: Expose Your Application (Kubernetes Service)

Your KubeVirt VM will get an IP address within the Kubernetes pod network. To access your application from outside the cluster, you'll need a Kubernetes Service.

### Create a Service Resource

Create a file named `03-service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-docker-compose-app-service
  namespace: default # Or your desired namespace
spec:
  selector:
    app: my-docker-compose-app # Matches the label on your KubeVirt VM
  ports:
    - protocol: TCP
      port: 80 # The port exposed by your Kubernetes Service
      targetPort: 80 # The port exposed by your Docker Compose app *on the VM's host* (from docker-compose.yml: "80:3000")
      name: http-webapp
  type: LoadBalancer # Or NodePort, ClusterIP depending on your needs
```

:::note Service Types
- **ClusterIP**: Only accessible within the Kubernetes cluster (default)
- **NodePort**: Exposes the service on a specific port on each Node
- **LoadBalancer**: Exposes the service using a cloud provider's load balancer
:::

### Apply the Service Resource

```bash
kubectl apply -f 03-service.yaml
```

### Accessing Your Application

If you used `type: LoadBalancer`, get the external IP:

```bash
kubectl get svc my-docker-compose-app-service -o wide
```

Example output:

```
NAME                           TYPE           CLUSTER-IP      EXTERNAL-IP     PORT(S)        AGE
my-docker-compose-app-service  LoadBalancer   10.96.123.45    203.0.113.10    80:31234/TCP   2m
```

You can now access your application at `http://EXTERNAL-IP` (or the NodePort if you used that type).

### Alternative: Create an Ingress Resource (Optional)

If you have an Ingress controller in your cluster, you can also create an Ingress resource to expose your application:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-docker-compose-app-ingress
  namespace: default
  annotations:
    # Add any necessary annotations for your Ingress controller
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
    - host: my-app.example.com  # Replace with your domain
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-docker-compose-app-service
                port:
                  number: 80
```

Apply the Ingress resource:

```bash
kubectl apply -f 04-ingress.yaml
```

## Verifying Your Deployment

### Check All Resources

```bash
kubectl get vm,vmi,pod,pvc,svc -l app=my-docker-compose-app
```

### Test Connectivity

```bash
# Using curl (replace with your actual service IP or hostname)
curl http://203.0.113.10

# Or open in a browser
```

### View VM Logs

```bash
# Connect to the VM console
virtctl console my-docker-compose-vm

# Or if you have SSH set up:
virtctl ssh my-docker-compose-vm
```

Once inside the VM, you can check the Docker Compose logs:

```bash
cd /path/to/your/docker-compose/directory
docker-compose logs
```

## Next Steps

Now that you have successfully deployed your Docker Compose application in a KubeVirt VM and exposed it via a Kubernetes Service, we'll explore best practices, considerations, and the complete deployment process summary in the next section.

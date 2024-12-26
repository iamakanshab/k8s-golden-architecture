# SharkLLM Bare Metal Installation Guide
Its important to understand the security considerations for making a external IP available for SGLand Integrations or 
sending text generation requests. 

## Prerequisites
- MI300X GPU with ROCm 5.7+
- Kubernetes cluster
- kubectl configured
- Container runtime with ROCm support
- Local model storage

## Network Access Types

### LoadBalancer Service (Cloud Environment)
- Automatically provisions external IP address
- Enables access from outside the cluster
- Requires cloud provider integration
- Not suitable for bare metal labs without proper infrastructure

### NodePort Service (Bare Metal Labs)
- Exposes service on static port on each cluster node
- No external IP required
- Accessible within lab network
- More secure for internal testing

## Installation

1. **Deploy Application**
```bash
kubectl apply -f llama-app-deployment.yaml
```

2. **Verify Deployment**
```bash
kubectl get pods
```

## Accessing the Service

### Bare Metal Access (NodePort)
```yaml
apiVersion: v1
kind: Service
metadata:
  name: shark-llama-app-service
spec:
  type: NodePort
  ports:
  - port: 80
    targetPort: 8080
  selector:
    app: shark-llama-app
```

Access options:
1. Direct NodePort access:
```bash
NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
NODE_PORT=$(kubectl get service shark-llama-app-service -o jsonpath='{.spec.ports[0].nodePort}')
curl http://$NODE_IP:$NODE_PORT
```

2. Secure port forwarding:
```bash
kubectl port-forward service/shark-llama-app-service 8080:80
# Access via localhost:8080
```

## Troubleshooting

### Service Access Issues
```bash
# Check service status
kubectl get service shark-llama-app-service

# Verify endpoints
kubectl get endpoints shark-llama-app-service

# Check pod logs
kubectl logs -f deployment/shark-llama-app-deployment
```

### GPU Issues
```bash
# Verify GPU in pod
kubectl exec -it <pod-name> -- rocm-smi

# Check resource allocation
kubectl describe pod <pod-name>
```

## Cleanup
```bash
kubectl delete deployment shark-llama-app-deployment
kubectl delete service shark-llama-app-service
```

## Security Considerations
- NodePort services expose fixed ports on all nodes
- Implement network policies for access control
- Use port forwarding for secure debugging
- Monitor access logs and resource usage

## Performance Tuning
```yaml
resources:
  limits:
    amd.com/gpu: 1
    memory: "32Gi"
  requests:
    amd.com/gpu: 1
    memory: "16Gi"
env:
  - name: GPU_MEMORY_UTILIZATION
    value: "0.90"
```

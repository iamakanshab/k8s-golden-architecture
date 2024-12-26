# Kubernetes Cluster Setup with AMD MI300 GPUs

This guide provides step-by-step instructions for setting up a Kubernetes cluster with AMD MI300 GPUs on bare metal.
The setup includes one control plane node and two MI300 worker nodes.

## Prerequisites

- Three servers (one for control plane, two with AMD MI300 GPUs)
- Ubuntu/Debian-based Linux distribution
- Root or sudo access on all machines
- Network connectivity between all nodes

## System Preparation (All Nodes)

All machines (control plane and both MI300 nodes) with the necessary system configurations:

```bash
# Disable swap
sudo swapoff -a
sudo sed -i '/ swap / s/^/#/' /etc/fstab

# Load required kernel modules
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF
sudo modprobe overlay
sudo modprobe br_netfilter

# Set network parameters
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF
sudo sysctl --system
```

## ROCm Installation (MI300 Nodes Only)

Install ROCm on both MI300 nodes:

```bash
# Add ROCm apt repository
sudo apt update
wget https://repo.radeon.com/rocm/rocm.gpg.key -O - | sudo apt-key add -
echo 'deb [arch=amd64] https://repo.radeon.com/rocm/apt/debian/ ubuntu main' | sudo tee /etc/apt/sources.list.d/rocm.list
sudo apt update

# Install ROCm
sudo apt install rocm-dkms

# Add user to video group
sudo usermod -a -G video,render $LOGNAME
```

## Container Runtime Installation (All Nodes)

Install and configure containerd on all nodes:

```bash
# Install containerd
sudo apt-get update
sudo apt-get install -y containerd

# Configure containerd
sudo mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml
sudo systemctl restart containerd
```

## Kubernetes Components Installation (All Nodes)

Install Kubernetes components on all nodes:

```bash
# Add Kubernetes apt repository
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.29/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.29/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list

# Install kubelet, kubeadm, kubectl
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl
```

## Control Plane Initialization

On the control plane node only:

```bash
# Initialize control plane
sudo kubeadm init --pod-network-cidr=192.168.0.0/16 --control-plane-endpoint="<control-plane-ip>"

# Set up kubeconfig
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

## Network Plugin Installation

Install Calico network plugin from the control plane node:

```bash
kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.27.0/manifests/calico.yaml
```

## Join Worker Nodes

On both MI300 nodes, run the join command that was output by `kubeadm init`:

```bash
sudo kubeadm join <control-plane-ip>:6443 --token <token> --discovery-token-ca-cert-hash <hash>
```

## AMD GPU Operator Installation

Install the AMD GPU Operator using Helm:

```bash
# Add Helm repo
helm repo add amd https://helm.amd.com/amdgpu
helm repo update

# Install operator
helm install amd-gpu-operator amd/amdgpu-operator \
  --set driver.enabled=false \
  --set devicePlugin.enabled=true \
  --namespace gpu-operator \
  --create-namespace
```

## Verification

```bash
# Check nodes
kubectl get nodes

# Check GPU operator pods
kubectl get pods -n gpu-operator

# Check GPU detection
kubectl get nodes -o custom-columns=NAME:.metadata.name,GPUs:.status.allocatable.amd\.com/gpu
```

## Test GPU Access

Create a test pod to verify GPU access:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: gpu-test
spec:
  containers:
  - name: gpu-test
    image: rocm/pytorch:latest
    command: ["sleep", "infinity"]
    resources:
      limits:
        amd.com/gpu: 1
```

```bash
kubectl apply -f gpu-test.yaml
```

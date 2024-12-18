# Problem Solving
### We must not open any ports on bare-metal servers, as such a hybrid push-pull approach might be optimal to work around this.

### Solution
• Use pull for cloud environments where service discovery is easier.
Use push for bare-metal nodes to avoid opening ports unnecessarily.
```
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'kubernetes-nodes-cloud'
    kubernetes_sd_configs:
      - role: node

  - job_name: 'bare-metal-nodes'
    static_configs:
      - targets:
          - 'bare-metal-node1.example.com:9091' # Pushgateway URL
          - 'bare-metal-node2.example.com:9091'
```
###   Centralizing configurations within git repositories

```
/k8s-config
├── base/
│   ├── namespaces.yaml
│   ├── rbac.yaml
│   ├── resource-quotas.yaml
│   └── network-policies.yaml
├── overlays/
│   ├── prod/
│   └── dev/
└── apps/
    ├── app1/
    └── app2/
```

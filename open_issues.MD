# We must not open any ports on bare-metal servers, as such a hybrid push-pull approach might be optimal to work around this.
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

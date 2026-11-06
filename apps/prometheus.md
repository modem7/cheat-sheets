# Prometheus
Open source monitoring and alerting toolkit that scrapes and stores metrics as time series. Pairs with [Grafana](grafana.md).

Project Homepage: [Prometheus](https://prometheus.io)
Documentation: [Prometheus Docs](https://prometheus.io/docs/)

---
## Run with Docker
```bash
docker run -d --name prometheus -p 9090:9090 \
  -v ./prometheus.yml:/etc/prometheus/prometheus.yml:ro \
  -v prometheus-data:/prometheus \
  prom/prometheus
```

## Minimal prometheus.yml
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - alerts.yml

scrape_configs:
  - job_name: prometheus
    static_configs:
      - targets: ["localhost:9090"]
  - job_name: node
    static_configs:
      - targets: ["server1:9100", "server2:9100"]
```

## Operations
COMMAND | DESCRIPTION
---|---
`promtool check config prometheus.yml` | Validate the config
`promtool check rules alerts.yml` | Validate rule files
`curl -X POST localhost:9090/-/reload` | Reload config (needs `--web.enable-lifecycle`)
`curl localhost:9090/-/healthy` | Health check
`curl localhost:9090/-/ready` | Readiness check
`curl 'localhost:9090/api/v1/query?query=up'` | Run an instant query via the API
`curl localhost:9090/api/v1/targets` | List scrape targets and health
`--storage.tsdb.retention.time=30d` | Flag: how long to keep data
`--storage.tsdb.retention.size=20GB` | Flag: cap storage size

## PromQL Basics
QUERY | DESCRIPTION
---|---
`up` | 1 if a target is up, 0 if down
`up == 0` | Targets that are down
`http_requests_total{job="api", code=~"5.."}` | Label matchers (`=`, `!=`, `=~`, `!~`)
`rate(http_requests_total[5m])` | Per-second rate over 5 minutes (use on counters)
`sum by (job) (rate(http_requests_total[5m]))` | Aggregate by label
`histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))` | 95th percentile latency
`increase(errors_total[1h])` | Total increase over an hour
`topk(5, sum by (instance) (rate(node_cpu_seconds_total{mode!="idle"}[5m])))` | Top 5 by CPU
`predict_linear(node_filesystem_avail_bytes[6h], 24*3600) < 0` | Disk full within 24h

## Useful node_exporter Queries
QUERY | DESCRIPTION
---|---
`100 - avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100` | CPU usage %
`(1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100` | Memory usage %
`100 - (node_filesystem_avail_bytes{fstype!~"tmpfs\|overlay"} / node_filesystem_size_bytes * 100)` | Disk usage %
`rate(node_network_receive_bytes_total[5m]) * 8` | Inbound bits per second

## Example Alert Rule
```yaml
groups:
  - name: basic
    rules:
      - alert: InstanceDown
        expr: up == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "{{ $labels.instance }} is down"
```

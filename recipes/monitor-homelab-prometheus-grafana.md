# Monitor a Homelab with Prometheus and Grafana
Run Prometheus, Alertmanager, node_exporter, cAdvisor and Grafana from one Compose file, scrape the host and its containers, alert on the things that actually bite (down, disk, memory) and get told when the alerting itself goes quiet.

Documentation: [Prometheus configuration](https://prometheus.io/docs/prometheus/latest/configuration/configuration/) · [Alertmanager configuration](https://prometheus.io/docs/alerting/latest/configuration/) · [node_exporter](https://github.com/prometheus/node_exporter) · [cAdvisor: running](https://github.com/google/cadvisor/blob/master/docs/running.md)

> **Verification:** the whole stack below was started with Docker Compose on a test host. All four scrape targets reported `up`, the six alert rules loaded as healthy, `promtool check config`, `promtool check rules` and `amtool check-config` passed, the `Watchdog` alert reached Alertmanager, and Grafana accepted the provisioned data source and the `GF_SECURITY_ADMIN_PASSWORD__FILE` secret. **Not verified:** real e-mail delivery (the SMTP server in the example does not exist), the dead-man's-switch webhook, the dashboard imports and the extra-host node_exporter install.

## Goal
One dashboard for CPU, memory, disk, network and per-container usage, and e-mail alerts when a target is down, a disk will fill within a day, or memory stays high. A constantly firing `Watchdog` alert pings an external service, so you are also told if monitoring itself stops.

## Prerequisites
- A Docker host as in [New Server Checklist](new-server-checklist.md), with the layout used in [Docker Service Deploy](docker-service-deploy.md) (stack in `/opt/stacks/monitoring`)
- An SMTP account for alerts (or another [Alertmanager receiver](https://prometheus.io/docs/alerting/latest/configuration/#receiver))
- A [Healthchecks.io](https://healthchecks.io) check for the dead-man's switch
- Optional: a reverse proxy for Grafana ([Docker Service Deploy](docker-service-deploy.md))

## Steps
### 1. Layout and secrets
```bash
mkdir -p /opt/stacks/monitoring/{prometheus,alertmanager,secrets,grafana/provisioning/datasources}
cd /opt/stacks/monitoring
openssl rand -base64 24 > secrets/grafana_admin_password
install -m 600 /dev/null secrets/smtp_password          # paste the SMTP password into it
chmod 700 secrets
```
Secret files that a container reads through a bind mount must be readable by that container's user. If a service reports `permission denied`, loosen the file mode to `644` inside the `700` directory.

### 2. The Compose file
`/opt/stacks/monitoring/compose.yaml` ([Docker-Compose](../docker/docker-compose.md)):
```yaml
services:
  prometheus:
    image: prom/prometheus:<VERSION>
    restart: unless-stopped
    command:
      - --config.file=/etc/prometheus/prometheus.yml
      - --storage.tsdb.retention.time=30d
      - --web.enable-lifecycle
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./prometheus/alerts.yml:/etc/prometheus/alerts.yml:ro
      - prometheus-data:/prometheus
    ports:
      - "127.0.0.1:9090:9090"
    networks: [monitoring]

  alertmanager:
    image: prom/alertmanager:<VERSION>
    restart: unless-stopped
    volumes:
      - ./alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml:ro
      - ./secrets/smtp_password:/etc/alertmanager/smtp_password:ro
      - alertmanager-data:/alertmanager
    ports:
      - "127.0.0.1:9093:9093"
    networks: [monitoring]

  node-exporter:
    image: quay.io/prometheus/node-exporter:<VERSION>
    restart: unless-stopped
    command:
      - --path.rootfs=/host
    pid: host
    volumes:
      - /:/host:ro,rslave
    networks: [monitoring]

  cadvisor:
    image: ghcr.io/google/cadvisor:<VERSION>
    restart: unless-stopped
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:rw
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
    networks: [monitoring]

  grafana:
    image: grafana/grafana-oss:<VERSION>
    restart: unless-stopped
    environment:
      GF_SECURITY_ADMIN_PASSWORD__FILE: /run/secrets/grafana_admin_password
    secrets: [grafana_admin_password]
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning:ro
    ports:
      - "127.0.0.1:3000:3000"
    networks: [monitoring]

secrets:
  grafana_admin_password:
    file: ./secrets/grafana_admin_password

volumes:
  prometheus-data:
  alertmanager-data:
  grafana-data:

networks:
  monitoring:
```
Notes:
- Pin each `<VERSION>` to a release tag, and let [Renovate](../cicd/renovate.md) or Diun report new ones ([Automate Container Updates Safely](automate-container-updates.md)).
- node_exporter keeps the default network namespace here and is reached by service name. The upstream example uses `network_mode: host`, which also exposes the host's real interface metrics; with the bridge network the `node_network_*` metrics describe the container's own interfaces, so use host networking (and scrape `<HOST_IP>:9100`) if you need host network graphs.
- cAdvisor needs read access to the host's `/`, `/sys` and `/var/lib/docker`. Treat it as privileged and keep it off public networks. On some distributions it needs extra flags, see the upstream run documentation.
- Prometheus, Alertmanager and Grafana are bound to `127.0.0.1`. Put a reverse proxy in front for remote access, and never publish Prometheus or Alertmanager unauthenticated ([Reverse Proxy Patterns](../homelab/reverse-proxy-patterns.md)).
- `GF_SECURITY_ADMIN_PASSWORD__FILE` is Grafana's file form of the admin password setting (`GF_<SECTION>_<KEY>` with a `__FILE` suffix, see [Grafana](../apps/grafana.md)).

### 3. Prometheus: scrape targets
`prometheus/prometheus.yml` ([Prometheus](../apps/prometheus.md)):
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - /etc/prometheus/alerts.yml

alerting:
  alertmanagers:
    - static_configs:
        - targets: ["alertmanager:9093"]

scrape_configs:
  - job_name: prometheus
    static_configs:
      - targets: ["localhost:9090"]
  - job_name: alertmanager
    static_configs:
      - targets: ["alertmanager:9093"]
  - job_name: node
    static_configs:
      - targets: ["node-exporter:9100"]
  - job_name: cadvisor
    static_configs:
      - targets: ["cadvisor:8080"]
```
Add other hosts later as more targets under `node` (install node_exporter there and open port 9100 to the Prometheus host only, [UFW (uncomplicated firewall)](../linux/ufw.md)).

### 4. Alert rules
`prometheus/alerts.yml`:
```yaml
groups:
  - name: homelab
    rules:
      - alert: TargetDown
        expr: up == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "{{ $labels.job }} on {{ $labels.instance }} is down"

      - alert: DiskFillingUp
        expr: predict_linear(node_filesystem_avail_bytes{fstype!~"tmpfs|overlay"}[6h], 24*3600) < 0
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "{{ $labels.mountpoint }} on {{ $labels.instance }} will be full within 24 hours"

      - alert: DiskAlmostFull
        expr: (node_filesystem_avail_bytes{fstype!~"tmpfs|overlay"} / node_filesystem_size_bytes{fstype!~"tmpfs|overlay"}) < 0.10
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "{{ $labels.mountpoint }} on {{ $labels.instance }} has under 10% free"

      - alert: HighMemoryUse
        expr: (1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) > 0.90
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "{{ $labels.instance }} is using over 90% of its memory"

      - alert: HighCpuUse
        expr: 100 - avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100 > 90
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "{{ $labels.instance }} CPU has been over 90% for 15 minutes"

      - alert: Watchdog
        expr: vector(1)
        labels:
          severity: none
        annotations:
          summary: "Always firing; route it to a dead-man's-switch so silence means the alerting path is broken"
```
The queries are from the PromQL tables in [Prometheus](../apps/prometheus.md). Tune thresholds after a week of real data. Disk alerts need the `rootfs` mount: they work here because of `--path.rootfs=/host`.

### 5. Alertmanager: route, e-mail and the dead-man's switch
`alertmanager/alertmanager.yml`:
```yaml
global:
  smtp_smarthost: "smtp.example.com:587"
  smtp_from: "alerts@example.com"
  smtp_auth_username: "alerts@example.com"
  smtp_auth_password_file: /etc/alertmanager/smtp_password

route:
  receiver: email
  group_by: [alertname, instance]
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 12h
  routes:
    - matchers:
        - alertname = "Watchdog"
      receiver: deadmans-switch
      repeat_interval: 5m

receivers:
  - name: email
    email_configs:
      - to: "you@example.com"
  - name: deadmans-switch
    webhook_configs:
      - url: "https://hc-ping.com/<UUID>"
        send_resolved: false

inhibit_rules:
  - source_matchers:
      - severity = "critical"
    target_matchers:
      - severity = "warning"
    equal: [instance]
```
Set the Healthchecks period to about 10 minutes. A missing ping then means Prometheus, Alertmanager or the network path is down. Alertmanager posts JSON; whether Healthchecks accepts that body unchanged is *unverified*, so check the check's log after the first ping. The inhibit rule silences warnings for an instance that already has a critical alert.

### 6. Grafana: data source
`grafana/provisioning/datasources/prometheus.yml` ([Grafana](../apps/grafana.md)):
```yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
```

### 7. Validate, start and import dashboards
Check the files before you start anything:
```bash
docker run --rm -v "$PWD/prometheus:/etc/prometheus:ro" --entrypoint promtool prom/prometheus:<VERSION> check config /etc/prometheus/prometheus.yml
docker run --rm -v "$PWD/alertmanager:/etc/alertmanager:ro" --entrypoint amtool prom/alertmanager:<VERSION> check-config /etc/alertmanager/alertmanager.yml
docker compose config -q
docker compose up -d
docker compose ps
```
Log in to Grafana on `http://127.0.0.1:3000` (user `admin`, the password from `secrets/grafana_admin_password`). Import dashboard `1860` (Node Exporter Full) and `893` (Docker and system monitoring) through **Dashboards, New, Import** ([Grafana](../apps/grafana.md), handy dashboard IDs). Whether those dashboards match your current exporter versions is *unverified*.

## Verify
```bash
curl -s localhost:9090/-/ready
curl -s localhost:9090/api/v1/targets | jq -r '.data.activeTargets[] | "\(.labels.job) \(.health)"'
curl -s localhost:9090/api/v1/rules | jq -r '.data.groups[].rules[] | "\(.name) \(.health)"'
curl -s localhost:9093/api/v2/alerts | jq -r '.[].labels.alertname'      # Watchdog
curl -s -u admin:<PASSWORD> localhost:3000/api/health
```
Every target should be `up`, every rule `ok`, and `Watchdog` listed. Then prove an alert reaches you: stop a scraped service (`docker compose stop cadvisor`), wait five minutes for `TargetDown`, check the e-mail, and start it again. Also check the Healthchecks dashboard shows recent pings.

## Troubleshooting
SYMPTOM | FIX
---|---
Target `down`, `no such host` | Wrong service name, or the service is not on the `monitoring` network
Target `down`, `connection refused` | Wrong port, or the exporter listens only on `127.0.0.1` (node_exporter with host networking needs the host address)
node_exporter shows the container's disk, not the host's | The `/:/host:ro,rslave` mount or `--path.rootfs=/host` is missing
cAdvisor shows no per-container metrics | Check the four bind mounts; on SELinux or some kernels extra flags are needed (see upstream docs)
`promtool` or `amtool` reports a YAML error | Fix indentation; `docker compose logs prometheus alertmanager` show the same error
Alert fires but no e-mail | `docker compose logs alertmanager` shows the SMTP error; check the smarthost, port and password file permissions
`permission denied` reading a secret | The container user cannot read the file; set mode `644` inside the `700` secrets directory
Prometheus config change not applied | `curl -X POST localhost:9090/-/reload` (needs `--web.enable-lifecycle`, set above) or restart the container
Grafana shows "No data" | Data source URL must use the Compose service name (`http://prometheus:9090`); check the time range
Disk fills with metrics | Lower `--storage.tsdb.retention.time` or set `--storage.tsdb.retention.size`

## Rollback / Cleanup
```bash
cd /opt/stacks/monitoring
docker compose down          # keeps the data volumes
docker compose down -v       # destructive: also deletes metrics and Grafana state
```
Remove the Healthchecks check, and any firewall rule that opened port 9100 on other hosts.

## Related Sheets
- [Prometheus](../apps/prometheus.md) · [Grafana](../apps/grafana.md) · [Traefik](../apps/traefik.md) · [Linux Performance Troubleshooting](../linux/performance-troubleshooting.md) · [Docker Troubleshooting](../docker/docker-troubleshooting.md)
- [Docker-Compose](../docker/docker-compose.md) · [Docker Networking](../docker/docker-networking.md) · [UFW (uncomplicated firewall)](../linux/ufw.md) · [curl](../tools/curl.md) · [jq](../tools/jq.md)
- [Docker Service Deploy](docker-service-deploy.md) · [New Server Checklist](new-server-checklist.md) · [Automate Container Updates Safely](automate-container-updates.md) · [Off-Site Docker Host Backup with restic](offsite-docker-host-backup.md)

# Grafana
Operational dashboards for your data here, there, or anywhere. Commonly paired with [Prometheus](prometheus.md).

Project Homepage: [Grafana Homepage](https://grafana.com)
Documentation: [Grafana Docs](https://grafana.com/docs/)

---
## Run with Docker
```bash
docker run -d --name grafana -p 3000:3000 -v grafana-data:/var/lib/grafana grafana/grafana-oss
```
Default login is `admin` / `admin` (you are asked to change it on first login).

## Install on Ubuntu/Debian
```bash
sudo apt install -y apt-transport-https software-properties-common wget
sudo mkdir -p /etc/apt/keyrings
wget -q -O - https://apt.grafana.com/gpg.key | gpg --dearmor | sudo tee /etc/apt/keyrings/grafana.gpg > /dev/null
echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" | sudo tee /etc/apt/sources.list.d/grafana.list
sudo apt update && sudo apt install -y grafana
sudo systemctl enable --now grafana-server
```

## Files and Paths
PATH | DESCRIPTION
---|---
`/etc/grafana/grafana.ini` | Main config
`/var/lib/grafana/` | Database and plugins
`/var/log/grafana/` | Logs
`/etc/grafana/provisioning/` | Provision data sources and dashboards as code

## Operations
COMMAND | DESCRIPTION
---|---
`sudo systemctl restart grafana-server` | Restart
`sudo grafana cli admin reset-admin-password <NEWPASS>` | Reset the admin password
`sudo grafana cli plugins install <PLUGIN-ID>` | Install a plugin (restart afterwards)
`sudo grafana cli plugins ls` | List installed plugins
`curl -u admin:<PASS> localhost:3000/api/health` | Health check
`GF_SECURITY_ADMIN_PASSWORD=<PASS>` | Env var form of any `grafana.ini` setting: `GF_<SECTION>_<KEY>`

## Provision a Data Source
`/etc/grafana/provisioning/datasources/prometheus.yml`
```yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
```

## Provision Dashboards
`/etc/grafana/provisioning/dashboards/default.yml`
```yaml
apiVersion: 1
providers:
  - name: default
    folder: ""
    type: file
    options:
      path: /var/lib/grafana/dashboards
```

## Handy Dashboard IDs
Import via **Dashboards > New > Import** and enter the ID.

ID | DASHBOARD
---|---
`1860` | Node Exporter Full
`893` | Docker and system monitoring
`13946` | Traefik 2
`15757` | Kubernetes / Views / Global

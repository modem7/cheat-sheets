# Alertmanager
Alertmanager receives alerts from [Prometheus](prometheus.md), groups and de-duplicates them, and routes them to email, webhooks or chat. Use it to turn "metric crossed a line" into one useful notification. Pair it with [ntfy](ntfy.md) for phone push, and see [Monitor a Homelab with Prometheus and Grafana](../recipes/monitor-homelab-prometheus-grafana.md) for the full stack.

Documentation: [Alerting overview](https://prometheus.io/docs/alerting/latest/alertmanager/), [Configuration](https://prometheus.io/docs/alerting/latest/configuration/)

## Prometheus Side
Alert rules live in a rules file loaded by Prometheus, and `alerting:` tells Prometheus where Alertmanager is. Point Prometheus at every Alertmanager, not a load balancer.

```yaml
# prometheus.yml
rule_files:
  - /etc/prometheus/rules/*.yml
alerting:
  alertmanagers:
    - static_configs:
        - targets: ["alertmanager:9093"]
```

```yaml
# /etc/prometheus/rules/basic.yml
groups:
  - name: example
    rules:
      - alert: InstanceDown
        expr: up == 0
        for: 5m
        labels:
          severity: page
        annotations:
          summary: "Instance {{ $labels.instance }} down"
          description: "{{ $labels.instance }} of job {{ $labels.job }} has been down for more than 5 minutes."
```

Reload Prometheus with `POST /-/reload`, which needs `--web.enable-lifecycle`.

## alertmanager.yml
```yaml
global:
  smtp_smarthost: 'smtp.example.com:587'
  smtp_from: 'alertmanager@example.com'
  smtp_auth_username: 'alertmanager@example.com'
  smtp_auth_password: 'SMTP_PASSWORD'
route:
  receiver: 'hook'
  group_by: ['alertname', 'instance']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  routes:
    - receiver: 'mail'
      matchers:
        - severity = "page"
receivers:
  - name: 'hook'
    webhook_configs:
      - url: 'http://127.0.0.1:9000/hook'
  - name: 'mail'
    email_configs:
      - to: 'ops@example.com'
inhibit_rules:
  - source_matchers:
      - severity = "page"
    target_matchers:
      - severity = "warning"
    equal: ['instance']
```

SETTING | DEFAULT | MEANING
---|---|---
`group_wait` | 30s | Wait before the first notification for a new group
`group_interval` | 5m | Wait before notifying about new alerts in an existing group
`repeat_interval` | 4h | Re-send an unresolved alert (make it a multiple of `group_interval`)
`send_resolved` | false for email | Send a message when the alert clears

An inhibit rule mutes the target alerts while a source alert is firing and the `equal` labels match, for example mute warnings while a page-level alert is active. The default port is 9093.

## Run and Reload
COMMAND | DESCRIPTION
---|---
`./alertmanager --config.file=alertmanager.yml` | Start with a config file
`amtool check-config alertmanager.yml` | Validate the config before reloading
`curl -X POST http://localhost:9093/-/reload` | Reload the config (or send `SIGHUP`)

The Docker image name, and the `amtool alert`, `amtool silence` and `amtool config routes test` subcommands, are unverified here. Silences are managed in the Alertmanager web UI per the docs.

## Tips
- Group by labels that identify one problem (`alertname`, `instance`) so a dead host gives one message, not fifty.
- Use `for:` in rules to ignore blips.
- Add an always-firing `Watchdog` alert and monitor it from outside (for example a push monitor in [Uptime Kuma](uptime-kuma.md)) to detect a dead alerting pipeline.
- Keep secrets out of the file when sharing it: use a mounted secret file or environment substitution in your deployment tooling.

## See Also
- [Prometheus](prometheus.md)
- [Grafana](grafana.md)
- [ntfy](ntfy.md)
- [Uptime Kuma](uptime-kuma.md)

# Loki and Grafana Alloy
Loki stores logs and is queried with LogQL from [Grafana](grafana.md). Grafana Alloy is the agent that collects Docker and journald logs and ships them to Loki. Promtail reached end of life on 2 March 2026, so use Alloy for new setups. Metrics live in [Prometheus](prometheus.md). For quick live log viewing without a database see [Dozzle](dozzle.md).

Documentation: [Loki](https://grafana.com/docs/loki/latest/), [Alloy](https://grafana.com/docs/alloy/latest/)

## Loki in Docker
Single container, filesystem storage. Loki runs as UID 10001, so a named volume avoids permission problems.

```yaml
services:
  loki:
    image: grafana/loki:3.7.0
    command: -config.file=/etc/loki/loki-config.yaml
    ports:
      - "3100:3100"
    volumes:
      - ./loki-config.yaml:/etc/loki/loki-config.yaml
      - loki-data:/loki
volumes:
  loki-data:
```

`loki-config.yaml` (the single-binary example from the Loki docs, with the paths moved off `/tmp`):

```yaml
auth_enabled: false
server:
  http_listen_port: 3100
common:
  ring:
    instance_addr: 127.0.0.1
    kvstore:
      store: inmemory
  replication_factor: 1
  path_prefix: /loki
schema_config:
  configs:
    - from: 2020-05-15
      store: tsdb
      object_store: filesystem
      schema: v13
      index:
        prefix: index_
        period: 24h
storage_config:
  filesystem:
    directory: /loki/chunks
```

Check it is up with `curl http://localhost:3100/ready` (returns `ready`). In Grafana add a Loki data source at `http://loki:3100` (the Compose service name, not `localhost`).

## Retention
Retention only works with a 24h index period. Changes are not retroactive.

```yaml
compactor:
  working_directory: /loki/retention
  retention_enabled: true
  delete_request_store: filesystem
limits_config:
  retention_period: 744h
```

`delete_request_store` is required when retention is on. The value `filesystem` matches the `object_store` above (unverified for this exact setup, check Loki's startup log).

## Alloy in Docker
```yaml
services:
  alloy:
    image: grafana/alloy:latest
    command: run --server.http.listen-addr=0.0.0.0:12345 --storage.path=/var/lib/alloy/data /etc/alloy/config.alloy
    ports:
      - "12345:12345"
    volumes:
      - ./config.alloy:/etc/alloy/config.alloy
      - /var/run/docker.sock:/var/run/docker.sock
      - alloy-data:/var/lib/alloy/data
volumes:
  alloy-data:
```

- The UI listens on `127.0.0.1:12345` by default, so set `0.0.0.0` as above to reach it from outside the container.
- Persist `--storage.path`, which holds the read positions.
- Mounting `docker.sock` is root-equivalent on the host. The mount is needed for Docker log collection (inferred, not stated in the docs).

## Alloy Config: Docker Logs
`config.alloy`. The relabel step turns the container name into a `container` label, because `loki.write` drops labels that start with `__`.

```text
discovery.docker "containers" {
  host = "unix:///var/run/docker.sock"
}

loki.relabel "docker" {
  forward_to = []
  rule {
    source_labels = ["__meta_docker_container_name"]
    target_label  = "container"
  }
}

loki.source.docker "default" {
  host          = "unix:///var/run/docker.sock"
  targets       = discovery.docker.containers.targets
  labels        = {"job" = "docker"}
  relabel_rules = loki.relabel.docker.rules
  forward_to    = [loki.write.local.receiver]
}

loki.write "local" {
  endpoint {
    url = "http://loki:3100/loki/api/v1/push"
  }
}
```

Docker container names may carry a leading `/` in the label (unverified, check on your host).

## Alloy Config: journald
```text
loki.relabel "journal" {
  forward_to = []
  rule {
    source_labels = ["__journal__systemd_unit"]
    target_label  = "unit"
  }
}

loki.source.journal "read" {
  max_age       = "12h"
  relabel_rules = loki.relabel.journal.rules
  forward_to    = [loki.write.local.receiver]
  labels        = { job = "systemd-journal", host = "HOSTNAME" }
}
```

On a bare-metal install the `alloy` user must be in the `adm` and `systemd-journal` groups. Mounting the journal into a container is unverified.

## Alloy Commands
COMMAND | DESCRIPTION
---|---
`alloy run <CONFIG_FILE>` | Run in the foreground (a directory loads every `*.alloy` file)
`alloy fmt <FILE>` | Print the formatted file (`-w` rewrites it, `-t` exits non-zero if changes are needed)
`alloy convert --source-format=promtail --output=<OUT> <IN>` | Convert a Promtail config to Alloy
`curl -X POST http://localhost:12345/-/reload` | Reload the config (or send `SIGHUP`)

`alloy fmt` checks syntax only, not component arguments.

## LogQL
QUERY | DESCRIPTION
---|---
`{container="nginx"}` | All logs from a stream selector (`=`, `!=`, `=~`, `!~`)
`{container="nginx"} \|= "error"` | Lines containing a string (`!=` excludes, `\|~` is a regex)
`{container="nginx"} \|= "error" \| json` | Parse JSON lines into labels
`{job="docker"} \| logfmt \| level="error"` | Parse `key=value` lines and filter on a field
`count_over_time({container="nginx"}[5m])` | Number of lines in the last 5 minutes
`sum by (container) (rate({job="docker"} \|= "error" [1m]))` | Error rate per container

Put line filters (`|=`) before parsers because they are faster. Keep labels low-cardinality: container, host and job are fine, request IDs are not.

## logcli
COMMAND | DESCRIPTION
---|---
`export LOKI_ADDR=http://localhost:3100` | Point `logcli` at Loki
`logcli query '{container="nginx"}'` | Query (default: last hour, 30 lines)
`logcli query --since=6h --limit=0 '{job="docker"}'` | Everything from the last 6 hours
`logcli query --tail '{container="nginx"}'` | Follow live
`logcli labels` / `logcli labels job` | List label names, or the values of one label

## Troubleshooting
SYMPTOM | FIX
---|---
No logs in Grafana | Check the Alloy UI on port 12345 for failed components, then `docker logs alloy`
Alloy UI unreachable | Add `--server.http.listen-addr=0.0.0.0:12345`
Loki fails with permission denied | Use a named volume or `chown -R 10001:10001` the bind mount
Logs duplicate after a restart | The Alloy storage path was not persisted

## See Also
- [Grafana](grafana.md)
- [Prometheus](prometheus.md)
- [Dozzle](dozzle.md)
- [journalctl](../linux/journalctl.md)
- [Monitor a Homelab with Prometheus and Grafana](../recipes/monitor-homelab-prometheus-grafana.md)

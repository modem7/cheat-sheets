# Graylog
Graylog is a log management platform: it receives logs over syslog, GELF or Beats, stores them in a search backend and gives you streams, dashboards and alerts. Use it for central logging of a homelab when you want a ready-made UI. For a lighter option see [Loki and Alloy](loki-alloy.md), and for the Elastic alternative see [Elastic Stack](elastic-stack.md). These notes follow the 7.2 documentation.

Documentation: [Graylog docs](https://go2docs.graylog.org/current/)
Project: [Graylog2/docker-compose](https://github.com/Graylog2/docker-compose)

## Components
COMPONENT | ROLE
---|---
Graylog server | Web UI, API, inputs and processing
Data Node | Search and storage backend (OpenSearch based)
MongoDB | Graylog's own configuration and metadata

## Install (Docker)
Graylog publishes a compose file in `Graylog2/docker-compose` (the `open-core` directory) that runs `mongo:7.0`, `graylog/graylog-datanode:7.2` and `graylog/graylog:7.2`. Copy `.env.example` to `.env` and set two secrets:

VARIABLE | MEANING
---|---
`GRAYLOG_PASSWORD_SECRET` | Random string, at least 16 characters. The Data Node needs the same value as `GRAYLOG_DATANODE_PASSWORD_SECRET`
`GRAYLOG_ROOT_PASSWORD_SHA2` | SHA-256 hash of the admin password

Generate a secret and a hash with the commands from the Graylog docs:

```bash
< /dev/urandom tr -dc A-Z-a-z-0-9 | head -c${1:-96}; echo
echo -n "Enter Password: " && head -1 </dev/stdin | tr -d '\n' | sha256sum | cut -d" " -f1
```

Other variables in the compose file include `GRAYLOG_HTTP_BIND_ADDRESS=0.0.0.0:9000`, `GRAYLOG_HTTP_EXTERNAL_URI` (set it to the URL users browse to) and `GRAYLOG_MONGODB_URI`.

```bash
sudo sysctl -w vm.max_map_count=1048576
docker compose up -d
docker compose logs graylog
```

- Graylog's compose comments use `262144`. Elastic's current documentation says `1048576`, and the larger value satisfies both. Make it permanent in `/etc/sysctl.d/`.
- On first start the log shows a temporary admin user and password for the preflight page. Browse to port 9000 on the Docker host's IP, not `0.0.0.0`. After provisioning, log in as `admin` with the password you hashed.
- Keep `.env` out of Git.

## Ports
PORT | USE
---|---
9000 | Web UI and API
12201 | GELF (TCP and UDP)
5044 | Beats
5140 | Syslog (TCP and UDP) in the compose file
5555 | Raw (TCP and UDP)
13301, 13302 | Forwarder

The compose file binds all of these to `127.0.0.1`. Change that for the ports that other hosts need to reach, for example `"0.0.0.0:5140:5140/udp"`. Inputs are **not created for you**. Add them under System, Inputs in the UI, and use a port above 1024 so Graylog does not need root.

## Sending Logs
- Create an input first (Syslog UDP or TCP, GELF, or Beats), then point senders at its port.
- Docker's `gelf` logging driver and rsyslog forwarding both work in principle, but the exact snippets were **not verified** against the Graylog docs.
- For Beats senders see [Elastic Stack](elastic-stack.md). Alloy can also forward, see [Loki and Alloy](loki-alloy.md).

## Concepts
TERM | MEANING
---|---
Input | A listener that receives messages
Stream | A rule-based subset of messages, used for routing and alerts
Pipeline | Processing rules applied to messages
Index set | How messages are stored and rotated, including retention
Event | An alert definition run on a stream

Retention and rotation were not verified here, so check the index set settings in the UI and size them to your disk.

## Troubleshooting
SYMPTOM | CHECK
---|---
Preflight page will not load | Use the host's real IP, check `docker compose logs graylog`
Data Node will not start | `vm.max_map_count`, memory limits, and that both secrets match
Login fails | The hash must be of the plain password with no trailing newline or a trailing dash
No messages | The input exists, its port is published, and the sender uses the right protocol

## Not Verified
REST API token authentication, inputs and streams details, pipelines, extractors, index set retention, `server.conf`, and the rsyslog and Docker GELF snippets.

## See Also
- [Elastic Stack](elastic-stack.md)
- [Loki and Alloy](loki-alloy.md)
- [Grafana](grafana.md)
- [Notification Services](../homelab/notification-services.md)

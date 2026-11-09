# Beszel
Beszel is a lightweight monitoring hub for servers and Docker hosts: CPU, memory, disk, network, container stats, temperatures, GPU and SMART, with alerts and history. It uses far fewer resources than the [Prometheus](prometheus.md) and [Grafana](grafana.md) stack, so it suits small homelabs.

Documentation: [Beszel](https://beszel.dev/guide/getting-started)

## Architecture
- **Hub** is the web app (PocketBase based) on port 8090.
- **Agent** runs on each monitored host and listens on port 45876 by default (`LISTEN`).

## Hub (Docker)
```yaml
services:
  beszel:
    image: henrygd/beszel:latest
    restart: unless-stopped
    ports:
      - "8090:8090"
    volumes:
      - ./beszel_data:/beszel_data
    environment:
      APP_URL: https://beszel.example.com
```

Open the hub and create the admin account on first visit. Alternatively set `USER_EMAIL` and `USER_PASSWORD` for a new install. Binary install:

```bash
curl -sL https://get.beszel.dev/hub -o /tmp/install-hub.sh && chmod +x /tmp/install-hub.sh && /tmp/install-hub.sh
```

## Add a System
Use **Add System** in the hub. It generates the compose snippet or install command with the right key. A universal token at `/settings/tokens` (0.12.0 and later) lets an agent register itself.

## Agent (Docker)
```yaml
services:
  beszel-agent:
    image: henrygd/beszel-agent:latest
    restart: unless-stopped
    network_mode: host
    volumes:
      - ./beszel_agent_data:/var/lib/beszel-agent
      - /var/run/docker.sock:/var/run/docker.sock:ro
    environment:
      LISTEN: 45876
      KEY: "HUB_PUBLIC_KEY"
      HUB_URL: https://beszel.example.com
      TOKEN: "UNIVERSAL_TOKEN"
```

`PORT` is the old name for `LISTEN` and is deprecated. Binary agent install, with flags `-k` key, `-p` port, `-t` token, `-url` hub URL and `--auto-update`:

```bash
curl -sL https://get.beszel.dev -o /tmp/install-agent.sh && chmod +x /tmp/install-agent.sh && /tmp/install-agent.sh
```

It creates a `beszel` user and a systemd service. Update with `./beszel-agent update`.

## Hub and Agent on One Host
Share a socket instead of a network port: mount `./beszel_socket` into both containers, set the agent `LISTEN=/beszel_socket/beszel.sock`, and add the system with host `/beszel_socket/beszel.sock`. `localhost` does not work for the local agent.

## Agent Options
VARIABLE | DESCRIPTION
---|---
`SMART_DEVICES` | Disks to read, e.g. `/dev/nvme0:nvme,/dev/sda:sat` (see [smartctl](../linux/smartctl.md))
`SMART_INTERVAL` | Default `1h`
`GPU_COLLECTOR` | Ordered list: `nvtop`, `nvml`, `nvidia-smi`, `intel_sysfs`, `intel_gpu_top`, `amd_sysfs`, `rocm-smi`, `macmon`, `powermetrics`
`SENSORS`, `PRIMARY_SENSOR` | Choose temperature sensors
`EXTRA_FILESYSTEMS` | Monitor extra mounts
`SERVICE_PATTERNS` | Watch systemd services
`HEARTBEAT_URL`, `HEARTBEAT_INTERVAL`, `HEARTBEAT_METHOD` | Ping an external monitor such as [Uptime Kuma](uptime-kuma.md)
`DOCKER_HOST` | Use a socket proxy

Rootless containers may lose temperature, GPU, SMART and systemd metrics.

## Login and Backup
- **OIDC:** redirect URL is `https://BESZEL_URL/api/oauth2-redirect`. Enable OAuth2 on the `users` collection in the PocketBase admin at `/_/`. Works with [Authelia](../security/authelia.md), [Authentik](../security/authentik.md), [Pocket ID](pocket-id.md) and [Keycloak](../security/keycloak.md).
- **Variables:** `DISABLE_PASSWORD_AUTH=true`, `USER_CREATION=true`, `OAUTH_DEFAULT_USER_ROLE` (`user` or `readonly`), `MFA_OTP` (needs SMTP).
- **Backup:** Settings, Backups at `/#/settings/backups` (disk or S3-compatible), or stop the hub and copy `beszel_data`.

Alerts are configured in the UI (alert settings are not covered here).

## See Also
- [Uptime Kuma](uptime-kuma.md)
- [Prometheus](prometheus.md)
- [Grafana](grafana.md)
- [Komodo](komodo.md)

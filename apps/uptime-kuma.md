# Uptime Kuma
Uptime Kuma is a self-hosted uptime monitor with a web UI, many monitor types, notifications and public status pages. Use it to know when a service, host or certificate has gone down. For metrics-based alerting see [Prometheus](prometheus.md) and [Alertmanager](alertmanager.md).

Project: [Uptime Kuma](https://github.com/louislam/uptime-kuma)
Documentation: [Wiki](https://github.com/louislam/uptime-kuma/wiki)

## Install
```yaml
services:
  uptime-kuma:
    image: louislam/uptime-kuma:2
    restart: unless-stopped
    volumes:
      - ./data:/app/data
    ports:
      - "3001:3001"
```

Or `docker run -d --restart=always -p 3001:3001 -v uptime-kuma:/app/data --name uptime-kuma louislam/uptime-kuma:2`. Bind to localhost only with `-p 127.0.0.1:3001:3001`. Open `http://HOST:3001` to create the admin account.

## Update
```bash
docker compose pull
docker compose up -d --force-recreate
```

## Monitor Types
TYPE | USE
---|---
HTTP(s) | Status code and response time of a URL
HTTP(s) Keyword / Json Query | Page must contain text, or a JSON field must match
TCP Port | A port accepts connections
Ping | ICMP reachability
DNS Record | A record resolves to the expected value
Push | A job calls Uptime Kuma; alert if it stops (heartbeat for cron and backups)
Docker Container | Container is running
Websocket, Steam Game Server, SFTP | Other protocols (SFTP added in 2.5.4)

Notifications include Telegram, Discord, Gotify, Slack, Pushover and email (SMTP), and over 90 services in all. For a self-hosted push service see [ntfy](ntfy.md). Status pages can be mapped to their own domain.

## Reverse Proxy
Uptime Kuma needs WebSocket headers, and does **not** support a sub-path such as `/uptimekuma` (use a subdomain).

```nginx
location / {
  proxy_pass         http://localhost:3001;
  proxy_http_version 1.1;
  proxy_set_header   Upgrade $http_upgrade;
  proxy_set_header   Connection "upgrade";
  proxy_set_header   Host $host;
}
```

If the UI is only reachable through a proxy, set Settings, Reverse Proxy, HTTP Headers, Trust Proxy to Yes. See [Reverse Proxy Patterns](../homelab/reverse-proxy-patterns.md).

## Gotchas
- Keep `/app/data` on a local disk or Docker volume. NFS and SMB are not supported because SQLite needs POSIX file locks.
- Back up the data directory. A stop-then-copy backup is the safe approach (unverified, the project has no documented procedure).
- Run Uptime Kuma on a different host from the things it watches, or it goes down with them.

## See Also
- [Alertmanager](alertmanager.md)
- [ntfy](ntfy.md)
- [Prometheus](prometheus.md)
- [Docker Compose](../docker/docker-compose.md)

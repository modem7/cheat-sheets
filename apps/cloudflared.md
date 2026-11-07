# cloudflared
`cloudflared` is the Cloudflare Tunnel connector. It makes an outbound connection to Cloudflare and publishes local HTTP (and some TCP) services on your hostnames with no inbound port open. This sheet covers the CLI, a locally managed `config.yml` with ingress rules, and Docker Compose.

Documentation: [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/) · [Configuration file](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/local-management/configuration-file/)
Project: [cloudflare/cloudflared](https://github.com/cloudflare/cloudflared)

> **Verification:** command names, flags and environment variables were read from `cloudflared --help` output of the `cloudflare/cloudflared` image (version 2026.10.7), and the example `config.yml` was accepted by `cloudflared tunnel ingress validate` and `ingress rule`. Config keys and the create, route and run flow were checked against the Cloudflare docs. **Not verified** (no Cloudflare account was used): live tunnel creation, DNS routing, the `service install` behaviour, the default config and credentials directories on each OS, and the Compose health check. Cloudflare docs also cover the remotely managed (dashboard) tunnels in detail; this sheet covers them only briefly.

See also: [Cloudflare](../cloud/provider/cloudflare.md) · [Expose a Service with Cloudflare Tunnel](../recipes/expose-service-cloudflare-tunnel.md) · [Docker-Compose](../docker/docker-compose.md) · [Reverse Proxy Patterns](../homelab/reverse-proxy-patterns.md) · [Tailscale](tailscale.md) · [Traefik](traefik.md)

---
## Two Ways to Run a Tunnel
MODE | HOW IT WORKS | USE IT WHEN
---|---|---
Remotely managed | Create the tunnel and hostnames in the Zero Trust dashboard, run `cloudflared tunnel run --token TOKEN` | You want to change routes without touching the host
Locally managed | `cloudflared tunnel login`, `create`, `route dns`, and a `config.yml` with ingress rules | You want the routes in a file under version control

A tunnel is one or the other: a tunnel created with the dashboard takes its ingress from the dashboard, and `config.yml` ingress is ignored for it (unverified detail; check the Cloudflare docs).

## CLI Commands
COMMAND | DESCRIPTION
---|---
`cloudflared --version` / `cloudflared version` | Print the version
`cloudflared tunnel login` | Open a browser, pick a zone, and write `cert.pem`
`cloudflared tunnel create NAME` | Create a tunnel and write `<TUNNEL_UUID>.json` credentials
`cloudflared tunnel create --credentials-file FILE NAME` | Write the credentials to a chosen path
`cloudflared tunnel list` | List tunnels (`--name`, `--name-prefix`, `--show-deleted`, `--output json`)
`cloudflared tunnel info NAME` | Active connectors for a tunnel
`cloudflared tunnel route dns NAME app.example.com` | Create a CNAME to `<UUID>.cfargotunnel.com`
`cloudflared tunnel route dns -f NAME app.example.com` | Overwrite an existing DNS record
`cloudflared tunnel run NAME` | Run the tunnel using the default config
`cloudflared tunnel --config FILE run NAME` | Run with a specific config file
`cloudflared tunnel run --token TOKEN` | Run a dashboard-managed tunnel from its token
`cloudflared tunnel token NAME` | Print the run token for an existing tunnel (a secret)
`cloudflared tunnel run --url http://localhost:8080 NAME` | Single origin with no ingress rules
`cloudflared tunnel run --hello-world NAME` | Serve a built-in test page
`cloudflared tunnel ready` | Call `/ready` and exit non-zero if not ready
`cloudflared tunnel cleanup NAME` | Stop stale connections for a tunnel (`-c` limits to one connector ID)
`cloudflared tunnel delete NAME` | Delete a tunnel with no active connections
`cloudflared tunnel delete -f NAME` | Delete even if connected or with routes attached
`cloudflared tunnel diag` | Create a diagnostic report from a local instance
`cloudflared tail` | Stream logs from a remote cloudflared
`sudo cloudflared service install` / `uninstall` | Install or remove the system service
`cloudflared update` | Update the binary (not for containers)

A tunnel can only be deleted with no connections, so stop the connector first. Remove the DNS records made by `route dns` yourself after deleting a tunnel (unverified).

## Useful Options and Variables
OPTION | VARIABLE | MEANING
---|---|---
`--config FILE` | | Config file in YAML (placed after `tunnel`)
`--no-autoupdate` | `NO_AUTOUPDATE` | Stop periodic self-update and restart
`--loglevel LEVEL` | | `debug`, `info`, `warn`, `error` or `fatal`
`--logfile FILE` | `TUNNEL_LOGFILE` | Log to a file
`--output json` | `TUNNEL_LOG_OUTPUT` | JSON log lines
`--metrics ADDR` | `TUNNEL_METRICS` | Metrics listen address (default binds to all interfaces in a container)
`--credentials-file FILE` | `TUNNEL_CRED_FILE` | Credentials JSON path
`--origincert FILE` | `TUNNEL_ORIGIN_CERT` | Path to `cert.pem`
`--token TOKEN` | `TUNNEL_TOKEN` | Run token (also `TUNNEL_TOKEN_FILE`)
`--region VALUE` | `TUNNEL_REGION` | Edge region (empty is global)
`--edge-ip-version 4\|6\|auto` | `TUNNEL_EDGE_IP_VERSION` | Edge IP family
`--label TEXT` | | Name for this connector
`--grace-period DURATION` | | Wait for in-flight requests on stop

## config.yml and Ingress
Put it at `~/.cloudflared/config.yml`, or pass `--config`. The last ingress rule must be a catch-all, and it must have no hostname.

```yaml
tunnel: TUNNEL_UUID
credentials-file: /etc/cloudflared/TUNNEL_UUID.json

originRequest:
  connectTimeout: 30s

ingress:
  - hostname: app.example.com
    service: http://app:8080
  - hostname: api.example.com
    path: ^/v1/
    service: http://api:3000
    originRequest:
      noTLSVerify: true
  - hostname: "*.example.com"
    service: http://app:8080
  - service: http_status:404
```

FIELD | MEANING
---|---
`tunnel` | Tunnel UUID
`credentials-file` | Path to the credentials JSON
`ingress` | Ordered list of rules; the first match wins
`hostname` | Exact name or `*.example.com` (the wildcard cannot be mid-name)
`path` | Regular expression matched against the URL path
`service` | Origin: `http://HOST:PORT`, `https://HOST:PORT`, `ssh://HOST:22`, `tcp://HOST:PORT`, `unix:/PATH`, `http_status:CODE`, `hello_world` (the last two unverified)
`originRequest` | Per-origin settings; top-level values are defaults. Documented example keys: `connectTimeout`, `disableChunkedEncoding`; `noTLSVerify` and `httpHostHeader` are common (unverified)

COMMAND | DESCRIPTION
---|---
`cloudflared tunnel --config FILE ingress validate` | Check the rules (the catch-all must be last)
`cloudflared tunnel --config FILE ingress rule https://app.example.com/x` | Show which rule matches a URL

## Docker Compose
Dashboard-managed (token) tunnel. Keep the token out of the file with a secret file (mode `600`, not in git):

```yaml
services:
  cloudflared:
    image: cloudflare/cloudflared:2026.10.7
    restart: unless-stopped
    command: tunnel --no-autoupdate run
    environment:
      TUNNEL_TOKEN_FILE: /run/secrets/tunnel_token
    secrets: [tunnel_token]
    networks: [proxy]

secrets:
  tunnel_token:
    file: ./tunnel-token

networks:
  proxy:
    external: true
```

Locally managed tunnel with `config.yml`. Origins are reached by service name on a shared network:

```yaml
services:
  cloudflared:
    image: cloudflare/cloudflared:2026.10.7
    restart: unless-stopped
    command: tunnel --no-autoupdate --config /etc/cloudflared/config.yml run
    volumes:
      - ./cloudflared:/etc/cloudflared:ro
    networks: [proxy]

networks:
  proxy:
    external: true
```

Put `config.yml` and `TUNNEL_UUID.json` in `./cloudflared/`, with `credentials-file: /etc/cloudflared/TUNNEL_UUID.json`. Run `login` and `create` once on any machine with a browser, then copy the JSON across. `cloudflared tunnel ready` returns a non-zero exit code when the tunnel is not ready, so it suits a health check (the exact Compose health check was not tested).

Pin the image to a release tag rather than `latest`, and use `--no-autoupdate` in containers ([Automate Container Updates Safely](../recipes/automate-container-updates.md)).

## Notes
- Cloudflare terminates TLS and sees traffic in clear text. Large video streaming over the self-serve plans is restricted ([Cloudflare](../cloud/provider/cloudflare.md)), so Plex or Jellyfin media streams are a poor fit.
- Put Cloudflare Access in front of private apps. A public hostname alone is open to everyone.
- The credentials JSON and run token are secrets: anyone holding them can run your tunnel.

## Troubleshooting
The error codes below come from Cloudflare's general error pages and were not reproduced (unverified).

SYMPTOM | FIX
---|---
Error 1033 | The tunnel has no healthy connector; check `cloudflared tunnel info NAME` and the container logs
Error 502 or 503 | The origin is unreachable from the connector; use a service name on the same Docker network, not `localhost`
`localhost` origin fails in a container | `localhost` is the cloudflared container itself; use the origin's service name
`ingress validate` fails | Last rule is not a catch-all, or a wildcard sits mid-hostname
DNS name does not resolve | Run `cloudflared tunnel route dns NAME HOSTNAME`; use `-f` to replace an existing record
Cannot delete a tunnel | Stop connectors, run `tunnel cleanup NAME`, or use `delete -f`
Self-update restarts the container | Add `--no-autoupdate`

## See Also
- [Cloudflare](../cloud/provider/cloudflare.md)
- [Expose a Service with Cloudflare Tunnel](../recipes/expose-service-cloudflare-tunnel.md)
- [Docker-Compose](../docker/docker-compose.md)
- [Reverse Proxy Patterns](../homelab/reverse-proxy-patterns.md)
- [Tailscale](tailscale.md)
- [Traefik](traefik.md)

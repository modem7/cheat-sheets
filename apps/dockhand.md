# Dockhand
Self-hosted web UI for managing **Docker ([[docker]])** hosts: containers, images, volumes, networks and Compose stacks ([[docker-compose]]) across one or many hosts. Similar in purpose to [[portainer]], but Docker-only and newer.

Project Homepage: [Dockhand](https://dockhand.pro)
Documentation: [Dockhand Manual](https://dockhand.pro/manual)
Source: [Finsys/dockhand](https://github.com/Finsys/dockhand)
Remote agent: [Finsys/hawser](https://github.com/Finsys/hawser)

---
## Install (Docker)
```bash
docker run -d \
  --name dockhand \
  --restart unless-stopped \
  -p 3000:3000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v dockhand_data:/app/data \
  fnsys/dockhand:latest
```
Open `http://<HOST>:3000`.

### Docker Compose
```yaml
services:
  dockhand:
    image: fnsys/dockhand:latest
    container_name: dockhand
    restart: unless-stopped
    ports:
      - "3000:3000"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - dockhand_data:/app/data
volumes:
  dockhand_data:
```

### Stacks With Relative Paths (Matching Paths)
If your Compose stacks use relative bind mounts such as `./config.yml:/config.yml`, the Docker daemon resolves them on the host. Use the same path inside and outside the container and set `DATA_DIR`:
```bash
mkdir -p /opt/dockhand
docker run -d \
  --name dockhand \
  --restart unless-stopped \
  -p 3000:3000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /opt/dockhand:/opt/dockhand \
  -e DATA_DIR=/opt/dockhand \
  fnsys/dockhand:latest
```

## First Run
- **Authentication is disabled on first launch.** Go to **Settings > Authentication**, enable it and create the first admin user straight away.
- Dockhand shows a warning if it is reachable beyond localhost with auth off and a read-write Docker socket: anyone who can reach it can create containers on the host.

## Configuration (Environment Variables)
VARIABLE | DESCRIPTION
---|---
`DATA_DIR` | Directory for persistent data (database, stacks, git repos). Default `/app/data`
`DATABASE_URL` | `postgres://user:pass@host:5432/dbname`. Unset means SQLite (default). Switching does not migrate data
`PUID` / `PGID` | Run as a specific user; the entrypoint fixes permissions then drops privileges
`OIDC_AUTOLOGIN` | Skip the login form when exactly one OIDC provider is enabled (`/login?local=1` still reaches the form)

> The manual lists many more variables. Check the manual for the version you run.

## Managing Other Hosts (Environments)
Add hosts under **Settings > Environments**. Connection types:

TYPE | DESCRIPTION
---|---
Local socket | The Docker socket mounted into Dockhand
Direct TCP/TLS | Docker's remote API on the target host
Hawser (standard) | Agent listens on the remote host, Dockhand connects to it (LAN or static IP)
Hawser (edge) | Agent dials out to Dockhand over WebSocket (VPS, NAT, dynamic IP, no inbound port)

Hawser is the Dockhand agent. In standard mode a `TOKEN` is mandatory for non-loopback binds, otherwise the agent refuses to start.

```bash
# Standard mode (agent listens on 2376)
docker run -d --name hawser --restart unless-stopped \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /opt/hawser-stacks:/opt/hawser-stacks \
  -e STACKS_DIR=/opt/hawser-stacks \
  -e TOKEN=<SECRET_TOKEN> \
  -p 2376:2376 \
  ghcr.io/finsys/hawser:latest

# Edge mode (agent connects out to Dockhand)
docker run -d --name hawser --restart unless-stopped \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /opt/hawser-stacks:/opt/hawser-stacks \
  -e STACKS_DIR=/opt/hawser-stacks \
  -e DOCKHAND_SERVER_URL=wss://<DOCKHAND_HOST>/api/hawser/connect \
  -e TOKEN=<AGENT_TOKEN> \
  ghcr.io/finsys/hawser:latest
```
Hawser can also be installed as a systemd service from a release binary (`/etc/hawser/config` holds `TOKEN`, `PORT` or `DOCKHAND_SERVER_URL`). Use TLS (`TLS_CERT`, `TLS_KEY`) for standard mode in production.

## Operations
COMMAND | DESCRIPTION
---|---
`docker logs dockhand` | Check start-up and errors
`docker pull fnsys/dockhand:latest && docker rm -f dockhand` then re-run the install command | Manual upgrade (data stays in `dockhand_data`)
`docker run --rm -v dockhand_data:/data -v $(pwd):/backup busybox tar czf /backup/dockhand.tgz /data` | Back up the data volume (stop Dockhand first for a consistent SQLite copy)

- Settings > About has a self-update check. If you use a socket proxy instead of mounting `docker.sock`, add an environment pointing at that Docker host so the check can reach the daemon.
- **Keep the `.encryption_key` file** in the data directory with the database. Stored secrets (registry passwords, Git credentials, Hawser tokens, OIDC and LDAP secrets) are encrypted with it and are unreadable without it.
- Built-in **Restic** backup destinations back up your containers' volume data on a schedule, with restore, check and prune.

## Features Worth Knowing
- **Compose stacks**: visual and YAML editor; deploy from Git with webhooks and auto-sync.
- **Containers**: live logs, interactive shell, file browser, upload and download.
- **Images**: update tracking, layer inspection, Grype and Trivy vulnerability scans, scheduled prune and auto-update.
- **Network graph**, **volume browser**, **activity log** (audit trail) and **notifications**.
- **Auth**: local users and OIDC/SSO are free; RBAC and LDAP/AD are Enterprise features. In the free edition every logged-in user is a full admin.
- **Metrics**: a Prometheus `/metrics` endpoint (see [[prometheus]]). Keep it private if auth is off or it is made public.

## Security Notes
- `docker.sock` is root-equivalent on the host. Put Dockhand behind a reverse proxy ([[traefik]], [[nginx]]) with TLS, or on a VPN such as [[tailscale]]; do not publish port 3000 to the internet.
- Turn authentication on before anything else.
- Prefer Hawser with a token and TLS over exposing the raw Docker TCP API.
- The manual documents running Dockhand through a Docker socket proxy with restricted API permissions.

## Licence
Business Source License 1.1 (source-available, not open source). Per the project README: free for home labs and personal use, non-profits, education, sole traders, and for dev, test, staging, CI and evaluation by anyone. Running an organisation's live systems on it needs a commercial licence. Each version converts to Apache 2.0 four years after release. Read `LICENSE.txt` upstream for the exact terms.

## Portainer vs Dockhand
| | [[portainer]] | Dockhand |
|---|---|---|
| Scope | Docker, Swarm, Kubernetes, Nomad | Docker only |
| Maturity | Long established, large ecosystem | Newer, fast-moving |
| Licence | Community Edition (zlib), paid Business Edition | BSL 1.1, free for personal and non-production use |
| Remote hosts | Portainer Agent, Edge Agent | Hawser (standard and edge), direct TCP/TLS |
| Git stacks | Yes | Yes, with webhooks and auto-sync |
| Vulnerability scans | Limited in CE | Grype and Trivy built in |
| Access control | RBAC in Business Edition | RBAC and LDAP in Enterprise; OIDC free |
| First-run auth | Admin created on first visit (5 minute window) | Auth off until you enable it |

Pick Portainer for Kubernetes or Swarm, or if you want the most established tool. Pick Dockhand for a lightweight Docker-only UI with Git-driven stacks and image scanning.

## Not Verified
- Commands and settings were taken from the upstream README and manual (fetched Nov 2026) and not executed here.
- Image tags: the manual uses `fnsys/dockhand:latest`; Docker Hub tag lists, ARM support and a `ghcr.io/finsys/dockhand` mirror were not checked (a ghcr reference appears in the manual's compose example only).
- The Portainer column relies on general knowledge of Portainer, not a fresh feature-by-feature check.
- Pricing of the commercial and Enterprise tiers was not checked.

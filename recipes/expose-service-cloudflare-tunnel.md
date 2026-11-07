# Expose a Service with Cloudflare Tunnel
Publish a self-hosted web app on `https://app.example.com` without opening any inbound port, using `cloudflared` in Docker Compose and a tunnel token, then put an access policy in front of it.

Documentation: [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/) · [Cloudflare Zero Trust Access](https://developers.cloudflare.com/cloudflare-one/policies/access/)
Project: [cloudflare/cloudflared](https://github.com/cloudflare/cloudflared)

> **Verification:** the `cloudflared` image (version 2026.10.7) was pulled and its `--help` output confirmed `tunnel run --token`, the `TUNNEL_TOKEN` and `TUNNEL_TOKEN_FILE` variables, `--no-autoupdate` and `tunnel ready`. **Not verified** (no Cloudflare account was used): the dashboard menu names and click path, the public hostname and Access policy steps, and the compose health check. The dashboard changes names often, so follow the current Cloudflare docs where this differs.

## Goal
`https://app.example.com` reaches an app that only listens on a private Docker network. The host has no port 80 or 443 forwarded, the origin IP is not published, and only the people you allow can get past a login in front of the app.

## Prerequisites
- A domain whose DNS is on Cloudflare ([Cloudflare](../cloud/provider/cloudflare.md))
- A host with Docker and the Compose plugin ([New Server Checklist](new-server-checklist.md)) and an app already running in Compose ([Docker Service Deploy](docker-service-deploy.md), without the Traefik labels if you do not also want a reverse proxy)
- A Cloudflare account with Zero Trust enabled (the free plan covers a small number of users, see [Cloudflare](../cloud/provider/cloudflare.md))

> **Check the terms first.** Proxying large amounts of video through the self-serve plans is restricted, so a media server such as Plex or Jellyfin is a poor fit for a tunnel ([Cloudflare](../cloud/provider/cloudflare.md), proxied records). Non-HTTP services (SSH, game servers) need a different route, such as [Tailscale](../apps/tailscale.md) or [WireGuard Remote Access](wireguard-remote-access.md).

## Steps
### 1. Decide whether a tunnel is the right tool
APPROACH | USE IT WHEN
---|---
Cloudflare Tunnel (this recipe) | You are behind CGNAT or cannot forward ports, or you do not want to publish the origin IP; the app is HTTP
Reverse proxy with ports 80 and 443 open | You control the router and want no third party in the path ([Docker Service Deploy](docker-service-deploy.md), [Reverse Proxy Patterns](../homelab/reverse-proxy-patterns.md))
VPN only | The app is for you and your household; nothing is public ([Tailscale](../apps/tailscale.md), [VPN (Virtual Private Network)](../networking/vpn.md))

A tunnel means Cloudflare terminates TLS and can see the traffic in the clear.

### 2. Create the tunnel and copy its token
In the Cloudflare Zero Trust dashboard create a tunnel of the **Cloudflared** type (the dashboard path is currently under Networks, then Tunnels; *unverified*), name it, and copy the **token** the dashboard shows for the Docker install. Treat the token as a password: anyone with it can run your tunnel.

### 3. Run cloudflared in Compose
Keep the token out of the Compose file. Put it in a file with mode `600` that is excluded from git, in `/opt/stacks/cloudflared`:
```bash
mkdir -p /opt/stacks/cloudflared && cd /opt/stacks/cloudflared
install -m 600 /dev/null tunnel-token          # paste the token into it
docker network create tunnel                    # shared with the app stack
```
`/opt/stacks/cloudflared/compose.yaml`:
```yaml
services:
  cloudflared:
    image: cloudflare/cloudflared:<VERSION>
    command: tunnel --no-autoupdate run
    restart: unless-stopped
    environment:
      TUNNEL_TOKEN_FILE: /run/secrets/tunnel_token
    secrets: [tunnel_token]
    networks: [tunnel]

secrets:
  tunnel_token:
    file: ./tunnel-token

networks:
  tunnel:
    external: true
```
`TUNNEL_TOKEN_FILE` is the file form of `TUNNEL_TOKEN` (both are listed in `cloudflared tunnel run --help`). Pin `<VERSION>` to a release tag (see the [cloudflared releases](https://github.com/cloudflare/cloudflared/releases)), and let Renovate or Diun tell you about new ones ([Automate Container Updates Safely](automate-container-updates.md)). `--no-autoupdate` stops the process restarting itself inside a container.

```bash
docker compose up -d
docker compose logs --tail 30 cloudflared
```
The log should show connections registered to the Cloudflare edge, and the dashboard should list the tunnel as **Healthy**.

### 3a. Attach the app to the tunnel network
In the app's `compose.yaml` add the `tunnel` network to the service (containers on a shared network reach each other by Compose service name, so `cloudflared` will resolve `app`):
```yaml
services:
  app:
    networks: [internal, tunnel]
networks:
  tunnel:
    external: true
```
Do **not** publish the app's port on the host. The app is then reachable only from containers on the `tunnel` network ([Docker Networking](../docker/docker-networking.md)).

### 4. Add a public hostname
In the tunnel's settings add a **public hostname**: subdomain `app`, domain `example.com`, service type `HTTP`, URL `app:8080` (the Compose service name and the container port). The dashboard creates the DNS record for you. Check it with:
```bash
dig +short CNAME app.example.com
curl -sI https://app.example.com | head -n 1
```
If the origin speaks HTTPS with its own certificate, use `HTTPS` and set the origin server name or CA in the hostname's additional settings rather than disabling verification.

### 5. Put an access policy in front
In Zero Trust, add a self-hosted **Access application** for `app.example.com` with an **Allow** policy limited to your email addresses or identity provider group (*click path unverified*). Without it the app is public. If the app has its own login, still add this layer for admin interfaces. For apps with SSO, see [Single Sign-On with authentik](sso-with-authentik.md).

### 6. Tidy the firewall and DNS
Remove any old router port forwards and any `A` record that still points at your home IP. The host does not need 80 or 443 for this app ([UFW (uncomplicated firewall)](../linux/ufw.md)).

## Verify
```bash
docker compose ps
docker compose exec cloudflared cloudflared tunnel ready      # exit code 0 when connected
curl -sI https://app.example.com | head -n 1                  # a Cloudflare Access redirect or the app
curl -s -o /dev/null -w '%{http_code}\n' --connect-timeout 5 http://<PUBLIC_IP>:8080   # must fail from outside
```
The last check, run from a machine outside your network, proves the app port is not exposed. `cloudflared tunnel ready` calls the `/ready` endpoint of the running process; whether the container exposes it without `--metrics` is *unverified*, so set `--metrics 0.0.0.0:20241` on the command if it cannot connect.

## Troubleshooting
SYMPTOM | FIX
---|---
Tunnel shows **Down** or **Inactive** | Check `docker compose logs cloudflared`; the token is wrong or truncated, or outbound connections to Cloudflare are blocked
Cloudflare error 1033 | The tunnel is not running or not connected; start it and check the dashboard status
`502 Bad Gateway` | The service URL is wrong (name, port or scheme), or the app is not on the `tunnel` network
`ERR_TOO_MANY_REDIRECTS` | The app redirects HTTP to HTTPS behind the tunnel; set the app's trusted-proxy or forwarded-proto option ([Reverse Proxy Patterns](../homelab/reverse-proxy-patterns.md))
DNS name does not resolve | The hostname was not created; add the public hostname again, check [DNS Troubleshooting](dns-troubleshooting.md)
Uploads fail above 100 MB | Cloudflare limits request bodies on the Free plan ([Cloudflare](../cloud/provider/cloudflare.md))
Websocket app broken | Check the app's own proxy settings; test directly from another container on the `tunnel` network
Token leaked | Roll or delete the tunnel in the dashboard, create a new one and replace the file

## Rollback / Cleanup
```bash
cd /opt/stacks/cloudflared && docker compose down
docker network rm tunnel                     # once no stack uses it
```
Delete the tunnel and the Access application in the dashboard, then delete the DNS record. To go back to a reverse proxy, follow [Docker Service Deploy](docker-service-deploy.md).

## Related Sheets
- [Cloudflare](../cloud/provider/cloudflare.md) · [Reverse Proxy Patterns](../homelab/reverse-proxy-patterns.md) · [Traefik](../apps/traefik.md) · [Tailscale](../apps/tailscale.md) · [WireGuard](../apps/wireguard.md)
- [cloudflared](../apps/cloudflared.md) · [Docker-Compose](../docker/docker-compose.md) · [Docker Networking](../docker/docker-networking.md) · [DNS Record Types](../networking/dns-record-types.md) · [curl](../tools/curl.md)
- [authentik](../security/authentik.md) · [CrowdSec](../security/crowdsec.md) · [Security](../security/security.md)
- [Docker Service Deploy](docker-service-deploy.md) · [WireGuard Remote Access](wireguard-remote-access.md) · [Single Sign-On with authentik](sso-with-authentik.md) · [DNS Troubleshooting](dns-troubleshooting.md)

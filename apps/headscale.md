# Headscale
Headscale is an open source, self-hosted implementation of the Tailscale control server. You keep the official Tailscale clients and run the coordination server yourself. It serves a single tailnet. Compare the options in [Mesh VPN Comparison](../networking/mesh-vpn-comparison.md), and see [Tailscale](tailscale.md) for the client commands.

Documentation: [Headscale](https://headscale.net/stable/)

## Install (Docker)
The container page is community-maintained, not verified by the Headscale developers. Match the config file to the version you run.

```bash
mkdir -p ./headscale/{config,lib}
wget -O ./headscale/config/config.yaml https://raw.githubusercontent.com/juanfont/headscale/v0.29.5/config-example.yaml
```

```yaml
services:
  headscale:
    image: docker.io/headscale/headscale:VERSION
    restart: unless-stopped
    container_name: headscale
    read_only: true
    tmpfs:
      - /var/run/headscale
    ports:
      - "127.0.0.1:8080:8080"
      - "127.0.0.1:9090:9090"
    volumes:
      - ./headscale/config:/etc/headscale:ro
      - ./headscale/lib:/var/lib/headscale
    command: serve
```

Put a reverse proxy with HTTPS in front of port 8080 (see [Reverse Proxy Patterns](../homelab/reverse-proxy-patterns.md)). Check with `curl http://127.0.0.1:8080/health`.

## config.yaml Essentials
```yaml
server_url: https://headscale.example.com
listen_addr: 0.0.0.0:8080
metrics_listen_addr: 127.0.0.1:9090
prefixes:
  v4: 100.64.0.0/10
  v6: fd7a:115c:a1e0::/48
dns:
  magic_dns: true
  base_domain: tailnet.example.net
  nameservers:
    global:
      - 1.1.1.1
policy:
  mode: file
  path: /etc/headscale/policy.hujson
```

- `server_url` is the public HTTPS URL clients use.
- `base_domain` must differ from the `server_url` domain.
- Keep prefixes inside `100.64.0.0/10` and `fd7a:115c:a1e0::/48`, other ranges are unsupported.
- `derp.server.enabled: true` runs an embedded DERP relay and needs an `https` `server_url` and `stun_listen_addr` (3478/udp). By default Headscale uses Tailscale's public DERP map.
- Validate with `headscale configtest`. Config is searched in `/etc/headscale`, `~/.headscale`, then the working directory.

## Commands
In Docker prefix with `docker exec -it headscale`. The CLI talks to a unix socket, so use `sudo`, run as the `headscale` user or join the `headscale` group.

COMMAND | DESCRIPTION
---|---
`headscale users create <USER>` / `headscale users list` | Manage users
`headscale preauthkeys create --user <USER_ID>` | Pre-auth key (single use, valid one hour by default). The ID is the number from `users list`
`headscale preauthkeys create --tags tag:<TAG>` | Key that tags the node on join
`headscale auth register --user <USER> --auth-id <AUTH_ID>` | Approve a node that used interactive login
`headscale nodes list` | List nodes
`headscale nodes list-routes` | Routes advertised by nodes
`headscale nodes approve-routes --identifier <ID> --routes 192.0.2.0/24` | Approve subnet routes
`headscale configtest` | Check the config file

For reusable, ephemeral and expiry flags see `headscale preauthkeys --help`. Deleting and expiring nodes is also in `headscale nodes --help` (unverified here).

## Connect a Client
COMMAND | DESCRIPTION
---|---
`tailscale up --login-server https://headscale.example.com` | Interactive login, then approve with `auth register` on the server
`tailscale up --login-server <URL> --authkey <KEY>` | Join with a pre-auth key
`sudo tailscale up --login-server <URL> --advertise-routes=192.0.2.0/24` | Act as a subnet router
`sudo tailscale set --accept-routes` | Accept routes on a client
`sudo tailscale up --login-server <URL> --advertise-exit-node` | Offer an exit node (approve `0.0.0.0/0` on the server)
`sudo tailscale set --exit-node <NODE>` | Use an exit node

Subnet routers need IP forwarding enabled, see [Tailscale](tailscale.md).

## Policy (ACLs)
Without a policy file everything can talk to everything. A deny-all policy is `{"grants": []}`. Reload with `sudo systemctl reload headscale` or `sudo kill -HUP $(pidof headscale)`. Auto-approve routes with a tag:

```json
{
  "tagOwners": {
    "tag:router": ["alice@"]
  },
  "autoApprovers": {
    "routes": {
      "192.0.2.0/24": ["tag:router"]
    }
  }
}
```

Advertise the tag from the node with `--advertise-tags tag:router`. Supported: ACLs and grants, groups, tagOwners, autoApprovers, Tailscale SSH. Not supported: device posture and IP sets.

## Ports
PORT | USE
---|---
`8080/tcp` | Control server (behind your HTTPS proxy)
`9090/tcp` | Metrics (keep local)
`3478/udp` | STUN, only with the embedded DERP server
`41641/udp` | Default client WireGuard port

## Gotchas
- One Headscale server is one tailnet.
- OIDC groups cannot be used in ACLs.
- If you use a web UI, policy usually has to be in `database` mode instead of `file` (unverified, see the UI's docs).

## See Also
- [Tailscale](tailscale.md)
- [WireGuard](wireguard.md)
- [Mesh VPN Comparison](../networking/mesh-vpn-comparison.md)
- [NetBird](netbird.md)

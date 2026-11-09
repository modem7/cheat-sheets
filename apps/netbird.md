# NetBird
NetBird is an open source WireGuard-based mesh VPN with a web dashboard, groups and access policies. You can use NetBird Cloud or self-host the control plane. Compare it with the others in [Mesh VPN Comparison](../networking/mesh-vpn-comparison.md).

Documentation: [NetBird docs](https://docs.netbird.io/)

## Self-hosted vs Cloud
- Self-hosted has built-in local user management (embedded Dex since v0.62), so no external identity provider is required.
- IdP user and group provisioning (SCIM), traffic event logging, event streaming, EDR integrations and peer approval are Cloud or Enterprise-licence features.
- Self-hosted needs its own relay. The quickstart runs one in the compose stack.

## Self-host Quickstart
Needs a Linux VM (1 CPU, 2 GB RAM), a public DNS name, public `80/tcp`, `443/tcp` and `3478/udp`, plus Docker with Compose v2, `jq` and `curl`.

```bash
curl -fsSL https://github.com/netbirdio/netbird/releases/latest/download/getting-started.sh | bash
```

Read the script before piping it to a shell. Choose option 0 (built-in Traefik with automatic Let's Encrypt). It generates `docker-compose.yml`, `config.yaml` and `dashboard.env`. Then open `https://NETBIRD_DOMAIN/setup` to create the first account.

Unattended:

```bash
export NETBIRD_DOMAIN=netbird.example.com
export NETBIRD_LETSENCRYPT_EMAIL=admin@example.com
export NETBIRD_NON_INTERACTIVE=true
```

If you front it with your own reverse proxy, set `NETBIRD_TRUSTED_PEERS`. A re-run will not overwrite an existing `config.yaml`.

## Client Commands
Client install steps are on the [NetBird install page](https://docs.netbird.io/get-started) (not verified here).

COMMAND | DESCRIPTION
---|---
`netbird up` | Connect (uses the last profile, or NetBird Cloud by default)
`netbird up --management-url https://netbird.example.com:443` | Connect to a self-hosted server (SSO login in a browser)
`netbird up --setup-key SETUP_KEY` | Join non-interactively with a setup key (`-k`, or `--setup-key-file`)
`netbird login` | Authenticate without bringing the connection up (same flags)
`netbird status` | Summary: management, signal, relays, NetBird IP, peer count
`netbird status -d` | Detail: P2P or relayed, ICE candidates
`netbird status --filter-by-status connected` | Only connected peers
`netbird down` | Disconnect
`netbird networks list` | Networks you can use
`netbird networks select <NETWORK>` / `deselect <NETWORK>` | Turn a network on or off for this client
`netbird service install` / `start` / `stop` / `restart` | Manage the background service
`netbird debug bundle` | Create a debug bundle for support

Every flag has an environment variable form such as `NB_MANAGEMENT_URL`. Order of precedence: environment variable, then flag, then profile file. Useful `up` flags: `--wireguard-port` (default 51820), `--interface-name` (default `wt0`), `--hostname`, `--block-inbound`, `--disable-dns`, `--allow-server-ssh`.

## Access Control
- Policies are allow-only. There is no priority or processing order.
- A new account has a Default policy that allows all peers to reach all peers. **Delete it** before relying on your own policies.
- Peers must be assigned to groups, either by hand or automatically via setup keys.
- The `All` group cannot be edited.
- A policy picks source groups, destination groups, protocol, ports and direction.

## Networks and Routes
- **Routes are deprecated.** Every use case except exit nodes has moved to **Networks**. Use Networks for subnet access. Details are in the [Networks docs](https://docs.netbird.io/manage/networks) (not verified here).
- Exit nodes are still a `0.0.0.0/0` route.
- By default routes bypass access control rules. Restrict with ACL groups on the route, and keep routing peers dedicated so routes and Networks do not overlap.

## Firewall
- **Server:** `80/tcp`, `443/tcp`, `3478/udp`.
- **Clients:** no inbound ports needed. Allow the interface itself, for example `sudo ufw allow in on wt0`, or add `wt0` to the firewalld trusted zone.

## See Also
- [Mesh VPN Comparison](../networking/mesh-vpn-comparison.md)
- [Tailscale](tailscale.md)
- [WireGuard](wireguard.md)
- [VPN](../networking/vpn.md)

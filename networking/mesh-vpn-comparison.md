# Mesh VPN Comparison
A mesh VPN connects devices directly to each other (with a relay as fallback) instead of through one central gateway. This sheet compares the common options for a homelab: [Tailscale](../apps/tailscale.md), [Headscale](../apps/headscale.md), [NetBird](../apps/netbird.md), [ZeroTier](../apps/zerotier.md) and plain [WireGuard](../apps/wireguard.md). General VPN concepts are in [VPN](vpn.md).

Based on each project's own documentation. Where the docs were not checked a cell says so. Check the current docs before choosing, as these projects change quickly.

## At a Glance
| | Tailscale | Headscale | NetBird | ZeroTier | Plain WireGuard |
|---|---|---|---|---|---|
| Data plane | WireGuard | WireGuard (uses Tailscale clients) | WireGuard | ZeroTier protocol (not verified as WireGuard) | WireGuard |
| Control plane | Hosted by Tailscale | Self-hosted, single tailnet | Cloud or self-hosted | Central (hosted) or own controller | None (you manage keys and peers) |
| Clients | Official Tailscale | Official Tailscale | NetBird | ZeroTier | WireGuard |
| NAT traversal | Direct, DERP relays | Direct, embedded or Tailscale DERP | ICE and STUN, relay over 443 | Direct on UDP 9993, root servers, TCP fallback | Manual (needs one reachable endpoint) |
| Subnet routing | Yes | Yes, approve routes | Yes (Networks) | Managed routes | `AllowedIPs` and forwarding |
| Exit node | Yes | Yes | Yes (route `0.0.0.0/0`) | Documented guide (not read) | `AllowedIPs = 0.0.0.0/0` |
| Access control | ACLs | ACL policy file | Group policies, allow-only | Rules and tags | Firewall rules only |
| SSO | Yes | OIDC | Yes, embedded Dex when self-hosted | Not verified | None |
| Licence | Not checked here | "Open source" (name not checked) | "Open source" (name not checked) | BSL 1.1 (client) | GPL kernel module (not checked here) |

## How to Choose
NEED | PICK
---|---
Easiest setup, someone else runs the coordination server | [Tailscale](../apps/tailscale.md)
Tailscale clients and polish, but you own the control server | [Headscale](../apps/headscale.md)
Self-hosted with a dashboard, groups and policies | [NetBird](../apps/netbird.md)
Flat virtual LAN, join by network ID | [ZeroTier](../apps/zerotier.md)
Two or three fixed endpoints, no extra software | [WireGuard](../apps/wireguard.md)
Public access to a web service, not private access | [Cloudflare Tunnel](../apps/cloudflared.md)

## Trade-offs
- **Self-hosting the control plane** removes the dependency on a vendor, but you run an internet-facing service and its backups and updates. If it is down, existing connections usually keep working but new devices cannot join (the general behaviour, check each project).
- **A relay is a fallback**, not the normal path. Traffic is end-to-end encrypted, but a relay sees volumes and timing.
- **Headscale** serves one tailnet only and tracks the Tailscale client's behaviour, so a client update can need a server update.
- **NetBird Cloud-only features** include SCIM provisioning, traffic event logging and peer approval.
- **Plain WireGuard** has no discovery, so every peer needs a configured endpoint and key. It is the lightest and most transparent option for a fixed set of sites.

## See Also
- [VPN](vpn.md)
- [Tailscale](../apps/tailscale.md)
- [WireGuard](../apps/wireguard.md)
- [WireGuard Remote Access](../recipes/wireguard-remote-access.md)

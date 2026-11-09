# UniFi Firewall and VPN
The zone-based firewall, port forwarding, IDS/IPS, and the VPN options on UniFi gateways. Sources are Ubiquiti help articles. Where sources disagreed, that is noted, so confirm behaviour on your own console before relying on it.

Documentation: [Zone-Based Firewalls](https://help.ui.com/hc/en-us/articles/115003173168) · [Port Forwarding](https://help.ui.com/hc/en-us/articles/235723207) · [IDS/IPS](https://help.ui.com/hc/en-us/articles/360006893234) · [WireGuard VPN Server](https://help.ui.com/hc/en-us/articles/115005445768) · [Teleport](https://help.ui.com/hc/en-us/articles/5246403561495)

## Zone-Based Firewall
Introduced in Network 9.0.108. Migrating from the legacy rules **cannot be undone** except by restoring a backup, so take one first ([UniFi Backups and Migration](unifi-backups.md)).

CONCEPT | MEANING
---|---
Zone | A group of networks. Each network sits in exactly one zone
Built-in zones | Internal, External, Gateway, VPN, Hotspot, DMZ
Custom zone | Add your own. Deleting one deletes its policies
Policy | Allow, block or reject traffic from one zone to another
Predefined policy | Shown with a lock, cannot be edited
Auto Allow Return Traffic | A built-in reply policy using established and related state

- Your own policies placed above the predefined ones override them.
- Default behaviour between zones is **not consistent across sources** (the help table shows Internal to Internal as allowed, one guide says zones block each other). New custom zones are reported to block by default. Test it.
- Put IoT and Guest networks in their own zones and write explicit allows, for example IoT to a Home Assistant host only. See [Home Assistant](../apps/home-assistant.md).

## Port Forwarding
- Settings, Routing (or Security), Port Forwarding. Forward a WAN port to an internal IP and port.
- Hairpin NAT, so internal clients can reach a forward by the public name, is on by default per the help summary.
- Prefer a [reverse proxy](../homelab/reverse-proxy-patterns.md) on 443 over many forwards, and prefer a VPN to forwarding admin ports.

## Traffic and Policy Management
Traffic rules, routes and content filtering are now combined under Traffic and Policy Management. Exact options differ by release and were **not verified**.

## IDS/IPS
- Raises CPU and memory use, limits how many networks it can cover, and may cut throughput.
- It disables hardware offload on older gateways. Throughput figures quoted online are old, so use Ubiquiti's spec sheet for your model.
- QoS rules also disable hardware offload.
- Whether the engine is Suricata was **not confirmed**.

## VPN Options
VPN | NOTES
---|---
WireGuard server | UDP 51820 by default. UniFi recommends WireGuard or Teleport over L2TP
Teleport | WireGuard-based, one tap invite, works behind NAT. Invites last 24 hours and are single-device
Site Magic | Site-to-site between UniFi gateways. Needs one public-IP gateway and non-overlapping subnets
VPN client | Connect out to another provider. With policy-based routing only chosen traffic uses the tunnel
OpenVPN and L2TP | Available, details not checked

Policy-based routing sends chosen clients or traffic through a VPN client. By default only traffic for the remote LAN crosses.

For a WireGuard client config on your own devices see [Mesh VPN Comparison](../networking/mesh-vpn-comparison.md) and [VPN](../networking/vpn.md).

## Not Verified
Default inter-zone behaviour, traffic rule details, IDS/IPS engine and throughput, OpenVPN and L2TP setup, Site Magic site limits.

## See Also
- [UniFi](unifi.md)
- [UniFi Networks and VLANs](unifi-networks-vlans.md)
- [UniFi Routing and WAN](unifi-routing-wan.md)
- [VPN](../networking/vpn.md)

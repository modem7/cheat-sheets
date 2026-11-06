# Homelab
Overview of a typical self-hosted homelab and network-services stack, with a suggested service map, addressing plan and a build order. Each service has its own sheet; this page shows how they fit together so you decide what to run and where.

> **Verification:** this page is a planning guide with example addressing from private ranges. The linked sheets carry their own verification notes, and none of their commands were executed.

---
## Sheets in This Section
SHEET | USE IT FOR
---|---
[[vlans]] | Segmenting the network, trunk/access ports, Proxmox VLAN-aware bridges, inter-VLAN firewall rules, mDNS reflection
[[pihole]] | Network-wide ad/tracker blocking and local DNS records (v6)
[[adguard-home]] | Alternative DNS filter with built-in DoH/DoT/DoQ and per-client settings
[[unbound]] | Recursive, validating resolver behind Pi-hole or AdGuard; local zones
[[dnsmasq-dhcp]] | DHCP ranges, static leases, local DNS and DHCP relay
[[reverse-proxy-patterns]] | Traefik vs Nginx vs Caddy, wildcard certificates by DNS-01, split-horizon DNS, internal-only services
[[wake-on-lan]] | Powering machines on remotely
[[nut-ups]] | UPS monitoring and clean shutdown

Related sheets elsewhere: [[proxmox-overview]], [[proxmox-networking]], [[proxmox-firewall]], [[docker-networking]], [[docker-compose]], [[tailscale]], [[wireguard]], [[vpn]], [[traefik]], [[nginx]], [[cert-manager]], [[ufw]], [[iptables]], [[dns-record-types]], [[tls]], [[prometheus]], [[grafana]].

---
## Suggested Service Map
LAYER | SERVICE | RUNS ON | NOTES
---|---|---|---
Gateway | Router/firewall (OPNsense, UniFi, OpenWrt) | Dedicated box | Owns VLAN gateways, inter-VLAN rules, WAN; see [[vlans]]
DHCP | Router DHCP, or dnsmasq / Kea | Gateway or a small server | One per VLAN; relay if central; see [[dnsmasq-dhcp]]
DNS filter | Pi-hole or AdGuard Home | Two small instances (LXC/VM/Pi) | Give two resolvers for redundancy; see [[pihole]], [[adguard-home]]
DNS resolver | Unbound | Next to each filter | Recursive and DNSSEC; see [[unbound]]
Reverse proxy | Traefik / Caddy / Nginx | Docker host or LXC | Wildcard certificate via DNS-01; see [[reverse-proxy-patterns]]
Remote access | Tailscale or WireGuard | Gateway or a subnet router | See [[tailscale]], [[wireguard]]
Virtualisation | Proxmox cluster | 1-3 nodes | See [[proxmox-overview]], [[proxmox-networking]]
Containers | Docker/Compose | VM or LXC on Proxmox | See [[docker-compose]]
Monitoring | Prometheus, Grafana, NUT exporter | Docker host | See [[prometheus]], [[grafana]], [[nut-ups]]
Power | UPS with NUT | Node cabled to UPS | Clients shut down first; see [[nut-ups]]
Wake | Wake-on-LAN | Gateway or helper host | See [[wake-on-lan]]

---
## Example Addressing Plan
Use one `/24` per VLAN and put the VLAN ID in the third octet so addresses are readable (use RFC1918 space; documentation ranges such as `192.0.2.0/24` are for examples only).

VLAN | SUBNET | GATEWAY | DHCP RANGE | STATIC
---|---|---|---|---
10 Trusted | `192.168.10.0/24` | `.1` | `.100-.250` | `.2-.99`
20 Servers | `192.168.20.0/24` | `.1` | `.100-.200` | `.2-.99`: DNS `.2` and `.3`, proxy `.10`, Proxmox `.21-.23`
30 IoT | `192.168.30.0/24` | `.1` | `.100-.250` | few
40 Guest | `192.168.40.0/24` | `.1` | `.100-.250` | none
99 Management | `192.168.99.0/24` | `.1` | none | switches, APs, IPMI, UPS network cards

Conventions: gateway is `.1`, infrastructure sits below `.100`, DHCP above, and reservations live outside the dynamic range.

---
## Build Order
1. **Network:** router, VLANs and a management network ([[vlans]]). Keep a console route in case of lockout.
2. **DHCP and DNS:** pick the DHCP server, then two DNS filters with Unbound ([[pihole]], [[unbound]]). Hand out both resolvers through DHCP.
3. **Hypervisor:** Proxmox with VLAN-aware bridge ([[proxmox-networking]]), storage and backups ([[proxmox-backup]]).
4. **Reverse proxy and certificates:** wildcard certificate, internal DNS record pointing at the proxy ([[reverse-proxy-patterns]]).
5. **Remote access:** VPN to the LAN, with the internal resolver pushed to clients ([[tailscale]], [[wireguard]]).
6. **Power and monitoring:** UPS and NUT, then metrics and alerts ([[nut-ups]], [[prometheus]]).
7. **Services:** deploy apps as Compose stacks behind the proxy ([[docker-compose]]).

---
## Design Rules
- **Two DNS servers.** If the only resolver is down, nothing works. Run two, on different hosts, and give both through DHCP.
- **DNS is not a firewall.** Clients can use DoH or hardcoded resolvers. Enforce at the gateway: allow port 53 only to your resolvers, and block or redirect the rest ([[vlans]]).
- **One DHCP server per VLAN.** Rogue servers are a common cause of intermittent failure.
- **Management on its own VLAN.** Keep hypervisors, switches and IPMI off the user networks.
- **Do not expose services directly.** Use DNS-01 certificates for internal names, keep 80/443 closed to the internet unless a service is public, and reach the rest over a VPN.
- **Have a boot-order plan.** DNS and DHCP must start before things that need them; after a power outage the UPS, Proxmox start order and [[wake-on-lan]] decide how smoothly it comes back.
- **Back up configs.** Pi-hole Teleporter, AdGuard `AdGuardHome.yaml`, `/etc/nut`, router exports, and Compose directories belong in git (without secrets) or backups ([[proxmox-backup]]).
- **Document the IPs.** A table like the one above, kept next to the Compose files, saves hours.

---
## Quick Diagnostics
COMMAND | DESCRIPTION
---|---
`dig +short <NAME> @<RESOLVER>` | Does this resolver answer, and with what
`dig +trace <NAME>` | Walk the delegation from the root
`resolvectl status` | Which DNS servers does this Linux client use
`ip -br addr; ip route` | Addresses and default route
`ss -lntup` | What is listening, on which port
`sudo tcpdump -ni <IFACE> port 53` | Watch DNS traffic
`sudo tcpdump -nei <IFACE> port 67 or port 68` | Watch DHCP traffic
`curl -vk --resolve <NAME>:443:<IP> https://<NAME>` | Test the reverse proxy without DNS
`mtr <HOST>` | Path and loss
`upsc <UPS>@<HOST> ups.status` | Is the UPS online

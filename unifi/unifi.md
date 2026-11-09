# UniFi
UniFi is Ubiquiti's managed networking platform: gateways, switches, access points, cameras and storage, all managed from one application. This section covers running and operating it in a homelab. Facts were checked against Ubiquiti's help articles where possible, and anything not confirmed is marked in each sheet.

Documentation: [UniFi Help Center](https://help.ui.com/) · [UniFi developer docs](https://developer.ui.com/) · [Tech Specs](https://techspecs.ui.com/)

## Sheets
SHEET | COVERS
---|---
[UniFi Hosting](unifi-hosting.md) | UniFi OS Server, legacy Network Server, Docker, consoles, ports
[UniFi Backups and Migration](unifi-backups.md) | System backups, `.unf` files, moving to new hardware
[UniFi Device CLI and Adoption](unifi-device-cli.md) | SSH, `set-inform`, factory reset, L3 adoption
[UniFi Networks and VLANs](unifi-networks-vlans.md) | Networks, switch ports, DHCP options, multicast
[UniFi Firewall and VPN](unifi-firewall-vpn.md) | Zone-based firewall, port forwards, IDS/IPS, WireGuard, Teleport
[UniFi WiFi](unifi-wifi.md) | SSIDs, bands, 6 GHz, IoT networks, roaming
[UniFi Routing and WAN](unifi-routing-wan.md) | Multi-WAN, IPv6, OSPF, local DNS, QoS, jumbo frames
[UniFi Protect](unifi-protect.md) | Cameras, recording, RTSPS, backups
[UniFi API and Automation](unifi-api-automation.md) | Integration API, Terraform, Home Assistant, Unpoller
[UniFi NAS](../infra/unifi-nas.md) | UNAS storage appliances

## The Moving Parts
TERM | MEANING
---|---
UniFi OS | The operating system on consoles and gateways that hosts the applications
UniFi Network | The application that manages gateways, switches and access points
UniFi Protect | The camera application
Console | Hardware that runs UniFi OS (Cloud Gateway, Cloud Key, UNVR)
UniFi OS Server | Ubiquiti's self-hosted UniFi OS for your own Linux host
Site Manager | The cloud view at `unifi.ui.com` for remote access and multiple consoles
Site | A logical grouping of devices inside the Network application

## Versions
UniFi Network uses `major.minor.build` numbering, and several majors are current at once (9.x, 10.x and 11.x in the release feed checked on 2026-11-09). Version numbers move fast, so check [community.ui.com/releases](https://community.ui.com/releases) and read the release notes before upgrading. Ubiquiti's channels are Official and Early Access.

## Good Habits
- Take a backup before every upgrade, and keep one off the console ([UniFi Backups and Migration](unifi-backups.md)).
- Use a local admin account for automations and integrations, not your cloud SSO account.
- Put management, IoT, guests and cameras on separate networks ([UniFi Networks and VLANs](unifi-networks-vlans.md), [VLANs](../homelab/vlans.md)).
- Avoid Early Access builds on production gear.

## See Also
- [VLANs](../homelab/vlans.md)
- [UniFi NAS](../infra/unifi-nas.md)
- [Home Assistant](../apps/home-assistant.md)
- [Mesh VPN Comparison](../networking/mesh-vpn-comparison.md)

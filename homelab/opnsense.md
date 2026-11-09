# OPNsense
OPNsense is an open source firewall and router distribution based on FreeBSD, managed mainly through a web UI. This sheet covers install, the console menu, firewall rule order, NAT, services and the few command line tools the docs describe. For the other popular choice see [pfSense](pfsense.md).

Documentation: [OPNsense manual](https://docs.opnsense.org/manual/)

## Install
MEDIA | USE
---|---
`dvd` | ISO with a VGA live system
`vga` | USB image, VGA console
`serial` | USB image, serial console at 115200 baud
`nano` | 4 GB or larger USB, SD or CF image, serial console

- Log in to the installer as `installer` with password `opnsense`. If that fails, log in as `root`, choose 8 (Shell) and run `opnsense-installer`. `opnsense-importer` is run the same way.
- A new install is `root` with password `opnsense` at `https://192.168.1.1/`. Change it at once.
- ZFS is needed for snapshots and boot environments.

## Releases
- Two major releases a year, with minor updates about every two weeks. Versions are `YY.M`, so 25.1 is January 2025.
- The Community Edition uses the `x.1` and `x.7` series. The Business Edition uses `x.4` and `x.10`, with more conservative changes and a commercial firmware repository.
- Major upgrades can be run from console option 12.

## Console Menu
OPTION | ACTION
---|---
0 | Logout
1 | Assign interfaces
2 | Set interface IP addresses
3 | Reset the root password
4 | Reset to factory defaults (**destructive**)
5 | Reboot
6 | Halt
7 | Ping host
8 | Shell
9 | pfTop
10 | Filter logs
11 | Restart web interface
12 | Upgrade from console
13 | Restore a configuration

Options 1 and 2 recover a box with a wrong LAN address or VLAN. Option 11 helps when the web UI hangs.

## Command Line
COMMAND | DESCRIPTION
---|---
`opnsense-update -kr <VERSION>` | Revert the kernel to a version, then reboot (test machines only)
`opnsense-update -k` | Return to the current kernel
`opnsense-revert -r <VERSION> <PACKAGE>` | Install an older version of a package
`opnsense-revert <PACKAGE>` | Return a package to the current version
`opnsense-revert -r <VERSION> opnsense` | Revert the whole release
`opnsense-patch <COMMIT>` | Apply a core commit (`-c plugins` for the plugins repository). Running it again reverts it
`configctl sshd restart` | Restart a service through the configuration daemon
`service configd restart` | Restart the configuration daemon
`configctl unbound check` | Validate custom Unbound configuration

`pluginctl`, `opnsense-code`, the `pfctl` shell commands and a generic `configctl service restart` form were not found in the docs read, so check them on your own install.

## Backups and Snapshots
- Backups are under System, Configuration, Backups. You can set a password. The History tab compares and reverts, and a reboot may be needed.
- The configuration is `/conf/config.xml`. Only the USB import path for that file was seen in the docs, so check it before relying on it.
- Snapshots need ZFS. Activate one under System, Snapshots, or from boot menu option 8. Take one before every upgrade.
- Copy configuration backups off the box. See [Restic](../backup/restic.md).

## Firewall Rules
- Order: floating rules, then interface groups, then interface rules. Priorities are 200000, 300000 and 400000. NAT is processed before filtering.
- With `quick`, the first match wins. Without it, the last match wins. Inbound is denied by default and outbound is allowed.
- Automatic rules are visible through Inspect.
- The anti-lockout rule always allows the web UI and SSH on LAN. "Disable anti-lockout" removes it, so only do that with another way in.
- Aliases hold hosts, networks, ports, MAC addresses, URL tables, GeoIP and groups. They can be nested, so use them instead of repeating addresses.

## NAT
- Port forwards are under Firewall, NAT, Destination NAT. The filter rule association options are Manual, Pass and Register rule (recommended).
- Outbound NAT modes are Automatic (default), Manual, Hybrid and Disable.

## Services
- **VLANs:** Interfaces, Devices, VLAN. Set the parent, a tag from 1 to 4094 and an optional PCP. See [VLANs](vlans.md).
- **DHCP:** Dnsmasq is the default and suits fewer than 1000 clients. Kea suits large and HA setups. ISC is end of life. See [dnsmasq DHCP](dnsmasq-dhcp.md).
- **DNS:** Unbound is the default resolver. Custom configuration goes in `/usr/local/etc/unbound.opnsense.d`. See [Unbound](unbound.md).
- **VPN:** OpenVPN and IPsec are core. WireGuard is at VPN, WireGuard. See [VPN](../networking/vpn.md).
- **IDS and IPS:** Suricata modes are PCAP (IDS), Netmap and Divert (IPS). Turn off hardware offload for IPS.
- **High availability:** needs CARP virtual IPs. Preempt is off by default and configuration sync is on demand.

## Diagnostics
- Interfaces, Diagnostics, Packet Capture runs `tcpdump` (default count 100) and the capture opens in Wireshark.
- The firewall log has Live View and Plain View. Only the first packet of a flow is logged.

## Not Verified
`pluginctl`, `opnsense-code`, `pfctl` from the shell, the location of `config.xml` beyond the USB import path, backup plugins, Zenarmor, the VLAN how-to page, and when WireGuard moved into core.

## See Also
- [pfSense](pfsense.md)
- [VLANs](vlans.md)
- [Unbound](unbound.md)
- [Network Troubleshooting](../recipes/network-troubleshooting.md)

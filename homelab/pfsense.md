# pfSense
pfSense is a FreeBSD based firewall and router from Netgate, managed through a web UI. This sheet covers editions, install, the console menu, the `pfSsh.php` helper, backups, firewall rule order, NAT and services. For the community fork see [OPNsense](opnsense.md).

Documentation: [Netgate pfSense documentation](https://docs.netgate.com/pfsense/en/latest/)

## Editions
- **CE** is the free open project. In January 2021 Netgate launched **Plus** and renamed the open project CE.
- Plus-only features include ZFS boot environments, OpenVPN DCO, Intel QAT and unicast CARP (CE supports multicast CARP only).
- Plus needs a subscription. The installer lets you choose CE, or toggle CE repositories under Advanced Options.

## Install
- Download the free Netgate Installer from the Netgate Store (a store account is needed). Images are AMD64 memstick (USB), AMD64 ISO (IPMI, VM, optical) and AARCH64 memstick. Check the SHA-256 on the checksums page.
- The installer is online. It asks for the WAN interface, filesystem, disk and version.
- ZFS is the default and best practice, and gives boot environments. UFS is lighter, has no boot environments and is fragile on power loss. Disks under 4 GB default to UFS.
- Minimum hardware: 64-bit x86-64, 1 GB RAM and 8 GB disk. Netgate says that is not suitable for every environment.

## Console Menu
OPTION | ACTION
---|---
0 | Logout (SSH)
1 | Assign interfaces
2 | Set interface IP addresses
3 | Reset admin account and password
4 | Reset to factory defaults (**destructive**)
5 | Reboot
6 | Halt
7 | Ping host
8 | Shell
9 | pfTop
10 | Filter logs
11 | Restart the GUI
12 | PHP shell and pfSense tools
13 | Upgrade from console (runs `pfSense-upgrade`)
14 | Enable or disable sshd
15 | Restore a recent configuration
16 | Restart PHP-FPM

## pfSsh.php
Run helper tasks from the shell (option 8) or the PHP shell (option 12):

COMMAND | DESCRIPTION
---|---
`pfSsh.php playback changepassword` | Reset a user's password
`pfSsh.php playback enablesshd` | Enable SSH
`pfSsh.php playback disablereferercheck` | Turn off the HTTP referer check (for access by IP or name)
`pfSsh.php playback enableallowallwan` | Add an allow-all rule on WAN. Use only to regain access, then remove it
`pfSsh.php playback gatewaystatus brief` | Gateway status
`pfSsh.php playback generateguicert` | Make a new web GUI certificate
`pfSsh.php playback resetwebgui` | Reset the web GUI settings
`pfSsh.php playback restartallwan` | Restart the WAN interfaces
`pfSsh.php playback restartdhcpd` | Restart the DHCP server
`pfSsh.php playback restartipsec` | Restart IPsec
`pfSsh.php playback listpkg` | List packages (also `installpkg`, `uninstallpkg`)
`pfSsh.php playback pftabledrill` | Show firewall table contents (also `pfanchordrill`)
`pfSsh.php playback svc restart <SERVICE> [OPTIONS]` | Control a service, for example `svc restart openvpn client 2` (also `stop`, `start`)

Other documented playbacks include `cryptconfig`, `disablecarp`, `enablecarp`, `disabledhcpd`, `removeshaper` and `upgradeconfig`. `gitsync` is for CE developers and is not for Plus.

## Configuration and Backups
- The configuration is `/conf/config.xml`. `viconfig` edits it, and after a manual edit run `rm /tmp/config.cache`.
- Back up under Diagnostics, Backup and Restore, with optional AES-256 encryption. A full restore reboots.
- Config History keeps 30 revisions by default, and restoring from it does not reboot by itself.
- Console option 15 lists and restores recent configurations.
- Services, Auto Config Backup is free on CE and Plus. Copy backups off the box too, see [Restic](../backup/restic.md).
- Packages are under System, Packages.

## Firewall Rules
- Defaults: LAN has "Default allow LAN to any" (IPv4 and IPv6) plus the anti-lockout rule. WAN has no user rules, and blocks private and bogon networks only if enabled.
- Processing order: L2, outbound NAT, inbound NAT, RADIUS rules, internal automatic rules, floating rules, group rules, interface rules, then automatic VPN rules.
- Interface rules always stop at the first match. Floating rules without Quick are last match wins.
- Aliases (Firewall, Aliases) have tabs for IP, Ports, URLs and All. Use them instead of repeating addresses.
- States are under Diagnostics, States, with a **Kill States** button.

## NAT
- Port forwards are under Firewall, NAT, Port Forward, with an associated firewall rule by default. NAT reflection is set per rule.
- Outbound NAT modes: Automatic (default), Hybrid, Manual and Disable.

## Services
- **VLANs:** Interfaces, Assignments, VLANs tab, add, then assign it. See [VLANs](vlans.md).
- **DHCP:** Services, DHCP Server, with Kea and ISC backends. The default LAN pool is `.100` to `.199`.
- **DNS:** the Resolver (Unbound) is the default and can forward. The Forwarder (dnsmasq) only forwards. See [Unbound](unbound.md).
- **Packages:** WireGuard, pfBlockerNG (and pfBlockerNG-devel), Snort, Suricata and OpenVPN Client Export.
- **OpenVPN:** the wizard is under VPN, OpenVPN, Wizards.
- **High availability:** two nodes only. CARP virtual IPs are under Firewall, Virtual IPs, pfsync and XMLRPC under System, High Availability, and status under Status, CARP.

## Upgrade and Recovery
- Upgrade from System, Update, or console option 13 (`pfSense-upgrade`).
- Plus on ZFS creates a boot environment before an upgrade. From 24.03 it can roll back automatically, and the verification timer defaults to 300 seconds. Boot environments need Plus 22.05 or later.
- In the loader menu, option 8 usually selects a boot environment, for the current boot only.
- Take a configuration backup before every upgrade.

## Not Verified
`pfctl` commands (`-sr`, `-ss`, `-si`, `-t <TABLE> -T show`) are not documented on the Netgate site, command line `pkg` usage, whether console option 15 reboots, and Auto Config Backup retention.

## See Also
- [OPNsense](opnsense.md)
- [VLANs](vlans.md)
- [Unbound](unbound.md)
- [Network Troubleshooting](../recipes/network-troubleshooting.md)

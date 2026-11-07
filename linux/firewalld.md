# firewalld
firewalld is the default firewall manager on Fedora, RHEL and derivatives. It groups interfaces and sources into zones, allows traffic by service or port, and applies changes without dropping existing connections. Use `firewall-cmd` to manage it; it drives nftables underneath (see [nftables](nftables.md)).

Documentation: [firewalld documentation](https://firewalld.org/documentation/) · [firewall-cmd(1)](https://firewalld.org/documentation/man-pages/firewall-cmd.html)
Project: [firewalld](https://firewalld.org/)

> **Verification:** options were checked against the `firewall-cmd` man page in Ubuntu 24.04 (`firewalld`). No rules were applied to a live firewall. Zone and service names (`public`, `ssh`, `http`) are firewalld defaults.

## Runtime vs Permanent
Changes without `--permanent` apply immediately and are lost on reload or reboot. With `--permanent` they are saved but only take effect after `--reload`.

COMMAND | DESCRIPTION
---|---
`sudo firewall-cmd --state` | Is firewalld running
`sudo firewall-cmd --reload` | Load permanent config; keeps connections, drops runtime-only changes
`sudo firewall-cmd --runtime-to-permanent` | Save the current runtime config
`sudo firewall-cmd --list-all` | Active default zone: services, ports, rich rules
`sudo firewall-cmd --list-all-zones` | Every zone
`sudo firewall-cmd --get-default-zone` | Default zone
`sudo firewall-cmd --get-active-zones` | Zones with interfaces or sources

## Zones
COMMAND | DESCRIPTION
---|---
`sudo firewall-cmd --get-zones` | All zone names
`sudo firewall-cmd --set-default-zone=public` | Change the default zone
`sudo firewall-cmd --zone=public --list-all` | One zone
`sudo firewall-cmd --zone=internal --change-interface=<IF> --permanent` | Move an interface to a zone
`sudo firewall-cmd --zone=internal --add-source=192.0.2.0/24 --permanent` | Treat a network as part of a zone
`sudo firewall-cmd --get-zone-of-interface=<IF>` | Which zone an interface is in
`sudo firewall-cmd --new-zone=<ZONE> --permanent` | Create a custom zone (needs `--reload`)

## Services and Ports
COMMAND | DESCRIPTION
---|---
`sudo firewall-cmd --get-services` | Predefined service names
`sudo firewall-cmd --add-service=https --permanent` | Allow a service in the default zone
`sudo firewall-cmd --zone=internal --add-service=ssh --permanent` | In a chosen zone
`sudo firewall-cmd --remove-service=http --permanent` | Remove a service
`sudo firewall-cmd --add-port=8080/tcp --permanent` | Allow a port
`sudo firewall-cmd --add-port=60000-60010/udp --permanent` | Allow a port range
`sudo firewall-cmd --remove-port=8080/tcp --permanent` | Remove a port
`sudo firewall-cmd --query-service=https` | Is a service allowed (prints `yes` or `no`)
`sudo firewall-cmd --add-service=https --timeout=300` | Temporary rule that expires after 300 seconds

## Rich Rules
```bash
# allow SSH only from one network
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="192.0.2.0/24" service name="ssh" accept'

# reject traffic from one address
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="198.51.100.20" reject'

sudo firewall-cmd --list-rich-rules
sudo firewall-cmd --reload
```

## Forwarding and NAT
COMMAND | DESCRIPTION
---|---
`sudo firewall-cmd --add-masquerade --permanent` | Masquerade (source NAT) outgoing traffic in the zone
`sudo firewall-cmd --add-forward-port=port=80:proto=tcp:toport=8080 --permanent` | Redirect a local port
`sudo firewall-cmd --add-forward-port=port=80:proto=tcp:toport=80:toaddr=192.0.2.20 --permanent` | Forward to another host (needs masquerade)
`sudo firewall-cmd --list-forward-ports` | Show forwards

## Safety Net
Before locking down a remote host, test with a timeout so a mistake reverts itself, and use panic mode only at the console:

COMMAND | DESCRIPTION
---|---
`sudo firewall-cmd --add-service=<SERVICE> --timeout=60` | Rule that disappears after 60 seconds
`sudo firewall-cmd --panic-on` / `--panic-off` | Drop all traffic / restore (cuts your SSH session)

## Docker
Docker writes its own nftables or iptables rules and can bypass zone rules for published ports. See [Docker Troubleshooting](../docker/docker-troubleshooting.md) before relying on firewalld to close a published container port.

## Troubleshooting
SYMPTOM | FIX
---|---
Rule gone after reboot | It was runtime-only: repeat with `--permanent` or `--runtime-to-permanent`
Permanent rule not active | Run `sudo firewall-cmd --reload`
Service reachable from the wrong network | Check the interface's zone: `--get-active-zones`
`FirewallD is not running` | `sudo systemctl enable --now firewalld`
Unsure what is blocked | `sudo firewall-cmd --list-all`; logs: `sudo firewall-cmd --set-log-denied=all` then `journalctl -k`

## See Also
- [nftables](nftables.md)
- [IPTables](iptables.md)
- [UFW (uncomplicated firewall)](ufw.md)
- [SELinux and AppArmor](selinux-apparmor.md)
- [Fedora](../distros/fedora.md)
- [Docker Troubleshooting](../docker/docker-troubleshooting.md)

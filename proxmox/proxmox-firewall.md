# Proxmox Firewall
The built-in firewall works at three levels: datacenter (cluster), node (host) and guest (VM or container). Rules are stored in `/etc/pve` and replicated across the cluster.

Documentation: [Proxmox VE Firewall](https://pve.proxmox.com/pve-docs/chapter-pve-firewall.html)

> **Verification:** config file locations, the port list, and `pve-firewall status|start|stop|localnet` were checked against the docs. The docs state that traffic is blocked by default once enabled (with an exception for GUI and SSH from the local network), but do not give exact default policy values, so the "input DROP, output ACCEPT" detail below is from experience and unverified. `pve-firewall compile` and `simulate` are **not** documented for the legacy iptables firewall (`compile` appears for the newer nftables `proxmox-firewall`), so they are not listed. No command was executed.

See also: [[proxmox-networking]] · [[proxmox-access-api]] · [[proxmox-cluster-ha]] · [[ufw]] · [[iptables]]

---
## Enable Safely
The firewall is off until enabled at the **datacenter** level (Datacenter -> Firewall -> Options -> Firewall). Once on, incoming traffic is blocked unless allowed, apart from the web UI and SSH from the local network. Add rules for your own management network **before** enabling, and keep console access ready.

Enabling at the datacenter level is not enough for guests: each VM or container also needs its firewall enabled (Firewall -> Options) and the NIC's **Firewall** checkbox ticked.

COMMAND | DESCRIPTION
---|---
`pve-firewall status` | Is it running and enabled
`pve-firewall start` / `pve-firewall stop` | Start or stop the service (stop is useful if you locked yourself out)
`pve-firewall localnet` | Show the detected local network
`systemctl status pve-firewall` | Service health
`iptables-save \| less` | See the generated rules (legacy firewall, see [[iptables]])

---
## Config Files
FILE | SCOPE
---|---
`/etc/pve/firewall/cluster.fw` | Datacenter: options, rules, aliases, IP sets, security groups
`/etc/pve/nodes/<NODE>/host.fw` | One node
`/etc/pve/firewall/<VMID>.fw` | One VM or container

Format:
```
[OPTIONS]
enable: 1
policy_in: DROP

[RULES]
IN ACCEPT -source 192.168.1.0/24 -p tcp -dport 8006 -log nolog
IN SSH(ACCEPT) -source 192.168.1.0/24
```
Rules are `<IN|OUT|GROUP> <ACTION> [options]`. Actions: `ACCEPT`, `DROP`, `REJECT`. Macros such as `SSH`, `HTTP`, `HTTPS`, `Ping`, `DNS` expand to the right ports.

---
## Ports to Allow
PORT | USE
---|---
TCP 8006 | Web UI and API
TCP 22 | SSH
TCP 3128 | SPICE proxy
UDP 5405-5412 | Corosync cluster traffic
TCP 60000-60050 | Live migration
TCP 5900-5999 | VNC console (via the proxy, normally not needed externally)

Keep the cluster and migration networks on their own subnet and allow them with IP sets ([[proxmox-cluster-ha]]).

---
## IP Sets, Aliases and Security Groups
- **Alias:** a name for an IP or CIDR (`mgmt = 192.168.1.0/24`).
- **IP set:** a named list, reusable in rules with `+<SETNAME>`. The special `management` set is allowed to reach the UI and SSH.
- **Security group:** reusable rule bundle, applied with `GROUP <NAME>`.

---
## Typical Setup
1. Datacenter: create IP set `management` with your admin network, add rules for 8006 and 22.
2. Datacenter: enable firewall, keep default policy for input as DROP.
3. Nodes: enable the node firewall (Node -> Firewall -> Options).
4. Guests: enable per guest, add only the inbound ports needed.
5. Check logs: `journalctl -u pve-firewall` and the firewall log in the GUI.

If you lock yourself out, use the console, run `pve-firewall stop`, fix the rules in `/etc/pve/firewall/cluster.fw` or the node file, then `pve-firewall start`. On Debian-based guests, a host firewall inside the guest can be done with [[ufw]].

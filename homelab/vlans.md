# VLANs
A VLAN (IEEE 802.1Q) splits one physical switch network into several isolated layer-2 broadcast domains by adding a 4-byte tag with a 12-bit VLAN ID (1-4094) to Ethernet frames. In a homelab it is the standard way to separate trusted devices, servers, IoT and guests, then control traffic between them with a router/firewall. Traffic between VLANs must be routed, so that is where firewall rules apply.

Documentation: [ip-link(8), VLAN type (man7.org)](https://man7.org/linux/man-pages/man8/ip-link.8.html) · [Netplan reference](https://netplan.readthedocs.io/en/stable/netplan-yaml/) · [Proxmox network configuration](https://pve.proxmox.com/pve-docs/chapter-sysadmin.html#sysadmin_network_configuration)

> **Verification:** the commands and config snippets here were written from the upstream documentation and **not executed**. Test on a machine with console access, because a wrong network or switch config can lock you out. OPNsense and UniFi menu paths change between releases, so check the current UI.

See also: [Homelab](homelab.md) · [Proxmox Networking](../proxmox/proxmox-networking.md) · [Proxmox Firewall](../proxmox/proxmox-firewall.md) · [Docker Networking](../docker/docker-networking.md) · [UFW (uncomplicated firewall)](../linux/ufw.md) · [IPTables](../linux/iptables.md) · [dnsmasq DHCP and DNS](dnsmasq-dhcp.md) · [Reverse Proxy Patterns](reverse-proxy-patterns.md)

---
## Concepts
TERM | MEANING
---|---
Tagged / trunk | Port carries several VLANs; each frame has an 802.1Q tag. Used between switch, router, hypervisor and APs
Untagged / access | Port belongs to one VLAN; frames leave without a tag. Used for end devices
Native VLAN (PVID) | VLAN assigned to untagged frames arriving on a trunk. Keep it unused or match on both ends
Hybrid port | One untagged VLAN plus several tagged ones (vendor naming varies)
SVI / sub-interface | Router interface for a VLAN, usually the gateway address
Router-on-a-stick | One trunk link from switch to router carrying every VLAN
MTU | Tag adds 4 bytes; most gear handles 1500 payload fine, but check on tunnels and jumbo frames

Example plan (adapt IDs and ranges, documentation or RFC1918 space only):

VLAN | NAME | SUBNET | PURPOSE
---|---|---|---
1 / 10 | LAN / Trusted | `192.168.10.0/24` | Laptops, phones
20 | Servers | `192.168.20.0/24` | Docker hosts, Proxmox, NAS
30 | IoT | `192.168.30.0/24` | Cameras, TVs, smart plugs
40 | Guest | `192.168.40.0/24` | Internet only
99 | Management | `192.168.99.0/24` | Switches, APs, IPMI

---
## Linux: iproute2 (temporary)
COMMAND | DESCRIPTION
---|---
`ip link add link <IFACE> name <IFACE>.<VID> type vlan id <VID>` | Create a VLAN sub-interface
`ip addr add 192.168.20.10/24 dev <IFACE>.<VID>` | Assign an address
`ip link set <IFACE>.<VID> up` | Bring it up
`ip -d link show <IFACE>.<VID>` | Show VLAN details (the `-d` prints `vlan protocol 802.1Q id`)
`ip -br link show type vlan` | List all VLAN interfaces
`ip link del <IFACE>.<VID>` | Remove it
`cat /proc/net/vlan/config` | Kernel view of VLANs (needs the `8021q` module)
`sudo modprobe 8021q` | Load the module if missing
`tcpdump -nei <IFACE> vlan` | Capture only tagged frames and show the tag
`tcpdump -nei <IFACE> vlan <VID>` | Only one VLAN

Changes made with `ip` are lost on reboot; use netplan, NetworkManager or `/etc/network/interfaces` to persist.

---
## Linux: netplan (Ubuntu)
`/etc/netplan/60-vlans.yaml`:
```yaml
network:
  version: 2
  ethernets:
    eno1:
      dhcp4: false
  vlans:
    vlan20:
      id: 20
      link: eno1
      addresses: [192.168.20.10/24]
      routes:
        - to: default
          via: 192.168.20.1
      nameservers:
        addresses: [192.168.20.2]
    vlan30:
      id: 30
      link: eno1
      dhcp4: true
```
```bash
sudo chmod 600 /etc/netplan/60-vlans.yaml
sudo netplan try        # applies, reverts after 120 s unless confirmed
sudo netplan apply
```

A bridge for VMs, with a tagged VLAN member:
```yaml
network:
  version: 2
  ethernets:
    eno1: {}
  vlans:
    eno1.20:
      id: 20
      link: eno1
  bridges:
    br20:
      interfaces: [eno1.20]
      addresses: [192.168.20.10/24]
```

---
## Linux: NetworkManager (nmcli)
```bash
nmcli con add type vlan con-name vlan20 ifname vlan20 dev eno1 id 20 \
  ipv4.method manual ipv4.addresses 192.168.20.10/24 ipv4.gateway 192.168.20.1
nmcli con up vlan20
```

---
## Proxmox: VLAN-aware bridge
Make the bridge VLAN-aware once, then set the VLAN tag on each VM/CT NIC. The physical switch port to the node must be a trunk carrying those VLANs. See [Proxmox Networking](../proxmox/proxmox-networking.md).

`/etc/network/interfaces`:
```
auto vmbr0
iface vmbr0 inet static
    address 192.168.99.10/24
    gateway 192.168.99.1
    bridge-ports eno1
    bridge-stp off
    bridge-fd 0
    bridge-vlan-aware yes
    bridge-vids 2-4094
```
```bash
ifreload -a             # apply (ifupdown2)
```

COMMAND | DESCRIPTION
---|---
`qm set <VMID> --net0 virtio,bridge=vmbr0,tag=20` | Put a VM NIC on VLAN 20
`pct set <CTID> --net0 name=eth0,bridge=vmbr0,tag=20,ip=dhcp` | Same for an LXC container
`qm set <VMID> --net0 virtio,bridge=vmbr0,tag=20,trunks=20\;30` | NIC that is a trunk for several VLANs (leave `tag` off for a pure trunk)
`bridge vlan show` | Show per-port VLAN membership on the host

Put the host management address on a tagged sub-interface (for example `vmbr0.99`) when the management VLAN is not the native one.

---
## Docker: macvlan / ipvlan on a VLAN
Give containers addresses on a VLAN directly (see [Docker Networking](../docker/docker-networking.md)):
```bash
docker network create -d macvlan \
  --subnet=192.168.30.0/24 --gateway=192.168.30.1 \
  -o parent=eno1.30 vlan30
```
Docker host cannot reach its own macvlan containers by default; add a macvlan shim interface on the host if needed.

---
## OPNsense
STEP | WHERE
---|---
Create VLAN | Interfaces -> Devices -> VLAN: parent interface, tag, description (device name `vlan0.20` or similar)
Assign | Interfaces -> Assignments: add the VLAN device, then enable it and set a static IPv4 (the gateway address)
DHCP | Services -> Dnsmasq DNS & DHCP (or ISC/Kea) per interface: range and options; see [dnsmasq DHCP and DNS](dnsmasq-dhcp.md)
Firewall | Firewall -> Rules -> `<VLAN NAME>`: rules are evaluated on traffic entering that interface, first match wins, default deny
Aliases | Firewall -> Aliases: group hosts, ports and networks (for example `RFC1918`) to keep rules short

---
## UniFi
- Settings -> Networks -> New Virtual Network: set name, VLAN ID, gateway/subnet, DHCP.
- Switch ports: set the **Native VLAN/Network** (untagged) and optionally **Tagged VLAN Management** (allow all / block all / custom) for trunks.
- Wi-Fi: Settings -> WiFi, choose the network each SSID maps to (IoT SSID -> IoT network).
- Isolation: use the Network/Zone and firewall settings of your UniFi OS version; "Isolate Network" or zone policies block inter-VLAN traffic, with allow rules above for exceptions.
- Management VLAN: adopt switches and APs on a dedicated VLAN; do not leave the default VLAN 1 as the only network.

---
## Inter-VLAN Firewalling
Default posture: each VLAN may reach the internet and the router's DNS/DHCP, and nothing else. Add narrow allows.

SOURCE | DEST | PORTS | ACTION | NOTE
---|---|---|---|---
Trusted | Servers | any | allow | Admin access
Servers | Trusted | any | block | Servers rarely need to initiate to clients (rule order matters, stateful return traffic is allowed automatically)
IoT | Router | UDP 53, UDP 67/68, UDP 123 | allow | DNS, DHCP, NTP
IoT | `RFC1918` alias | any | block | Place after the router allow, above "allow to internet"
IoT | any | any | allow | Internet access
Guest | `RFC1918` alias | any | block | Internet only
Trusted | IoT | any | allow | Control devices; replies are stateful
Any | Management | any | block | Allow only from a trusted admin host

Tips:
- Rules are stateful: allow Trusted -> IoT and the replies come back without an IoT -> Trusted rule.
- Force clients to use your DNS ([Pi-hole](pihole.md), [AdGuard Home](adguard-home.md)) by allowing UDP/TCP 53 only to it and redirecting or blocking other port-53 traffic. DoH/DoT to public resolvers needs separate blocks (443/853).
- For host firewalls on Linux use [UFW (uncomplicated firewall)](../linux/ufw.md) or [IPTables](../linux/iptables.md); for the hypervisor layer see [Proxmox Firewall](../proxmox/proxmox-firewall.md).

---
## mDNS and Discovery Across VLANs
mDNS (UDP 5353, multicast `224.0.0.251`) and SSDP (UDP 1900) do not cross routers, so AirPlay, Chromecast, printers and Home Assistant discovery break between VLANs.

OPTION | HOW
---|---
OPNsense | Install `os-mdns-repeater`, pick the interfaces to repeat between. Allow the actual service traffic by firewall rule too
UniFi | Settings -> Networks -> enable **Multicast DNS** (mDNS) on the networks (or the Multicast DNS / Network Discovery setting in newer releases)
Linux `avahi-daemon` | In `/etc/avahi/avahi-daemon.conf` set `[reflector]` `enable-reflector=yes` (and optionally `reflect-ipv=no`); the host needs an interface in each VLAN
pfSense | Avahi package, same reflector idea

Reflection only relays discovery. The unicast connection that follows still needs a firewall allow rule (for example Trusted -> IoT).

---
## Troubleshooting
SYMPTOM | CHECK
---|---
No DHCP lease in a VLAN | Is the VLAN allowed on the trunk? Is a DHCP server or relay on that VLAN? `tcpdump -nei <IFACE> port 67 or port 68`
Works on one port, not another | Port VLAN/PVID mismatch; trunk "allowed VLANs" list missing the ID
Host sees tags but cannot talk | Wrong gateway, or firewall rule order (first match wins)
VM on Proxmox has no network | Bridge not `bridge-vlan-aware yes`, tag typed wrongly, or switch port not a trunk
Management lost after change | Native VLAN changed on one end only; use `netplan try` or console and revert
Large packets fail over a tunnel | MTU/MSS: test `ping -M do -s 1472 <HOST>`
Discovery works only in one VLAN | mDNS reflector or repeater not enabled on every involved interface
`ip -d link` shows no VLAN | `8021q` module not loaded: `sudo modprobe 8021q`

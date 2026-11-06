# Proxmox Networking
PVE networking is configured in `/etc/network/interfaces` (Debian ifupdown2) and edited in the GUI under Node -> System -> Network. Guests attach to Linux bridges (`vmbr0`).

Documentation: [Network Configuration](https://pve.proxmox.com/pve-docs/chapter-sysadmin.html#sysadmin_network_configuration) · [Software-Defined Network](https://pve.proxmox.com/pve-docs/chapter-pvesdn.html)

> **Verification:** `ifreload -a` and the `/etc/network/interfaces.new` pending-change flow were checked against the docs. The VLAN-aware bridge, bond, and SDN snippets, and the hostname/IP change notes, were **not** verified against the docs, and no command was executed. Compare with the docs example before use. Test on a node with console or IPMI access, because a wrong network config locks you out.

See also: [Proxmox Firewall](proxmox-firewall.md) · [Proxmox Clustering and HA](proxmox-cluster-ha.md) · [Proxmox Troubleshooting and One-Liners](proxmox-troubleshooting.md) · [Linux](../linux/linux.md) · [IPTables](../linux/iptables.md) · [WireGuard](../apps/wireguard.md)

---
## Commands
COMMAND | DESCRIPTION
---|---
`ip -br a` | Addresses (brief)
`ip -br link` | Link state
`bridge vlan show` | VLANs on bridge ports
`ifreload -a` | Apply `/etc/network/interfaces` without a reboot
`diff /etc/network/interfaces /etc/network/interfaces.new` | Pending GUI changes
`ifquery -a` | Parse and show the config
`cat /proc/net/bonding/bond0` | Bond state and slaves
`ethtool <NIC>` | Link speed and duplex
`hostname --ip-address` | Must be the node's real IP

GUI changes are written to `interfaces.new` and applied with **Apply Configuration** (or on reboot).

---
## Basic Bridge
`/etc/network/interfaces`:
```
auto lo
iface lo inet loopback

iface eno1 inet manual

auto vmbr0
iface vmbr0 inet static
    address 192.168.1.10/24
    gateway 192.168.1.1
    bridge-ports eno1
    bridge-stp off
    bridge-fd 0
```
Guests use `--net0 virtio,bridge=vmbr0` ([Proxmox qm and pct](proxmox-qm-pct.md)).

---
## VLAN-aware Bridge
One bridge carries all VLANs; set the tag on each guest NIC.
```
auto vmbr0
iface vmbr0 inet static
    address 192.168.1.10/24
    gateway 192.168.1.1
    bridge-ports eno1
    bridge-stp off
    bridge-fd 0
    bridge-vlan-aware yes
    bridge-vids 2-4094
```
COMMAND | DESCRIPTION
---|---
`qm set <VMID> --net0 virtio,bridge=vmbr0,tag=<VLAN>` | Tag a VM NIC
`pct set <CTID> --net0 name=eth0,bridge=vmbr0,tag=<VLAN>,ip=dhcp` | Tag a container NIC
`qm set <VMID> --net0 virtio,bridge=vmbr0,trunks=10;20` | Trunk several VLANs to a guest

The switch port must be a trunk with the matching VLANs. To put the host itself on a VLAN, add an interface such as `vmbr0.<VLAN>` and move the address there.

---
## Bond (LACP)
```
auto bond0
iface bond0 inet manual
    bond-slaves eno1 eno2
    bond-miimon 100
    bond-mode 802.3ad
    bond-xmit-hash-policy layer2+3

auto vmbr0
iface vmbr0 inet static
    address 192.168.1.10/24
    gateway 192.168.1.1
    bridge-ports bond0
    bridge-stp off
    bridge-fd 0
```
`802.3ad` needs a matching LACP group on the switch. `active-backup` needs no switch support.

---
## Separate Management, Storage and Cluster Networks
Use dedicated NICs or VLANs where possible: one for the web UI/SSH, one for corosync (cluster traffic is latency sensitive, [Proxmox Clustering and HA](proxmox-cluster-ha.md)), one for storage such as [NFS](../linux/nfs.md) or Ceph ([Proxmox Storage](proxmox-storage.md)), and one for guests.

---
## SDN (overview)
Datacenter -> SDN lets you define virtual networks cluster wide. Changes are staged and then applied with **Apply**. Configuration is stored in `/etc/pve/sdn`.

ZONE TYPE | USE
---|---
Simple | Isolated bridge on each node, no uplink
VLAN | Uses VLANs on an existing bridge
QinQ | Stacked VLANs
VXLAN | L2 overlay across L3 networks
EVPN | VXLAN with routing (BGP), most complex

Basic flow: create a zone, create a VNet in it, optionally add a subnet (and DHCP/IPAM), then apply. Guests then pick the VNet as their bridge.

---
## Change a Node's IP or Hostname
- Edit `/etc/network/interfaces` and `/etc/hosts` so the hostname resolves to the new IP.
- A standalone node can usually be renamed or re-addressed, but a **clustered** node must not be renamed. IP changes in a cluster also need the corosync config updated, see the docs before attempting.
- Run `pvecm updatecerts` after a change if the web UI reports certificate errors.

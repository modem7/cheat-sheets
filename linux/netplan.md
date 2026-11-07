# Netplan
Netplan is the network configuration layer on Ubuntu: YAML files in `/etc/netplan/` are rendered into configuration for `systemd-networkd` or NetworkManager. Use it to set static addresses, DHCP, VLANs, bridges and bonds on Ubuntu servers and cloud images.

Documentation: [Netplan reference](https://netplan.readthedocs.io/en/stable/netplan-yaml/) · [Netplan how-to guides](https://netplan.readthedocs.io/en/stable/)
Project: [Netplan](https://netplan.io/)

> **Verification:** commands were checked against the `netplan` man pages in Ubuntu 24.04. YAML keys follow the Netplan reference; configurations were validated with `netplan generate` only, and were not applied to a live network. Interface names (`enp1s0`) and addresses are examples.

## Commands
COMMAND | DESCRIPTION
---|---
`sudo netplan try` | Apply with automatic rollback unless you confirm within the timeout
`sudo netplan try --timeout 30` | Choose the confirmation timeout in seconds
`sudo netplan apply` | Apply the configuration now
`sudo netplan generate` | Render backend config and check the YAML without applying
`sudo netplan get` | Show the merged configuration
`sudo netplan status` | Interface state, addresses and routes
`sudo netplan status --all` | Include interfaces Netplan does not manage
`sudo netplan --debug generate` | Debug output for parse problems
`ls /etc/netplan/` | Configuration files, merged in lexical order

Always use `netplan try` on a remote machine: a wrong address on `apply` can lock you out.

## Static Address
Netplan files must not be world-readable; use `chmod 600`.

```yaml
# /etc/netplan/01-static.yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    enp1s0:
      dhcp4: false
      addresses:
        - 192.0.2.10/24
      routes:
        - to: default
          via: 192.0.2.1
      nameservers:
        addresses:
          - 192.0.2.53
        search:
          - example.com
```

## DHCP
```yaml
network:
  version: 2
  ethernets:
    enp1s0:
      dhcp4: true
      dhcp6: false
```

## VLAN
```yaml
network:
  version: 2
  ethernets:
    enp1s0: {}
  vlans:
    enp1s0.20:
      id: 20
      link: enp1s0
      addresses:
        - 198.51.100.10/24
```

## Bridge
```yaml
network:
  version: 2
  ethernets:
    enp1s0: {}
  bridges:
    br0:
      interfaces:
        - enp1s0
      addresses:
        - 192.0.2.10/24
      routes:
        - to: default
          via: 192.0.2.1
      nameservers:
        addresses:
          - 192.0.2.53
```

## Bond
```yaml
network:
  version: 2
  ethernets:
    enp1s0: {}
    enp2s0: {}
  bonds:
    bond0:
      interfaces:
        - enp1s0
        - enp2s0
      parameters:
        mode: active-backup
      dhcp4: true
```

## Useful Keys
KEY | PURPOSE
---|---
`renderer: networkd` / `NetworkManager` | Backend that applies the configuration
`dhcp4`, `dhcp6` | Enable DHCP per family
`addresses` | List of `ADDRESS/PREFIX`
`routes` with `to` and `via` | Static routes; `to: default` is the default route
`nameservers` with `addresses`, `search` | DNS servers and search domains
`mtu` | Link MTU
`match` with `macaddress` or `name` | Select interfaces by MAC or name pattern
`set-name` | Rename a matched interface (needs `match`)
`wakeonlan: true` | Wake-on-LAN, see [Wake-on-LAN](../homelab/wake-on-lan.md)
`optional: true` | Do not wait for this interface at boot

## Troubleshooting
SYMPTOM | FIX
---|---
`Permissions ... are too open` warning | `sudo chmod 600 /etc/netplan/*.yaml`
YAML error on `generate` | Use spaces, never tabs; check indentation and list dashes
Config ignored | A later file overrides it; check `netplan get` and file order
Cloud image reverts the config | `cloud-init` writes `50-cloud-init.yaml`; disable its network config (see the cloud-init docs) or edit that file
No DNS after change | `resolvectl status`, and check `nameservers` is under the interface, not at the top level
Interface not managed | `netplan status --all`; another tool (NetworkManager, ifupdown) may own it

## See Also
- [ip and ss](ip-and-ss.md)
- [VLANs](../homelab/vlans.md)
- [Wake-on-LAN](../homelab/wake-on-lan.md)
- [Proxmox Networking](../proxmox/proxmox-networking.md)
- [Proxmox Cloud-Init Templates](../proxmox/proxmox-cloud-init.md)
- [Ubuntu](../distros/ubuntu.md)

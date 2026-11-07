# ethtool
`ethtool` queries and changes the settings of Ethernet network interfaces: link speed and duplex, offloads, ring buffers, driver details and Wake-on-LAN. Use it when a link negotiates slower than expected or a NIC drops packets.

Documentation: [ethtool(8)](https://man7.org/linux/man-pages/man8/ethtool.8.html)
Project: [ethtool](https://mirrors.edge.kernel.org/pub/software/network/ethtool/)

> **Verification:** options were checked against the ethtool man page in Ubuntu 24.04. Support for each option depends on the NIC and driver, and virtual NICs often reject changes. Changes are lost at reboot unless persisted (see below).

## Link
COMMAND | DESCRIPTION
---|---
`sudo ethtool <IF>` | Speed, duplex, auto-negotiation and link detected
`sudo ethtool -s <IF> speed 1000 duplex full autoneg off` | Force speed and duplex (both ends must match)
`sudo ethtool -s <IF> autoneg on` | Re-enable auto-negotiation
`sudo ethtool -r <IF>` | Restart auto-negotiation
`sudo ethtool -i <IF>` | Driver, driver version and firmware
`sudo ethtool -P <IF>` | Permanent MAC address

## Statistics
COMMAND | DESCRIPTION
---|---
`sudo ethtool -S <IF>` | NIC and driver counters (errors, drops, missed)
`sudo ethtool -S <IF> \| grep -iE 'err\|drop\|miss'` | Only the error counters
`sudo ethtool -m <IF>` | SFP/SFP+ module data (optical levels, vendor)
`sudo ethtool -T <IF>` | Timestamping capabilities

## Offloads
COMMAND | DESCRIPTION
---|---
`sudo ethtool -k <IF>` | Show offload features
`sudo ethtool -K <IF> tso off gso off gro off` | Disable TCP segmentation, generic segmentation and generic receive offload
`sudo ethtool -K <IF> rx-checksumming off` | Disable receive checksum offload

Turn offloads off to diagnose odd packet captures or a driver bug, not as a permanent fix. See [tcpdump captures in Network Troubleshooting](../recipes/network-troubleshooting.md).

## Ring Buffers and Queues
COMMAND | DESCRIPTION
---|---
`sudo ethtool -g <IF>` | Current and maximum ring buffer sizes
`sudo ethtool -G <IF> rx 4096 tx 4096` | Enlarge ring buffers (up to the reported maximum)
`sudo ethtool -l <IF>` | Channel (queue) counts
`sudo ethtool -c <IF>` | Interrupt coalescing settings

## Wake-on-LAN
COMMAND | DESCRIPTION
---|---
`sudo ethtool <IF> \| grep -i wake` | Supported and current Wake-on modes (`g` = magic packet)
`sudo ethtool -s <IF> wol g` | Enable wake on magic packet

Persist it with your network manager; see [Wake-on-LAN](../homelab/wake-on-lan.md).

## Persist a Setting
`ethtool` changes do not survive a reboot. With systemd-networkd, put them in the `.link` file:

```ini
# /etc/systemd/network/10-lan.link
[Match]
MACAddress=00:00:5e:00:53:01

[Link]
WakeOnLan=magic
```

With NetworkManager, use `nmcli connection modify <CONNECTION> ethtool.feature-tso off` (property names follow the offload names in `nmcli` documentation; unverified here).

## Troubleshooting
SYMPTOM | FIX
---|---
Link at 100 Mb/s on a gigabit port | Check the cable and both ends; `ethtool <IF>` shows what the partner advertises
Rising `rx_missed` or `rx_dropped` | Enlarge the ring buffer with `ethtool -G`, check CPU load and IRQ balance
`Operation not supported` | The driver does not implement that feature (common on virtual NICs)
No `Link detected` | Cable, switch port or SFP; try `ethtool -r <IF>`

## See Also
- [ip and ss](ip-and-ss.md)
- [Network Troubleshooting](../recipes/network-troubleshooting.md)
- [Linux Performance Troubleshooting](performance-troubleshooting.md)
- [Proxmox Networking](../proxmox/proxmox-networking.md)

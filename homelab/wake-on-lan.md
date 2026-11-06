# Wake-on-LAN
Wake-on-LAN (WoL) powers on a machine by sending it a "magic packet": 6 bytes of `FF` followed by the target MAC address repeated 16 times, normally in a UDP broadcast to port 9 (some tools use 7). It needs support in the BIOS/UEFI and the network card, and the card must stay powered while the machine is off. It is layer 2, so crossing VLANs needs a directed broadcast or a relay.

Documentation: [ethtool man page](https://man7.org/linux/man-pages/man8/ethtool.8.html) · [Netplan reference (wakeonlan)](https://netplan.readthedocs.io/en/stable/netplan-yaml/) · [systemd.link](https://www.freedesktop.org/software/systemd/man/latest/systemd.link.html)

> **Verification:** commands and snippets were written from the upstream documentation and **not executed**. Behaviour depends heavily on NIC, driver and firmware, so test with the machine fully shut down, not just suspended.

See also: [Homelab](homelab.md) · [VLANs](vlans.md) · [Proxmox Networking](../proxmox/proxmox-networking.md) · [Proxmox qm and pct](../proxmox/proxmox-qm-pct.md) · [NUT (Network UPS Tools)](nut-ups.md) · [Tailscale](../apps/tailscale.md) · [WireGuard](../apps/wireguard.md)

---
## Target Machine Setup
1. Enable **Wake on LAN** / **Power on by PCIe** in BIOS/UEFI. Disable "ErP/EuP" or deep-power-saving options that cut standby power to the NIC.
2. Find the interface name and MAC: `ip -br link`.
3. Enable magic-packet wake in the driver (below) and make it persistent.

COMMAND | DESCRIPTION
---|---
`sudo ethtool <IFACE> \| grep -i wake` | `Supports Wake-on` letters and the current `Wake-on:` value
`sudo ethtool -s <IFACE> wol g` | Enable magic packet wake (`g`); `d` disables
`ip -br link show <IFACE>` | Read the MAC address
`cat /sys/class/net/<IFACE>/address` | Same, script-friendly

`ethtool` letters: `p` PHY activity, `u` unicast, `m` multicast, `b` broadcast, `a` ARP, `g` magic packet, `s` SecureOn password, `d` disabled.

The setting is lost on reboot on many systems; persist it one of these ways.

### systemd-networkd `.link` file
`/etc/systemd/network/50-wol.link`:
```ini
[Match]
MACAddress=aa:bb:cc:dd:ee:ff

[Link]
WakeOnLan=magic
```
Reboot (or `sudo udevadm trigger -c add -s net`) to apply.

### Netplan
```yaml
network:
  version: 2
  ethernets:
    eno1:
      dhcp4: true
      wakeonlan: true
```
```bash
sudo netplan apply
```

### NetworkManager
```bash
nmcli -f 802-3-ethernet.wake-on-lan connection show "<CONNECTION>"
nmcli connection modify "<CONNECTION>" 802-3-ethernet.wake-on-lan magic
nmcli connection up "<CONNECTION>"
```

### Proxmox / ifupdown
In `/etc/network/interfaces`, under the physical NIC that is a bridge port:
```
iface eno1 inet manual
    post-up /usr/sbin/ethtool -s eno1 wol g
```
Apply with `ifreload -a`. See [Proxmox Networking](../proxmox/proxmox-networking.md). Proxmox can also start guests on a schedule or by API ([Proxmox qm and pct](../proxmox/proxmox-qm-pct.md)), which is often easier than waking the host; wake the **node** with WoL, then start its VMs.

### Windows
Device Manager -> network adapter -> Properties: Advanced "Wake on Magic Packet" enabled, Power Management "Allow this device to wake the computer" and "Only allow a magic packet to wake the computer". Disable Fast Startup, which often breaks WoL after a shutdown.

---
## Sending a Magic Packet
COMMAND | DESCRIPTION
---|---
`wakeonlan <MAC>` | Debian/Ubuntu package `wakeonlan`, broadcasts to 255.255.255.255:9
`wakeonlan -i 192.168.20.255 <MAC>` | Send to a subnet's directed broadcast address
`wakeonlan -p 7 <MAC>` | Use another UDP port
`sudo etherwake -i <IFACE> <MAC>` | Package `etherwake`, sends a raw layer-2 frame out of one interface
`wol <MAC>` | Package `wol`, similar to `wakeonlan`
`ether-wake -i <IFACE> <MAC>` | BusyBox / OpenWrt / many routers

Python with no extra package:
```bash
python3 - <<'EOF'
import socket
mac = bytes.fromhex("aabbccddeeff")
pkt = b"\xff" * 6 + mac * 16
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.sendto(pkt, ("192.168.20.255", 9))
EOF
```

Docker (no install on the sender):
```bash
docker run --rm --network host alpine:3 sh -c 'apk add -q wakeonlan && wakeonlan <MAC>'
```
Host networking is needed so the broadcast leaves on the real LAN.

---
## Waking Across VLANs and Remotely
APPROACH | NOTES
---|---
Same VLAN | Broadcast works as-is
Directed broadcast | Send to `192.168.20.255:9` from another VLAN; the router must forward directed broadcasts (often disabled by default, and a firewall rule is needed)
Helper host | Run a small always-on device (Raspberry Pi, router, container) on the target VLAN, and SSH to it: `ssh pi 'wakeonlan <MAC>'`
Router feature | OPNsense: Services -> Wake on LAN (stores devices, one-click wake); UniFi: client page -> Wake-on-LAN option (UniFi gateways with this feature); OpenWrt: `etherwake` or `luci-app-wol`
Over VPN | Connect with [Tailscale](../apps/tailscale.md) or [WireGuard](../apps/wireguard.md), then SSH to an always-on machine on the LAN, or use a Tailscale subnet router there
WoL does not work over Wi-Fi | Most laptops only wake from wired NICs (some support "Wake on Wireless LAN")

Web front-ends such as a small WoL container or Home Assistant's `wake_on_lan` integration give a button without SSH; whichever you use, keep it internal-only ([Reverse Proxy Patterns](reverse-proxy-patterns.md)).

---
## Check That the Machine Woke
```bash
wakeonlan <MAC> && until ping -c1 -W1 <HOST_IP> >/dev/null 2>&1; do sleep 2; done && echo up
```
Watch for the packet arriving on a sibling machine: `sudo tcpdump -ni <IFACE> 'udp port 9 or ether proto 0x0842'` (0x0842 is the raw WoL EtherType used by `etherwake`).

---
## Troubleshooting
SYMPTOM | CHECK
---|---
`Wake-on: d` after every boot | Setting not persisted: use a `.link` file, netplan, NetworkManager or `post-up`
`ethtool` does not list `g` in "Supports Wake-on" | NIC or driver has no magic-packet support; try a different NIC or USB adapter that supports it
Works from suspend, not from power off | BIOS "Power on by PCIe/PCI" or ErP/EuP setting; on Windows disable Fast Startup
Works from same VLAN only | Broadcast is not routed: use a directed broadcast, a helper host, or the router's WoL feature
NIC link light off when machine is off | Standby power is cut; check BIOS options, and note that some PSUs or switches (EEE, power saving) can drop the link
Wrong MAC | Bonded or bridged NIC: use the MAC of the **physical** port that has WoL, not the bridge MAC (`ip -br link`)
Packet arrives but nothing happens | Verify with `tcpdump` on the switch side or another host; the problem is the target's BIOS/NIC, not the sender

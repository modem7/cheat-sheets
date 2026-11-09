# UniFi Device CLI and Adoption
Adopting UniFi devices over layer 3, and the small set of SSH commands you need when a device is stuck. Ubiquiti's advice is to use the Debug Console in the UI and use SSH only when support asks, so treat the commands here as a last resort.

Documentation: [Device SSH](https://help.ui.com/hc/en-us/articles/204909374) · [Layer 3 adoption](https://help.ui.com/hc/en-us/articles/204909754) · [Adopting devices](https://help.ui.com/hc/en-us/articles/360012622613)

## SSH Access
- **Consoles:** SSH is off by default. Enable it in Settings, Control Plane, Console. Username `root`.
- **Devices:** SSH is on by default. The credentials are in Network, Devices, Device Updates and Settings, Device SSH Authentication.
- **Factory defaults:** `ui` / `ui` on devices (older ones `ubnt` / `ubnt`), `root` / `ui` on consoles and gateways (older ones `root` / `ubnt`).

```bash
ssh <USER>@<DEVICE_IP>
```

Change the SSH credentials after adoption and keep them in your password manager.

## Commands
COMMAND | DESCRIPTION
---|---
`info` | Show model, firmware and the current inform URL
`set-inform http://<CONTROLLER>:8080/inform` | Point the device at a controller
`set-default` | Factory reset (**destructive**)
`reboot`, `poweroff` | Restart or shut down
`uptime` | How long it has been running
`upgrade <FIRMWARE_URL>.bin` | Install firmware from a URL
`ubnt-systool cputemp`, `cpuload`, `portstatus` | Hardware status
`ubnt-device-info summary` | Device summary
`tail -f /var/log/messages` | System log

The commands in the table after `set-inform` come from a 2023 community guide, so run `help` on the device and check them on your firmware. Some commands such as `swctrl ...` (switches), `mca-cli-op info` and `iwconfig` were **not verified**.

`set-inform` often has to be run twice, once to register and once after the device appears as Pending Adoption in the controller.

## Layer 3 Adoption
Devices on the same layer 2 network find the controller on their own. Across VLANs or sites, use one of these and make sure TCP 8080 and UDP 10001 are open:

METHOD | HOW
---|---
SSH | `set-inform http://<CONTROLLER>:8080/inform`, then click Adopt
DNS | Make the name `unifi` resolve to the controller (A record on your DNS, see [dnsmasq DHCP and DNS](../homelab/dnsmasq-dhcp.md))
DHCP option 43 | Send the controller address as hex (below)
ZTP | Zero-touch provisioning, see Ubiquiti's article

Option 43, IP form: `0104` followed by the controller IP in hex. For `192.0.2.10` (`c0.00.02.0a`) that is `0104c000020a`. A hostname form exists too (`02`, then the length in hex, then the hex of the inform URL). In UniFi gateway DHCP settings option 43 is predefined, see [UniFi Networks and VLANs](unifi-networks-vlans.md).

## Remote Controller
If the controller is on the internet, forward TCP 8080 to it. Double NAT will not work for adoption. Prefer a VPN to the site instead.

## Stuck Devices
STATE | WHAT TO TRY
---|---
Adopting or Pending forever | Check TCP 8080 reaches the controller, repeat `set-inform`, and check the firewall between VLANs
Managed by another console | Forget the device on the old console, or factory reset
Provisioning or Isolated | No official fix was found. Check uplink and VLAN, reboot, then factory reset and re-adopt
Wrong controller after a migration | "Override Inform Host" on the old controller, or `set-inform` to the new one

Factory reset and re-adopt is the documented last resort. After a restore, devices must be able to reach the new host.

## Firmware
- Upgrade devices from the Network application where possible.
- Release channels are Official and Early Access.
- Upgrade order and downgrade behaviour were **not verified**.

## Not Verified
`swctrl`, `mca-cli-op`, `mca-dump`, `iwconfig`, `syswrapper.sh restore-default` on current firmware, MongoDB query examples (`mongo --port 27117 ace`), stuck-state fixes beyond reset.

## See Also
- [UniFi](unifi.md)
- [UniFi Hosting](unifi-hosting.md)
- [UniFi Backups and Migration](unifi-backups.md)
- [dnsmasq DHCP and DNS](../homelab/dnsmasq-dhcp.md)

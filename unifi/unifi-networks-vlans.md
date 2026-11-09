# UniFi Networks and VLANs
How networks, VLANs, switch port profiles, DHCP and multicast fit together in UniFi Network. For general VLAN design see [VLANs](../homelab/vlans.md). Menu names change between releases, so look for the setting by name if a path differs.

Documentation: [Switch Port VLAN Assignment](https://help.ui.com/hc/en-us/articles/26136855808919) · [Switch Settings](https://help.ui.com/hc/en-us/articles/33402927617047) · [DHCP Options](https://help.ui.com/hc/en-us/articles/360012097513) · [Managing Broadcast Traffic](https://help.ui.com/hc/en-us/articles/27384925962647)

## Concepts
TERM | MEANING
---|---
Network | A subnet with a VLAN ID, gateway and DHCP settings
Native VLAN | The untagged network for devices plugged into a port
Tagged VLAN | Extra VLANs carried on a port (trunk)
Port profile | A saved bundle of native and tagged VLANs, at Settings, Profiles, Switch Ports
Port isolation | Stops a port talking to other ports on the same switch, even in the same VLAN

## Tagged VLAN Management
Per port:

MODE | MEANING
---|---
Allow All | Trunk carrying every VLAN (the default)
Block All | Access port, native network only
Custom | Pick which tagged VLANs pass

Use Block All on ports for end devices and Custom on uplinks to other switches, so unwanted VLANs do not travel everywhere. Changing the native network on an uplink can cut off the devices below it, so change it from the console on a wired connection.

## A Typical Layout
VLAN | USE
---|---
Default or management | Gateway, switches, access points, controller
Trusted | Computers and phones
IoT | Smart devices ([UniFi WiFi](unifi-wifi.md) for the SSID)
Cameras | [UniFi Protect](unifi-protect.md) devices
Guest | Internet only
Servers | Homelab hosts

Pair each VLAN with firewall rules, see [UniFi Firewall and VPN](unifi-firewall-vpn.md). A VLAN on its own gives no isolation.

## DHCP
- The DHCP server is on per network by default.
- Predefined options include 43 (UniFi controller), 42 (NTP), 66 and 67 (network boot, see [PXE Boot](../homelab/pxe-boot.md)).
- Set a DHCP range that leaves room for static addresses.
- DHCP relay is available for networks served elsewhere. A community post says to leave the port field blank, which is **unverified**.
- For fixed addresses use a fixed IP on the client in the UI, not a static address set on the device.

## Multicast and Discovery
SETTING | USE
---|---
IGMP snooping | Sends multicast only to ports with group members. Helps IPTV and busy switches
mDNS | Lets Bonjour and Chromecast discovery cross VLANs. Use a dedicated VLAN and relay only where needed
Client isolation | Stops WiFi clients talking to each other. Ubiquiti calls it a last resort

For Home Assistant and casting across VLANs, enable mDNS across just the networks involved rather than everywhere.

## Management VLAN
A non-default management VLAN reportedly needs a Network Override on the switch. This comes from an old community thread, so check it on your version before relying on it.

## 802.1X
UniFi can use a RADIUS server for port-based access control. The setup steps were **not verified** here.

## Jumbo Frames
Typical MTU is 9216 and every device in the path must support it. See [UniFi Routing and WAN](unifi-routing-wan.md).

## Not Verified
DHCP relay detail, management VLAN override, 802.1X setup, and exact menu paths in your release.

## See Also
- [UniFi](unifi.md)
- [VLANs](../homelab/vlans.md)
- [UniFi Firewall and VPN](unifi-firewall-vpn.md)
- [dnsmasq DHCP and DNS](../homelab/dnsmasq-dhcp.md)

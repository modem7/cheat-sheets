# UniFi Routing and WAN
WAN, IPv6, dynamic routing, local DNS, QoS and jumbo frames on UniFi gateways.

Documentation: [Multi-WAN](https://help.ui.com/hc/en-us/articles/360052548713) · [IPv6](https://help.ui.com/hc/en-us/articles/36378535649687) · [OSPF](https://help.ui.com/hc/en-us/articles/12115251061143) · [DNS Records](https://help.ui.com/hc/en-us/articles/15179064940439) · [Smart Queues](https://help.ui.com/hc/en-us/articles/12648661321367) · [Jumbo Frames](https://help.ui.com/hc/en-us/articles/18039891529879)

## Multi-WAN
- Modes are failover and load balancing, with weights for load balancing.
- A second WAN as pure failover is the simplest and most predictable.
- The maximum number of WANs was not confirmed.

## IPv6
- WAN: SLAAC, DHCPv6 or static.
- Enter the prefix delegation size your ISP gives you.
- Check each internal network's IPv6 setting separately. Details of the options were not read.

## Dynamic Routing
OSPF is supported. Neighbours must match hello and dead timers, area and MTU. BGP and OSPF sit under Policy Table, Dynamic Routing in recent releases. BGP configuration was **not verified**.

## Local DNS
Local DNS records support A, AAAA, CNAME, MX, TXT and SRV. They resolve only for clients that use the gateway as their DNS server. If clients use a Pi-hole or another resolver, put the records there. See [dnsmasq DHCP and DNS](../homelab/dnsmasq-dhcp.md) and [Reverse Proxy Patterns](../homelab/reverse-proxy-patterns.md) for split-horizon names.

## QoS
- Smart Queues suits connections under about 300 Mbps. Do not use it on faster links.
- QoS rules disable hardware offload, which can cut throughput on gigabit and faster links.

## Jumbo Frames
Typical MTU is 9216 and every device in the path must support it. Enable it only where you need it, for example storage networks.

## Not Verified
Number of WANs, BGP, DDNS, DNS Shield, static route detail, and hardware offload numbers.

## See Also
- [UniFi](unifi.md)
- [UniFi Firewall and VPN](unifi-firewall-vpn.md)
- [UniFi Networks and VLANs](unifi-networks-vlans.md)
- [dnsmasq DHCP and DNS](../homelab/dnsmasq-dhcp.md)

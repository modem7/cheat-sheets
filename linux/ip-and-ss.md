# ip and ss
`ip` (from iproute2) shows and changes interfaces, addresses, routes and the neighbour (ARP) table; `ss` lists sockets and replaces `netstat`. Both are on every modern Linux distribution. Changes made with `ip` are lost at reboot unless also written to the network configuration.

Documentation: [ip(8)](https://man7.org/linux/man-pages/man8/ip.8.html) · [ss(8)](https://man7.org/linux/man-pages/man8/ss.8.html)
Project: [iproute2](https://wiki.linuxfoundation.org/networking/iproute2)

> **Verification:** options were checked against the iproute2 6.1 man pages in Ubuntu 24.04 and the read-only commands run in a container. Commands that change the host network were not run.

## Interfaces
COMMAND | DESCRIPTION
---|---
`ip -br link` | Brief interface list with state and MAC
`ip link show <IF>` | One interface in detail
`ip -s link show <IF>` | Packet, error and drop counters
`sudo ip link set <IF> up` / `sudo ip link set <IF> down` | Bring an interface up or down
`sudo ip link set <IF> mtu 9000` | Change the MTU
`sudo ip link add link <IF> name <IF>.20 type vlan id 20` | Create a VLAN sub-interface
`sudo ip link add <BRIDGE> type bridge` | Create a bridge
`sudo ip link set <IF> master <BRIDGE>` | Attach an interface to a bridge
`sudo ip link delete <IF>` | Remove a virtual interface

## Addresses
COMMAND | DESCRIPTION
---|---
`ip -br addr` | Brief address list
`ip -4 addr show <IF>` / `ip -6 addr show <IF>` | One address family only
`sudo ip addr add 192.0.2.10/24 dev <IF>` | Add an address
`sudo ip addr del 192.0.2.10/24 dev <IF>` | Remove an address
`sudo ip addr flush dev <IF>` | Remove all addresses from an interface
`ip -j addr` | JSON output (pipe to `jq`, see [jq](../tools/jq.md))

## Routes
COMMAND | DESCRIPTION
---|---
`ip route` | Main routing table
`ip route get 198.51.100.1` | Which route, source address and interface would be used
`sudo ip route add default via 192.0.2.1` | Set the default gateway
`sudo ip route add 198.51.100.0/24 via 192.0.2.254 dev <IF>` | Static route to a network
`sudo ip route del 198.51.100.0/24` | Remove a route
`ip -6 route` | IPv6 routes
`ip rule` | Policy routing rules

## Neighbours (ARP)
COMMAND | DESCRIPTION
---|---
`ip neigh` | Neighbour table; `REACHABLE`, `STALE`, `FAILED`
`ip neigh show dev <IF>` | One interface
`sudo ip neigh flush dev <IF>` | Clear cached entries
`sudo ip neigh add 192.0.2.50 lladdr 00:00:5e:00:53:01 dev <IF>` | Add a static entry (the MAC is from the documentation range)

## Network Namespaces
COMMAND | DESCRIPTION
---|---
`ip netns list` | List namespaces
`sudo ip netns add <NAME>` | Create a namespace
`sudo ip netns exec <NAME> ip addr` | Run a command inside it

## Monitor
COMMAND | DESCRIPTION
---|---
`ip monitor` | Watch link, address and route changes live
`ip -s -s link show <IF>` | Extra detail on error counters

## ss Sockets
COMMAND | DESCRIPTION
---|---
`ss -tulpn` | Listening TCP and UDP sockets with owning process (`sudo` shows other users' processes)
`ss -tln` | Listening TCP, numeric
`ss -tn state established` | Established TCP connections
`ss -tn dst 198.51.100.1` | Connections to one address
`ss -tn 'sport = :443'` | Filter by local port
`ss -tn 'dport = :22'` | Filter by remote port
`ss -s` | Socket totals per protocol
`ss -tnp` | Connections with process
`ss -ti` | TCP internals (RTT, congestion window, retransmits)
`ss -xl` | Listening Unix sockets
`ss -ltn sport = :8080` | Is anything listening on a port

Flags: `-t` TCP, `-u` UDP, `-l` listening, `-n` numeric, `-p` process, `-a` all, `-4` / `-6` family.

## Old Commands
OLD | REPLACEMENT
---|---
`ifconfig` | `ip addr`, `ip link`
`route -n` | `ip route`
`arp -a` | `ip neigh`
`netstat -tulpn` | `ss -tulpn`
`netstat -s` | `nstat` or `ss -s`

## See Also
- [Network Troubleshooting](../recipes/network-troubleshooting.md)
- [ethtool](ethtool.md)
- [VLANs](../homelab/vlans.md)
- [Proxmox Networking](../proxmox/proxmox-networking.md)
- [Docker Networking](../docker/docker-networking.md)
- [Linux Performance Troubleshooting](performance-troubleshooting.md)

# Network Troubleshooting
A layered approach for "A cannot reach B": check the link, the address and route, name resolution, the path, the port, and finally the application, and stop at the first layer that fails.

Documentation: [ip(8)](https://man7.org/linux/man-pages/man8/ip.8.html) · [ss(8)](https://man7.org/linux/man-pages/man8/ss.8.html) · [tcpdump](https://www.tcpdump.org/manpages/tcpdump.1.html)

## Goal
Locate the failing layer and the device or rule responsible.

## Prerequisites
- Shell access to the client, ideally also to the server
- `iputils-ping`, `mtr-tiny`, `tcpdump`, `dnsutils`, `curl`, `nmap` (`sudo apt install -y mtr-tiny tcpdump dnsutils nmap`)
- Source `192.0.2.20`, destination `198.51.100.10` and gateway `192.0.2.1` below are examples

## Steps
### 1. Link and address (L1/L2)
COMMAND | DESCRIPTION
---|---
`ip -br link` | Interface state: `UP` and `LOWER_UP` mean link
`ip -br addr` | Addresses per interface
`ethtool eth0` | Speed, duplex, `Link detected`
`ip neigh` | ARP/neighbour table; `FAILED` or `INCOMPLETE` for the gateway means no L2 reply

No address (DHCP failed), `NO-CARRIER` or a wrong subnet ends the search here.

### 2. Routing (L3, local)
```bash
ip route
ip route get 198.51.100.10        # shows the interface, gateway and source address chosen
ping -c 3 192.0.2.1               # default gateway
```
No default route or a wrong gateway: fix the network configuration. Several interfaces or VPNs often cause the wrong route to win (`ip route get` shows which).

### 3. Reach the destination by IP
```bash
ping -c 4 198.51.100.10
mtr -rwzc 50 198.51.100.10        # report mode, 50 cycles, with AS numbers
traceroute -n 198.51.100.10
```
Reading `mtr`: loss that **continues to the last hop** is real. Loss at one middle hop that disappears further on is a router rate-limiting ICMP and is harmless. Many networks block ICMP, so a failed `ping` alone does not prove the host is down; go on to step 5.

### 4. Name resolution
```bash
getent hosts app.example.com
dig +short app.example.com
```
If the IP works and the name does not, follow [[dns-troubleshooting]].

### 5. Port and service
```bash
nc -vz 198.51.100.10 443
curl -v --connect-timeout 5 http://198.51.100.10:8080/
nmap -Pn -p 22,80,443 198.51.100.10
```
RESULT | MEANING
---|---
Connected | Path and port are fine, the problem is in the application
`Connection refused` | Host reachable, nothing listening (or a firewall `REJECT`)
Timeout | Packets dropped by a firewall, security group, wrong route or the host is down

### 6. On the server: is it listening, and where?
```bash
sudo ss -tulpn                    # listening TCP and UDP sockets with process
sudo ss -tn state established '( sport = :443 )'
```
A service bound to `127.0.0.1:8080` is not reachable from other hosts; it must listen on `0.0.0.0` or the LAN address. Containers: check the published ports with `docker ps` ([[docker-networking]]).

### 7. Firewall
```bash
sudo ufw status verbose
sudo iptables -S                  # or: sudo nft list ruleset
sudo iptables -L -n -v | head -50 # packet counters show which rule is matching
```
Also check the router, cloud security groups and the destination's own firewall ([[ufw]], [[iptables]]). Docker publishes ports with its own rules that UFW does not control.

### 8. Watch the packets
Capture on the server while the client tries to connect:
```bash
sudo tcpdump -ni eth0 host 192.0.2.20 and tcp port 443
sudo tcpdump -ni eth0 icmp
sudo tcpdump -ni any port 53
sudo tcpdump -ni eth0 -w /tmp/cap.pcap host 192.0.2.20      # save for Wireshark
```
WHAT YOU SEE | MEANING
---|---
No packets at all | They never arrive: routing, upstream firewall or NAT
`SYN` in, no `SYN-ACK` out | Local firewall drops it, or nothing listens
`SYN` in, `RST` out | Port closed
`SYN, SYN-ACK`, then no `ACK` | Return path or asymmetric routing problem
Large transfers stall, small ones work | MTU problem: test `ping -M do -s 1472 198.51.100.10` and lower the size until it passes (typical with VPNs, see [[wireguard-remote-access]])

### 9. The application layer
```bash
curl -v https://app.example.com/
curl -sS -o /dev/null -w 'dns %{time_namelookup} connect %{time_connect} tls %{time_appconnect} first-byte %{time_starttransfer} total %{time_total}\n' https://app.example.com/
```
Certificate errors: [[tls-troubleshooting]]. HTTP status codes: [[http-status-codes]].

## Verify
```bash
ping -c 3 198.51.100.10
nc -vz 198.51.100.10 443
curl -sSI https://app.example.com | head -n 1
```
Then repeat from the original failing client, not only from where you debugged.

## Rollback / Cleanup
Everything above is read-only apart from `tcpdump`. Delete capture files (`rm /tmp/cap.pcap`) because they can contain sensitive traffic. If you changed a firewall rule while testing, remove it (`sudo ufw delete <NUMBER>`) and confirm with `sudo ufw status numbered`.

## Related Sheets
- [[tcp-vs-udp]] · [[linux]] · [[linuxbasics]] · [[iptables]] · [[ufw]]
- [[nmap]] · [[curl]] · [[http-status-codes]]
- [[docker-networking]] · [[proxmox-networking]] · [[kubernetes-dns]]
- [[dns-troubleshooting]] · [[tls-troubleshooting]] · [[wireguard-remote-access]]

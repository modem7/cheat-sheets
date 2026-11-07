# tcpdump
`tcpdump` captures and prints network packets from the command line using BPF filter expressions. Use it to confirm whether traffic reaches a host, to debug DHCP, DNS or VLAN problems, and to save a capture for [Wireshark and tshark](wireshark-tshark.md).

Documentation: [tcpdump(1)](https://www.tcpdump.org/manpages/tcpdump.1.html) · [pcap-filter(7)](https://www.tcpdump.org/manpages/pcap-filter.7.html)
Project: [tcpdump and libpcap](https://www.tcpdump.org/)

> **Verification:** options and filter primitives were checked against the tcpdump and pcap-filter man pages in Ubuntu 24.04. Captures need root (`sudo`) and were not run against live traffic here.

## Basics
COMMAND | DESCRIPTION
---|---
`sudo tcpdump -D` | List capture interfaces
`sudo tcpdump -i <IF>` | Capture on one interface
`sudo tcpdump -i any` | All interfaces (Linux)
`sudo tcpdump -n` | No name resolution of hosts
`sudo tcpdump -nn` | No name or port-name resolution
`sudo tcpdump -c 20` | Stop after 20 packets
`sudo tcpdump -q` | Quieter, shorter lines
`sudo tcpdump -e` | Show link-level headers (MAC addresses, VLAN tags)
`sudo tcpdump -v` / `-vv` | More detail (TTL, flags, checksums)
`sudo tcpdump -A` | Print payload as ASCII
`sudo tcpdump -X` | Payload as hex and ASCII
`sudo tcpdump -s 0` | Capture whole packets (the default snapshot length is already 262144 bytes on current versions)
`sudo tcpdump -l` | Line-buffered output, for piping to `grep`

## Filters
COMMAND | DESCRIPTION
---|---
`sudo tcpdump -nn host 192.0.2.10` | Traffic to or from a host
`sudo tcpdump -nn src host 192.0.2.10` | From a host
`sudo tcpdump -nn dst host 192.0.2.10` | To a host
`sudo tcpdump -nn net 192.0.2.0/24` | A network
`sudo tcpdump -nn port 443` | A port, either direction
`sudo tcpdump -nn portrange 8000-8100` | A port range
`sudo tcpdump -nn tcp` / `udp` / `icmp` | One protocol
`sudo tcpdump -nn host 192.0.2.10 and port 22` | Combine with `and`
`sudo tcpdump -nn 'port 53 or port 853'` | Combine with `or`
`sudo tcpdump -nn not port 22` | Exclude (handy over SSH)
`sudo tcpdump -nn vlan 20` | Frames tagged with a VLAN ID
`sudo tcpdump -nn ether host 00:00:5e:00:53:01` | A MAC address
`sudo tcpdump -nn arp` | ARP only
`sudo tcpdump -nn 'tcp[tcpflags] & (tcp-syn) != 0'` | TCP SYN packets
`sudo tcpdump -nn 'tcp[tcpflags] & (tcp-rst) != 0'` | TCP resets

Quote any filter that contains brackets, parentheses or `!`.

## Save and Read
COMMAND | DESCRIPTION
---|---
`sudo tcpdump -i <IF> -w capture.pcap` | Write raw packets to a file
`sudo tcpdump -i <IF> -w capture.pcap -C 100 -W 5` | Rotate at 100 MB, keep 5 files
`sudo tcpdump -i <IF> -w 'cap-%F-%H%M.pcap' -G 3600` | New file every hour (`-G` seconds, time format in the name)
`tcpdump -nn -r capture.pcap` | Read a file (no root needed)
`tcpdump -nn -r capture.pcap port 53` | Apply a filter when reading
`sudo tcpdump -i <IF> -z gzip -w capture.pcap -G 3600` | Compress rotated files (needs `-G` or `-C`)

## Common Tasks
Watch DHCP exchanges:

```bash
sudo tcpdump -nn -e -i eth0 'port 67 or port 68'
```

Watch DNS queries to and from one resolver:

```bash
sudo tcpdump -nn -i any 'host 192.0.2.53 and port 53'
```

Check ping reaches the host:

```bash
sudo tcpdump -nn -i eth0 icmp
```

See traffic without exposing your own SSH session:

```bash
sudo tcpdump -nn -i eth0 'not port 22'
```

## Troubleshooting
SYMPTOM | FIX
---|---
`permission denied` | Run with `sudo`, or grant the binary capture capabilities
Nothing captured | Wrong interface (`-D`), or the traffic is on a bridge or VLAN sub-interface
`dropped by kernel` at exit | Capture is too slow: add `-n`, use `-w`, filter, or raise `-B <KiB>` buffer size
Capture inside a container | Run it in the container's network namespace: `sudo nsenter -t <PID> -n tcpdump -nn`

## See Also
- [Wireshark and tshark](wireshark-tshark.md)
- [Network Troubleshooting](../recipes/network-troubleshooting.md)
- [ip and ss](../linux/ip-and-ss.md)
- [VLANs](../homelab/vlans.md)
- [Docker Troubleshooting](../docker/docker-troubleshooting.md)

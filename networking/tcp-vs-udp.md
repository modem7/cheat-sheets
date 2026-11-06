# TCP vs UDP
The two main transport-layer protocols. TCP gives reliable ordered delivery, UDP gives fast best-effort datagrams.

## Comparison
&nbsp; | TCP | UDP
---|---|---
Connection | Connection-oriented (3-way handshake) | Connectionless
Reliability | Acknowledged, retransmitted | None, packets may be lost or reordered
Ordering | Guaranteed | Not guaranteed
Flow and congestion control | Yes | No
Header size | 20+ bytes | 8 bytes
Speed / overhead | Higher overhead | Lower latency
Typical use | Web (HTTP/1.1, HTTP/2), SSH, email, databases | DNS, VoIP, video, games, VPNs, HTTP/3 (QUIC)

## Common Ports
PORT | PROTOCOL | SERVICE
---|---|---
`22` | TCP | SSH
`53` | UDP and TCP | DNS
`80` / `443` | TCP (443 also UDP for HTTP/3) | HTTP / HTTPS
`123` | UDP | NTP
`51820` | UDP | WireGuard
`853` | TCP | DNS over TLS

## The TCP Handshake and Teardown
1. Client sends `SYN`
2. Server replies `SYN, ACK`
3. Client sends `ACK`: connection established
4. Closing: `FIN` / `ACK` in each direction (or `RST` to abort)

## Testing Ports
COMMAND | DESCRIPTION
---|---
`nc -zv <HOST> <PORT>` | Test a TCP port
`nc -zvu <HOST> <PORT>` | Test a UDP port (unreliable, no reply means open or filtered)
`nmap -sU -p <PORT> <HOST>` | UDP scan, see [[nmap]]
`ss -tulpn` | Listening sockets on this host
`sudo tcpdump -ni any 'tcp[tcpflags] & (tcp-syn) != 0'` | Watch SYN packets
`iperf3 -s` / `iperf3 -c <HOST>` | TCP throughput test
`iperf3 -c <HOST> -u -b 100M` | UDP throughput and loss test

## Some notes

Each frame goes through several buffers as you send it: The application buffer, The Protocol Buffer, The Software interface buffer and the Hardware interface buffer. As you start stressing the stack by sending high speed data you will fill up these buffers and either block or lose data. You also have strategies for timeliness and polling that can impact your performance. For example, by using a larger buffer and poll less often you can get much better performance while sacrificing latency.

TCP is optimized for high speed bulk transfers while UDP is optimized for low latency in the Linux kernel. This has an impact on buffer sizes and how data is polled and handed over. In addition to this, you frequently have offloading to hardware for TCP. I would expect considerably better performance for TCP compared to UDP.

Note that sending high speed data over UDP is usually a bad idea, unless you implement your own congestion control. TCP protects your network from congestion collapses. Use UDP when you have small amounts of data or high timeliness requirements.

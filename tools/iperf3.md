# iperf3
`iperf3` measures network throughput between two hosts: one runs as a server, the other as a client. Use it to test a link, a VLAN, a VPN or Wi-Fi, and to separate network problems from disk or application problems.

Documentation: [iperf3 user documentation](https://iperf.fr/iperf-doc.php) · [iperf3(1)](https://man7.org/linux/man-pages/man1/iperf3.1.html)
Project: [iperf3 on GitHub](https://github.com/esnet/iperf)

> **Verification:** options were checked against the iperf3 man page in Ubuntu 24.04. No throughput test was run between real hosts. Both ends should run the same major version.

## Basics
COMMAND | DESCRIPTION
---|---
`iperf3 -s` | Run a server (default TCP port 5201)
`iperf3 -s -D` | Server as a daemon
`iperf3 -s -1` | Serve one client then exit
`iperf3 -c <SERVER>` | Run a 10-second TCP test to the server
`iperf3 -c <SERVER> -R` | Reverse: server sends, client receives
`iperf3 -c <SERVER> --bidir` | Test both directions at once
`iperf3 -c <SERVER> -t 30` | Test for 30 seconds
`iperf3 -c <SERVER> -P 4` | Four parallel streams
`iperf3 -c <SERVER> -p 5202` | Non-default port (use `-p` on the server too)
`iperf3 -c <SERVER> -O 3` | Omit the first 3 seconds (TCP slow start)
`iperf3 -c <SERVER> -J` | JSON output

## UDP
COMMAND | DESCRIPTION
---|---
`iperf3 -c <SERVER> -u -b 100M` | UDP at 100 Mbit/s; the report shows jitter and loss
`iperf3 -c <SERVER> -u -b 0` | UDP, unlimited bandwidth
`iperf3 -c <SERVER> -u -b 100M -l 1200` | Set datagram size to test fragmentation and MTU

## Tuning
COMMAND | DESCRIPTION
---|---
`iperf3 -c <SERVER> -w 4M` | Socket buffer (window) size
`iperf3 -c <SERVER> -M 1400` | TCP maximum segment size
`iperf3 -c <SERVER> -C bbr` | Congestion control algorithm (Linux)
`iperf3 -c <SERVER> -4` / `iperf3 -c <SERVER> -6` | Force IPv4 or IPv6
`iperf3 -c <SERVER> -B <LOCAL_IP>` | Bind to a local address or interface address
`iperf3 -c <SERVER> -i 5` | Report every 5 seconds

## Containers
A container on the default Docker bridge adds NAT overhead. To test the host's own network, run the test from the host or in a container with `--network host`. The `iperf3` package is in the standard Debian and Ubuntu repositories (`sudo apt install iperf3`).

## Reading Results
FIELD | MEANING
---|---
`Bitrate` | Throughput over the interval
`Retr` | TCP retransmits; steady growth points to loss or a bad link
`Cwnd` | Congestion window; a small, stuck value points to loss
`Jitter` / `Lost/Total` | UDP delay variation and loss
`sender` / `receiver` summary | Compare both; large gaps mean loss in transit

## Troubleshooting
SYMPTOM | FIX
---|---
`Connection refused` | Server not running, or a firewall blocks TCP 5201 (`ss -tln`)
Gigabit link tops out near 100 Mbit/s | Check cable and negotiated speed with [ethtool](../linux/ethtool.md)
One stream slow, parallel streams fast | Single-flow limit (window size, CPU); use `-P` or `-w`
Fast one way only | Test with `-R`; check duplex, asymmetric routing or QoS
VPN much slower than the LAN | Try UDP; check MTU and the VPN CPU limit; see [VPN](../networking/vpn.md)

## See Also
- [ethtool](../linux/ethtool.md)
- [ip and ss](../linux/ip-and-ss.md)
- [TCP vs UDP](../networking/tcp-vs-udp.md)
- [Network Troubleshooting](../recipes/network-troubleshooting.md)
- [Linux Performance Troubleshooting](../linux/performance-troubleshooting.md)

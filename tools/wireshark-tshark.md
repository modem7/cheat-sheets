# Wireshark and tshark
Wireshark is a graphical packet analyser and `tshark` is its command-line twin. Capture with [tcpdump](tcpdump.md) on a server, then open the `.pcap` in Wireshark to follow streams, or use `tshark` to filter and extract fields in scripts.

Documentation: [Wireshark user guide](https://www.wireshark.org/docs/wsug_html_chunked/) · [tshark(1)](https://www.wireshark.org/docs/man-pages/tshark.html) · [Display filter reference](https://www.wireshark.org/docs/dfref/)
Project: [Wireshark](https://www.wireshark.org/)

> **Verification:** `tshark` options were checked against the man page in Ubuntu 24.04. Display filter field names follow the display filter reference. Wireshark GUI menu paths are from the user guide and were not run here.

## Capture Filters and Display Filters
Capture filters (BPF, set before capturing, same syntax as tcpdump) drop packets early. Display filters (Wireshark syntax) hide packets after capture and are far more expressive. The two syntaxes differ.

DISPLAY FILTER | SHOWS
---|---
`ip.addr == 192.0.2.10` | Traffic to or from a host
`ip.src == 192.0.2.10` / `ip.dst == 192.0.2.10` | One direction
`tcp.port == 443` | A TCP port either side
`udp.port == 53` | A UDP port
`dns` / `http` / `tls` / `dhcp` / `arp` / `icmp` | One protocol
`dns.qry.name == "example.com"` | DNS queries for a name
`tls.handshake.type == 1` | TLS Client Hello
`tls.handshake.extensions_server_name == "example.com"` | TLS SNI
`http.request.method == "POST"` | HTTP requests by method
`tcp.flags.syn == 1 && tcp.flags.ack == 0` | New connection attempts
`tcp.analysis.retransmission` | Retransmitted segments
`tcp.analysis.flags` | Any TCP problem flagged by analysis
`vlan.id == 20` | A VLAN
`eth.addr == 00:00:5e:00:53:01` | A MAC address
`!(arp or icmp)` | Exclude protocols
`frame contains "needle"` | Packets containing a string

Combine with `&&`, `||` and `!`.

## tshark Capture
COMMAND | DESCRIPTION
---|---
`tshark -D` | List interfaces
`sudo tshark -i <IF>` | Capture and print on an interface
`sudo tshark -i <IF> -f 'port 53'` | With a capture filter
`sudo tshark -i <IF> -c 100 -w capture.pcapng` | Save 100 packets to a file
`sudo tshark -i <IF> -a duration:60 -w capture.pcapng` | Stop after 60 seconds
`sudo tshark -i <IF> -b filesize:102400 -b files:5 -w capture.pcapng` | Ring buffer: 100 MB files, keep 5

## tshark Read and Extract
COMMAND | DESCRIPTION
---|---
`tshark -r capture.pcap` | Read a file
`tshark -r capture.pcap -Y 'dns'` | Apply a display filter (`-Y`)
`tshark -r capture.pcap -Y 'http.request' -T fields -e ip.src -e http.host -e http.request.uri` | Print chosen fields
`tshark -r capture.pcap -T fields -e dns.qry.name -Y 'dns.flags.response == 0'` | List queried DNS names
`tshark -r capture.pcap -q -z conv,tcp` | TCP conversation statistics
`tshark -r capture.pcap -q -z io,stat,1` | Packets and bytes per second
`tshark -r capture.pcap -q -z endpoints,ip` | Traffic per IP address
`tshark -r capture.pcap -q -z follow,tcp,ascii,0` | Reassemble TCP stream 0
`tshark -r capture.pcap -T json` | JSON output

## Decrypt TLS in Your Own Traffic
Browsers and many libraries write session keys when `SSLKEYLOGFILE` is set. Wireshark can use that file to decrypt your own captured TLS.

```bash
export SSLKEYLOGFILE="$HOME/tls-keys.log"
# start the client from this shell, capture, then:
tshark -r capture.pcap -o tls.keylog_file:"$HOME/tls-keys.log" -Y http
```

In the GUI: Edit, Preferences, Protocols, TLS, set the (Pre)-Master-Secret log filename. Treat the key log as a secret.

## Wireshark GUI Tips
ACTION | HOW
---|---
Follow one conversation | Right-click a packet, Follow, TCP Stream
Statistics overview | Statistics, Conversations / Protocol Hierarchy / IO Graphs
Find slow responses | Display filter `tcp.analysis.ack_rtt > 0.2`
Name resolution of IPs | View, Name Resolution
Capture from a remote host | `ssh HOST 'sudo tcpdump -U -s0 -w - not port 22' \| wireshark -k -i -`

## See Also
- [tcpdump](tcpdump.md)
- [Network Troubleshooting](../recipes/network-troubleshooting.md)
- [TLS Handshake](../networking/tls-handshake.md)
- [DNS Troubleshooting](../recipes/dns-troubleshooting.md)

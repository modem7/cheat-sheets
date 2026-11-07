# socat and netcat
`nc` (netcat) opens simple TCP or UDP connections and listeners; `socat` relays data between almost any two endpoints (TCP, UDP, UNIX sockets, files, TLS, processes). Use them for port checks, quick transfers and testing services. For port scanning see [NMap](../tools/nmap.md).

Project: [socat](http://www.dest-unreach.org/socat/)
Documentation: `man nc`, `man socat`

> **Verification:** options come from the OpenBSD netcat (`netcat-openbsd`) and socat man pages and `--help` output on Ubuntu 24.04. The `nc -z`, listener, relay, UNIX socket and `EXEC` examples were run against `127.0.0.1` in a throwaway container. Netcat variants differ (OpenBSD, Nmap `ncat`, traditional): check `nc -h` on your system. Only test hosts you are allowed to probe.

See also: [NMap](../tools/nmap.md) · [curl](../tools/curl.md) · [Ports and Protocols](ports-and-protocols.md)

---
## netcat (OpenBSD)
COMMAND | DESCRIPTION
---|---
`nc -zv <HOST> <PORT>` | Check whether a TCP port is open
`nc -zv <HOST> <START>-<END>` | Scan a range of TCP ports
`nc -zvu <HOST> <PORT>` | UDP probe (results are unreliable)
`nc -w <SECONDS> <HOST> <PORT>` | Connect with a timeout
`nc <HOST> <PORT>` | Open an interactive connection
`nc -l <PORT>` | Listen on a TCP port (accepts one connection, then exits)
`nc -lk <PORT>` | Keep listening for further connections
`nc -lu <PORT>` | Listen on UDP
`nc -N <HOST> <PORT> < FILE` | Send a file and shut down the socket at end of input
`nc -l <PORT> > FILE` | Receive a file
`nc -U <SOCKET_PATH>` | Connect to a UNIX domain socket
`nc -x <PROXY>:<PORT> -X 5 <HOST> <PORT>` | Connect via a SOCKS5 proxy
`printf 'GET / HTTP/1.0\r\n\r\n' \| nc <HOST> 80` | Speak a protocol by hand

A listener accepts a single connection: probing it with `nc -z` uses that connection up.

---
## socat
Syntax: `socat [OPTIONS] ADDRESS1 ADDRESS2`. Data flows both ways between the two addresses.

COMMAND | DESCRIPTION
---|---
`socat - TCP:<HOST>:<PORT>` | Connect stdin/stdout to a TCP port (like `nc`)
`socat TCP-LISTEN:<PORT>,reuseaddr,fork -` | Listener that handles each connection in a child process
`socat TCP-LISTEN:<PORT>,reuseaddr,fork TCP:<HOST>:<PORT>` | TCP port forward (simple relay)
`socat UNIX-LISTEN:<PATH>,fork TCP:<HOST>:<PORT>` | Expose a TCP service as a UNIX socket
`socat - UNIX-CONNECT:<PATH>` | Talk to a UNIX socket
`socat TCP-LISTEN:<PORT>,reuseaddr,fork EXEC:'<COMMAND>'` | Run a command per connection
`socat -u - TCP:<HOST>:<PORT>` | One-way (unidirectional) transfer from stdin
`socat -d -d <ADDR1> <ADDR2>` | Print warnings and notices while running
`socat -V` | Version and compiled-in features
`socat -h` | Help with address types

---
## Common Tasks
Forward a local port to a remote service, for example to reach a service from another network interface:

```bash
socat TCP-LISTEN:8080,reuseaddr,fork TCP:SERVER_NAME:80
```

Quick file transfer on a trusted network:

```bash
# receiver
nc -l 9000 > received.bin
# sender
nc -N RECEIVER_HOST 9000 < file.bin
```

Test a TLS service (needs socat built with OpenSSL):

```bash
socat - OPENSSL:SERVER_NAME:443,verify=1
```

---
## Troubleshooting
SYMPTOM | FIX
---|---
`Address already in use` | Another process holds the port (`ss -tlnp`); add `reuseaddr` to socat listeners
Listener exits after one connection | Normal for `nc -l`; use `-k` or socat with `fork`
Transfer hangs at the end | Use `-N` (OpenBSD) or `-q <SECONDS>` so `nc` closes after EOF
Options differ between machines | Netcat has several implementations; check `nc -h` and `man nc`
UDP "success" means nothing | UDP is connectionless; a probe only shows an ICMP refusal when closed

---
## See Also
- [NMap](../tools/nmap.md)
- [curl](../tools/curl.md)
- [OpenSSH Cheat-Sheet](../tools/openssh.md)
- [Ports and Protocols](ports-and-protocols.md)

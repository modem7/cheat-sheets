# NMap
Nmap ("Network Mapper") is an open source tool for network discovery and security auditing.

Project Homepage: [nmap.org](https://nmap.org)
Documentation: [Nmap Reference Guide](https://nmap.org/book/man.html)

> Only scan networks and hosts you own or have written permission to test.

## Host Discovery
COMMAND | DESCRIPTION
---|---
`nmap -sn 192.168.1.0/24` | Ping sweep, no port scan
`nmap -sn -PR 192.168.1.0/24` | ARP discovery on the local LAN (most reliable)
`nmap -Pn <HOST>` | Skip discovery, treat host as up (hosts that block ping)
`nmap -iL hosts.txt` | Scan targets from a file
`nmap 192.168.1.0/24 --exclude 192.168.1.1` | Exclude hosts

## Port Scanning
COMMAND | DESCRIPTION
---|---
`nmap <HOST>` | Scan the 1000 most common TCP ports
`nmap -p- <HOST>` | Scan all 65535 TCP ports
`nmap -p 22,80,443 <HOST>` | Scan specific ports
`nmap -p 1-1024 <HOST>` | Scan a range
`nmap --top-ports 100 <HOST>` | Scan the 100 most common ports
`nmap -sS <HOST>` | TCP SYN scan (default as root)
`nmap -sT <HOST>` | TCP connect scan (no root needed)
`nmap -sU --top-ports 20 <HOST>` | UDP scan of common ports (slow)
`nmap -F <HOST>` | Fast scan (100 ports)

## Service, OS and Script Detection
COMMAND | DESCRIPTION
---|---
`nmap -sV <HOST>` | Detect service versions
`nmap -O <HOST>` | OS detection (needs root)
`nmap -A <HOST>` | Aggressive: OS, versions, scripts, traceroute
`nmap -sC <HOST>` | Run the default NSE scripts
`nmap --script vuln <HOST>` | Run vulnerability scripts
`nmap --script ssl-enum-ciphers -p 443 <HOST>` | List supported TLS ciphers
`nmap --script http-title -p 80,443 <HOST>` | Grab web page titles
`nmap --script-help <SCRIPT>` | Help for a script

## Timing and Output
COMMAND | DESCRIPTION
---|---
`nmap -T4 <HOST>` | Faster timing (0 paranoid to 5 insane; 3 is default)
`nmap --min-rate 1000 <HOST>` | Send at least 1000 packets per second
`nmap -v <HOST>` | Verbose
`nmap -oN scan.txt <HOST>` | Save normal output
`nmap -oX scan.xml <HOST>` | Save XML output
`nmap -oA scan <HOST>` | Save all formats
`nmap --open <HOST>` | Show only open ports
`nmap --reason <HOST>` | Show why a port is in its state

## Useful Combinations
COMMAND | DESCRIPTION
---|---
`sudo nmap -sS -p- --min-rate 1000 -T4 <HOST>` | Quick full TCP port sweep
`sudo nmap -sV -sC -p <PORTS> <HOST>` | Deep scan of ports found open
`sudo nmap -sn 192.168.1.0/24 -oG - \| awk '/Up$/{print $2}'` | List live IPs on a subnet

See also: [socat and netcat](../networking/socat-and-netcat.md)

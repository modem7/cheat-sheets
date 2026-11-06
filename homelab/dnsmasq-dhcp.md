# dnsmasq DHCP and DNS
dnsmasq is a small DNS forwarder and DHCP server (with TFTP and router advertisement) in one process. Pi-hole's FTL is built on it, OPNsense can use it, and it is a common choice for a lab DHCP server. It hands out leases, optionally registers lease hostnames in DNS, serves local records, and can **relay** DHCP requests from a VLAN to a DHCP server elsewhere.

Documentation: [dnsmasq man page](https://thekelleys.org.uk/dnsmasq/docs/dnsmasq-man.html) · [dnsmasq docs index](https://thekelleys.org.uk/dnsmasq/doc.html)

> **Verification:** option syntax for `dhcp-range`, `dhcp-host`, `dhcp-option`, `dhcp-relay`, `dhcp-proxy`, `address`, `host-record`, `cname`, `server`, `local`, `domain-needed`, `bogus-priv` and `--test` was checked against the man page. **Not verified:** the dnsmasq version that introduced `dhcp-relay`, how `giaddr` is set in every case, the Debian/Ubuntu service details, and the `nmap`/`dhcping` test commands. DHCP option numbers (3, 6, 15, 42) are from memory. No command was executed.

See also: [[homelab]] · [[vlans]] · [[pihole]] · [[adguard-home]] · [[unbound]] · [[proxmox-networking]] · [[wake-on-lan]] · [[ufw]] · [[docker-compose]]

---
## Install and Run
```bash
sudo apt install dnsmasq
sudo dnsmasq --test                       # syntax check of /etc/dnsmasq.conf and conf-dir
sudo systemctl enable --now dnsmasq
journalctl -u dnsmasq -f
```
Config lives in `/etc/dnsmasq.conf` and `/etc/dnsmasq.d/*.conf` (when `conf-dir=/etc/dnsmasq.d` is enabled; Debian does this by default). Prefer small files in the directory.

On Ubuntu `systemd-resolved` holds port 53 on `127.0.0.53`. Either use `bind-interfaces` with a specific `listen-address`, or disable the stub (`DNSStubListener=no`).

COMMAND | DESCRIPTION
---|---
`dnsmasq --test` | Check config syntax
`dnsmasq --version` | Version and compiled-in features (look for `DHCP`, `DHCPv6`)
`sudo kill -USR1 $(pidof dnsmasq)` | Dump stats and cache info to the log
`sudo kill -HUP $(pidof dnsmasq)` | Re-read hosts files and clear cache (not the main config)
`sudo systemctl restart dnsmasq` | Apply config changes
`cat /var/lib/misc/dnsmasq.leases` | Current leases (Debian path; `expiry mac ip hostname clientid`)

---
## Base Configuration
`/etc/dnsmasq.d/10-base.conf`:
```ini
# Listen only where intended
interface=eth0
bind-interfaces
listen-address=127.0.0.1,192.168.20.2

# DNS hygiene
domain-needed                 # do not forward names without a dot
bogus-priv                    # do not forward private-range reverse lookups
no-resolv                     # ignore /etc/resolv.conf
server=127.0.0.1#5335         # upstream, e.g. Unbound; see unbound sheet
cache-size=1000

# Local domain
domain=home.example.com
local=/home.example.com/      # answer this domain only from local data
expand-hosts                  # add the domain to names in /etc/hosts
```
Use `listen-address` together with `127.0.0.1` explicitly if you set it, or local tools on the host cannot query it.

---
## DHCP Ranges and Options
```ini
dhcp-authoritative            # reply to requests for unknown leases (single server on the subnet)
dhcp-leasefile=/var/lib/misc/dnsmasq.leases
log-dhcp                      # verbose DHCP logging while testing

dhcp-range=192.168.20.100,192.168.20.200,255.255.255.0,12h

dhcp-option=option:router,192.168.20.1
dhcp-option=option:dns-server,192.168.20.2
dhcp-option=option:domain-name,home.example.com
dhcp-option=option:ntp-server,192.168.20.2
```
FORM | MEANING
---|---
`dhcp-range=<START>,<END>[,<NETMASK>][,<LEASE>]` | Dynamic range; lease like `12h`, `1d`, `infinite`
`dhcp-range=192.168.20.0,static` | Only hand out addresses from `dhcp-host` entries
`dhcp-range=tag:iot,192.168.30.50,192.168.30.150,12h` | Tag a range
`dhcp-range=set:vlan30,192.168.30.50,192.168.30.150,12h` | Set a tag used by `dhcp-option`
`dhcp-range=::,constructor:eth0,ra-only` | IPv6 router advertisements only (SLAAC, no DHCPv6)
`dhcp-option=3,<IP>` or `option:router,<IP>` | Gateway (option 3)
`dhcp-option=6,<IP>[,<IP>]` or `option:dns-server,...` | DNS servers (option 6)
`dhcp-option=15,<DOMAIN>` or `option:domain-name,...` | Domain name (option 15)
`dhcp-option=42,<IP>` or `option:ntp-server,...` | NTP server (option 42)
`dhcp-option=tag:vlan30,option:router,192.168.30.1` | Per-network option using a tag
`dhcp-option=option:router` | Empty value removes the default gateway option
`dhcp-option=6,0.0.0.0` | `0.0.0.0` means "this dnsmasq host"

dnsmasq decides which `dhcp-range` applies by the interface the request arrived on (and, via relays, the relay address `giaddr`), so each subnet needs its own range line and the host needs an address in it (or a relay in front).

Multiple VLANs on one server (the box has interfaces `eth0.20`, `eth0.30`, see [[vlans]]):
```ini
interface=eth0.20
interface=eth0.30
dhcp-range=set:servers,192.168.20.100,192.168.20.200,12h
dhcp-range=set:iot,192.168.30.100,192.168.30.200,12h
dhcp-option=tag:servers,option:router,192.168.20.1
dhcp-option=tag:iot,option:router,192.168.30.1
dhcp-option=tag:iot,option:dns-server,192.168.20.2
```

---
## Static Leases
```ini
dhcp-host=aa:bb:cc:dd:ee:01,192.168.20.10,nas,infinite
dhcp-host=aa:bb:cc:dd:ee:02,192.168.20.11,proxy
dhcp-host=aa:bb:cc:dd:ee:03,set:iot,192.168.30.20,camera1
dhcp-hostsfile=/etc/dnsmasq.d/hosts.dhcp                # same format, reloaded on SIGHUP
```
FORM | MEANING
---|---
`dhcp-host=<MAC>,<IP>,<NAME>` | Reserve an IP and set a hostname
`dhcp-host=<MAC>,<MAC2>,<IP>` | Same host with Ethernet and Wi-Fi (only one is active at a time)
`dhcp-host=id:<CLIENTID>,<IP>` | Match on DHCP client identifier
`dhcp-host=<MAC>,ignore` | Never lease to this device
`dhcp-host=<NAME>,<IP>` | Match on name the client sends

The reserved IP should be **outside** the dynamic range, or at least not already leased. Lease hostnames are added to DNS, so `nas` and `nas.home.example.com` resolve.

---
## DNS Records
```ini
address=/blocked.example.com/0.0.0.0            # answer for the domain and all subdomains
address=/blocked.example.com/                   # NXDOMAIN for it
address=/home.example.com/192.168.20.11         # wildcard: domain and every subdomain
host-record=nas.home.example.com,192.168.20.10
host-record=nas.home.example.com,192.168.20.10,fd00:20::10     # also AAAA
cname=grafana.home.example.com,proxy.home.example.com          # target must be known to dnsmasq
server=/corp.example.com/192.168.50.2           # forward one domain
server=/20.168.192.in-addr.arpa/192.168.20.1    # reverse zone forward
ptr-record=10.20.168.192.in-addr.arpa,nas.home.example.com
rebind-domain-ok=/home.example.com/             # allow private answers for this domain
```
`address=` and `server=` matches apply to subdomains too. A `cname=` target must be something dnsmasq itself can answer (a DHCP lease, `host-record`, or `/etc/hosts` entry); a CNAME to an external name that dnsmasq only forwards will not work. See [[dns-record-types]] and, for split-horizon, [[reverse-proxy-patterns]].

---
## dnsmasq as a DHCP Relay
A relay forwards DHCP broadcasts from a segment with no DHCP server (for example a VLAN) to a real server on another network, by unicast, and sets the `giaddr` field to the relay's address so the server can choose the right subnet.

```ini
# /etc/dnsmasq.d/relay.conf on the host that has an address in the client VLAN
dhcp-relay=192.168.30.1,192.168.20.2
```
`dhcp-relay=<LOCAL_ADDRESS>[,<SERVER_ADDRESS>[#<PORT>]][,<INTERFACE>]`

PART | MEANING
---|---
`<LOCAL_ADDRESS>` | The relay's own IPv4 (or IPv6) address on the client side. Becomes `giaddr`, so the server must have a scope containing it and a route back to it
`<SERVER_ADDRESS>` | The real DHCP server. Must be an **IP literal**, not a hostname. Optional `#port`
`<INTERFACE>` | Limit the relay to requests arriving on this interface
Repeat the option | Relay to several servers: `dhcp-relay=...,192.168.20.2` and `dhcp-relay=...,192.168.20.3`
Server omitted | dnsmasq broadcasts (IPv4) or multicasts (IPv6); needs a non-wildcard `interface`

Rules and limits:
- IPv4 and IPv6 are both supported; an IPv4 request cannot be relayed to an IPv6 server or the reverse.
- A server and a relay on the **same interface** is unsupported (the relay wins). Do not define a `dhcp-range` for the subnet you relay.
- The DHCP server needs a scope for the relay subnet (for example `192.168.30.0/24` with `giaddr` `192.168.30.1`) and must be able to reach `giaddr` for replies. Add the route or keep the relay on a routed path.
- The relay host's firewall must allow UDP 67 and 68 on the client side ([[ufw]]).
- `dhcp-proxy` (IPv4 only) makes dnsmasq a full DHCP proxy: it rewrites the server identifier so clients talk back to the relay, for use when the relay cannot rely on RFC 5107 server-identifier-override support. Read the man page entry before using it.
- Often the simplest alternative is a router DHCP relay/"DHCP helper" on the VLAN gateway (OPNsense: Services -> DHCPv4 -> Relay; Cisco `ip helper-address`; UniFi: DHCP Relay setting on the network). Use dnsmasq only when the gateway cannot relay.

Server on the other end (also dnsmasq), a scope for the relayed VLAN:
```ini
interface=eth0
dhcp-range=set:iot,192.168.30.100,192.168.30.200,255.255.255.0,12h
dhcp-option=tag:iot,option:router,192.168.30.1
```
`dhcp-range` addresses are matched against the relay's `giaddr`, so one server can serve many relayed subnets by listing one range each.

Check what arrives:
```bash
sudo tcpdump -nei any 'udp port 67 or udp port 68'
```
Look for the request leaving the client side as broadcast and a unicast copy with `giaddr` set going to the server.

---
## Test and Debug
COMMAND | DESCRIPTION
---|---
`sudo dnsmasq --test` | Validate config
`sudo dnsmasq --no-daemon --log-dhcp --log-queries` | Run in foreground with verbose logging (stop the service first)
`dig +short nas.home.example.com @192.168.20.2` | Query local DNS
`sudo nmap --script broadcast-dhcp-discover -e <IFACE>` | Discover DHCP servers on a segment (finds rogue servers)
`sudo dhclient -v -r <IFACE> && sudo dhclient -v <IFACE>` | Release and renew a lease on a test client
`resolvectl status` | What a systemd-resolved client believes

---
## Troubleshooting
SYMPTOM | CHECK
---|---
`dnsmasq: failed to create listening socket: Address already in use` | Another resolver on port 53 (`ss -lntup 'sport = :53'`): systemd-resolved stub, Pi-hole, Unbound
No lease on the client | Is dnsmasq listening on that interface (`interface=`, `log-dhcp`)? Is the VLAN trunked? Does `dhcp-range` match the interface subnet?
`no address range available for DHCP request via eth0` | The server's interface has no address in any `dhcp-range`; add an address, a range, or use a relay
Two DHCP servers | Rogue router: scan with nmap; disable one
Relay: client gets nothing | Server has no scope for `giaddr`'s subnet; no route back to `giaddr`; relay host firewall; check with tcpdump on both sides
Static lease ignored | MAC typed in wrong case or with dashes, IP inside a dynamic lease already held; remove the old lease entry and restart
Hostname not resolving | Lease name missing or `domain` / `expand-hosts` missing; name contains disallowed characters
`dnsmasq: bad option`/start failure | `dnsmasq --test` reports the file and line
Changes not applied | `systemctl restart dnsmasq`; SIGHUP does not re-read the main config

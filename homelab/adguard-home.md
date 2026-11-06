# AdGuard Home
AdGuard Home is a network-wide DNS filter and resolver with a built-in web UI, per-client settings, DNS rewrites, optional DHCP, and native encrypted DNS in both directions: it can use DoH/DoT/DoQ **upstreams** and serve DoH/DoT/DoQ to your own clients. It ships as a single Go binary, which makes it a simple alternative to [[pihole]].

Documentation: [AdGuard Home on GitHub](https://github.com/AdguardTeam/AdGuardHome) · [Knowledge base](https://adguard-dns.io/kb/adguard-home/getting-started/) · [Configuration wiki (marked outdated)](https://github.com/AdguardTeam/AdGuardHome/wiki/Configuration) · [Docker image](https://hub.docker.com/r/adguard/adguardhome)

> **Verification:** the Docker volumes and ports, CLI flags (`-c`, `-w`, `-s`, `--check-config`, `--web-addr`), the YAML keys `dns.upstream_dns`, `dns.bootstrap_dns`, `filtering.rewrites`, `clients.persistent`, `tls.port_https/port_dns_over_tls/port_dns_over_quic`, and the upstream syntax were checked against the docs. **Not verified:** exact default encrypted-DNS ports for your version (the DoQ default changed from 754 to 853 in v0.108), `AdGuardHome.yaml` key layout in the latest release, and the `/control` API calls. The upstream wiki says its own pages are outdated, so confirm against the Knowledge Base. No command was executed.

See also: [[homelab]] · [[pihole]] · [[unbound]] · [[dnsmasq-dhcp]] · [[reverse-proxy-patterns]] · [[dns-over-https]] · [[dns-over-tls]] · [[dns-encryption]] · [[docker-compose]] · [[docker-networking]]

---
## Docker Compose
```yaml
services:
  adguardhome:
    image: adguard/adguardhome:latest
    container_name: adguardhome
    restart: unless-stopped
    ports:
      - "53:53/tcp"
      - "53:53/udp"
      - "3000:3000/tcp"          # first-run setup wizard; remove after setup
      - "8080:80/tcp"            # web UI after setup (whatever port you chose in the wizard)
      # - "443:443/tcp"          # DoH / HTTPS UI
      # - "443:443/udp"          # DoH over HTTP/3
      # - "853:853/tcp"          # DoT
      # - "853:853/udp"          # DoQ
      # - "67:67/udp"            # DHCP (needs host networking)
    volumes:
      - ./work:/opt/adguardhome/work
      - ./conf:/opt/adguardhome/conf
```
```bash
docker compose up -d
# browse to http://<HOST>:3000 and finish the wizard
```
Use `network_mode: host` instead of `ports:` if you want the built-in DHCP server or real client IPs in the logs (on a bridge network all queries can appear to come from the Docker gateway).

---
## Bare Metal Install
```bash
# Download a release from the GitHub releases page, then:
tar xf AdGuardHome_linux_amd64.tar.gz && cd AdGuardHome
sudo ./AdGuardHome -s install           # install and start as a service
```
FLAG | DESCRIPTION
---|---
`-s install` / `uninstall` | Add or remove the system service
`-s start` / `stop` / `restart` / `reload` / `status` | Control the service
`-c <FILE>` | Config file (`AdGuardHome.yaml`)
`-w <DIR>` | Working directory (data, logs, filters)
`--check-config` | Validate the config and exit
`--web-addr <IP:PORT>` | Override the web UI listen address
`--no-check-update` | Skip the update check

Setup wizard listens on port 3000; after setup it uses the port you picked (80 by default). Update from the UI (**Dashboard**), or replace the binary and restart.

---
## Upstream DNS
Set under **Settings -> DNS settings**, or `dns.upstream_dns` in `AdGuardHome.yaml`. One per line.

SYNTAX | MEANING
---|---
`1.1.1.1` | Plain DNS
`tcp://1.1.1.1` | Plain DNS over TCP
`tls://one.one.one.one` | DNS-over-TLS (port 853)
`https://dns.cloudflare.com/dns-query` | DNS-over-HTTPS
`h3://dns.google/dns-query` | DoH forced over HTTP/3
`quic://dns.adguard-dns.com` | DNS-over-QUIC
`sdns://<STAMP>` | DNSCrypt or DoH/DoT stamp
`192.168.20.3:5335` | Local [[unbound]] on a custom port
`[/home.example.com/]192.168.20.1` | Domain-specific upstream (conditional forwarding)
`[/lab.example.com/]#` | Use the default upstreams for this domain, as an exception
`[//]192.168.20.1` | Upstream for unqualified names only (no dot)

Related settings:
- **Bootstrap DNS** (`dns.bootstrap_dns`): plain IPs used to resolve the hostnames of DoH/DoT upstreams. Needed whenever an upstream is given by name (`tls://...`).
- **Upstream mode**: load balancing (default), parallel requests (fastest answer), or fastest IP address.
- **Private reverse DNS** (`dns.local_ptr_upstreams`): where to send PTR lookups for private addresses (your router) so client names show up.
- **DNSSEC**: enable in DNS settings only if your upstream does not validate; with [[unbound]] you can leave it off here.

```yaml
dns:
  bind_hosts: [0.0.0.0]
  port: 53
  upstream_dns:
    - tls://one.one.one.one
    - tls://dns.quad9.net
    - '[/home.example.com/]192.168.20.1'
  bootstrap_dns:
    - 1.1.1.1
    - 9.9.9.9
```
Stop the service before hand-editing the file, then start it again, or it may overwrite your changes. Run `AdGuardHome --check-config -c <FILE>` before restarting.

---
## DNS Rewrites and Filtering
**Filters -> DNS rewrites** (`filtering.rewrites` in the YAML). Use this for local names and split-horizon DNS ([[reverse-proxy-patterns]]).

DOMAIN | ANSWER | RESULT
---|---|---
`nas.home.example.com` | `192.168.20.10` | A record
`*.home.example.com` | `192.168.20.11` | Wildcard A: every subdomain goes to the proxy
`grafana.home.example.com` | `proxy.home.example.com` | CNAME (answer is a domain)
`old.example.com` | `A` | Block (an answer of `A` means the A/AAAA types only get an empty result)

```yaml
filtering:
  rewrites:
    - domain: '*.home.example.com'
      answer: 192.168.20.11
      enabled: true        # the enabled field exists in newer releases
```
Other filter features:

FEATURE | WHERE
---|---
Blocklists | **Filters -> DNS blocklists**: add a list URL, or choose from the built-in catalogue
Allowlists | **Filters -> DNS allowlists**
Custom rules | **Filters -> Custom filtering rules**, AdBlock syntax
Block a domain and subdomains | `\|\|ads.example.com^`
Allow (exception) | `@@\|\|good.example.com^`
Block only for a client | `\|\|example.com^$client='192.168.30.5'`
Response for blocked | **Settings -> DNS settings -> Blocking mode** (default, NXDOMAIN, null IP, custom IP)
Query log | **Query Log** page; retention in **Settings -> General**
Parental / safe search | **Settings -> General settings**, or per client

---
## Encryption: serving DoH, DoT, DoQ
**Settings -> Encryption settings**. Needs a certificate whose name matches the server name clients use. A wildcard certificate obtained by DNS-01 ([[reverse-proxy-patterns]]) works well.

```yaml
tls:
  enabled: true
  server_name: dns.home.example.com
  force_https: false
  port_https: 443
  port_dns_over_tls: 853
  port_dns_over_quic: 853
  certificate_path: /opt/adguardhome/conf/certs/fullchain.pem
  private_key_path: /opt/adguardhome/conf/certs/privkey.pem
```
PROTOCOL | PORT | CLIENT SETTING
---|---|---
DoH | TCP 443 (and UDP 443 for HTTP/3) | `https://dns.home.example.com/dns-query`
DoT | TCP 853 | Private DNS hostname `dns.home.example.com` (Android) or `tls://...`
DoQ | UDP 853 | `quic://dns.home.example.com`
Per-client DoH path | `/dns-query/<CLIENT_ID>` | Identifies the client in logs and rules
Per-client DoT name | `<CLIENT_ID>.dns.home.example.com` | Same, for DoT/DoQ (needs a wildcard certificate)

Remote use: don't expose 53; expose 853/443 only if you need it, or reach AdGuard through [[tailscale]] or [[wireguard]]. Check `ports` for your version, as defaults changed over time.

---
## Clients
**Settings -> Client settings** (`clients.persistent` in YAML): give a device a name and apply its own filters, upstreams, blocked services and safe-search.

IDENTIFIER | NOTE
---|---
IP address / CIDR | Simplest; needs stable IPs ([[dnsmasq-dhcp]] static leases)
MAC address | Needs AdGuard Home to be the DHCP server, or run on a host that sees the MAC
ClientID | Works through DoH/DoT/DoQ even behind NAT or changing IPs
Runtime clients | Detected from the query log and ARP/rDNS; edit to make them persistent

Clients not behind the same network (a VPN) look like one IP; use ClientIDs. Tags (`user_admin`, `device_phone`, ...) let one rule apply to many clients.

---
## DHCP
**Settings -> DHCP settings** (requires the container to see broadcasts: host network). Set gateway, subnet mask, range and lease time, add static leases. Only one DHCP server per network, so turn off the router's. For a feature-rich or relayed DHCP setup see [[dnsmasq-dhcp]] and [[vlans]].

---
## API
The web UI uses a REST API at `/control`, protected by the same login. Examples (HTTP Basic auth):
```bash
curl -s -u <USER>:<PASS> http://adguard.home.example.com/control/status | jq
curl -s -u <USER>:<PASS> -X POST http://adguard.home.example.com/control/protection \
  -H 'Content-Type: application/json' -d '{"enabled":false,"duration":300000}'
```
`duration` is in milliseconds. Verify endpoint names against `openapi.yaml` in the project repository.

---
## Troubleshooting
SYMPTOM | CHECK
---|---
Cannot reach the wizard | Port 3000 mapped? Another service on 80? `docker logs adguardhome`
Port 53 already in use | `sudo ss -lntup 'sport = :53'`; on Ubuntu set `DNSStubListener=no` in `/etc/systemd/resolved.conf` and restart `systemd-resolved`
All clients show one IP | Bridge networking: use host networking, or ClientIDs
Upstream `tls://name` fails at start | No bootstrap DNS or it is unreachable; use IPs in `bootstrap_dns`
Config changes disappear | Edited while the service was running; stop it, edit, start it
Rewrite not working | Browser using its own DoH; the client got a different DNS from DHCP; cache: flush and test `dig +short <NAME> @<ADGUARD_IP>`
Local hostnames not shown in the query log | Set private reverse DNS upstream to your router, enable "Use private reverse DNS resolvers"
Certificate error on DoH/DoT | Name in `server_name` must match the certificate; key file readable by the container
Validate config | `AdGuardHome --check-config -c <FILE>`
Run a test | `dig doubleclick.net @<ADGUARD_IP>` (a blocked domain returns `0.0.0.0` with default mode)

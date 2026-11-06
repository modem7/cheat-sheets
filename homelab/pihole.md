# Pi-hole
Pi-hole is a network-wide DNS sinkhole: a DNS server (FTL, a fork of dnsmasq) that answers blocked domains from adlists (the "gravity" database) with a null address, and forwards everything else to upstream resolvers. It can also serve local DNS records and, optionally, DHCP. This sheet targets **Pi-hole v6**, with the main v5 differences noted where old guides will mislead you.

Documentation: [Pi-hole docs](https://docs.pi-hole.net/) · [`pihole` command](https://docs.pi-hole.net/main/pihole-command/) · [FTL config reference](https://docs.pi-hole.net/ftldns/configfile/) · [docker-pi-hole](https://github.com/pi-hole/docker-pi-hole) · [Unbound guide](https://docs.pi-hole.net/guides/dns/unbound/)

> **Verification:** Docker env var format, `pihole.toml` location, the `pihole` subcommand list, `dns.*` and `webserver.port` keys, listening modes and the Unbound upstream (`127.0.0.1#5335`) were checked against the docs above. **Not verified:** the `pihole-FTL --config` usage and the v5 file locations (from memory), `misc.dnsmasq_lines`, the REST API calls, the cloudflared example, and the DHCP/Docker host-mode notes. No command was executed.

See also: [Homelab](homelab.md) · [Unbound](unbound.md) · [AdGuard Home](adguard-home.md) · [dnsmasq DHCP and DNS](dnsmasq-dhcp.md) · [Reverse Proxy Patterns](reverse-proxy-patterns.md) · [DNS over TLS (DoT)](../networking/dns-over-tls.md) · [DNS over HTTPS (DoH)](../networking/dns-over-https.md) · [DNS Encryption](../networking/dns-encryption.md) · [Docker-Compose](../docker/docker-compose.md) · [Docker Networking](../docker/docker-networking.md) · [UFW (uncomplicated firewall)](../linux/ufw.md)

---
## Install
```bash
# Bare metal (Debian/Ubuntu/Raspberry Pi OS): read the script first
curl -sSL https://install.pi-hole.net -o pihole-install.sh
less pihole-install.sh
sudo bash pihole-install.sh
sudo pihole setpassword          # set the web UI / API password (v6)
```
Give the host a static IP (or a DHCP reservation, see [dnsmasq DHCP and DNS](dnsmasq-dhcp.md)) and point your router's DHCP DNS option, or each client, at it.

---
## Docker Compose
```yaml
services:
  pihole:
    image: pihole/pihole:latest
    container_name: pihole
    restart: unless-stopped
    ports:
      - "53:53/tcp"
      - "53:53/udp"
      - "8080:80/tcp"            # web UI over HTTP
      - "8443:443/tcp"           # web UI over HTTPS (self-signed)
      # - "67:67/udp"            # only if Pi-hole is the DHCP server
    environment:
      TZ: Europe/London
      FTLCONF_webserver_api_password: ${PIHOLE_PASSWORD}
      FTLCONF_dns_listeningMode: ALL           # needed on the default bridge network
      FTLCONF_dns_upstreams: 1.1.1.1;1.0.0.1   # semicolon separated list
    volumes:
      - ./etc-pihole:/etc/pihole
      # - ./etc-dnsmasq.d:/etc/dnsmasq.d       # only for custom dnsmasq files, see below
    cap_add:
      # - NET_ADMIN    # only for DHCP
      # - SYS_TIME     # only for the built-in NTP
      - SYS_NICE       # optional, lets FTL raise its priority
```
`.env`: `PIHOLE_PASSWORD=<STRONG_PASSWORD>`. Keep it out of git.

COMMAND | DESCRIPTION
---|---
`docker compose up -d` | Start
`docker exec pihole pihole status` | Run the CLI inside the container
`docker exec -it pihole pihole-FTL --config` | Dump every setting
`docker compose pull && docker compose up -d` | Update (config persists in `./etc-pihole`)
`docker logs -f pihole` | Follow logs

Rules for the container:
- Every setting can be set with `FTLCONF_<section>_<key>`, for example `dns.listeningMode` becomes `FTLCONF_dns_listeningMode`. Variables set this way are **read-only in the web UI**; remove the variable to edit in the UI again.
- On a bridge network use `listeningMode: ALL` and keep the DNS port exposure inside your LAN. `LOCAL` (the default) answers only requests that arrive from a directly connected subnet, which usually breaks bridge-mode NAT.
- Port 80/443 conflicts with a reverse proxy: remap as above, or put Pi-hole on a macvlan/host network ([Docker Networking](../docker/docker-networking.md)).
- DHCP needs the broadcast to reach the container: use `network_mode: host` or macvlan, plus `NET_ADMIN`.
- Running Pi-hole and Unbound in one compose project: see [Unbound](unbound.md).

---
## `pihole` CLI (v6)
COMMAND | DESCRIPTION
---|---
`pihole status` | Is DNS blocking enabled
`pihole enable` | Turn blocking on
`pihole disable` | Turn blocking off indefinitely
`pihole disable 5m` | Off for a period (`30s`, `5m`; plain number means seconds)
`pihole -g` | Update gravity (re-download adlists, rebuild the database)
`pihole -up` | Update Pi-hole (bare metal)
`pihole tail` | Live query log
`pihole -q <DOMAIN>` | Which lists block this domain
`pihole repair` | Re-run the installer's repair logic
`pihole setpassword [<PASSWORD>]` | Set the web/API password (prompts when omitted)
`pihole reloaddns` | Reload the DNS resolver config
`pihole reloadlists` | Reload gravity lists without a full gravity run
`pihole flush` | Flush the network table and logs
`pihole debug` | Generate a debug log (with an upload option)
`pihole -v` | Versions

Allow/deny lists in v6 are managed in the web UI (**Domains**) or by the API; the old `pihole -w`, `pihole -b` and `pihole --regex` helpers are deprecated or removed in v6. Check `pihole help` on your install for what is still present.

---
## Configuration: `pihole-FTL --config`
v6 stores settings in `/etc/pihole/pihole.toml`. Edit with the web UI (**Settings -> All settings**), by hand, or with the CLI. `setupVars.conf` is gone.

COMMAND | DESCRIPTION
---|---
`sudo pihole-FTL --config` | List all settings and values
`sudo pihole-FTL --config dns.upstreams` | Read one value
`sudo pihole-FTL --config dns.upstreams '["1.1.1.1","1.0.0.1"]'` | Set an array (JSON syntax, mind the quotes)
`sudo pihole-FTL --config dns.dnssec true` | Set a boolean
`sudo pihole-FTL --config webserver.port '80o,443os,[::]:80o,[::]:443os'` | Set a string
`sudo systemctl restart pihole-FTL` | Restart after hand-editing the TOML

Useful keys:

KEY | MEANING
---|---
`dns.upstreams` | Array of upstream resolvers, `IP` or `IP#port`. **If empty, non-local queries will not resolve.** Example `["127.0.0.1#5335"]` for Unbound
`dns.listeningMode` | `LOCAL` (default), `SINGLE`, `BIND`, `ALL`, `NONE`
`dns.interface` | Interface to listen on (used with `LOCAL`/`SINGLE`/`BIND`)
`dns.dnssec` | Validate DNSSEC in FTL (default `false`); not needed if your upstream (Unbound) validates
`dns.hosts` | Local DNS records, `"IP HOST [HOST...]"`
`dns.cnameRecords` | Local CNAMEs, `"alias,target[,TTL]"`
`dns.blocking.mode` | How blocked queries are answered (`NULL`, `IP`, `NXDOMAIN`, ...)
`dns.domain.name` / `dns.domain.local` | Local domain and whether it is answered locally
`dns.rateLimit.count` / `.interval` | Per-client query rate limit
`dns.revServers` | Conditional forwarding: `"true,192.168.1.0/24,192.168.1.1,lan"`
`webserver.port` | Listen addresses. Suffix `o` optional, `s` TLS, `r` redirect to HTTPS
`webserver.api.password` | API/UI password hash (use `pihole setpassword`)
`misc.etc_dnsmasq_d` | Read `/etc/dnsmasq.d/*.conf` (default off in v6)
`misc.dnsmasq_lines` | Raw dnsmasq config lines, array of strings
`dhcp.active`, `dhcp.start`, `dhcp.end`, `dhcp.router` | Built-in DHCP server

---
## Local DNS Records
**v6:** web UI **Settings -> Local DNS Records** (and **Local CNAME Records**), or the keys:
```bash
sudo pihole-FTL --config dns.hosts '["192.168.20.10 nas.home.example.com nas","192.168.20.11 proxy.home.example.com"]'
sudo pihole-FTL --config dns.cnameRecords '["grafana.home.example.com,proxy.home.example.com"]'
```
**v5 (for old guides):** `/etc/pihole/custom.list` with lines `192.168.20.10 nas.home.example.com`, and `/etc/dnsmasq.d/05-pihole-custom-cname.conf` with `cname=grafana.home.example.com,proxy.home.example.com`.

Wildcards are not supported by `dns.hosts`. For a whole domain use a dnsmasq line (enable it with `misc.dnsmasq_lines` or `misc.etc_dnsmasq_d`):
```
address=/home.example.com/192.168.20.10
```
This matches the domain **and all subdomains**. Used for split-horizon DNS in [Reverse Proxy Patterns](reverse-proxy-patterns.md).

Test:
```bash
dig +short nas.home.example.com @192.168.20.2
```

---
## Adlists and Gravity
- Web UI: **Lists** (v6) or **Adlists** (v5). Add the list URL, then run `pihole -g` (or **Tools -> Update Gravity**).
- A reasonable start: the default list plus one larger curated list. More lists means more false positives and a larger `gravity.db`.
- Add exceptions under **Domains** (allow exact or regex), or use per-client **Groups** to relax filtering for particular devices.
- `pihole -q <DOMAIN>` tells you which list blocks something.
- Schedule: gravity runs weekly via cron/systemd timer; run `pihole -g` manually after list changes.

---
## Upstreams: Unbound, DoT, DoH
CHOICE | HOW
---|---
Plain upstream | `dns.upstreams = ["1.1.1.1","1.0.0.1"]`: fast, but queries are unencrypted and visible to your ISP
Recursive resolver (recommended) | Run [Unbound](unbound.md) on `127.0.0.1#5335`, set `dns.upstreams = ["127.0.0.1#5335"]`. No third-party resolver sees all your queries, and Unbound does DNSSEC
Encrypted forwarding | Pi-hole FTL speaks plain DNS to upstreams only. Put Unbound ([Unbound](unbound.md) "forward over TLS") or cloudflared/dnscrypt-proxy in front and point Pi-hole at it. See [DNS over TLS (DoT)](../networking/dns-over-tls.md), [DNS over HTTPS (DoH)](../networking/dns-over-https.md), [DNS Encryption](../networking/dns-encryption.md)

cloudflared `proxy-dns` (DoH to a local port) is a common alternative, but check the current cloudflared docs, as the feature's status has been in flux; [Unbound](unbound.md) or `dnscrypt-proxy` are safer for new setups. Example only:
```bash
cloudflared proxy-dns --port 5053 --upstream https://1.1.1.1/dns-query --address 127.0.0.1
# then: pihole-FTL --config dns.upstreams '["127.0.0.1#5053"]'
```

Pi-hole plus Unbound in Compose (internal network, only Pi-hole publishes port 53):
```yaml
services:
  unbound:
    image: mvance/unbound:latest       # community image; or build your own
    restart: unless-stopped
    networks:
      dns:
        ipv4_address: 172.30.0.2
  pihole:
    image: pihole/pihole:latest
    restart: unless-stopped
    ports: ["53:53/tcp", "53:53/udp", "8080:80/tcp"]
    environment:
      FTLCONF_dns_upstreams: 172.30.0.2#53
      FTLCONF_dns_listeningMode: ALL
      FTLCONF_webserver_api_password: ${PIHOLE_PASSWORD}
    volumes: ["./etc-pihole:/etc/pihole"]
    networks: [dns]
networks:
  dns:
    ipam:
      config:
        - subnet: 172.30.0.0/24
```
Check the image's own README for its listen port and config path before use.

---
## Built-in DHCP
Turn on only if your router cannot do per-client DNS options: **Settings -> DHCP**, or `dhcp.active`, `dhcp.start`, `dhcp.end`, `dhcp.router`. Static leases are listed in the same page. Only one DHCP server may run per VLAN. For richer DHCP (options, tags, relay) see [dnsmasq DHCP and DNS](dnsmasq-dhcp.md). On other VLANs, either run a DHCP relay or hand out Pi-hole's address as DNS from the router ([VLANs](vlans.md)).

---
## REST API (v6)
v6 has an HTTP API under `/api` (live docs at `http://<PIHOLE>/api/docs`).
```bash
SID=$(curl -s -X POST http://pi.hole/api/auth \
  -H 'Content-Type: application/json' \
  -d '{"password":"<PASSWORD>"}' | jq -r .session.sid)
curl -s -H "sid: $SID" http://pi.hole/api/stats/summary | jq
curl -s -X DELETE -H "sid: $SID" http://pi.hole/api/auth      # log out
```
Use an application password (**Settings -> Web interface / API**) for scripts rather than your main password.

---
## v5 vs v6
TOPIC | v5 | v6
---|---|---
Config | `/etc/pihole/setupVars.conf`, `pihole-FTL.conf`, `/etc/dnsmasq.d/*` | Single `/etc/pihole/pihole.toml`
Web server | lighttpd + PHP | Built into FTL (CivetWeb), HTTPS built in, ports from `webserver.port`
Docker env | `WEBPASSWORD`, `PIHOLE_DNS_`, `DNSMASQ_LISTENING` | `FTLCONF_*` (old names deprecated)
Local DNS | `custom.list`, `05-pihole-custom-cname.conf` | `dns.hosts`, `dns.cnameRecords`
dnsmasq snippets | Always read from `/etc/dnsmasq.d` | Only if `misc.etc_dnsmasq_d = true`; or `misc.dnsmasq_lines`
Allow/deny | `pihole -w/-b` | Web UI and API (CLI helpers removed or deprecated)
API | `api.php` | REST `/api`, session ID authentication
Upgrade | `pihole -up` | `pihole -up` migrates settings once; **back up first** (Settings -> Teleporter)

---
## Backup and Restore
- Web UI: **Settings -> Teleporter** exports a zip (config, lists, local records).
- Docker: back up `./etc-pihole`.
- CLI: `pihole-FTL --teleporter` writes an export file in the current directory.

---
## Troubleshooting
SYMPTOM | CHECK
---|---
Nothing resolves after setup | `dns.upstreams` empty, or Unbound not listening: `dig pi-hole.net @127.0.0.1 -p 5335`
Clients cannot reach Pi-hole in Docker | Bridge network with `LOCAL` mode: set `FTLCONF_dns_listeningMode=ALL`
Port 53 already in use | `sudo ss -lntup 'sport = :53'`; on Ubuntu disable the stub: `DNSStubListener=no` in `/etc/systemd/resolved.conf`, then `systemctl restart systemd-resolved`
Site wrongly blocked | `pihole -q <DOMAIN>`, then allow it in **Domains**
Local names do not resolve | Record in `dns.hosts`? Client using another resolver (DoH in the browser, IPv6 DNS from the router)?
Setting reverts after restart | It is set by an `FTLCONF_` env var; edit the compose file instead
Web UI unreachable | `webserver.port` changed, or the reverse proxy has the port; `sudo ss -lntp \| grep pihole-FTL`
Slow first queries | Cold cache with recursive upstream; that is normal for Unbound and improves with `prefetch`
Check logs | `pihole tail`, `/var/log/pihole/FTL.log`, `/var/log/pihole/pihole.log`; Docker: `docker logs pihole`
Query test with a specific resolver | `dig example.com @<PIHOLE_IP>`; `dig doubleclick.net @<PIHOLE_IP>` should return `0.0.0.0` when blocked

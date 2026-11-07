# Unbound
Unbound is a validating, recursive, caching DNS resolver from NLnet Labs. In a homelab it usually sits behind [Pi-hole](pihole.md) or [AdGuard Home](adguard-home.md): it resolves names itself from the root servers (so no single upstream sees your queries), validates DNSSEC, caches, and can also serve local zones. It can instead forward all queries over DNS-over-TLS to a public resolver.

Documentation: [unbound.conf](https://unbound.docs.nlnetlabs.nl/en/latest/manpages/unbound.conf.html) · [unbound-control](https://nlnetlabs.nl/documentation/unbound/unbound-control/) · [Pi-hole + Unbound guide](https://docs.pi-hole.net/guides/dns/unbound/)

> **Verification:** the Pi-hole-style listener (port 5335, `prefetch`, `edns-buffer-size: 1232`, `use-caps-for-id: no`, `private-address` lines) and the `unbound-control` subcommands `flush`, `flush_zone`, `list_local_data`, `local_data`, `dump_cache`, `stats_noreset`, `reload` were checked against the docs. **Not verified:** DoT forwarding options, `access-control`, trust-anchor handling, `unbound-checkconf`/`unbound-anchor`, and the packaging paths (from memory). No command was executed.

See also: [Homelab](homelab.md) · [DNS over TLS (DoT)](../networking/dns-over-tls.md) · [DNS Encryption](../networking/dns-encryption.md) · [DNS Record Types](../networking/dns-record-types.md) · [Reverse Proxy Patterns](reverse-proxy-patterns.md) · [Docker-Compose](../docker/docker-compose.md)

---
## Install
```bash
sudo apt install unbound dnsutils
sudo unbound-checkconf                  # validate configuration
sudo systemctl enable --now unbound
dig example.com @127.0.0.1 -p 5335      # test (use the port you configured)
```
Debian/Ubuntu read `/etc/unbound/unbound.conf`, which includes `/etc/unbound/unbound.conf.d/*.conf`. Put your own settings in a new file in that directory. Ubuntu enables `unbound-resolvconf` which may rewrite `/etc/resolv.conf`; disable it if it conflicts (`sudo systemctl disable --now unbound-resolvconf`).

---
## Recursive Resolver for Pi-hole (port 5335)
`/etc/unbound/unbound.conf.d/pi-hole.conf`:
```yaml
server:
    verbosity: 0
    interface: 127.0.0.1
    port: 5335
    do-ip4: yes
    do-udp: yes
    do-tcp: yes
    do-ip6: no                  # set yes only if the host has working IPv6

    # Privacy and hardening
    hide-identity: yes
    hide-version: yes
    harden-glue: yes
    harden-dnssec-stripped: yes
    harden-referral-path: no
    use-caps-for-id: no
    qname-minimisation: yes

    # Performance
    edns-buffer-size: 1232
    prefetch: yes
    num-threads: 1
    so-rcvbuf: 1m
    cache-min-ttl: 300
    cache-max-ttl: 86400

    # Never return private ranges from the public internet (rebind protection)
    private-address: 10.0.0.0/8
    private-address: 172.16.0.0/12
    private-address: 192.168.0.0/16
    private-address: 169.254.0.0/16
    private-address: fd00::/8
    private-address: fe80::/10
```
```bash
sudo unbound-checkconf && sudo systemctl restart unbound
dig pi-hole.net @127.0.0.1 -p 5335            # NOERROR, answer
dig fail01.dnssec.works @127.0.0.1 -p 5335    # should be SERVFAIL (bad signature)
dig dnssec.works @127.0.0.1 -p 5335           # NOERROR with "ad" flag
```
Then in Pi-hole: `dns.upstreams = ["127.0.0.1#5335"]` (see [Pi-hole](pihole.md)). Do not turn on DNSSEC in both Pi-hole and Unbound; Unbound is enough.

For other hosts on the LAN (not just localhost) use `interface: 0.0.0.0` and restrict who may ask:
```yaml
    interface: 0.0.0.0
    port: 53
    access-control: 127.0.0.0/8 allow
    access-control: 192.168.0.0/16 allow
    access-control: 0.0.0.0/0 refuse
```
Never leave a recursive resolver open to the internet (reflection/amplification abuse).

---
## DNSSEC
Validation is on by default in Debian/Ubuntu packages through the root trust anchor.
```yaml
server:
    auto-trust-anchor-file: "/var/lib/unbound/root.key"
```
COMMAND | DESCRIPTION
---|---
`sudo unbound-anchor -a /var/lib/unbound/root.key` | Create or update the root trust anchor
`dig +dnssec example.com @127.0.0.1 -p 5335` | Look for the `ad` (authenticated data) flag
`dig +cd example.com @127.0.0.1 -p 5335` | Disable validation for a test (checking cause of SERVFAIL)
`sudo unbound-control list_insecure` | Names configured as insecure
`domain-insecure: "internal.example.com"` | Skip validation for a private zone with no DS (config)

A clock that is wrong breaks validation (signatures appear expired); check NTP first on SERVFAIL for everything.

---
## Local Zones and Data
For names that only exist inside the house, or to override public answers (split-horizon DNS, see [Reverse Proxy Patterns](reverse-proxy-patterns.md)):
```yaml
server:
    local-zone: "home.example.com." transparent
    local-data: "nas.home.example.com. IN A 192.168.20.10"
    local-data: "proxy.home.example.com. IN A 192.168.20.11"
    local-data-ptr: "192.168.20.10 nas.home.example.com"
    local-data: "grafana.home.example.com. IN CNAME proxy.home.example.com."
```
ZONE TYPE | BEHAVIOUR
---|---
`transparent` | Answer from `local-data` if the name is listed, otherwise resolve normally (best for overrides)
`static` | Answer only from local data; unknown names in the zone get NXDOMAIN
`redirect` | The zone's data answers for the **zone and all subdomains** (wildcard-style)
`typetransparent` | Like `transparent`, but a name with only other record types returns normally
`deny` / `refuse` | Drop / REFUSED all queries in the zone
`always_nxdomain` | Return NXDOMAIN for everything under the name (block a domain)

Wildcard:
```yaml
    local-zone: "home.example.com." redirect
    local-data: "home.example.com. IN A 192.168.20.11"
```
Zone and record names are written as fully qualified names ending in a dot. For lots of records use `include: "/etc/unbound/local-records.conf"`, or add them at runtime with `unbound-control` (below).

---
## Forwarding Over TLS (DoT)
Instead of recursing, send everything to an upstream resolver over TLS:
```yaml
server:
    tls-cert-bundle: /etc/ssl/certs/ca-certificates.crt

forward-zone:
    name: "."
    forward-tls-upstream: yes
    forward-addr: 1.1.1.1@853#cloudflare-dns.com
    forward-addr: 1.0.0.1@853#cloudflare-dns.com
    forward-addr: 9.9.9.9@853#dns.quad9.net
```
Syntax is `IP@PORT#TLS-AUTH-NAME`. The name after `#` is verified against the server certificate. Only the destination resolver sees your queries, so you trade privacy from your ISP for trust in the resolver. See [DNS over TLS (DoT)](../networking/dns-over-tls.md) and [DNS Encryption](../networking/dns-encryption.md).

Forward only one domain (for example, a corporate or lab zone) to another server:
```yaml
forward-zone:
    name: "lab.example.com."
    forward-addr: 192.168.50.2
```
If a `forward-zone` for `.` exists, Unbound no longer recurses, even for names outside it.

---
## Local Reverse Lookups and Private Domains
```yaml
server:
    private-domain: "home.example.com"      # allow private addresses in answers for this domain
    domain-insecure: "home.example.com"     # only needed if the internal zone has no DNSSEC chain
```
`private-address` strips private IPs from public answers; `private-domain` lets selected names return them, so rebind protection stays on while your own records work.

---
## `unbound-control`
Enable the control socket in `/etc/unbound/unbound.conf.d/remote-control.conf`:
```yaml
remote-control:
    control-enable: yes
    control-interface: /run/unbound.ctl      # or 127.0.0.1 with certificates
```
Debian generates keys with `sudo unbound-control-setup` when using TCP control.

COMMAND | DESCRIPTION
---|---
`unbound-control status` | Is it running, version, uptime
`unbound-control reload` | Re-read config and flush the cache
`unbound-control reload_keep_cache` | Re-read config but keep cache (newer versions)
`unbound-control flush <NAME>` | Remove one name from the cache
`unbound-control flush_zone <NAME>` | Remove a name and everything below it
`unbound-control flush_negative` | Drop cached NXDOMAIN answers
`unbound-control dump_cache > cache.txt` | Dump the cache
`unbound-control load_cache < cache.txt` | Load a cache dump
`unbound-control stats_noreset` | Statistics without resetting counters
`unbound-control stats` | Statistics and reset counters
`unbound-control list_local_data` | Show runtime local data
`unbound-control local_data <RR>` | Add a record, for example `local_data nas.home.example.com. 300 IN A 192.168.20.10`
`unbound-control local_data_remove <NAME>` | Remove one
`unbound-control list_forwards` | Show configured forwards
`unbound-control forward <IP>` | Change the "." forwarder at runtime
`unbound-control verbosity <N>` | Change logging level live

Records added with `local_data` are lost on restart; put permanent ones in the config.

---
## Docker Compose
Run it as a plain service and point [Pi-hole](pihole.md) at it (see the combined example there). Mount your config read-only:
```yaml
services:
  unbound:
    image: <UNBOUND_IMAGE>:<TAG>
    restart: unless-stopped
    volumes:
      - ./unbound.conf.d:/etc/unbound/unbound.conf.d:ro
    networks: [dns]
```
Use an image whose config path and listen port you have read in its README. Bind to `0.0.0.0` inside the container and only publish ports you intend to (`access-control` must include the Docker subnet).

---
## Troubleshooting
SYMPTOM | CHECK
---|---
`SERVFAIL` on everything | Wrong clock; broken trust anchor (`unbound-anchor`); no outbound UDP/TCP 53; try `dig +cd` to see if DNSSEC is the cause
`SERVFAIL` on one domain | Broken DNSSEC at the domain: `dig +cd` answers but plain does not; check with a DNSSEC debugger
`REFUSED` from other hosts | `access-control` does not allow that client; `interface` only on localhost
Config rejected | `sudo unbound-checkconf` shows the file and line
Local data ignored | Zone name missing the trailing dot; `local-zone` type `static` hiding other names; a `forward-zone` overrides nothing locally but check `unbound-control list_local_data`
Public answers missing private IPs | `private-address` stripped them: add `private-domain`
Very slow after start | Cold cache; enable `prefetch: yes` and `serve-expired: yes` (serves stale then refreshes)
Port 53 in use | systemd-resolved stub: `ss -lntup 'sport = :53'`; use another port or disable the stub
Error `could not open ssl` / certificate verify failed for DoT | `tls-cert-bundle` path wrong, or the name after `#` does not match the server certificate
Logs | `journalctl -u unbound -f`; temporarily `verbosity: 2` or `unbound-control verbosity 2`

# DNS over TLS (DoT)
DoT wraps standard DNS queries in a TLS ([TLS (Transport Layer Security)](tls.md)) session on **TCP port 853**, so queries cannot be read or tampered with on the path. Compare with [DNS over HTTPS (DoH)](dns-over-https.md) and see the overview in [DNS Encryption](dns-encryption.md).

## DoT vs DoH
&nbsp; | DoT | DoH
---|---|---
Port | 853 (dedicated) | 443 (blends with web traffic)
Easy to block or monitor | Yes, by port | Hard
Typical use | OS, router, resolver | Browser

## Public Resolvers
PROVIDER | HOSTNAME (use for TLS validation) | IPs
---|---|---
Cloudflare | `one.one.one.one` | `1.1.1.1`, `1.0.0.1`
Google | `dns.google` | `8.8.8.8`, `8.8.4.4`
Quad9 | `dns.quad9.net` | `9.9.9.9`, `149.112.112.112`

## Testing
COMMAND | DESCRIPTION
---|---
`kdig -d @1.1.1.1 +tls-host=one.one.one.one +tls example.com` | Query over DoT (`knot-dnsutils`)
`dig +tls @1.1.1.1 example.com` | Query over DoT (dig 9.18+)
`openssl s_client -connect 1.1.1.1:853 -servername one.one.one.one` | Check the TLS endpoint
`nc -zv 1.1.1.1 853` | Check the port is reachable

## systemd-resolved (Linux)
`/etc/systemd/resolved.conf`
```ini
[Resolve]
DNS=1.1.1.1#one.one.one.one 1.0.0.1#one.one.one.one
DNSOverTLS=yes
```
```bash
sudo systemctl restart systemd-resolved
resolvectl status
```
Use `DNSOverTLS=opportunistic` to fall back to plain DNS if DoT fails.

## Unbound
```yaml
server:
    tls-cert-bundle: /etc/ssl/certs/ca-certificates.crt
forward-zone:
    name: "."
    forward-tls-upstream: yes
    forward-addr: 1.1.1.1@853#one.one.one.one
    forward-addr: 9.9.9.9@853#dns.quad9.net
```

## Android
**Settings > Network > Private DNS** and enter the provider hostname, e.g. `one.one.one.one`.

## Block Plain DNS Leaks
Allow outbound `853/tcp` and block outbound `53/tcp,udp` except from your resolver, see [UFW (uncomplicated firewall)](../linux/ufw.md) and [IPTables](../linux/iptables.md).

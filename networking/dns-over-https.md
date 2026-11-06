# DNS over HTTPS (DoH)
DoH sends DNS queries inside HTTPS ([[tls]]) on **TCP port 443**, as defined in RFC 8484. It looks like normal web traffic. Compare with [[dns-over-tls]] and see the overview in [[dns-encryption]].

## Public Endpoints
PROVIDER | URL
---|---
Cloudflare | `https://cloudflare-dns.com/dns-query`
Google | `https://dns.google/dns-query`
Quad9 | `https://dns.quad9.net/dns-query`

## Testing
COMMAND | DESCRIPTION
---|---
`curl -s -H 'accept: application/dns-json' 'https://cloudflare-dns.com/dns-query?name=example.com&type=A' \| jq` | JSON query to Cloudflare
`curl -s 'https://dns.google/resolve?name=example.com&type=A' \| jq` | JSON query to Google
`q example.com @https://dns.google/dns-query` | Wire-format query with the `q` tool
`dig +https @dns.google example.com` | Query over DoH (dig 9.18+)

## Browsers
BROWSER | WHERE
---|---
Firefox | Settings > Privacy & Security > DNS over HTTPS
Chrome / Edge | Settings > Privacy and security > Security > Use secure DNS
Windows 11 | Settings > Network & internet > (adapter) > DNS server assignment > Encrypted

## Run a Local DoH Proxy
Stub resolvers that listen on `127.0.0.1:53` and forward over HTTPS:

TOOL | NOTES
---|---
`cloudflared proxy-dns` | Cloudflare's proxy
`dnscrypt-proxy` | Supports DoH, DoT-like and DNSCrypt, with blocklists
`AdGuard Home` / `Pi-hole + cloudflared` | Filtering resolver with DoH upstream
`Technitium DNS` | Self-hosted resolver with DoH

dnscrypt-proxy `dnscrypt-proxy.toml`:
```toml
server_names = ['cloudflare', 'google']
listen_addresses = ['127.0.0.1:53']
doh_servers = true
dnscrypt_servers = false
require_dnssec = true
```

## Caveats
- Browser DoH bypasses local DNS filtering and split-horizon names. Enterprises usually disable it with the Firefox canary domain `use-application-dns.net`.
- DoH hides queries from the network but not from the resolver. Pick one you trust.
- The SNI in the TLS handshake may still reveal the server name unless ECH is used.

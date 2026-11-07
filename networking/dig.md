# dig
`dig` queries DNS servers and prints the full answer. Use it to check records, test a specific resolver, follow delegation from the root and see whether a zone is signed. `host` and `nslookup` are simpler alternatives, and `resolvectl` queries through `systemd-resolved`.

Documentation: [dig(1)](https://man7.org/linux/man-pages/man1/dig.1.html) · [host(1)](https://man7.org/linux/man-pages/man1/host.1.html)
Project: [BIND 9](https://www.isc.org/bind/)

> **Verification:** options were checked against the `dig` and `host` man pages in Ubuntu 24.04 (`bind9-dnsutils`). `resolvectl` rows follow the systemd documentation and were not run. Use `example.com` style names; output varies by resolver.

## Queries
COMMAND | DESCRIPTION
---|---
`dig example.com` | A record using the system resolver
`dig example.com MX` | A given record type (`AAAA`, `MX`, `TXT`, `NS`, `CNAME`, `SOA`, `CAA`)
`dig @192.0.2.53 example.com` | Ask a specific server
`dig -x 192.0.2.10` | Reverse (PTR) lookup
`dig -4 example.com` / `dig -6 example.com` | Force IPv4 or IPv6 transport to the server
`dig -p 5353 @127.0.0.1 example.com` | Non-standard port
`dig -f NAMES.txt +short` | Batch queries from a file, one per line

## Output Control
COMMAND | DESCRIPTION
---|---
`dig +short example.com` | Answer data only
`dig +noall +answer example.com` | Answer section only, with TTLs
`dig +noall +answer +ttlunits example.com` | TTL as `1h`, `5m`
`dig +multiline example.com SOA` | SOA fields on separate lines
`dig +nocmd +noall +stats example.com` | Query time and server only

## Resolver Behaviour
COMMAND | DESCRIPTION
---|---
`dig +tcp example.com` | Use TCP instead of UDP
`dig +norecurse @192.0.2.53 example.com` | Do not ask the server to recurse (test its cache or authoritative data)
`dig +time=2 +tries=1 example.com` | Short timeout, one attempt
`dig +search host` | Apply the `search` domains from `resolv.conf`
`dig +trace example.com` | Follow delegation from the root servers
`dig +nssearch example.com` | Ask each authoritative server for the SOA and compare serials
`dig +bufsize=1232 example.com` | Set the EDNS buffer size

## DNSSEC
COMMAND | DESCRIPTION
---|---
`dig +dnssec example.com` | Request signatures; the `ad` flag means the resolver validated
`dig example.com DNSKEY +short` | Zone keys
`dig example.com DS +short` | Delegation signer at the parent
`dig +cd example.com` | Checking disabled: see data that fails validation

## Zone Transfer
COMMAND | DESCRIPTION
---|---
`dig AXFR example.com @192.0.2.53` | Full zone transfer, if the server permits it from you
`dig IXFR=<SERIAL> example.com @192.0.2.53` | Incremental transfer from a serial

## host and nslookup
COMMAND | DESCRIPTION
---|---
`host example.com` | A, AAAA and MX in short form
`host -t TXT example.com` | One record type
`host 192.0.2.10` | Reverse lookup
`host example.com 192.0.2.53` | Use a given server
`nslookup example.com 192.0.2.53` | Same query with `nslookup`

## systemd-resolved
COMMAND | DESCRIPTION
---|---
`resolvectl status` | Per-link DNS servers and domains
`resolvectl query example.com` | Resolve through `systemd-resolved` (shows which link and protocol answered)
`resolvectl flush-caches` | Clear the local cache
`resolvectl statistics` | Cache hits, DNSSEC counters

## Reading the Answer
FIELD | MEANING
---|---
`status: NOERROR` | The query worked (an empty answer means no such record type)
`status: NXDOMAIN` | The name does not exist
`status: SERVFAIL` | The resolver could not get an answer; often a DNSSEC or upstream failure
`flags: qr rd ra` | Response, recursion desired, recursion available
`flags: aa` | Answer is authoritative
`flags: ad` | Authenticated data: DNSSEC validated
`;; Query time` | Round trip to the server
`SERVER:` | The resolver that answered

## See Also
- [DNS Troubleshooting](../recipes/dns-troubleshooting.md)
- [DNS Record Types](dns-record-types.md)
- [DNS over TLS (DoT)](dns-over-tls.md)
- [Unbound](../homelab/unbound.md)
- [Network Troubleshooting](../recipes/network-troubleshooting.md)

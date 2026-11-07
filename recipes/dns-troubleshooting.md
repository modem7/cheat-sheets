# DNS Troubleshooting
Trace a failing or wrong DNS answer from the application down through the local resolver, the upstream resolver and the authoritative servers, including DoT/DoH and Kubernetes CoreDNS.

Documentation: [dig](https://bind9.readthedocs.io/en/latest/manpages.html#dig-dns-lookup-utility) · [resolvectl](https://www.freedesktop.org/software/systemd/man/latest/resolvectl.html) · [Debugging DNS Resolution (Kubernetes)](https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/)

## Goal
Find where in the resolver chain a lookup goes wrong and fix it.

## Prerequisites
- `dig` (`sudo apt install dnsutils`), optionally `kdig` (`knot-dnsutils`) and `curl`
- The failing name (`app.example.com`) and the host it fails on

## The Resolver Chain
```text
application -> libc / stub (127.0.0.53) -> local resolver (systemd-resolved, router, Pi-hole)
            -> upstream or recursive resolver -> root -> TLD -> authoritative servers
```
Test each hop on its own, starting at the client and moving outward.

## Steps
### 1. What does this host actually use?
COMMAND | DESCRIPTION
---|---
`resolvectl status` | Per-link DNS servers, search domains, DoT state (systemd-resolved)
`resolvectl query app.example.com` | Resolve through the system path, shows which link and protocol answered
`cat /etc/resolv.conf` | `127.0.0.53` means the systemd stub is in use
`getent hosts app.example.com` | What applications using libc see (honours `/etc/hosts`, `nsswitch.conf`)

If `getent` works but `dig` does not (or the reverse), the difference is `/etc/hosts`, `nsswitch.conf` or a search-domain issue, not DNS itself.

### 2. Query the resolvers directly
```bash
dig app.example.com                       # uses the system resolver
dig app.example.com @192.0.2.53           # your local or LAN resolver
dig app.example.com @1.1.1.1              # a public resolver for comparison
dig +short app.example.com A
dig +short app.example.com AAAA
```
Read the `status:` field.

STATUS | MEANING
---|---
`NOERROR` with an answer | Name exists and resolved
`NOERROR` with no answer | Name exists but not for that record type (try `AAAA`, `CNAME`)
`NXDOMAIN` | The name does not exist (typo, missing record, split-horizon mismatch)
`SERVFAIL` | The resolver failed (broken delegation, DNSSEC failure, unreachable authoritative server)
`REFUSED` | The server will not answer you (ACL, wrong server)
no reply | UDP/53 blocked or server down, try `dig +tcp`

### 3. Local resolver says one thing, public says another
- **Cache**: flush it. `sudo resolvectl flush-caches`; on a browser, restart it or clear its host cache.
- **Split horizon / local override**: Pi-hole, router or an internal zone returns a private address for the name. Compare answers from step 2.
- **Negative caching**: an `NXDOMAIN` is cached for the SOA minimum TTL. Check `dig +noall +answer +authority app.example.com`.

### 4. Walk the delegation
```bash
dig +trace app.example.com
dig NS example.com +short
dig app.example.com @<AUTHORITATIVE-NS> +norecurse
dig +dnssec app.example.com @1.1.1.1
```
`+trace` queries from the root and shows where the chain breaks. If the authoritative server answers but a recursive one returns `SERVFAIL`, suspect DNSSEC (an expired signature or wrong DS record at the registrar). Check `dig +cd app.example.com @1.1.1.1`, where `+cd` disables DNSSEC validation. A working `+cd` answer confirms a DNSSEC problem. For signing and validation detail see [DNSSEC](../networking/dnssec.md). For record types see [DNS Record Types](../networking/dns-record-types.md).

### 5. Encrypted DNS (DoT and DoH)
```bash
nc -zv 1.1.1.1 853                                                     # DoT port reachable
openssl s_client -connect 1.1.1.1:853 -servername one.one.one.one </dev/null | head
kdig -d @1.1.1.1 +tls-host=one.one.one.one +tls example.com            # DoT query
dig +tls @1.1.1.1 example.com                                          # dig 9.18+
curl -s -H 'accept: application/dns-json' 'https://cloudflare-dns.com/dns-query?name=example.com&type=A'   # DoH
```
If plain DNS works but DoT fails, port 853 may be blocked. With `DNSOverTLS=yes` in `/etc/systemd/resolved.conf` resolution stops entirely in that case, `opportunistic` falls back. See [DNS over TLS (DoT)](../networking/dns-over-tls.md), [DNS over HTTPS (DoH)](../networking/dns-over-https.md) and [DNS Encryption](../networking/dns-encryption.md).

### 6. Slow lookups
```bash
dig app.example.com | grep 'Query time'
resolvectl statistics
```
Common causes: a dead first DNS server in the list (each query waits for a timeout before the next), an IPv6 `AAAA` lookup that times out, or a long `search` list causing multiple failed lookups. Remove the dead server or fix its reachability.

### 7. Kubernetes (CoreDNS)
```bash
kubectl -n kube-system get pods -l k8s-app=kube-dns
kubectl -n kube-system logs -l k8s-app=kube-dns --tail 50
kubectl -n kube-system get svc kube-dns
kubectl run dns-test --rm -it --image=busybox:1.36 --restart=Never -- nslookup kubernetes.default
kubectl run dns-test --rm -it --image=busybox:1.36 --restart=Never -- nslookup example.com
```
If `kubernetes.default` fails, CoreDNS or the Service/network path to it is broken. If only external names fail, CoreDNS cannot reach its upstream (check the `forward` line in its ConfigMap and the node's `/etc/resolv.conf`). Pods inherit the cluster `ndots:5` setting, so short external names trigger several search-domain lookups first; use a trailing dot (`example.com.`) to bypass them. Details in [Kubernetes DNS](../kubernetes/kubernetes-dns.md), [Kubectl](../kubernetes/kubectl.md) and [K9s](../kubernetes/k9s.md).

### 8. Docker
Containers on a user-defined network use Docker's embedded resolver at `127.0.0.11`, which forwards to the host's resolvers. Test with `docker exec <CONTAINER> nslookup app.example.com`. If the host uses a `127.0.0.53` stub, Docker substitutes the real upstream servers, so check `resolvectl status` on the host ([Docker Networking](../docker/docker-networking.md)).

## Verify
```bash
resolvectl query app.example.com
dig +short app.example.com @1.1.1.1
dig +short app.example.com @192.0.2.53      # both should return the same address
```
From the affected application, repeat the failing lookup and a real connection (`curl -v https://app.example.com`).

## Rollback / Cleanup
Lookups are read-only. If you changed resolver settings, keep a copy of the previous `/etc/systemd/resolved.conf` and restart with `sudo systemctl restart systemd-resolved`. Lower a record's TTL **before** a planned change, and wait out the old TTL before you rely on it.

## Related Sheets
- [DNS Record Types](../networking/dns-record-types.md) · [DNS over TLS (DoT)](../networking/dns-over-tls.md) · [DNS over HTTPS (DoH)](../networking/dns-over-https.md) · [DNS Encryption](../networking/dns-encryption.md) · [Mail Server DNS Records Cheat-Sheet](../networking/dns-record-mailserver.md)
- [Kubernetes DNS](../kubernetes/kubernetes-dns.md) · [Kubectl](../kubernetes/kubectl.md) · [K3S](../kubernetes/k3s.md)
- [Docker Networking](../docker/docker-networking.md) · [Windows DNS Server](../windows/windows-dns-server.md)
- [Network Troubleshooting](network-troubleshooting.md) · [TLS Troubleshooting](tls-troubleshooting.md)
- [Pi-hole](../homelab/pihole.md) · [AdGuard Home](../homelab/adguard-home.md) · [Unbound](../homelab/unbound.md) · [dnsmasq DHCP and DNS](../homelab/dnsmasq-dhcp.md)

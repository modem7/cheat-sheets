# TLS Troubleshooting
A decision tree for "the certificate is broken" problems. Work top to bottom: each step either finds the fault or rules a layer out.

Documentation: [OpenSSL s_client](https://docs.openssl.org/master/man1/openssl-s_client/) · [curl manual](https://curl.se/docs/manpage.html)

## Goal
Identify which layer fails (DNS, network, handshake, certificate chain, name, validity, protocol) and fix it.

## Prerequisites
- A shell with `dig`, `curl`, `openssl` and (optionally) `nmap`
- The hostname (`app.example.com`) and, if known, the expected address (`203.0.113.10`)

## Decision Tree
SYMPTOM | LIKELY LAYER | GO TO
---|---|---
Name not found, wrong address | DNS | Step 1
Timeout, connection refused | Network, firewall, service | Step 2
Browser says "wrong site" or `certificate is not valid for` | SAN or SNI | Steps 4 and 6
`unable to get local issuer certificate`, works in browser but not curl | Missing intermediate | Step 3
`certificate has expired` | Validity or clock | Step 5 and 8
`handshake failure`, `protocol version`, `no shared cipher` | Protocol or cipher | Step 7
Works with the name but not by IP, or serves the wrong certificate | SNI | Step 6
Certificate "not yet valid" | Client or server clock | Step 8

## Steps
### 1. DNS
```bash
dig +short app.example.com
dig +short app.example.com @1.1.1.1      # compare with a public resolver
```
If the answers differ or are empty, switch to [DNS Troubleshooting](dns-troubleshooting.md).

### 2. Port reachability
```bash
nc -vz app.example.com 443
curl -v --connect-timeout 5 -o /dev/null https://app.example.com
nmap -Pn -p 443 app.example.com
```
STATE | MEANING
---|---
`open` | Something is listening and nothing blocks you
`closed` | Host reachable, nothing listening on 443 (service down, wrong port)
`filtered` / timeout | Firewall or routing drops the packets ([Network Troubleshooting](network-troubleshooting.md))

### 3. Certificate chain
```bash
openssl s_client -connect app.example.com:443 -servername app.example.com -showcerts </dev/null
```
Read the end of the output: `Verify return code: 0 (ok)` is a good chain. Check that the server sends the leaf **and** the intermediate(s) (`s:` is the subject, `i:` the issuer). Browsers can fetch a missing intermediate, `curl` and most libraries cannot. Fix by serving the full chain (`fullchain.pem`, not `cert.pem`; for Nginx see [Nginx](../apps/nginx.md)).

Test a saved chain file:
```bash
openssl verify -CAfile root.pem -untrusted intermediate.pem leaf.pem
```
Behind a corporate proxy or a self-signed CA, point the client at the right trust store: `curl --cacert ca.pem https://app.example.com` ([SSL Certificates Cheat-Sheet](../misc/ssl-certs.md), [Certutil](../tools/certutil.md)).

### 4. Names (SAN)
```bash
echo | openssl s_client -connect app.example.com:443 -servername app.example.com 2>/dev/null \
  | openssl x509 -noout -subject -ext subjectAltName
```
The requested hostname must match a `DNS:` entry in the Subject Alternative Name (the Common Name is ignored by modern clients). Wildcards cover one label only: `*.example.com` matches `app.example.com` but not `a.b.example.com` or `example.com`.

### 5. Validity and expiry
```bash
echo | openssl s_client -connect app.example.com:443 -servername app.example.com 2>/dev/null \
  | openssl x509 -noout -dates -issuer
openssl x509 -in cert.pem -noout -checkend 2592000 && echo "OK for 30 days" || echo "expires within 30 days"
```
Renewal failed? For Traefik read `docker logs traefik`; for cert-manager use `kubectl describe certificate,certificaterequest,order,challenge` ([Cert-Manager](../apps/cert-manager.md), [Traefik](../apps/traefik.md)).

### 6. SNI
A server hosting several sites picks the certificate from the name the client sends. Compare:
```bash
openssl s_client -connect 203.0.113.10:443 -servername app.example.com </dev/null 2>/dev/null | openssl x509 -noout -subject
openssl s_client -connect 203.0.113.10:443 </dev/null 2>/dev/null | openssl x509 -noout -subject    # no SNI, default site
curl -v --resolve app.example.com:443:203.0.113.10 https://app.example.com
```
`--resolve` tests a specific backend with the correct name, which bypasses DNS. If a load balancer or CDN is in front, test each address it returns.

### 7. Protocol and ciphers
```bash
openssl s_client -connect app.example.com:443 -servername app.example.com -tls1_2 </dev/null
openssl s_client -connect app.example.com:443 -servername app.example.com -tls1_3 </dev/null
curl -v --tlsv1.2 --tls-max 1.2 https://app.example.com
nmap --script ssl-enum-ciphers -p 443 app.example.com
```
- A client too old for TLS 1.2, or a server that only offers TLS 1.0/1.1, gives `protocol version` or `handshake failure`.
- Test a single cipher: `openssl s_client -connect app.example.com:443 -tls1_2 -cipher ECDHE-RSA-AES128-GCM-SHA256`. For TLS 1.3 suites use `-ciphersuites`.
- Review the server's allowed versions and suites against [SSL Security Cheat-Sheet](../misc/ssl-security.md) and [TLS (Transport Layer Security)](../networking/tls.md).

### 8. Clock
```bash
date -u
timedatectl             # "System clock synchronized: yes"
curl -sI https://example.com | grep -i '^date'    # compare with a server's clock
```
A client clock that is off by more than the certificate's validity window gives "expired" or "not yet valid". Fix NTP on the client and the server ([New Server Checklist](new-server-checklist.md)).

### 9. Timing a slow handshake
```bash
curl -o /dev/null -s -w 'dns %{time_namelookup}  connect %{time_connect}  tls %{time_appconnect}  total %{time_total}\n' https://app.example.com
```
A large `dns` value points to the resolver, a large gap between `connect` and `tls` to the server or an inspecting middlebox.

## Verify
```bash
curl -sS -o /dev/null -w '%{http_code} %{ssl_verify_result}\n' https://app.example.com    # 200 0
echo | openssl s_client -connect app.example.com:443 -servername app.example.com -verify_return_error 2>&1 | grep -E 'Verify return code|Protocol'
```
`ssl_verify_result` of `0` means the chain verified. Re-test from a second network and from a client with a clean trust store.

## Rollback / Cleanup
These are read-only checks. If you changed a server certificate or protocol setting, keep the previous certificate and config until the new one is confirmed, and remove any temporary `--cacert` or `-k` workarounds. Never leave `curl -k` in scripts.

## Related Sheets
- [TLS (Transport Layer Security)](../networking/tls.md) · [TLS Handshake](../networking/tls-handshake.md) · [SSL Certificates Cheat-Sheet](../misc/ssl-certs.md) · [SSL Security Cheat-Sheet](../misc/ssl-security.md)
- [OpenSSL](../tools/openssl.md) · [curl](../tools/curl.md) · [NMap](../tools/nmap.md) · [Certutil](../tools/certutil.md)
- [Traefik](../apps/traefik.md) · [Nginx](../apps/nginx.md) · [Cert-Manager](../apps/cert-manager.md)
- [DNS Troubleshooting](dns-troubleshooting.md) · [Network Troubleshooting](network-troubleshooting.md)
- [Security](../security/security.md) · [Reverse Proxy Patterns](../homelab/reverse-proxy-patterns.md) · [Vault and OpenBao](../security/vault.md)

# SSL Security Cheat-Sheet
Checking and hardening TLS ([[tls]]). Commands in [[openssl]], handshake details in [[tls-handshake]], certificates in [[ssl-certs]].

## TLS Version and Ciphers
Scanning for TLS Version and supported Ciphers: `nmap --script ssl-enum-ciphers <target>`

COMMAND | DESCRIPTION
---|---
`nmap --script ssl-enum-ciphers -p 443 <HOST>` | Protocols and ciphers with a grade
`openssl s_client -connect <HOST>:443 -tls1_3` | Does the server support TLS 1.3?
`openssl s_client -connect <HOST>:443 -tls1_1` | Should fail: TLS 1.1 must be disabled
`testssl.sh <HOST>:443` | Thorough local scanner
`sslyze <HOST>` | Python scanner
`curl -vI https://<HOST> 2>&1 \| grep -i 'SSL connection\|TLS'` | Negotiated version and cipher

Tool | Link | Description
---|---|---
Qualys SSL Labs | https://www.ssllabs.com/ssltest/ | Online server test and grade
Mozilla Observatory | https://developer.mozilla.org/en-US/observatory | HTTP security header scan
Mozilla SSL Configuration Generator | https://ssl-config.mozilla.org | Ready-made server configs
testssl.sh | https://testssl.sh | CLI scanner
Hardenize | https://www.hardenize.com | TLS, DNS, email checks together

## Recommended Settings
Use Mozilla's "Intermediate" profile as a baseline, which is TLS 1.2 and 1.3 only with ECDHE and AEAD ciphers.

Nginx ([[nginx]]):
```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers off;
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:10m;
ssl_session_tickets off;
ssl_stapling on;
ssl_stapling_verify on;
add_header Strict-Transport-Security "max-age=63072000" always;
```

## HTTP Security Headers
HEADER | PURPOSE
---|---
`Strict-Transport-Security: max-age=63072000; includeSubDomains` | Force HTTPS (add `preload` only when sure)
`Content-Security-Policy` | Restrict script and resource sources
`X-Content-Type-Options: nosniff` | Stop MIME sniffing
`X-Frame-Options: DENY` or CSP `frame-ancestors` | Clickjacking protection
`Referrer-Policy: strict-origin-when-cross-origin` | Limit referrer leakage
`Permissions-Policy` | Disable unused browser features

Check headers: `curl -sI https://<HOST>`

## Checklist
- No SSLv3, TLS 1.0 or 1.1.
- Certificate valid, matching SAN, full chain served, renewed automatically.
- Forward secrecy (ECDHE) and AEAD ciphers only.
- OCSP stapling on, HSTS on.
- CAA DNS record to limit who may issue: `example.com. CAA 0 issue "letsencrypt.org"`
- Monitor expiry: `echo | openssl s_client -connect <HOST>:443 2>/dev/null | openssl x509 -noout -enddate`

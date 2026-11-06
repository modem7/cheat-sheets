# TLS (Transport Layer Security)
TLS encrypts and authenticates traffic between two parties. It is the successor to SSL, which is deprecated and must not be used. HTTPS is HTTP over TLS.

Related: [[tls-handshake]], [[ssl-certs]], [[ssl-security]], [[openssl]], [[certutil]], [[dns-over-tls]]

## What TLS Provides
PROPERTY | HOW
---|---
Confidentiality | Symmetric encryption of the session (AES-GCM, ChaCha20-Poly1305)
Integrity | Authenticated encryption or MAC detects tampering
Authentication | Server (and optionally client) proves identity with an X.509 certificate

## Versions
VERSION | STATUS
---|---
SSL 2.0 / 3.0 | Broken, disable
TLS 1.0 / 1.1 | Deprecated (RFC 8996), disable
TLS 1.2 | Supported, still widely needed
TLS 1.3 | Current. Faster handshake, only strong ciphers, forward secrecy always

## Certificates
TERM | MEANING
---|---
CA | Certificate Authority that signs certificates
Root / Intermediate | Chain of trust: server cert, intermediate(s), root in the trust store
SAN | Subject Alternative Name. The hostnames a cert is valid for. Browsers ignore CN
DV / OV / EV | Domain / Organisation / Extended Validation
Wildcard | `*.example.com`, covers one label only
mTLS | Mutual TLS, client also presents a certificate

File formats:

EXTENSION | MEANING
---|---
`.pem` | Base64 text, `-----BEGIN ...-----` blocks. Cert, key or chain
`.crt` / `.cer` | Certificate (PEM or DER)
`.key` | Private key
`.csr` | Certificate signing request
`.der` | Binary encoding
`.pfx` / `.p12` | PKCS#12 bundle holding key and certs

## Common Ports
PORT | PROTOCOL
---|---
`443` | HTTPS
`465` | SMTPS (implicit TLS)
`587` / `25` | SMTP with STARTTLS
`993` / `995` | IMAPS / POP3S
`636` | LDAPS
`853` | DNS over TLS, see [[dns-over-tls]]

## Quick Checks
COMMAND | DESCRIPTION
---|---
`openssl s_client -connect <HOST>:443 -servername <HOST>` | Inspect the chain and negotiated protocol
`curl -vI https://<HOST>` | Show handshake details and headers
`nmap --script ssl-enum-ciphers -p 443 <HOST>` | List accepted ciphers
`echo \| openssl s_client -connect <HOST>:443 2>/dev/null \| openssl x509 -noout -dates` | Certificate expiry

More commands in [[openssl]].

## Automating Certificates
- **Let's Encrypt** via ACME clients: certbot, acme.sh, Caddy, Traefik ([[traefik]]), cert-manager ([[cert-manager]]) on Kubernetes.
- Certificates are short-lived (90 days or less). Automate renewal and monitor expiry.

## Hardening Checklist
- Enable TLS 1.2 and 1.3 only.
- Use ECDHE key exchange and AEAD ciphers.
- Serve the full chain (leaf plus intermediates, not the root).
- Send `Strict-Transport-Security` once HTTPS is solid.
- Redirect HTTP to HTTPS.
- Test at [SSL Labs](https://www.ssllabs.com/ssltest/).

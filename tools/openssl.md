# OpenSSL
OpenSSL is a toolkit for TLS and general-purpose cryptography. See [[tls]], [[tls-handshake]], [[ssl-certs]] and [[certutil]].

## Private Keys and CSRs
COMMAND | DESCRIPTION
---|---
`openssl genrsa -out key.pem 4096` | Generate a 4096-bit RSA key
`openssl ecparam -genkey -name prime256v1 -noout -out key.pem` | Generate an ECDSA P-256 key
`openssl genpkey -algorithm ed25519 -out key.pem` | Generate an Ed25519 key
`openssl req -new -key key.pem -out req.csr` | Create a CSR from a key
`openssl req -new -newkey rsa:4096 -nodes -keyout key.pem -out req.csr` | Create key and CSR in one go
`openssl req -new -key key.pem -out req.csr -subj "/C=GB/O=Example/CN=example.com" -addext "subjectAltName=DNS:example.com,DNS:www.example.com"` | CSR with SANs, non-interactive

## Self-Signed Certificates
COMMAND | DESCRIPTION
---|---
`openssl req -x509 -newkey rsa:4096 -nodes -keyout key.pem -out cert.pem -days 365 -subj "/CN=localhost" -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"` | Self-signed cert with SANs
`openssl x509 -req -in req.csr -signkey key.pem -out cert.pem -days 365` | Self-sign an existing CSR

## Inspecting Files
COMMAND | DESCRIPTION
---|---
`openssl x509 -in cert.pem -noout -text` | Full certificate details
`openssl x509 -in cert.pem -noout -subject -issuer -dates` | Subject, issuer and validity
`openssl x509 -in cert.pem -noout -fingerprint -sha256` | SHA-256 fingerprint
`openssl x509 -in cert.pem -noout -ext subjectAltName` | Show SANs
`openssl req -in req.csr -noout -text -verify` | Inspect and verify a CSR
`openssl verify -CAfile ca.pem cert.pem` | Verify a cert against a CA
`openssl crl2pkcs7 -nocrl -certfile chain.pem \| openssl pkcs7 -print_certs -noout` | List every cert in a bundle

## Checking a Key Matches a Certificate
COMMAND | DESCRIPTION
---|---
`openssl x509 -in cert.pem -noout -pubkey \| openssl sha256` | Hash of the certificate's public key
`openssl pkey -in key.pem -pubout \| openssl sha256` | Hash of the key's public key. Must match the line above

## Remote Servers
COMMAND | DESCRIPTION
---|---
`openssl s_client -connect example.com:443 -servername example.com` | Open a TLS connection and show the chain
`openssl s_client -connect example.com:443 -servername example.com </dev/null 2>/dev/null \| openssl x509 -noout -dates` | Expiry of a remote cert
`openssl s_client -connect example.com:443 -tls1_2` | Test a specific TLS version
`openssl s_client -connect example.com:443 -showcerts` | Print the full chain
`openssl s_client -starttls smtp -connect mail.example.com:587` | TLS over STARTTLS (smtp, imap, pop3, ftp)
`echo \| openssl s_client -connect example.com:443 2>/dev/null \| openssl x509 -noout -checkend 2592000` | Exit non-zero if expiring within 30 days

## Format Conversion
COMMAND | DESCRIPTION
---|---
`openssl x509 -in cert.der -inform der -out cert.pem` | DER to PEM
`openssl x509 -in cert.pem -outform der -out cert.der` | PEM to DER
`openssl pkcs12 -export -out bundle.pfx -inkey key.pem -in cert.pem -certfile chain.pem` | PEM to PKCS#12 (.pfx)
`openssl pkcs12 -in bundle.pfx -nodes -out all.pem` | PKCS#12 to PEM (unencrypted)
`openssl rsa -in key.pem -out key-nopass.pem` | Remove a key passphrase

## Hashing, Encoding and Random Data
COMMAND | DESCRIPTION
---|---
`openssl rand -base64 32` | 32 random bytes, base64
`openssl rand -hex 16` | 16 random bytes, hex
`openssl dgst -sha256 file` | SHA-256 of a file
`openssl base64 -in file -out file.b64` | Base64 encode (`-d` to decode)
`openssl enc -aes-256-cbc -pbkdf2 -salt -in file -out file.enc` | Encrypt a file with a password
`openssl enc -d -aes-256-cbc -pbkdf2 -in file.enc -out file` | Decrypt it
`openssl passwd -6 <PASSWORD>` | SHA-512 crypt hash for `/etc/shadow`
`openssl dhparam -out dhparams.pem 2048` | Generate DH parameters

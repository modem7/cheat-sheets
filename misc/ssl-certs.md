# SSL Certificates Cheat-Sheet

X.509 is an ITU standard defining the format of public key certificates. X.509 certificates are used in TLS/SSL, the basis for HTTPS. An X.509 certificate binds an identity to a public key using a digital signature. A certificate contains an identity (hostname, organization, etc.) and a public key (RSA, DSA, ECDSA, ed25519, etc.), and is either signed by a Certificate Authority or is Self-Signed.

See [TLS (Transport Layer Security)](../networking/tls.md), [TLS Handshake](../networking/tls-handshake.md), [SSL Security Cheat-Sheet](ssl-security.md) and [OpenSSL](../tools/openssl.md). In Kubernetes, [Cert-Manager](../apps/cert-manager.md) automates issuing and renewal.

## Self-Signed Certificates

### Quick Single Certificate
One command for a self-signed certificate with a subject alternative name (OpenSSL 1.1.1 or later). Browsers ignore the CN and require the SAN:
```bash
openssl req -x509 -newkey rsa:4096 -sha256 -days 365 -nodes \
  -keyout key.pem -out cert.pem \
  -subj "/CN=your-dns.record" \
  -addext "subjectAltName=DNS:your-dns.record,IP:192.0.2.10"
```
`-nodes` leaves the private key unencrypted. Self-signed certificates must be trusted by hand on each client, so a private CA (below) is better when you have several hosts.

### Generate CA
1. Generate an encrypted RSA key
```bash
openssl genrsa -aes256 -out ca-key.pem 4096
```
2. Generate a public CA certificate
```bash
openssl req -new -x509 -sha256 -days 3650 -key ca-key.pem -out ca.pem
```

### Generate Certificate
1. Create an RSA key
```bash
openssl genrsa -out cert-key.pem 4096
```
2. Create a Certificate Signing Request (CSR)
```bash
openssl req -new -sha256 -subj "/CN=yourcn" -key cert-key.pem -out cert.csr
```
3. Create an `extfile` with all the alternative names (use `>` so a rerun does not append duplicates)
```bash
echo "subjectAltName=DNS:your-dns.record,IP:192.0.2.10" > extfile.cnf
```
```bash
# optional
echo "extendedKeyUsage = serverAuth" >> extfile.cnf
```
4. Create the certificate
```bash
openssl x509 -req -sha256 -days 365 -in cert.csr -CA ca.pem -CAkey ca-key.pem -out cert.pem -extfile extfile.cnf -CAcreateserial
```
Keep `ca-key.pem` private and offline if you can. Anyone with it can issue certificates your devices trust.

## Certificate Formats

X.509 certificates exist in Base64 formats **PEM (.pem, .crt, .ca-bundle)**, **PKCS#7 (.p7b, .p7s)** and binary formats **DER (.der, .cer)**, **PKCS#12 (.pfx, .p12)**.

### Convert Certs

COMMAND | CONVERSION
---|---
`openssl x509 -outform der -in cert.pem -out cert.der` | PEM to DER
`openssl x509 -inform der -in cert.der -out cert.pem` | DER to PEM
`openssl pkcs12 -in cert.pfx -out cert.pem -nodes` | PFX to PEM (key and cert)
`openssl pkcs12 -export -out cert.pfx -inkey cert-key.pem -in cert.pem -certfile ca.pem` | PEM to PFX

## Inspect and Verify Certificates
COMMAND | DESCRIPTION
---|---
`openssl verify -CAfile ca.pem -verbose cert.pem` | Verify against the CA
`openssl x509 -in cert.pem -noout -text` | Show everything
`openssl x509 -in cert.pem -noout -subject -issuer -dates` | Subject, issuer, validity
`openssl x509 -in cert.pem -noout -ext subjectAltName` | Show the SANs
`openssl x509 -in cert.pem -noout -fingerprint -sha256` | Fingerprint
`openssl s_client -connect host:443 -servername host </dev/null \| openssl x509 -noout -dates` | Check a live server
`openssl x509 -in cert.pem -noout -modulus \| openssl md5` | Compare with the key's modulus to check they match (use `openssl rsa -in key.pem -noout -modulus \| openssl md5`)

## Install the CA Cert as a trusted root CA

### On Debian & Derivatives
- Copy the CA certificate (`ca.pem`) to `/usr/local/share/ca-certificates/ca.crt` (the extension must be `.crt`).
- Update the cert store with:
```bash
sudo update-ca-certificates
```

Refer to the documentation [here](https://wiki.debian.org/Self-Signed_Certificate) and [here.](https://manpages.debian.org/buster/ca-certificates/update-ca-certificates.8.en.html)

### On Fedora
- Copy the CA certificate (`ca.pem`) to `/etc/pki/ca-trust/source/anchors/ca.pem` or `/usr/share/pki/ca-trust-source/anchors/ca.pem`
- Now run (with sudo if necessary):
```bash
sudo update-ca-trust
```

Refer to the documentation [here.](https://docs.fedoraproject.org/en-US/quick-docs/using-shared-system-certificates/)

### On Arch
System-wide, using p11-kit (from the Arch wiki):
- Run as root
```bash
trust anchor --store myCA.crt
```
- The certificate is written to `/etc/ca-certificates/trust-source/myCA.p11-kit` and the "legacy" directories are updated automatically.
- If you get "no configured writable location" or a similar error, import the CA manually: copy the certificate to the `/etc/ca-certificates/trust-source/anchors` directory and then run
```bash
sudo update-ca-trust
```
Wiki page [here](https://wiki.archlinux.org/title/User:Grawity/Adding_a_trusted_CA_certificate)

### On macOS
```bash
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain ca.pem
```
Or double-click the file to add it to Keychain Access, open it and set *Always Trust*.

### On Windows

Assuming the path to your generated CA certificate is `C:\ca.pem`, run in PowerShell as administrator:
```powershell
Import-Certificate -FilePath "C:\ca.pem" -CertStoreLocation Cert:\LocalMachine\Root
```
- Set `-CertStoreLocation` to `Cert:\CurrentUser\Root` if you want to trust certificates only for the logged-in user.

OR

In Command Prompt, run:
```sh
certutil.exe -addstore root C:\ca.pem
```

- `certutil.exe` is a built-in tool (see [Certutil](../tools/certutil.md)) and adds a system-wide trust anchor.

### In Firefox
Firefox uses its own store by default. Add the CA under Settings > Privacy & Security > View Certificates > Authorities > Import, or set `security.enterprise_roots.enabled` to `true` in `about:config` to use the system store.

### On Android

The exact steps vary between devices, but here is a general guide:
1. Open Phone Settings
2. Find the `Encryption and Credentials` section, generally under `Settings > Security > Encryption and Credentials`
3. Choose `Install a certificate`
4. Choose `CA Certificate`
5. Locate the certificate file `ca.pem` in internal storage using the file manager.
6. Select it to load it.
7. Done!

Since Android 7, apps ignore user-installed CAs unless they opt in, so browsers will trust it but many apps will not.

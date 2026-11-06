# Certutil
`certutil` is a Windows command-line tool for managing certificates and certificate stores. Run from an elevated prompt for machine-wide changes. For cross-platform work see [[openssl]], and for background see [[tls]] and [[ssl-certs]].

## Trusted Root Store
COMMAND | DESCRIPTION
---|---
`certutil -addstore -f "ROOT" new-root-certificate.crt` | Add a root certificate
`certutil -delstore "ROOT" serial-number-hex` | Delete a root certificate by serial number
`certutil -store ROOT` | List the root store
`certutil -store ROOT "<SERIAL-OR-NAME>"` | Show one certificate
`certutil -addstore -f "CA" intermediate.crt` | Add an intermediate CA
`certutil -user -addstore "ROOT" cert.crt` | Add to the current user store only

Common store names: `ROOT` (Trusted Root CAs), `CA` (Intermediate), `My` (Personal), `TrustedPublisher`, `AuthRoot`. Add `-user` for the user store, `-enterprise` for the enterprise store.

## Inspect and Verify
COMMAND | DESCRIPTION
---|---
`certutil -dump cert.crt` | Show certificate details
`certutil -verify -urlfetch cert.crt` | Verify the chain and fetch revocation info
`certutil -hashfile file.exe SHA256` | File hash (also `MD5`, `SHA1`, `SHA512`)
`certutil -store My` | List personal certificates

## PFX and Key Material
COMMAND | DESCRIPTION
---|---
`certutil -importpfx cert.pfx` | Import a PFX
`certutil -exportPFX -p "<PASSWORD>" My <SERIAL> out.pfx` | Export a certificate with its key
`certutil -repairstore My <SERIAL>` | Repair the key association

## Encoding and Conversion
COMMAND | DESCRIPTION
---|---
`certutil -encode in.bin out.b64` | Base64 encode a file
`certutil -decode in.b64 out.bin` | Base64 decode a file
`certutil -encodehex in.bin out.hex` | Hex encode
`certutil -decodehex in.hex out.bin` | Hex decode

## Network
COMMAND | DESCRIPTION
---|---
`certutil -urlcache -split -f <URL> <FILE>` | Download a file (often flagged by security tools, prefer `curl.exe` or `Invoke-WebRequest`)
`certutil -URL <URL>` | Open the URL retrieval tool
`certutil -ping` | Test connectivity to a CA

## PowerShell Equivalents
```powershell
Import-Certificate -FilePath .\root.crt -CertStoreLocation Cert:\LocalMachine\Root
Get-ChildItem Cert:\LocalMachine\Root | Select Subject, Thumbprint, NotAfter
Get-ChildItem Cert:\LocalMachine\My | Where NotAfter -lt (Get-Date).AddDays(30)
Remove-Item Cert:\LocalMachine\Root\<THUMBPRINT>
```
See [[powershell]].

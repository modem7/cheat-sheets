# TLS Handshake
In a TLS/SSL handshake, clients and servers exchange SSL certificates, cipher suite requirements, and randomly generated data for creating session keys.

TLS handshakes are a foundational part of how HTTPS works. The diagram below is the **TLS 1.2** handshake (two round trips after TCP). **TLS 1.3** needs only one.

SSL, or Secure Sockets Layer, was the original encryption protocol developed for HTTP. SSL was replaced by TLS, or Transport Layer Security, some time ago. SSL handshakes are now called TLS handshakes, although the "SSL" name is still in wide use.

```
┌───────────┐                ┌───────────┐
│  Client  │                │ 力 Server  │
└─────┬─────┘                └─────┬─────┘
      │                            │
      │                            │ 
      │ ─────────────────────────► │  ──┐
      │ 1. SYN                     │    │
      │                            │    │
      │                            │    │ TCP
      │ ◄───────────────────────── │    │
      │ 3. ACK          2. SYN ACK │  ──┘
      │                            │
      │ -------------------------- │
      │                            │
      │ ─────────────────────────► │  ──┐
      │ 4. ClientHello             │    │
      │                            │    │
      │ ◄───────────────────────── │    │
      │             5. ServerHello │    │
      │                Certificate │    │
      │            ServerHelloDone │    │
      │                            │    │ TLS
      │ ─────────────────────────► │    │
      │ 6. ClientKeyExchange       │    │
      │    ChangeCipherSpec        │    │
      │    Finished                │    │
      │                            │    │
      │ ◄───────────────────────── │    │
      │        7. ChangeCipherSpec │    │
      │           Finished         │  ──┘

```

## TLS 1.3
```
Client                                   Server
  │ ClientHello (versions, ciphers,        │
  │   key share, SNI)                      │
  │ ─────────────────────────────────────► │
  │                                        │
  │        ServerHello (key share)         │
  │        {EncryptedExtensions}           │
  │        {Certificate, CertificateVerify}│
  │        {Finished}                      │
  │ ◄───────────────────────────────────── │
  │ {Finished}                             │
  │ ─────────────────────────────────────► │
  │ Application data  ◄──────────────────► │
```
`{ }` marks encrypted messages. TLS 1.3 removes legacy ciphers, encrypts the certificate, and supports 0-RTT resumption (with replay caveats).

## Inspect a Handshake
COMMAND | DESCRIPTION
---|---
`openssl s_client -connect host:443 -servername host` | Handshake details, chain and negotiated cipher ([[openssl]])
`openssl s_client -connect host:443 -tls1_2` | Force TLS 1.2 (`-tls1_3` for 1.3)
`curl -v https://host` | Show the handshake summary ([[curl]])
`nmap --script ssl-enum-ciphers -p 443 host` | List supported versions and ciphers ([[nmap]])

See [[tls]], [[ssl-certs]] and [[ssl-security]].

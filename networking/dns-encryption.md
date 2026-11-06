# DNS Encryption
Ever since DNS was created in 1987, it has been largely unencrypted. Everyone between your device and the resolver is able to snoop on or even modify your DNS queries and responses.

Unencrypted DNS uses port 53, normally over UDP (and TCP for large answers).

Encrypting DNS makes it much harder for snoopers to look into your DNS messages, or to corrupt them in transit.

Two standardized mechanisms exist to secure the DNS transport between you and the resolver, DNS over TLS ([[dns-over-tls]]), and DNS queries over HTTPS ([[dns-over-https]]).

Both are based on Transport Layer Security ([[tls]]) which is also used to secure communication between you and a website using HTTPS.

DoT and DoH are now widely supported by browsers, operating systems and public resolvers, but many networks and home routers still use plain DNS by default.

## Legacy DNS (unencrypted)
```
  ┌─────────────────┐
  │   DNS Protocol  │
  ├─────────────────┤
  │   UDP Protocol  │
  │   (Port 53)     │
  ├─────────────────┤
  │   IP Protocol   │
  └─────────────────┘
```

## DNS over TLS
DNS over TLS, or DoT, is a standard for encrypting DNS queries to keep them secure and private. DoT uses the same security protocol, TLS, that HTTPS websites use to encrypt and authenticate communications. (TLS is also known as "SSL.") DoT wraps DNS in a TLS session over TCP port 853.

```
  ┌─────────────────┐ ──┐
  │   DNS Protocol  │   │  encrypted
  ├─────────────────┤   ├── traffic
  │  TLS Protocol  │   │   via TLS
  ├─────────────────┤ ──┘
  │   UDP Protocol  │
  │   (Port 853)    │
  ├─────────────────┤
  │   IP Protocol   │
  └─────────────────┘
```

## DNS over HTTPS
DNS over HTTPS, or DoH, is an alternative to DoT. With DoH, DNS queries and responses are encrypted, but they are sent via the HTTP or HTTP/2 protocols instead of a dedicated DNS port (443, like normal web traffic). 

Like DoT, DoH ensures that attackers can't forge or alter DNS traffic. DoH traffic looks like other HTTPS traffic – e.g. normal user-driven interactions with websites and web apps – from a network administrator's perspective.

```
  ┌─────────────────┐ ──┐
  │ 爵 HTTP Protocol │   │  encrypted
  ├─────────────────┤   ├── traffic
  │  TLS Protocol  │   │   via HTTPS
  ├─────────────────┤ ──┘
  │   TCP Protocol  │
  │   (Port 443)    │
  ├─────────────────┤
  │   IP Protocol   │
  └─────────────────┘

  GET/POST
  url/dns-request?dns-...
```

Test with `kdig -d @1.1.1.1 +tls-host=cloudflare-dns.com example.com` (DoT, needs knot-dnsutils) or `curl -H 'accept: application/dns-json' 'https://cloudflare-dns.com/dns-query?name=example.com&type=A'` (DoH). See [[dns-record-types]].

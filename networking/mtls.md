# mTLS (Mutual TLS)
In ordinary TLS only the server proves its identity. With **mutual TLS** the client also presents a certificate, and the server checks it against a CA it trusts. Use it to lock a service to known devices or services without passwords: admin UIs behind a reverse proxy, service-to-service calls and API clients. General TLS background is in [TLS (Transport Layer Security)](tls.md) and [TLS Handshake](tls-handshake.md).

Documentation: [OpenSSL](https://docs.openssl.org/) · [curl --cert](https://curl.se/docs/manpage.html#--cert)

> **Verification:** the OpenSSL, curl and `s_client` commands were run against a local `openssl s_server` test. The proxy settings were checked against each project's documentation, not run. Per-proxy sections: [Nginx](../apps/nginx.md#mtls-client-certificates), [Traefik](../apps/traefik.md#mtls-client-certificates), [HAProxy](../apps/haproxy.md#mtls-client-certificates).

## How It Works
1. The server asks the client for a certificate during the handshake.
2. The client sends its certificate and proves it holds the private key.
3. The server verifies the chain against its **client CA** and, if it passes, lets the connection through.

The client CA is separate from the CA that signed the server certificate, so a private CA is the usual choice. Keep the CA key offline, and give each client its own short-lived certificate so one can be revoked on its own.

## Create a Private CA
COMMAND | DESCRIPTION
---|---
`openssl req -x509 -newkey rsa:4096 -nodes -days 365 -keyout ca.key -out ca.crt -subj "/CN=Example Homelab CA"` | Self-signed CA key and certificate

## Issue a Client Certificate
```bash
printf 'extendedKeyUsage=clientAuth\nkeyUsage=digitalSignature\n' > client-ext.cnf
openssl req -newkey rsa:2048 -nodes -keyout client.key -out client.csr -subj "/CN=alice"
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -days 90 -out client.crt -extfile client-ext.cnf
```

COMMAND | DESCRIPTION
---|---
`openssl verify -CAfile ca.crt client.crt` | Check the client certificate against the CA
`openssl x509 -in client.crt -noout -subject -enddate -ext extendedKeyUsage` | Show subject, expiry and usage
`openssl pkcs12 -export -inkey client.key -in client.crt -out client.p12` | Bundle for importing into a browser or phone (prompts for a password)

## Test a Connection
COMMAND | DESCRIPTION
---|---
`curl --cacert <SERVER_CA> --cert client.crt --key client.key https://<HOST>/` | Request with a client certificate
`curl --cacert <SERVER_CA> https://<HOST>/` | Without one, to confirm it is refused
`openssl s_client -connect <HOST>:443 -servername <HOST> -cert client.crt -key client.key` | Inspect the handshake with a client certificate
`openssl s_server -accept 8443 -cert srv.crt -key srv.key -CAfile ca.crt -Verify 1 -www` | Throwaway test server that requires a client certificate

`--cacert` is the CA that signed the **server** certificate, not the client CA. A request with no certificate to a server that requires one fails at the TLS layer, and curl exits non-zero without an HTTP status.

## Caddy
No separate Caddy sheet exists here, so the Caddyfile settings are below.

```text
example.com {
    tls {
        client_auth {
            mode require_and_verify
            trust_pool file /etc/caddy/ca.crt
        }
    }
    reverse_proxy localhost:4000
}
```

Modes: `request`, `require`, `verify_if_given`, `require_and_verify`. To present a client certificate to a backend, put `tls_client_auth <CERT> <KEY>` and `tls_trust_pool file <CA>` inside `transport http { }` in `reverse_proxy`. Older configs use `trusted_ca_cert_file`, which the current docs page does not mention *(not confirmed as deprecated)*. Documentation: [tls](https://caddyserver.com/docs/caddyfile/directives/tls) · [reverse_proxy](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy)

## Tips
- Give client certificates the `clientAuth` extended key usage, as above.
- Keep lifetimes short and track expiry. Certificate revocation lists need extra setup (see each proxy's `crl` option).
- Pass the verified identity on to the app with a header, and make sure the proxy overwrites any copy sent by the client.
- Do not put the client CA's private key on the proxy. It only needs `ca.crt`.

## See Also
- [TLS (Transport Layer Security)](tls.md)
- [OpenSSL](../tools/openssl.md)
- [SSL Security Cheat-Sheet](../misc/ssl-security.md)
- [Nginx](../apps/nginx.md)
- [Traefik](../apps/traefik.md)
- [HAProxy](../apps/haproxy.md)

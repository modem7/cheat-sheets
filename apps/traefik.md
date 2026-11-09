# Traefik
Traefik is an open-source Edge Router for **[Docker](../docker/docker.md)**, and **[Kubernetes](../kubernetes/kubernetes.md)** that makes publishing your services a fun and easy experience. It receives requests on behalf of your system and finds out which components are responsible for handling them.

Documentation & Project Homepage: [Traefik Docs](https://doc.traefik.io/traefik/)

Two kinds of configuration: **static** (`traefik.yml` or CLI flags: entrypoints, providers, resolvers, log) is read at start-up; **dynamic** (routers, services, middlewares, TLS, from labels, the file provider or Kubernetes) reloads live.

---
## Run with Docker Compose
```yaml
services:
  traefik:
    image: traefik:v3
    container_name: traefik
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./traefik.yml:/etc/traefik/traefik.yml:ro
      - ./acme:/acme
```
Mounting `docker.sock` (even read-only) is powerful. Consider a socket proxy for production.

---
## Dashboard and API
Enable it in the static configuration. Do not use `insecure: true` on anything reachable from outside.
```yaml
api:
  dashboard: true
  insecure: false
```
Expose it through a router with authentication (labels on the Traefik container):
```yaml
- "traefik.enable=true"
- "traefik.http.routers.dashboard.rule=Host(`traefik.example.com`)"
- "traefik.http.routers.dashboard.entrypoints=websecure"
- "traefik.http.routers.dashboard.tls.certresolver=yourresolver"
- "traefik.http.routers.dashboard.service=api@internal"
- "traefik.http.routers.dashboard.middlewares=dashboard-auth"
# generate with: htpasswd -nB admin   (double every $ as $$ in labels)
- "traefik.http.middlewares.dashboard-auth.basicauth.users=admin:$$2y$$05$$..."
```

---
## EntryPoints
Ports Traefik listens on.

### HTTP Redirection
```yaml
entryPoints:
  web:
    address: :80
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
```

### HTTPS
```yaml
entryPoints:
  websecure:
    address: :443
    http:
      tls:
        certResolver: yourresolver
```
Setting `tls.certResolver` on the entrypoint makes it the default for every router on it.

---
## Routers
Docker labels. `router` is a name you choose.

LABEL | DESCRIPTION
---|---
`traefik.enable=true` | Expose this container (needed when `exposedByDefault: false`)
`traefik.http.routers.router.entrypoints=websecure` | Entrypoint for the router. Use together with `tls`
`traefik.http.routers.router.rule=Host(`app.example.com`)` | Match rule (also `PathPrefix`, `Headers`, `&&`, `\|\|`)
`traefik.http.routers.router.tls=true` | Enable TLS on the router
`traefik.http.routers.router.tls.certresolver=yourresolver` | Certificate resolver for the router
`traefik.http.routers.router.middlewares=mw1,mw2` | Attach middlewares
`traefik.http.services.router.loadbalancer.server.port=8080` | Container port to forward to (needed if the image exposes several or none)

### PathPrefix and StripPrefix
```yml
- "traefik.enable=true"
- "traefik.http.routers.nginx-test.entrypoints=websecure"
- "traefik.http.routers.nginx-test.tls=true"
- "traefik.http.routers.nginx-test.rule=PathPrefix(`/nginx-test`)"
- "traefik.http.routers.nginx-test.middlewares=nginx-test"
- "traefik.http.middlewares.nginx-test.stripprefix.prefixes=/nginx-test"
```

---
## Middlewares
Common ones, as labels (`name` is yours):
```yml
# redirect to a different scheme or host
- "traefik.http.middlewares.name.redirectscheme.scheme=https"
# basic auth
- "traefik.http.middlewares.name.basicauth.users=user:$$apr1$$..."
# security headers
- "traefik.http.middlewares.name.headers.stsSeconds=31536000"
# rate limit
- "traefik.http.middlewares.name.ratelimit.average=100"
# allow only some source IPs (v3 name)
- "traefik.http.middlewares.name.ipallowlist.sourcerange=192.168.0.0/16"
```
Traefik v2 names the last one `ipwhitelist`.

---
## CertificatesResolvers

### httpChallenge
```yaml
certificatesResolvers:
  yourresolver:
    acme:
      email: "your-mail-address"
      storage: /acme/acme.json
      httpChallenge:
        entryPoint: web
```

### dnsChallenge
DNS providers such as `cloudflare`, `digitalocean`, `civo`, and more. For the full list and the environment variables each needs, see the [Traefik ACME Documentation](https://doc.traefik.io/traefik/https/acme/). Required for wildcard certificates.

```yaml
certificatesResolvers:
  yourresolver:
    acme:
      email: "your-mail-address"
      storage: /acme/acme.json
      # caServer: https://acme-staging-v02.api.letsencrypt.org/directory  # for testing
      dnsChallenge:
        provider: your-dns-provider
        resolvers:
          - "1.1.1.1:53"
```
Provider credentials are passed as environment variables, e.g. `CF_DNS_API_TOKEN` for Cloudflare. `acme.json` must have permissions `600`. See also [Cert-Manager](cert-manager.md) for the Kubernetes-native alternative.

---
## ServersTransport

### InsecureSkipVerify
To skip TLS verification from **Traefik** to your backend servers (for example self-signed backends), add this to the static config:
```yaml
serversTransport:
  insecureSkipVerify: true
```

---
## TLS Settings
Dynamic configuration (file provider).

### defaultCertificates
```yaml
tls:
  stores:
    default:
      defaultCertificate:
        certFile: /your-traefik-cert.crt
        keyFile: /your-traefik-key.key
```

### options
Set a minimum TLS version (this disables TLS 1.0 and 1.1). See [SSL Security Cheat-Sheet](../misc/ssl-security.md).
```yaml
tls:
  options:
    default:
      minVersion: VersionTLS12
```

### mTLS (Client Certificates)
Define a TLS option that requires client certificates (dynamic config), then attach it to a router. See [mTLS (Mutual TLS)](../networking/mtls.md) for creating the CA and client certificates.
```yaml
tls:
  options:
    mtls:
      clientAuth:
        caFiles:
          - /certs/ca.crt
        clientAuthType: RequireAndVerifyClientCert
```

`clientAuthType` | MEANING
---|---
`NoClientCert` | Do not ask for a certificate
`RequestClientCert` | Ask, but accept none or an unverified one
`RequireAnyClientCert` | Require one, not verified against the CA
`VerifyClientCertIfGiven` | Optional, but verified if sent
`RequireAndVerifyClientCert` | Required and verified (what mTLS normally means)

Attach it with a label, or `tls: options: mtls` in a file-provider router:
```yaml
labels:
  - traefik.http.routers.app.tls=true
  - traefik.http.routers.app.tls.options=mtls@file
```

Pass the client certificate to the backend with the `passTLSClientCert` middleware (sets `X-Forwarded-Tls-Client-Cert` and `X-Forwarded-Tls-Client-Cert-Info`):
```yaml
http:
  middlewares:
    pass-cert:
      passTLSClientCert:
        pem: true
```

To present a client certificate **to** a backend, use a ServersTransport (`certificates` takes a list of paths, `rootCAs` the backend CA) and set `loadBalancer.serversTransport` on the service.

Documentation: [TLS options](https://doc.traefik.io/traefik/reference/routing-configuration/http/tls/tls-options/) · [PassTLSClientCert](https://doc.traefik.io/traefik/reference/routing-configuration/http/middlewares/passtlsclientcert/) · [ServersTransport](https://doc.traefik.io/traefik/reference/routing-configuration/http/load-balancing/serverstransport/)

---
## Providers

### File
```yaml
providers:
  file:
    directory: /etc/traefik/dynamic
    watch: true
```

### Docker
With `exposedByDefault: false`, Traefik won't expose any containers unless they carry the label `traefik.enable=true`.

```yaml
providers:
  docker:
    exposedByDefault: false
    network: proxy   # network shared with Traefik when a container has several
```

### Kubernetes
```yaml
providers:
  kubernetesCRD: {}      # IngressRoute, Middleware and other CRDs
  kubernetesIngress: {}  # standard Ingress objects
```
Traefik's CRD API group is `traefik.io/v1alpha1` (v3 and later v2 releases); older v2 uses `traefik.containo.us/v1alpha1`. [K3s](../kubernetes/k3s.md) ships Traefik by default. For an `IngressRoute` example see [Argo CD](argocd.md).

---
## Log
```yaml
log:
  level: ERROR   # DEBUG when troubleshooting
accessLog: {}    # enable the access log
```

---
## Global
```yaml
global:
  checkNewVersion: true
  sendAnonymousUsage: false
```

---
## Troubleshooting
COMMAND | DESCRIPTION
---|---
`docker logs traefik` | Start-up and routing errors
`curl -s http://localhost:8080/api/http/routers` | List routers (needs the API on 8080, keep it private)
`traefik healthcheck --ping` | Health check (needs `ping: {}` in the static config)
- `404 page not found`: no router matched. Check the Host rule, entrypoint and that the container is on the same Docker network.
- `Bad Gateway` (502): wrong backend port, set `loadbalancer.server.port`.
- Certificate not issued: check `docker logs traefik` for ACME errors and that `acme.json` is `chmod 600`.

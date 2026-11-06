# Reverse Proxy Patterns
How to put a reverse proxy in front of homelab services, with the same task shown in Traefik, Nginx and Caddy: routing by hostname, a wildcard certificate through the ACME DNS-01 challenge, split-horizon DNS and internal-only services. Tool-specific detail lives in [Traefik](../apps/traefik.md), [Nginx](../apps/nginx.md) and [Cert-Manager](../apps/cert-manager.md); this sheet is about choosing and combining them.

Documentation: [Traefik ACME](https://doc.traefik.io/traefik/https/acme/) · [Caddy automatic HTTPS](https://caddyserver.com/docs/automatic-https) · [certbot DNS plugins](https://eff-certbot.readthedocs.io/en/stable/using.html#dns-plugins) · [Let's Encrypt challenge types](https://letsencrypt.org/docs/challenge-types/)

> **Verification:** snippets were written from the upstream documentation and **not executed**. Check image tags, provider names and DNS-plugin options against the current docs before use.

See also: [Homelab](homelab.md) · [Pi-hole](pihole.md) · [AdGuard Home](adguard-home.md) · [Unbound](unbound.md) · [VLANs](vlans.md) · [Tailscale](../apps/tailscale.md) · [WireGuard](../apps/wireguard.md) · [Docker-Compose](../docker/docker-compose.md) · [Docker Networking](../docker/docker-networking.md) · [TLS (Transport Layer Security)](../networking/tls.md) · [DNS Record Types](../networking/dns-record-types.md)

---
## Traefik vs Nginx vs Caddy
| | Traefik | Nginx | Caddy |
|---|---|---|---|
| Config model | Dynamic: Docker labels, file provider, Kubernetes | Static files, reload on change | Caddyfile or JSON, reload on change |
| Docker auto-discovery | Built in (labels) | No (use nginx-proxy or templates) | Via `caddy-docker-proxy` plugin |
| Automatic HTTPS | Yes (ACME resolvers) | No (use certbot or acme.sh) | Yes, on by default |
| DNS-01 / wildcard | Built in, many providers via lego | certbot DNS plugins or acme.sh | Needs a build with a DNS provider module |
| Dashboard | Yes | No (Nginx Proxy Manager adds a UI) | No |
| Best for | Many containers that come and go | Static sites, caching, fine control, non-HTTP via `stream` | Simplest config for a handful of services |
| Gotcha | Labels get long; Docker socket access is sensitive | Manual certificate renewal wiring | DNS provider needs `xcaddy` or the downloaded custom build |

Pick one edge proxy per host or per VLAN, and keep services on a private Docker network so only the proxy publishes ports 80/443 ([Docker Networking](../docker/docker-networking.md)).

---
## Wildcard Certificates via DNS-01
HTTP-01 needs port 80 reachable from the internet. DNS-01 proves control by creating a `_acme-challenge` TXT record through your DNS provider's API, so it works for **internal-only** hostnames and for wildcards (`*.home.example.com`). Use a scoped API token (edit DNS for that zone only), kept in an env file or Docker secret, never in the compose file.

### Traefik
`traefik.yml` (static):
```yaml
entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint: { to: websecure, scheme: https }
  websecure:
    address: ":443"
    http:
      tls:
        certResolver: le
        domains:
          - main: "home.example.com"
            sans: ["*.home.example.com"]
certificatesResolvers:
  le:
    acme:
      email: admin@example.com
      storage: /letsencrypt/acme.json
      dnsChallenge:
        provider: cloudflare
        resolvers: ["1.1.1.1:53", "1.0.0.1:53"]
providers:
  docker:
    exposedByDefault: false
```
Compose side:
```yaml
services:
  traefik:
    image: traefik:v3
    restart: unless-stopped
    ports: ["80:80", "443:443"]
    env_file: .env            # CF_DNS_API_TOKEN=<TOKEN>
    volumes:
      - ./traefik.yml:/etc/traefik/traefik.yml:ro
      - ./letsencrypt:/letsencrypt
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks: [proxy]
  whoami:
    image: traefik/whoami
    labels:
      - traefik.enable=true
      - traefik.http.routers.whoami.rule=Host(`whoami.home.example.com`)
      - traefik.http.routers.whoami.entrypoints=websecure
    networks: [proxy]
networks:
  proxy:
    name: proxy
```
`chmod 600 letsencrypt/acme.json` if you create it yourself. Provider names and env variables are listed in the [lego DNS provider docs](https://go-acme.github.io/lego/dns/).

### Caddy
The stock binary has no DNS providers. Build one with the module, or use a prebuilt image that includes it:
```bash
xcaddy build --with github.com/caddy-dns/cloudflare
```
`Caddyfile`:
```
*.home.example.com {
    tls {
        dns cloudflare {env.CF_API_TOKEN}
    }

    @grafana host grafana.home.example.com
    handle @grafana {
        reverse_proxy grafana:3000
    }

    @whoami host whoami.home.example.com
    handle @whoami {
        reverse_proxy whoami:80
    }

    handle {
        abort
    }
}
```
```bash
caddy validate --config /etc/caddy/Caddyfile
caddy reload --config /etc/caddy/Caddyfile
```

### Nginx with certbot
```bash
sudo apt install certbot python3-certbot-dns-cloudflare
printf 'dns_cloudflare_api_token = <TOKEN>\n' | sudo tee /etc/letsencrypt/cloudflare.ini >/dev/null
sudo chmod 600 /etc/letsencrypt/cloudflare.ini
sudo certbot certonly --dns-cloudflare \
  --dns-cloudflare-credentials /etc/letsencrypt/cloudflare.ini \
  -d home.example.com -d '*.home.example.com'
```
```nginx
server {
    listen 443 ssl;
    http2 on;                         # nginx 1.25.1+; older: "listen 443 ssl http2;"
    server_name grafana.home.example.com;

    ssl_certificate     /etc/letsencrypt/live/home.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/home.example.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;       # WebSockets
        proxy_set_header Connection $connection_upgrade;
    }
}
```
`$connection_upgrade` needs a `map` in the `http {}` block:
```nginx
map $http_upgrade $connection_upgrade { default upgrade; '' close; }
```
Renewals: `certbot renew --dry-run`, and a deploy hook `--deploy-hook "systemctl reload nginx"`.

### Staging first
Let's Encrypt rate-limits production. Test with the staging CA (`https://acme-staging-v02.api.letsencrypt.org/directory`: Traefik `caServer`, certbot `--staging`, Caddy `acme_ca` global option), then switch back.

---
## Split-Horizon DNS
Use the same hostname inside and outside the house: internal clients get the private IP, the internet gets the public IP or nothing.

APPROACH | HOW
---|---
Public zone has no record | Only the internal resolver knows `app.home.example.com` (nothing leaks, certificate still works via DNS-01)
Internal override | Local DNS record on [Pi-hole](pihole.md) / [AdGuard Home](adguard-home.md) / [Unbound](unbound.md) points the name or whole wildcard at the proxy IP
Wildcard rewrite | One record for `*.home.example.com` to the proxy IP, then routing happens by `Host` header in the proxy
Remote access | Reach the same names over [Tailscale](../apps/tailscale.md) or [WireGuard](../apps/wireguard.md); point the VPN DNS at the internal resolver

Wildcard to the proxy, three resolvers:
```
# Pi-hole v6: Settings -> Local DNS Records, or add to the config
pihole-FTL --config misc.dnsmasq_lines '["address=/home.example.com/192.168.20.10"]'

# AdGuard Home: Filters -> DNS rewrites
#   *.home.example.com  ->  192.168.20.10

# Unbound
local-zone: "home.example.com." redirect
local-data: "home.example.com. A 192.168.20.10"
```
`address=/domain/ip` and `redirect` both match the domain **and all subdomains**. Because an `A` answer is returned for every name, the proxy must reject unknown hosts (see the Caddy `abort` and the Traefik default 404).

Check from a client:
```bash
dig +short app.home.example.com @192.168.20.2        # internal resolver
dig +short app.home.example.com @1.1.1.1             # should be empty or public
```
Beware DNS rebinding protection: some routers and upstream resolvers drop answers that point to private ranges. Fix by using your own resolver, or add the domain to the rebind allow-list (for example `rebind-domain-ok=/home.example.com/` in dnsmasq).

---
## Internal-Only Services
GOAL | TECHNIQUE
---|---
Not reachable from the internet | Do not port-forward 80/443; use DNS-01 for certs; keep the public zone free of A records
Only from LAN or VPN | Traefik `ipAllowList` middleware (named `ipWhiteList` in v2), Nginx `allow 192.168.0.0/16; deny all;`, Caddy `@lan remote_ip private_ranges`
Separate entrypoints | Internal entrypoint bound to the LAN address (`address: "192.168.20.10:443"`), public one to the WAN side
Per-network proxies | One proxy instance on the public VLAN, one on the internal VLAN; see [VLANs](vlans.md)
Auth in front of apps | Forward-auth (Authelia, Authentik, oauth2-proxy) via Traefik `forwardAuth`, Nginx `auth_request`, Caddy `forward_auth`
Do not trust the header | Only trust `X-Forwarded-For` from your proxy: set `forwardedHeaders.trustedIPs` in Traefik, `set_real_ip_from` in Nginx

Traefik middleware example (labels):
```yaml
labels:
  - traefik.http.middlewares.lan-only.ipallowlist.sourcerange=192.168.0.0/16,100.64.0.0/10
  - traefik.http.routers.admin.rule=Host(`admin.home.example.com`)
  - traefik.http.routers.admin.middlewares=lan-only
```
Caddy:
```
admin.home.example.com {
    @denied not remote_ip private_ranges 100.64.0.0/10
    respond @denied 403
    reverse_proxy admin:8080
}
```
Nginx:
```nginx
location / {
    allow 192.168.0.0/16;
    allow 100.64.0.0/10;
    deny all;
    proxy_pass http://127.0.0.1:8080;
}
```

---
## Troubleshooting
SYMPTOM | CHECK
---|---
Certificate request fails with TXT lookup errors | Propagation: set the resolvers or delay (`propagation.delayBeforeChecks` in Traefik), and check split-horizon DNS is not hiding the public TXT record from the proxy's own resolver
`unauthorized` from DNS API | Token lacks Zone:DNS:Edit on the zone, or Zone:Zone:Read for the lookup
Browser shows the default Traefik cert | Router `Host()` rule does not match, or the router has no `tls`; check the dashboard
502 / 504 from proxy | Wrong upstream name or port, service on another Docker network, or the upstream listens on `127.0.0.1` only
Redirect loop | App behind the proxy thinks it is plain HTTP; set the forwarded proto header or the app's "trusted proxy" option
Works internally, fails externally | DNS is correct, but 443 is not forwarded, or the firewall blocks it ([UFW (uncomplicated firewall)](../linux/ufw.md))
Rate limited by Let's Encrypt | Use the staging CA while testing; wildcard reduces the number of certificates
`curl -vk --resolve app.home.example.com:443:192.168.20.10 https://app.home.example.com` | Test the proxy directly, bypassing DNS

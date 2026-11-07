# Cloudflare
Cloudflare for self-hosters: DNS and proxying, API tokens, Tunnel to expose services without opening ports, R2 object storage with no egress fees, Workers via `wrangler`, and ACME DNS-01 tokens for certificates.

Documentation: [Cloudflare Docs](https://developers.cloudflare.com/) · [Wrangler commands](https://developers.cloudflare.com/workers/wrangler/commands/) · [R2 pricing](https://developers.cloudflare.com/r2/pricing/) · [Terraform Cloudflare provider](https://registry.terraform.io/providers/cloudflare/cloudflare/latest) (see [Terraform](../../tools/terraform.md))

> **Verification:** commands and limits were checked against the Cloudflare developer docs and the certbot and lego plugin docs (November 2026). Nothing was run against an account. Items marked *(unverified)* were not confirmed.

## Services a Self-Hoster Uses
NEED | SERVICE | NOTES
---|---|---
DNS | Cloudflare DNS | Free, with an API
Reach a service without port forwarding | Tunnel (`cloudflared`) | Outbound-only connection
Access control | Zero Trust Access | Free plan covers 50 users
Object storage | R2 | S3-compatible, no egress fees
Small serverless apps | Workers, KV | `wrangler` CLI
Domain registration | Registrar | At cost, no markup
Certificates | DNS-01 challenge | Scoped API token

## API Tokens
Create a scoped API token in the dashboard (My Profile, API Tokens). Avoid the legacy Global API Key.

TOKEN USE | PERMISSIONS
---|---
DNS records only (ACME DNS-01, scripts) | Zone, DNS, Edit
Zone lookup by name (some clients) | Zone, Zone, Read

Scope the token to specific zones. Source for the ACME scopes: [lego Cloudflare provider](https://go-acme.github.io/lego/dns/cloudflare/) (`CF_DNS_API_TOKEN` needs Zone/DNS/Edit and `CF_ZONE_API_TOKEN` needs Zone/Zone/Read). The Traefik and Caddy docs do not state scopes *(unverified for those)*.

Cloudflare expects `Authorization: Bearer <TOKEN>`; `curl --oauth2-bearer` sends exactly that, with the token read from an environment variable (keep it out of shell history).

COMMAND | DESCRIPTION
---|---
`curl https://api.cloudflare.com/client/v4/user/tokens/verify --oauth2-bearer "$CLOUDFLARE_API_TOKEN"` | Check a token is valid
`curl https://api.cloudflare.com/client/v4/zones/<ZONE_ID>/dns_records --oauth2-bearer "$CLOUDFLARE_API_TOKEN"` | List DNS records (`GET /zones/{zone_id}/dns_records`)

Create a record (`POST /zones/{zone_id}/dns_records`). The fields `type`, `name`, `content`, `ttl` and `proxied` are documented; `ttl: 1` means automatic. The full request body below is *partly verified*:

```bash
curl -X POST "https://api.cloudflare.com/client/v4/zones/ZONE_ID/dns_records" \
  --oauth2-bearer "$CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"type":"A","name":"app.example.com","content":"203.0.113.10","ttl":1,"proxied":true}'
```

See [DNS Record Types](../../networking/dns-record-types.md) for record meanings.

## Proxied Records
- An orange-cloud (proxied) record sends traffic through Cloudflare, hiding your origin IP and adding caching.
- The Free plan limits uploads through the proxy to 100 MB ([default cache behaviour](https://developers.cloudflare.com/cache/concepts/default-cache-behavior/)).
- The service-specific terms restrict serving video or a disproportionate share of large files through the proxy on the self-serve plans ([terms](https://www.cloudflare.com/service-specific-terms-application-services/)). Check them before proxying a media server such as Plex or Jellyfin.
- Non-HTTP services (SSH, game servers) need a grey-cloud (DNS only) record or a Tunnel/Spectrum.

## Tunnel (cloudflared)
Tunnel connects out from your network to Cloudflare, so no inbound ports need opening.

COMMAND | DESCRIPTION
---|---
`cloudflared tunnel login` | Authenticate and download a certificate
`cloudflared tunnel create <NAME>` | Create a tunnel and its credentials file
`cloudflared tunnel route dns <NAME> app.example.com` | Point a hostname at the tunnel
`cloudflared tunnel run <NAME>` | Run the tunnel
`sudo cloudflared service install <TOKEN>` | Install as a service using a token from the dashboard
`cloudflared tunnel ingress validate` | Validate the ingress rules in the config file

Ingress config (`config.yml`); the last rule must be a catch-all:

```yaml
tunnel: TUNNEL_ID
credentials-file: /etc/cloudflared/TUNNEL_ID.json

ingress:
  - hostname: app.example.com
    service: http://localhost:8080
  - service: http_status:404
```

Running with a token on the command line or in Docker is *not verified* here. For reverse proxy setups see [Traefik](../../apps/traefik.md).

## Wrangler (Workers, R2, KV)
Install with npm (see [Node.js and npm](../../tools/node-npm.md)).

COMMAND | DESCRIPTION
---|---
`wrangler login` | Authenticate in a browser
`wrangler whoami` | Show the logged-in account
`wrangler init [NAME]` | Create a project
`wrangler dev [SCRIPT]` | Run locally
`wrangler deploy [PATH]` | Deploy a Worker
`wrangler tail [WORKER]` | Stream logs
`wrangler secret put <KEY>` | Set a secret for a Worker
`wrangler kv namespace create <NAME>` | Create a KV namespace
`wrangler r2 bucket create <NAME>` | Create an R2 bucket
`wrangler r2 bucket list` | List buckets
`wrangler r2 bucket delete <BUCKET>` | Delete a bucket (destructive)
`wrangler r2 object put <BUCKET>/<KEY> --file <FILE>` | Upload an object
`wrangler r2 object get <BUCKET>/<KEY>` | Download an object

## R2 Object Storage
- Free tier: 10 GB-month storage, 1 million Class A and 10 million Class B operations per month. No egress fees ([R2 pricing](https://developers.cloudflare.com/r2/pricing/)).
- S3 endpoint: `https://<ACCOUNT_ID>.r2.cloudflarestorage.com`, region `auto` ([AWS CLI example](https://developers.cloudflare.com/r2/examples/aws/aws-cli/)).
- Create an R2 API token with access to specific buckets; the access key and secret are shown once.

```bash
aws s3 ls --endpoint-url https://ACCOUNT_ID.r2.cloudflarestorage.com --region auto
```

Use R2 as a backup target with [restic](../../backup/restic.md) or [rclone](../../backup/rclone.md).

## Certificates with DNS-01
certbot with the Cloudflare plugin reads a credentials file (keep it `chmod 600`):

```ini
dns_cloudflare_api_token = API_TOKEN
```

```bash
certbot certonly --dns-cloudflare --dns-cloudflare-credentials /path/to/cloudflare.ini -d example.com
```

Source: [certbot-dns-cloudflare](https://certbot-dns-cloudflare.readthedocs.io/en/stable/). Kubernetes users see [Cert-Manager](../../apps/cert-manager.md).

## Pitfalls
PITFALL | DETAIL
---|---
Global API Key | Full account access; use scoped tokens
Token in shell history or Git | Use environment variables or a secrets manager
Proxying a media server | May breach the service terms and hits upload and caching limits
Tunnel as a single point | If `cloudflared` stops, the hostnames go offline
Zero Trust free plan | 50 users (check current limits on the Cloudflare plans page)

## See Also
- [Cloud-Provider Comparison](cloud-provider-comparison.md)
- [DNS Record Types](../../networking/dns-record-types.md)
- [Traefik](../../apps/traefik.md)
- [Cert-Manager](../../apps/cert-manager.md)
- [Node.js and npm](../../tools/node-npm.md)
- [Terraform](../../tools/terraform.md)

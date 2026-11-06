# Keycloak
Keycloak is an open source identity and access management server (CNCF project) providing SSO, OIDC, OAuth2, SAML, user federation (LDAP/AD), social login and fine-grained authorisation. It is heavier than [authentik](authentik.md) but very widely supported. Users and config live in realms.

Documentation: [Keycloak Guides](https://www.keycloak.org/guides) · [Running in a container](https://www.keycloak.org/server/containers)

## Quick Start (dev only)
`start-dev` uses an embedded H2 database and plain HTTP; never use it in production.
```bash
docker run --rm -p 8080:8080 \
  -e KC_BOOTSTRAP_ADMIN_USERNAME=admin \
  -e KC_BOOTSTRAP_ADMIN_PASSWORD=<PASSWORD> \
  quay.io/keycloak/keycloak:<TAG> start-dev
```
Admin console: `http://localhost:8080`. (Releases before 26 used `KEYCLOAK_ADMIN` / `KEYCLOAK_ADMIN_PASSWORD`.)

## Production Compose with PostgreSQL
Behind a TLS-terminating reverse proxy ([Traefik](../apps/traefik.md), [Nginx](../apps/nginx.md)):
```yaml
services:
  keycloak:
    image: quay.io/keycloak/keycloak:<TAG>
    restart: unless-stopped
    command: start
    environment:
      KC_DB: postgres
      KC_DB_URL: jdbc:postgresql://db:5432/keycloak
      KC_DB_USERNAME: keycloak
      KC_DB_PASSWORD: ${KC_DB_PASSWORD}
      KC_HOSTNAME: https://sso.example.com
      KC_HTTP_ENABLED: "true"            # proxy terminates TLS
      KC_PROXY_HEADERS: xforwarded       # or "forwarded"
      KC_HEALTH_ENABLED: "true"
      KC_BOOTSTRAP_ADMIN_USERNAME: admin           # first start only
      KC_BOOTSTRAP_ADMIN_PASSWORD: ${KC_BOOTSTRAP_ADMIN_PASSWORD}
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "127.0.0.1:8080:8080"
  db:
    image: postgres:<TAG>
    restart: unless-stopped
    environment:
      POSTGRES_DB: keycloak
      POSTGRES_USER: keycloak
      POSTGRES_PASSWORD: ${KC_DB_PASSWORD}
    volumes:
      - kc-db:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U keycloak"]
      interval: 10s
      retries: 5
volumes:
  kc-db:
```
The bootstrap admin is temporary: log in, create a permanent admin user and delete it. See [Docker-Compose](../docker/docker-compose.md) and [PostgreSQL Cheat-Sheet](../databases/postgres.md).

### Important Settings
OPTION / ENV | DESCRIPTION
---|---
`start-dev` | Development mode (HTTP, H2, caches off)
`start` | Production mode; requires hostname and TLS or proxy settings
`build` then `start --optimized` | Pre-build for faster startup (custom images)
`KC_HOSTNAME` | Public URL or hostname clients see
`KC_PROXY_HEADERS` | `xforwarded` or `forwarded`, to trust proxy headers (replaces the deprecated `KC_PROXY`)
`KC_HTTP_ENABLED` | Allow plain HTTP (needed behind a TLS-terminating proxy)
`KC_DB` / `KC_DB_URL` | Database vendor and JDBC URL
`KC_HEALTH_ENABLED` / `KC_METRICS_ENABLED` | Health and Prometheus endpoints, see [Prometheus](../apps/prometheus.md)
`KC_LOG_LEVEL` | `info`, `debug`, ...

## Create a Realm and OIDC Client
1. Create a realm (don't use `master` for apps), e.g. `homelab`.
2. **Clients → Create client**: type *OpenID Connect*, a Client ID (e.g. `grafana`).
3. Turn **Client authentication** on (confidential), enable *Standard flow*.
4. Set **Valid redirect URIs** to the app's callback (avoid wildcards) and **Web origins**.
5. **Credentials** tab holds the client secret.
6. Add users under **Users**, groups under **Groups**; expose groups with a *Group Membership* mapper.

OIDC endpoints for realm `<REALM>` at `https://sso.example.com`:
ENDPOINT | URL
---|---
Discovery | `/realms/<REALM>/.well-known/openid-configuration`
Authorise | `/realms/<REALM>/protocol/openid-connect/auth`
Token | `/realms/<REALM>/protocol/openid-connect/token`
Userinfo | `/realms/<REALM>/protocol/openid-connect/userinfo`
JWKS | `/realms/<REALM>/protocol/openid-connect/certs`
Logout | `/realms/<REALM>/protocol/openid-connect/logout`
Account console | `/realms/<REALM>/account`

Test a token with a client-credentials client:
```bash
curl -s -X POST https://sso.example.com/realms/<REALM>/protocol/openid-connect/token \
  -d grant_type=client_credentials -d client_id=<CLIENT_ID> -d client_secret=<CLIENT_SECRET> | jq .access_token
```
Decode and inspect JWTs with [jq](../tools/jq.md) (base64-decode the middle part).

## kcadm.sh (admin CLI)
Inside the container it lives at `/opt/keycloak/bin/kcadm.sh`.
COMMAND | DESCRIPTION
---|---
`kcadm.sh config credentials --server http://localhost:8080 --realm master --user admin` | Log in (prompts for password)
`kcadm.sh get realms` | List realms
`kcadm.sh create realms -s realm=homelab -s enabled=true` | Create a realm
`kcadm.sh create users -r homelab -s username=<USER> -s enabled=true` | Create a user
`kcadm.sh set-password -r homelab --username <USER> --new-password <PASSWORD>` | Set a password
`kcadm.sh get clients -r homelab -q clientId=<CLIENT_ID>` | Find a client
`kcadm.sh update realms/homelab -s sslRequired=external` | Change a realm setting

## Backup and Export
```bash
# DB backup is the real backup
docker compose exec db pg_dump -U keycloak keycloak > keycloak.sql
# realm export (stop the server container first, or use the admin console: Realm settings > Action > Partial export)
/opt/keycloak/bin/kc.sh export --dir /tmp/export --realm homelab
```

## Troubleshooting
SYMPTOM | FIX
---|---
`Invalid parameter: redirect_uri` | Add the exact callback to the client's Valid redirect URIs
Redirects to `http://` or wrong host behind a proxy | Set `KC_HOSTNAME` and `KC_PROXY_HEADERS`, and make the proxy send `X-Forwarded-Proto`/`Host`
`HTTPS required` on admin console | Realm `sslRequired`; fix proxy headers, or for `master` use `kcadm.sh update realms/master -s sslRequired=NONE` (temporary)
Locked out of admin | Start with `KC_BOOTSTRAP_ADMIN_*` on a fresh DB, or `kc.sh bootstrap-admin user` (recent releases)
Slow first start | Normal; use `build` + `start --optimized` for custom images
Token issuer mismatch | Apps must use the same public URL (`iss`) that Keycloak advertises; check `KC_HOSTNAME`

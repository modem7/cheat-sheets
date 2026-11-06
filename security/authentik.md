# authentik
authentik is a self-hosted identity provider: SSO via OIDC, OAuth2, SAML, LDAP and RADIUS, plus a forward-auth proxy outpost for apps with no native SSO. It is lighter than [[keycloak]] and has a flow/stage system for customising login. Since release 2025.10 it needs only PostgreSQL (Redis was removed).

Documentation: [authentik Docs](https://docs.goauthentik.io/) · [Docker Compose install](https://docs.goauthentik.io/install-config/install/docker-compose/)

## Install (Docker Compose)
```bash
mkdir authentik && cd authentik
curl -fLO https://goauthentik.io/docker-compose.yml     # official file, check the docs for the current URL
echo "PG_PASS=$(openssl rand -base64 36 | tr -d '\n')" >> .env
echo "AUTHENTIK_SECRET_KEY=$(openssl rand -base64 60 | tr -d '\n')" >> .env
# optional
echo "COMPOSE_PORT_HTTP=9000"  >> .env
echo "COMPOSE_PORT_HTTPS=9443" >> .env
docker compose pull
docker compose up -d
```
The stack is three services: `postgresql`, `server` (UI/API, ports 9000 and 9443) and `worker` (background tasks). Then browse to `http://<HOST>:9000/if/flow/initial-setup/` to set the `akadmin` password.

Never change `AUTHENTIK_SECRET_KEY` after first start: it encrypts stored data. Back it up with the database ([[bitwarden]]). See [[docker-compose]].

### Useful .env settings
VARIABLE | DESCRIPTION
---|---
`PG_PASS` | PostgreSQL password (used by the compose file)
`AUTHENTIK_SECRET_KEY` | Signing and encryption key
`AUTHENTIK_ERROR_REPORTING__ENABLED` | `false` disables error reporting
`AUTHENTIK_EMAIL__HOST` / `__PORT` / `__USERNAME` / `__PASSWORD` / `__FROM` | SMTP for recovery and notification emails
`AUTHENTIK_TAG` | Image tag to run (pin it, e.g. the current release)
`AUTHENTIK_LOG_LEVEL` | `info`, `debug`, ...

## Operations
COMMAND | DESCRIPTION
---|---
`docker compose ps` | Service state
`docker compose logs -f server worker` | Follow logs
`docker compose exec server ak create_recovery_key 10 akadmin` | One-time recovery link (valid 10 minutes) for a user
`docker compose exec server ak changepassword akadmin` | Reset a password from the CLI
`docker compose exec server ak --help` | List management commands
`docker compose exec postgresql pg_dump -U authentik authentik > authentik.sql` | Database backup, see [[postgres]]
`docker compose pull && docker compose up -d --remove-orphans` | Upgrade (read the release notes first; `--remove-orphans` cleans up the removed Redis container)

## Add an OIDC Application
In the admin UI (**Applications → Applications → Create with Provider**):
1. Name and **slug** (e.g. `grafana`).
2. Provider type **OAuth2/OpenID Connect**, authorisation flow *explicit consent* (or *implicit* to skip the prompt).
3. Client type **Confidential**; note the **Client ID** and **Client Secret**.
4. Add the app's **redirect URI** exactly as the app uses it (strict match).
5. Keep scopes `openid`, `profile`, `email`; add `offline_access` if the app needs refresh tokens.
6. Optionally bind a group to the application to restrict access.

Endpoints for a provider with slug `<SLUG>` (all under `https://auth.example.com`):
ENDPOINT | URL
---|---
Discovery | `/application/o/<SLUG>/.well-known/openid-configuration`
Authorise | `/application/o/authorize/`
Token | `/application/o/token/`
Userinfo | `/application/o/userinfo/`
JWKS | `/application/o/<SLUG>/jwks/`
End session | `/application/o/<SLUG>/end-session/`

Check the discovery document:
```bash
curl -s https://auth.example.com/application/o/<SLUG>/.well-known/openid-configuration | jq .issuer
```

### Example: Grafana ([[grafana]])
```ini
[auth.generic_oauth]
enabled = true
name = authentik
client_id = <CLIENT_ID>
client_secret = <CLIENT_SECRET>
scopes = openid profile email
auth_url = https://auth.example.com/application/o/authorize/
token_url = https://auth.example.com/application/o/token/
api_url = https://auth.example.com/application/o/userinfo/
login_attribute_path = preferred_username
role_attribute_path = contains(groups[*], 'Grafana Admins') && 'Admin' || 'Viewer'
```

## Forward Auth (apps without SSO)
Create a **Proxy provider** in *Forward auth (single application)* mode and attach it to an outpost (the embedded outpost works). Then in [[traefik]]:
```yaml
http:
  middlewares:
    authentik:
      forwardAuth:
        address: http://server:9000/outpost.goauthentik.io/auth/traefik
        trustForwardHeader: true
        authResponseHeaders:
          - X-authentik-username
          - X-authentik-groups
          - X-authentik-email
```
For [[nginx]] use `auth_request` against the same outpost path with the nginx variant of the snippet from the authentik docs.

## Troubleshooting
SYMPTOM | FIX
---|---
`redirect_uri` mismatch / `Redirect URI Error` | The URI configured in authentik must match the app's callback exactly (scheme, host, path, no trailing-slash differences)
Server starts but UI errors after upgrade | Always run `server` and `worker` on the same version; check `docker compose logs`
Lost admin access | `ak create_recovery_key` or `ak changepassword` (see above)
Login loops behind a reverse proxy | Pass `Host` and `X-Forwarded-*` headers; websockets must be allowed
Emails not sent | Set the SMTP variables and test from **System → Settings**; check the worker logs
Upgrade from older release fails on Redis | Follow the 2025.10 release notes; `--remove-orphans`
`AUTHENTIK_SECRET_KEY` lost | Encrypted fields (providers, sources) become unusable; restore from backup

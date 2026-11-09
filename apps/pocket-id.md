# Pocket ID
Pocket ID is a small OpenID Connect (OIDC) provider that signs users in with passkeys instead of passwords. Use it as single sign-on for self-hosted apps that support OIDC. It is simpler than [Authentik](../security/authentik.md) or [Keycloak](../security/keycloak.md), and it has no built-in forward-auth endpoint, so apps without OIDC need a proxy in front.

Documentation: [Pocket ID](https://pocket-id.org/docs)

## Install
```bash
curl -O https://raw.githubusercontent.com/pocket-id/pocket-id/v2/docker-compose.yml
curl -o .env https://raw.githubusercontent.com/pocket-id/pocket-id/v2/.env.example
docker compose up -d
```

Images are `ghcr.io/pocket-id/pocket-id` and `pocketid/pocket-id`. The service listens on port 1411 and stores data in `./data`. Edit `.env`:

```bash
APP_URL=https://id.example.com
ENCRYPTION_KEY=RANDOM_STRING_AT_LEAST_16_CHARS
```

Generate the key with `openssl rand -base64 32`. Passkeys need HTTPS, except on `localhost`, so put it behind a [reverse proxy](../homelab/reverse-proxy-patterns.md).

## First Run
1. Open `https://id.example.com/setup`.
2. Create the admin user and choose **Add Passkey**.
3. The setup page only works until the first account exists.

## Environment Variables
VARIABLE | DESCRIPTION
---|---
`ENCRYPTION_KEY` | Required. At least 16 characters (`ENCRYPTION_KEY_FILE` also works)
`APP_URL` | Public URL, default `http://localhost:1411`
`TRUST_PROXY` | Trust proxy headers (`true`, or an IP/CIDR list), default `false`
`PUID` / `PGID` | Run as this user and group, default 1000
`DB_CONNECTION_STRING` | Default `data/pocket-id.db` (SQLite). Use `postgres://USER:PASSWORD@HOST:5432/DB` for PostgreSQL
`ALLOW_USER_SIGNUPS` | `disabled`, `withToken` or `open`
`SMTP_HOST`, `SMTP_PORT`, `SMTP_FROM`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_TLS` | Email (`SMTP_TLS`: `none`, `starttls`, `tls`)
`STATIC_API_KEY` | Admin API key, minimum 16 characters
`VERSION_CHECK_DISABLED`, `ANALYTICS_DISABLED` | Disable outbound calls for offline setups
`AUDIT_LOG_RETENTION_DAYS` | Default 90

Do not put the SQLite database on NFS or SMB. Rotate the encryption key with:

```bash
docker compose exec pocket-id /app/pocket-id encryption-key-rotate --new-key NEW_KEY
```

## Connect an App (OIDC Client)
1. Go to Administration, OIDC Clients, Add OIDC Client.
2. Enter a name, a client type and callback URLs. Use a confidential client for apps with a backend, and a public client (PKCE) for single-page, mobile and desktop apps.
3. Click Create. The **client secret is shown once**. Replace a lost one under Credentials.
4. On the Access tab choose selected user groups or all users. A new client allows nobody until you do.

Values to give the app:

SETTING | VALUE
---|---
Issuer | `https://id.example.com` (your `APP_URL`)
Discovery | `https://id.example.com/.well-known/openid-configuration`
Scopes | `openid profile email` (add `groups` for group-based roles)
Token | `/api/oidc/token`
Userinfo | `/api/oidc/userinfo`
JWKS | `/.well-known/jwks.json`

The app's server must be able to reach the issuer URL. If it cannot, use `INTERNAL_APP_URL`.

## Apps Without OIDC
Pocket ID has no forward-auth endpoint. Options listed in its docs are Tinyauth, `caddy-security`, OAuth2 Proxy, Traefik forward auth and a Traefik OIDC plugin. For OAuth2 Proxy the callback is `https://SERVICE_DOMAIN/oauth2/callback`, and the config needs `provider="oidc"`, `oidc_issuer_url`, `upstreams` and `cookie_secret`. The proxy-services page is marked as an unreleased version, so check it against your release.

## See Also
- [Authelia](../security/authelia.md)
- [Authentik](../security/authentik.md)
- [Keycloak](../security/keycloak.md)
- [Beszel](beszel.md)

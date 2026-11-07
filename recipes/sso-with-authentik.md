# Single Sign-On with authentik
Put authentik behind Traefik at `https://auth.example.com`, give Grafana real OIDC single sign-on, and protect an app that has no SSO of its own with Traefik forward authentication.

Documentation: [authentik Docker Compose install](https://docs.goauthentik.io/install-config/install/docker-compose/) · [Proxy provider with Traefik](https://docs.goauthentik.io/add-secure-apps/providers/proxy/server_traefik/) · [authentik Grafana integration](https://integrations.goauthentik.io/monitoring/grafana/)

> **Verification:** the configuration was taken from the three pages above (read on 7 November 2026). **Nothing here was run**: authentik was not installed for this recipe. The internal address of the embedded outpost in step 5 is derived from the documented path and port rather than quoted, and the authentik menu names change between releases. Test each step as you go.

## Goal
One login at `auth.example.com` for your self-hosted apps. Grafana signs users in through OIDC and maps authentik entitlements to Grafana roles. An app without SSO (here `whoami.example.com`) is only reachable after authentik has authenticated the browser.

## Prerequisites
- A Docker host with Traefik and TLS as in [Docker Service Deploy](docker-service-deploy.md), and the shared `proxy` network
- DNS records for `auth.example.com`, `grafana.example.com` and `whoami.example.com` pointing at the host
- Grafana already running ([Monitor a Homelab with Prometheus and Grafana](monitor-homelab-prometheus-grafana.md))
- A backup routine that will cover authentik's database and secret key ([Off-Site Docker Host Backup with restic](offsite-docker-host-backup.md))
- A way to reach authentik without authentik: keep the `akadmin` recovery path (step 8) and your console access

> **Never lock yourself out.** Keep one admin session open while you protect apps, and keep a local login on Grafana until SSO works.

## Steps
### 1. Install authentik
Follow [authentik](../security/authentik.md) (install section) in `/opt/stacks/authentik`: download the official Compose file, write `PG_PASS` and `AUTHENTIK_SECRET_KEY` into `.env`, then:
```bash
cd /opt/stacks/authentik
docker compose pull
docker compose up -d
```
Never change `AUTHENTIK_SECRET_KEY` after the first start, and back it up with the database. Pin the image tag with `AUTHENTIK_TAG` ([Automate Container Updates Safely](automate-container-updates.md)).

### 2. Put it behind Traefik
Remove the published ports from the `server` service (or bind them to `127.0.0.1`), join the `proxy` network under an unambiguous alias, and add labels. The official file names the service `server`, a name that is too generic for a shared network, hence the alias:
```yaml
services:
  server:
    networks:
      default: {}
      proxy:
        aliases: [authentik-server]
    labels:
      - traefik.enable=true
      - traefik.docker.network=proxy
      - traefik.http.routers.authentik.rule=Host(`auth.example.com`)
      - traefik.http.routers.authentik.entrypoints=websecure
      - traefik.http.routers.authentik.tls.certresolver=letsencrypt
      - traefik.http.services.authentik.loadbalancer.server.port=9000
networks:
  proxy:
    external: true
```
Merge this into the downloaded file (for example in a `compose.override.yaml`) so upgrades of the official file stay simple. Then set the `akadmin` password at `https://auth.example.com/if/flow/initial-setup/` and enable MFA for your admin account.

### 3. Create a user and a group
In the admin interface create a normal user for yourself (do not use `akadmin` day to day) and, for Grafana, the **application entitlements** in step 4. Create the user under **Directory, Users**; menu names *(unverified)*.

### 4. Grafana with OIDC
**In authentik:** create an application with an **OAuth2/OpenID Connect** provider (**Applications, Applications, Create with Provider**). Follow [authentik](../security/authentik.md) (Add an OIDC Application) and the [Grafana integration page](https://integrations.goauthentik.io/monitoring/grafana/):
- Client type **Confidential**; note the **Client ID**, **Client Secret** and the **slug** (`grafana`)
- Redirect URI, type **Strict**: `https://grafana.example.com/login/generic_oauth`
- Logout URI `https://grafana.example.com/logout`, method **Front-channel**
- Select a **Signing Key**, and under **Advanced protocol settings, Selected Scopes** add the mapping *authentik default OAuth Mapping: Application Entitlements*
- On the application, create entitlements `Grafana Admins`, `Grafana Editors` and `Grafana Viewers`, and bind your user or a group to them. The names must match Grafana's `role_attribute_path` exactly

**In Grafana**, the environment variables (secrets from files, not the Compose file):
```yaml
    environment:
      GF_SERVER_ROOT_URL: https://grafana.example.com
      GF_AUTH_GENERIC_OAUTH_ENABLED: "true"
      GF_AUTH_GENERIC_OAUTH_NAME: authentik
      GF_AUTH_GENERIC_OAUTH_CLIENT_ID: <CLIENT_ID>
      GF_AUTH_GENERIC_OAUTH_CLIENT_SECRET__FILE: /run/secrets/grafana_oidc_secret
      GF_AUTH_GENERIC_OAUTH_SCOPES: openid profile email entitlements
      GF_AUTH_GENERIC_OAUTH_AUTH_URL: https://auth.example.com/application/o/authorize/
      GF_AUTH_GENERIC_OAUTH_TOKEN_URL: https://auth.example.com/application/o/token/
      GF_AUTH_GENERIC_OAUTH_API_URL: https://auth.example.com/application/o/userinfo/
      GF_AUTH_SIGNOUT_REDIRECT_URL: https://auth.example.com/application/o/grafana/end-session/
      GF_AUTH_GENERIC_OAUTH_ROLE_ATTRIBUTE_PATH: "contains(entitlements[*], 'Grafana Admins') && 'Admin' || contains(entitlements[*], 'Grafana Editors') && 'Editor' || 'Viewer'"
```
Add the `grafana_oidc_secret` file as a Compose secret, as in the monitoring recipe. The `__FILE` form of the client secret follows Grafana's general `__FILE` convention ([Grafana](../apps/grafana.md)); it is *unverified* for this setting. The documented integration uses the **`entitlements`** claim; the Grafana example in the [authentik](../security/authentik.md) sheet uses a `groups` claim instead, which works only if you map groups into the token yourself. Check the discovery document:
```bash
curl -s https://auth.example.com/application/o/grafana/.well-known/openid-configuration | jq -r .issuer
```
Restart Grafana (`docker compose up -d`), open it in a private window and use **Sign in with authentik**. Leave `oauth_auto_login` off until this works.

### 5. Forward auth for an app without SSO
**In authentik:** create an application `whoami` with a **Proxy provider** in **Forward auth (single application)** mode, external host `https://whoami.example.com`, and add it to the **embedded outpost** (**Applications, Outposts**). Single-application mode lets you bind different policies to each app; domain-level mode protects several apps under one parent domain but cannot enforce per-app rules.

**In Traefik**, the middleware and a router that sends the outpost path to authentik (from the [official Traefik page](https://docs.goauthentik.io/add-secure-apps/providers/proxy/server_traefik/)). As labels on the authentik `server` service:
```yaml
    labels:
      - traefik.http.middlewares.authentik.forwardauth.address=http://authentik-server:9000/outpost.goauthentik.io/auth/traefik
      - traefik.http.middlewares.authentik.forwardauth.trustForwardHeader=true
      - traefik.http.middlewares.authentik.forwardauth.authResponseHeaders=X-authentik-username,X-authentik-groups,X-authentik-email,X-authentik-name,X-authentik-uid
```
The `authentik-server:9000` address is the embedded outpost on the alias from step 2 (derived, *unverified*). The outpost listens on port 9000 for HTTP. The same middleware is also shown as a file-provider block in [authentik](../security/authentik.md) (Forward Auth). On the protected app:
```yaml
  whoami:
    image: traefik/whoami:<VERSION>
    networks: [proxy]
    labels:
      - traefik.enable=true
      - traefik.docker.network=proxy
      - traefik.http.routers.whoami.rule=Host(`whoami.example.com`)
      - traefik.http.routers.whoami.entrypoints=websecure
      - traefik.http.routers.whoami.tls.certresolver=letsencrypt
      - traefik.http.routers.whoami.middlewares=authentik@docker
      - traefik.http.routers.whoami-outpost.rule=Host(`whoami.example.com`) && PathPrefix(`/outpost.goauthentik.io/`)
      - traefik.http.routers.whoami-outpost.entrypoints=websecure
      - traefik.http.routers.whoami-outpost.tls.certresolver=letsencrypt
      - traefik.http.routers.whoami-outpost.priority=15
      - traefik.http.routers.whoami-outpost.service=authentik@docker
```
The second router (priority 15, above the app router) sends `/outpost.goauthentik.io/` on the app's host to authentik so the login redirect and callback work. It is only needed in single-application mode. The `traefik.http.services.authentik...` service from step 2 is what `authentik@docker` refers to. Validate before starting:
```bash
docker compose config -q
docker compose up -d
```

### 6. Restrict who may use each app
Bind a group or user to each application in authentik (the application's **Policy / Group / User Bindings** tab, *name unverified*). An application with no binding is open to every authenticated authentik user.

### 7. Add a second factor and recovery
Enable MFA in the authentication flow or per user (TOTP or WebAuthn), and save the recovery codes. Create a recovery link for yourself with the command in [authentik](../security/authentik.md) (Operations).

### 8. Plan for authentik being down
Everything behind forward auth is unreachable when authentik is, so monitor it ([Monitor a Homelab with Prometheus and Grafana](monitor-homelab-prometheus-grafana.md)), back up its database and `AUTHENTIK_SECRET_KEY`, and keep Grafana's local admin login. Do not protect authentik, Traefik's dashboard or your monitoring behind authentik alone.

## Verify
```bash
curl -sI https://auth.example.com/-/health/ready/ | head -n 1
curl -s https://auth.example.com/application/o/grafana/.well-known/openid-configuration | jq -r .issuer
curl -sI https://whoami.example.com | head -n 3        # redirect to authentik, not the app
```
- Opening Grafana and choosing **Sign in with authentik** lands you back in Grafana with the role from your entitlement.
- Opening `https://whoami.example.com` in a private window sends you to authentik and, after login, shows the app with an `X-Authentik-Username` header. The `/-/health/ready/` path is *unverified*; any `200` from `auth.example.com` shows Traefik reaches it.
- A user without the binding gets an access-denied page.

## Troubleshooting
SYMPTOM | FIX
---|---
`redirect_uri` mismatch or Redirect URI Error | The URI in authentik must equal Grafana's callback exactly, `https://grafana.example.com/login/generic_oauth`, and `GF_SERVER_ROOT_URL` must match how users reach Grafana
Grafana login works but everyone is a Viewer | The `entitlements` scope or mapping is missing, or the entitlement names differ from the role path
Redirect loop on the protected app | The outpost router is missing or has a lower priority than the app router; check the `PathPrefix` rule and priority 15
`502` on the outpost path | Wrong address or port in the middleware, or `server` is not on the `proxy` network under the alias
Login loops behind the proxy | Pass the `Host` and `X-Forwarded-*` headers and allow websockets ([authentik](../security/authentik.md), troubleshooting)
Browser shows the default Traefik certificate | Router rule does not match or the challenge failed ([TLS Troubleshooting](tls-troubleshooting.md))
Locked out of authentik | Create a recovery key from the CLI, see [authentik](../security/authentik.md) (Operations)
Encrypted fields unusable after restore | `AUTHENTIK_SECRET_KEY` differs from the original

## Rollback / Cleanup
- **Undo protection for one app:** remove the `middlewares` and outpost router labels from the app and run `docker compose up -d`. The app is public again, so also firewall it.
- **Undo Grafana SSO:** remove the `GF_AUTH_GENERIC_OAUTH_*` variables, restart Grafana and log in with the local admin account.
- **Remove authentik:** `docker compose down` in `/opt/stacks/authentik`; add `-v` only to delete the database volume as well (destructive, take a dump first, see [Database Dumps](../backup/database-dumps.md)).

## Related Sheets
- [authentik](../security/authentik.md) · [Keycloak](../security/keycloak.md) · [Security](../security/security.md) · [CrowdSec](../security/crowdsec.md)
- [Traefik](../apps/traefik.md) · [Grafana](../apps/grafana.md) · [Reverse Proxy Patterns](../homelab/reverse-proxy-patterns.md) · [Nginx](../apps/nginx.md)
- [Docker-Compose](../docker/docker-compose.md) · [PostgreSQL Cheat-Sheet](../databases/postgres.md) · [Database Dumps](../backup/database-dumps.md) · [curl](../tools/curl.md) · [jq](../tools/jq.md)
- [Docker Service Deploy](docker-service-deploy.md) · [Monitor a Homelab with Prometheus and Grafana](monitor-homelab-prometheus-grafana.md) · [Off-Site Docker Host Backup with restic](offsite-docker-host-backup.md) · [Expose a Service with Cloudflare Tunnel](expose-service-cloudflare-tunnel.md) · [TLS Troubleshooting](tls-troubleshooting.md)

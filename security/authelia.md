# Authelia
Authelia is a self-hosted authentication and authorisation server that adds login, two-factor and per-domain access rules in front of your apps through your reverse proxy (forward auth), and can also act as an OpenID Connect provider. It is lighter than [Authentik](authentik.md) or [Keycloak](keycloak.md). The proxy side is in [Reverse Proxy Patterns](../homelab/reverse-proxy-patterns.md).

Documentation: [Authelia](https://www.authelia.com/)

## How It Works
1. The reverse proxy asks Authelia (a forward-auth or auth-request call) whether each request is allowed.
2. If not, the browser is redirected to the Authelia portal to log in.
3. Authelia sets a session cookie on the parent domain and the proxy passes the request on, adding `Remote-User`, `Remote-Groups`, `Remote-Email` and `Remote-Name` headers.

Authelia must be served over HTTPS, and forward auth needs HTTPS on every protected app.

## Configuration Outline
`configuration.yml` sections: `authentication_backend` (file or LDAP), `storage` (SQLite for testing, PostgreSQL for production), `session`, `notifier` (filesystem or SMTP, only one) and `access_control`. Secrets can be supplied as environment variables or files. The docs referenced here describe version 4.39.

```yaml
server:
  address: 'tcp://0.0.0.0:9091/'

session:
  cookies:
    - domain: 'example.com'
      authelia_url: 'https://auth.example.com'
      default_redirection_url: 'https://www.example.com'

access_control:
  default_policy: deny
  rules:
    - domain: '*.example.com'
      policy: one_factor
```

The Docker image is `authelia/authelia` and the container listens on 9091 (the image name and compose layout are not verified here, see the docs). Commands such as `authelia crypto hash generate argon2` (for user passwords) and `authelia validate-config` exist in recent versions (unverified here).

## Access Policies
POLICY | MEANING
---|---
`deny` | Always refuse
`bypass` | No authentication
`one_factor` | Username and password
`two_factor` | Password plus a second factor

Use `default_policy: deny` and open specific domains or paths with rules.

## Reverse Proxy Endpoints
PROXY | ENDPOINT
---|---
Traefik and Caddy | `/api/authz/forward-auth`
nginx | `/api/authz/auth-request`
Envoy | `/api/authz/ext-authz`

Caddy (v2.5.1 or later), verbatim from the Authelia docs:

```text
nextcloud.example.com {
  forward_auth authelia:9091 {
    uri /api/authz/forward-auth
    copy_headers Remote-User Remote-Groups Remote-Email Remote-Name
  }
  reverse_proxy nextcloud:80
}
```

Traefik forward-auth middleware labels (the nginx and Traefik details below are from a summary of the docs, so confirm against the current pages):

```yaml
labels:
  - traefik.http.middlewares.authelia.forwardauth.address=http://authelia:9091/api/authz/forward-auth
  - traefik.http.middlewares.authelia.forwardauth.trustForwardHeader=true
  - traefik.http.middlewares.authelia.forwardauth.authResponseHeaders=Remote-User,Remote-Groups,Remote-Email,Remote-Name
```

Then attach `authelia@docker` to each router with `traefik.http.routers.<NAME>.middlewares=authelia@docker`. See [Traefik](../apps/traefik.md).

## Upgrading from 4.37 to 4.38 and Later
OLD | NEW
---|---
Top-level `default_redirection_url` and `session.domain` | `session.cookies[]` with `domain`, `authelia_url`, `default_redirection_url`
`session.remember_me_duration` | `session.remember_me`
`server.host`, `server.port`, `server.path` | `server.address: 'tcp://0.0.0.0:9091/PATH'`
`/api/verify?rd=...` | `/api/authz/*` endpoints
OIDC `issuer_private_key`, `issuer_certificate_chain` | `jwks` list with `key` and `certificate_chain`

Expect deprecation warnings in 4.38. Many old keys are due to be removed in v5.0.

## See Also
- [Pocket ID](../apps/pocket-id.md)
- [Authentik](authentik.md)
- [Keycloak](keycloak.md)
- [Reverse Proxy Patterns](../homelab/reverse-proxy-patterns.md)

# Vault and OpenBao
HashiCorp Vault stores and brokers secrets: a KV store, dynamic database and cloud credentials, PKI, and an encryption service, all behind policy-controlled tokens. OpenBao is the open source (MPL-2.0) fork maintained under the Linux Foundation; Vault is under the BUSL licence. The CLIs are nearly identical (`vault` vs `bao`), so every command below works with either; swap the binary name. For smaller setups see [SOPS and age](sops-age.md) or [Bitwarden Cheat-Sheet](../tools/bitwarden.md). Sealed-storage keys can be protected with [GPG](gpg.md).

Documentation: [Vault Docs](https://developer.hashicorp.com/vault/docs) · [OpenBao Docs](https://openbao.org/docs/)

## Environment
VARIABLE | DESCRIPTION
---|---
`VAULT_ADDR` / `BAO_ADDR` | Server address, e.g. `https://vault.example.com:8200` (`bao` prefers `BAO_*` and falls back to `VAULT_*`)
`VAULT_TOKEN` / `BAO_TOKEN` | Token to use (otherwise `~/.vault-token` written by `vault login`)
`VAULT_NAMESPACE` | Namespace (Vault Enterprise / OpenBao namespaces)
`VAULT_CACERT` | CA bundle for a private CA, see [TLS (Transport Layer Security)](../networking/tls.md)
`VAULT_FORMAT` | `json`, `yaml` or `table`

## Dev Server
In-memory, auto-unsealed, root token printed. Never use it for real secrets.
```bash
vault server -dev -dev-root-token-id=dev-only-token
export VAULT_ADDR=http://127.0.0.1:8200
export VAULT_TOKEN=dev-only-token
vault status
```
Or in [Docker](../docker/docker.md):
```bash
docker run --rm --cap-add=IPC_LOCK -p 8200:8200 \
  -e VAULT_DEV_ROOT_TOKEN_ID=dev-only-token hashicorp/vault
```

## Initialise and Unseal
Vault starts *sealed*: the master key is split into shares (Shamir) and a threshold must be supplied after every restart.
COMMAND | DESCRIPTION
---|---
`vault operator init -key-shares=5 -key-threshold=3` | One-time init; prints unseal keys and the initial root token
`vault operator unseal` | Submit one unseal key (repeat until the threshold is met)
`vault operator seal` | Seal a running server (emergency lockdown)
`vault status` | Sealed state, HA mode, version
`vault login` | Authenticate with a token
`vault token revoke -self` | Revoke the current token (do this for the initial root token once real auth is set up)

Give each key share to a different person and store them separately. Auto-unseal (cloud KMS, transit from another Vault/OpenBao, PKCS#11) removes the manual step; configure it in the `seal` stanza.

## Server Config (Raft storage)
`/etc/vault.d/vault.hcl`:
```hcl
ui            = true
api_addr      = "https://vault.example.com:8200"
cluster_addr  = "https://vault.example.com:8201"

storage "raft" {
  path    = "/opt/vault/data"
  node_id = "vault-1"
}

listener "tcp" {
  address       = "0.0.0.0:8200"
  tls_cert_file = "/opt/vault/tls/fullchain.pem"
  tls_key_file  = "/opt/vault/tls/privkey.pem"
}
```
Back up with `vault operator raft snapshot save backup.snap` and restore with `vault operator raft snapshot restore backup.snap`.

## Docker Compose
```yaml
services:
  vault:
    image: hashicorp/vault:<TAG>        # or quay.io/openbao/openbao:<TAG>
    restart: unless-stopped
    cap_add: [IPC_LOCK]
    command: server
    ports:
      - "127.0.0.1:8200:8200"
    environment:
      VAULT_ADDR: http://127.0.0.1:8200
    volumes:
      - ./config:/vault/config:ro
      - vault-data:/vault/file
volumes:
  vault-data:
```
Put TLS in front with [Traefik](../apps/traefik.md) or [Nginx](../apps/nginx.md), or enable TLS in the listener.

## KV Secrets
COMMAND | DESCRIPTION
---|---
`vault secrets enable -path=secret kv-v2` | Enable KV v2 (the dev server mounts it at `secret/`)
`vault secrets list` | List mounts
`vault kv put -mount=secret myapp/db user=app password=<PASSWORD>` | Write (creates a new version)
`vault kv get -mount=secret myapp/db` | Read latest
`vault kv get -mount=secret -field=password myapp/db` | Read one field
`vault kv get -mount=secret -version=2 myapp/db` | Read an old version
`vault kv list -mount=secret myapp` | List keys
`vault kv patch -mount=secret myapp/db password=<NEW>` | Update one field
`vault kv delete -mount=secret myapp/db` | Soft delete the latest version
`vault kv undelete -mount=secret -versions=3 myapp/db` | Recover
`vault kv metadata delete -mount=secret myapp/db` | Delete permanently, including history
`vault kv put -mount=secret myapp/cfg @config.json` | Write from a file

## Policies
Policies are deny-by-default. With KV v2 the API paths include `data/` and `metadata/`.
`app-read.hcl`:
```hcl
path "secret/data/myapp/*" {
  capabilities = ["read"]
}
path "secret/metadata/myapp/*" {
  capabilities = ["list", "read"]
}
```
COMMAND | DESCRIPTION
---|---
`vault policy write app-read app-read.hcl` | Create or update
`vault policy list` | List policies
`vault policy read app-read` | Show one
`vault policy delete app-read` | Remove
`vault token create -policy=app-read -ttl=1h` | Token with that policy
`vault token lookup` | Inspect the current token
`vault token capabilities secret/data/myapp/db` | What can this token do on a path?

## Auth Methods (AppRole example)
Machines should use AppRole, Kubernetes, OIDC or JWT auth, not long-lived tokens. For OIDC SSO see [authentik](authentik.md) or [Keycloak](keycloak.md).
```bash
vault auth enable approle
vault write auth/approle/role/myapp token_policies=app-read token_ttl=1h token_max_ttl=4h
vault read -field=role_id auth/approle/role/myapp/role-id
vault write -f -field=secret_id auth/approle/role/myapp/secret-id
vault write auth/approle/login role_id=<ROLE_ID> secret_id=<SECRET_ID>
```
COMMAND | DESCRIPTION
---|---
`vault auth list` | Enabled auth methods
`vault auth enable userpass` | Username/password (small setups)
`vault write auth/userpass/users/<USER> password=<PASSWORD> policies=app-read` | Add a user
`vault audit enable file file_path=/var/log/vault_audit.log` | Turn on auditing (enable before going live)

## HTTP API
```bash
curl -s -H "X-Vault-Token: $VAULT_TOKEN" "$VAULT_ADDR/v1/secret/data/myapp/db" | jq '.data.data'
```
See [curl](../tools/curl.md) and [jq](../tools/jq.md).

## Troubleshooting
SYMPTOM | FIX
---|---
`Vault is sealed` / HTTP 503 | `vault operator unseal` until the threshold is reached; consider auto-unseal
`permission denied` on KV v2 | Policy path is missing `data/` (reads) or `metadata/` (list); check with `vault token capabilities`
`http: server gave HTTP response to HTTPS client` | `VAULT_ADDR` scheme doesn't match the listener
`x509: certificate signed by unknown authority` | Set `VAULT_CACERT` or install the CA ([OpenSSL](../tools/openssl.md))
`Error initializing: ... already initialized` | Init is one-time; restore from backup or wipe storage on a lab server
`failed to lock memory` | Add `IPC_LOCK` capability, or `disable_mlock = true` with Raft (understand the trade-off)
Lost unseal keys | Not recoverable (except via recovery keys with auto-unseal); keep offline copies

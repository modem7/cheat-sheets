# Bitwarden Cheat-Sheet
Bitwarden is an open source password manager. This sheet covers the CLI (`bw`) and self-hosting with Vaultwarden.

Documentation: [Bitwarden CLI](https://bitwarden.com/help/cli/)

## Install the CLI
COMMAND | DESCRIPTION
---|---
`npm install -g @bitwarden/cli` | Install with npm
`sudo snap install bw` | Install with snap
`brew install bitwarden-cli` | Install on macOS
`choco install bitwarden-cli` | Install on Windows, see [Chocolatey](../windows/chocolatey.md)

## Login and Unlock
COMMAND | DESCRIPTION
---|---
`bw config server https://vault.example.com` | Point at a self-hosted server
`bw login` | Log in with email and master password
`bw login --apikey` | Log in with the API key (`BW_CLIENTID`, `BW_CLIENTSECRET`)
`bw unlock` | Unlock and print a session key
`export BW_SESSION="<KEY>"` | Use the session key in later commands
`bw unlock --raw` | Print only the key, for scripting: `export BW_SESSION=$(bw unlock --raw)`
`bw lock` | Lock the vault
`bw logout` | Log out
`bw status` | Show login and lock state
`bw sync` | Pull the latest vault

## Reading Items
COMMAND | DESCRIPTION
---|---
`bw list items --search <TERM>` | Search items (JSON)
`bw list folders` | List folders
`bw get item <NAME-OR-ID>` | Full item JSON
`bw get password <NAME-OR-ID>` | Print only the password
`bw get username <NAME-OR-ID>` | Print only the username
`bw get totp <NAME-OR-ID>` | Current 2FA code
`bw get notes <NAME-OR-ID>` | Print secure notes
`bw get uri <NAME-OR-ID>` | Print the first URI
`bw generate -ulns --length 24` | Generate a password (upper, lower, number, special)
`bw generate --passphrase --words 5` | Generate a passphrase

## Writing Items
```bash
bw get template item | jq '.name="Example" | .login.username="me" | .login.password="secret"' \
  | bw encode | bw create item
```
COMMAND | DESCRIPTION
---|---
`bw edit item <ID> <BASE64-JSON>` | Edit an item
`bw delete item <ID>` | Move to trash
`bw delete item <ID> --permanent` | Delete permanently
`bw export --format json --output vault.json` | Export (unencrypted, handle with care)
`bw import bitwardenjson vault.json` | Import

## Secrets in Scripts
```bash
export BW_SESSION=$(bw unlock --passwordenv BW_PASSWORD --raw)
DB_PASS=$(bw get password "prod-db")
```
Never commit `BW_SESSION`, `BW_PASSWORD` or exports. For automation consider Bitwarden Secrets Manager (`bws`).

## Self-Hosting with Vaultwarden
```yaml
services:
  vaultwarden:
    image: vaultwarden/server:latest
    restart: unless-stopped
    environment:
      DOMAIN: "https://vault.example.com"
      SIGNUPS_ALLOWED: "false"
    volumes:
      - ./vw-data:/data
    ports:
      - "127.0.0.1:8080:80"
```
Put it behind a TLS reverse proxy ([Nginx](../apps/nginx.md) or [Traefik](../apps/traefik.md)). Back up `./vw-data`.

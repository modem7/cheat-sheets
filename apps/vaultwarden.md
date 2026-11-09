# Vaultwarden
Vaultwarden is a lightweight, self-hosted server that is compatible with the Bitwarden clients and APIs. Use it to run your own password vault. The official clients are covered in [Bitwarden](../tools/bitwarden.md).

Project: [Vaultwarden](https://github.com/dani-garcia/vaultwarden)
Documentation: [Wiki](https://github.com/dani-garcia/vaultwarden/wiki)

## Install (Docker Compose)
```yaml
services:
  vaultwarden:
    image: vaultwarden/server:latest
    container_name: vaultwarden
    restart: always
    environment:
      DOMAIN: "https://vault.example.com"
      SIGNUPS_ALLOWED: "false"
    volumes:
      - ./vw-data:/data
    ports:
      - "127.0.0.1:11001:80"
```

Update:

```bash
docker compose pull && docker compose up -d && docker compose logs -f
```

Environment changes need the container recreated (`docker compose up -d`). Create your account first with `SIGNUPS_ALLOWED: "true"`, then set it to `false`.

## HTTPS and Reverse Proxy
The wiki calls HTTPS "pretty much required", because the web vault and clients rely on browser crypto APIs that need a secure context. Terminate TLS in a reverse proxy such as [Traefik](traefik.md) or [Nginx](nginx.md) and do not use `ROCKET_TLS`. Set `DOMAIN` to the full base URL, including `https://`. See [Reverse Proxy Patterns](../homelab/reverse-proxy-patterns.md).

WebSockets run on the main HTTP port since v1.31.0, so the old port 3012 is gone. The proxy must pass the `Upgrade` and `Connection` headers. Test `/notifications/hub`, which should return 101. Disable with `ENABLE_WEBSOCKET=false`.

## Configuration
SETTING | DESCRIPTION
---|---
`DOMAIN` | Full public URL. Required behind a proxy, for invitations and for attachments
`SIGNUPS_ALLOWED` | Allow open registration
`SMTP_HOST`, `SMTP_FROM`, `SMTP_PORT`, `SMTP_SECURITY`, `SMTP_USERNAME`, `SMTP_PASSWORD` | Outgoing mail
`ENV_FILE` | Load variables from a file
`<VAR>_FILE` | Read any variable from a file, e.g. `SMTP_PASSWORD_FILE=/run/secrets/smtp_password`

`SMTP_SECURITY` is `starttls` (587), `force_tls` (465) or `off` (25). Invitations need `DOMAIN` set and expire after 5 days. Precedence is built-in defaults, then `ENV_FILE`, then environment variables, then `config.json` (written by the admin page, not recommended). The admin page needs `ADMIN_TOKEN`. Generate a hashed token as the wiki describes (the exact command is unverified here).

## Connect Clients
In the Bitwarden app or browser extension choose self-hosted on the login screen and enter your `DOMAIN` URL.

## Backup
The data directory holds `db.sqlite3`, `attachments/`, `config.json`, `rsa_key*`, `sends/` and `icon_cache/`. Required: the database and `attachments/`. Recommended: `config.json` and `rsa_key*`.

```bash
sqlite3 data/db.sqlite3 ".backup '/path/to/backups/db-$(date '+%Y%m%d-%H%M').sqlite3'"
```

Since 1.32.1: `docker exec -it vaultwarden /vaultwarden backup`. The image has no `sqlite3` binary and no cron, so schedule the backup from the host. Do not copy a live SQLite file with `cp`. Restore with the container stopped. Test restores, see [Restore-Test a Backup](../recipes/restore-test-a-backup.md).

## Gotchas
- Microsoft basic-auth SMTP no longer works.
- Attachments need `DOMAIN` set to an HTTPS URL.
- Do not expose the admin page publicly.

## See Also
- [Bitwarden](../tools/bitwarden.md)
- [Passbolt](passbolt.md)
- [Restic](../backup/restic.md)
- [Reverse Proxy Patterns](../homelab/reverse-proxy-patterns.md)

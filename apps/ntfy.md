# ntfy
ntfy is a simple self-hostable push notification service: publish with `curl`, subscribe from the phone app, browser or CLI. Use it as the destination for [Alertmanager](alertmanager.md), [Uptime Kuma](uptime-kuma.md), backup jobs and UPS events.

Documentation: [ntfy docs](https://docs.ntfy.sh/)

## Install (Docker)
```yaml
services:
  ntfy:
    image: binwiederhier/ntfy
    restart: unless-stopped
    command: serve
    environment:
      NTFY_BASE_URL: https://ntfy.example.com
      NTFY_CACHE_FILE: /var/lib/ntfy/cache.db
      NTFY_AUTH_FILE: /var/lib/ntfy/auth.db
      NTFY_AUTH_DEFAULT_ACCESS: deny-all
      NTFY_BEHIND_PROXY: "true"
      NTFY_ATTACHMENT_CACHE_DIR: /var/lib/ntfy/attachments
      NTFY_ENABLE_LOGIN: "true"
    volumes:
      - ./ntfy:/var/lib/ntfy
    ports:
      - "80:80"
```

Equivalent `server.yml` keys: `base-url`, `listen-http`, `cache-file`, `auth-file`, `auth-default-access` (`read-write`, `read-only`, `write-only`, `deny-all`) and `behind-proxy`. Setting `auth-file` turns authentication on. Behind a proxy set `behind-proxy: true` and pass WebSocket headers (`Upgrade` and `Connection`).

## Users, Access and Tokens
Run these inside the container, for example `docker compose exec ntfy ntfy user list`.

COMMAND | DESCRIPTION
---|---
`ntfy user add --role=admin <USER>` | Create an admin (prompts for a password)
`ntfy user add <USER>` | Create a normal user
`ntfy user list` / `ntfy user del <USER>` | List or delete users
`ntfy user change-pass <USER>` | Change a password
`ntfy access <USER> <TOPIC> rw` | Grant access (`rw`, `ro`, `wo`, `deny`)
`ntfy access everyone "up*" write` | Let anyone publish to topics matching a pattern
`ntfy access --reset <USER>` | Remove a user's custom access rules
`ntfy token add --expires=30d --label="backups" <USER>` | Create an access token (`tk_...`)
`ntfy token list` / `ntfy token remove <USER> <TOKEN>` | List or remove tokens

## Publish
```bash
curl \
  -H "Title: Backup failed" \
  -H "Priority: high" \
  -H "Tags: warning,floppy_disk" \
  -d "borgmatic exited with status 2 on host01" \
  https://ntfy.example.com/backups
```

HEADER | DESCRIPTION
---|---
`Title` (or `t`) | Notification title
`Priority` (or `p`) | `1` to `5`, or `min`, `low`, `default`, `high`, `urgent`
`Tags` | Comma-separated tags; emoji short codes show as icons
`Click` | URL opened when tapped
`Attach` | URL of a file to attach
`Actions` | Up to three buttons, for example `view, Open, https://example.com`

Authenticate with a token: `curl -H "Authorization: Bearer tk_TOKEN" -d "message" https://ntfy.example.com/TOPIC`. Basic auth also works: `curl -u USER:PASSWORD ...`.

## Subscribe
COMMAND | DESCRIPTION
---|---
`ntfy subscribe <TOPIC>` | Print each message as JSON
`ntfy subscribe <TOPIC> '<COMMAND>'` | Run a command per message
`ntfy publish --title "..." --priority=high <TOPIC> "message"` | Publish with the CLI

The CLI reads `~/.config/ntfy/client.yml` (`default-host`, `default-user`, `default-password`, `default-token`). In the phone app add your server under Settings, then subscribe to the topic.

## Gotchas
- A topic name is effectively a password on an open server. Use `deny-all` plus users or tokens for anything private.
- Without `behind-proxy`, rate limits and logs see the proxy's address instead of the client.
- Users declared in `auth-users` are deleted at the next restart if you remove them from the config.
- To use ntfy from [Alertmanager](alertmanager.md), point a `webhook_configs` receiver at a small bridge or use ntfy's webhook-compatible publish URL (check the ntfy docs for your version, unverified here).

## See Also
- [Alertmanager](alertmanager.md)
- [Uptime Kuma](uptime-kuma.md)
- [apcupsd](../homelab/apcupsd.md)
- [Borgmatic](../backup/borgmatic.md)

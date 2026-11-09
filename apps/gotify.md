# Gotify
Gotify is a simple self-hosted push notification server with a web UI, a REST API and an Android app. Scripts and services send messages with an application token, and your devices receive them. It is the "inbox" style alternative to [ntfy](ntfy.md), and tools like [Apprise](apprise.md) and [Uptime Kuma](uptime-kuma.md) can send to it. This sheet covers Gotify 3.x.

Documentation: [Gotify docs](https://gotify.net/docs/)

## Install (Docker)
```yaml
services:
  gotify:
    image: gotify/server
    restart: unless-stopped
    ports:
      - "8080:80"
    environment:
      GOTIFY_DEFAULTUSER_PASS: "CHANGE_ME"
    volumes:
      - ./gotify_data:/app/data
```

The image is also published as `ghcr.io/gotify/server`. To run as a dedicated user, `sudo chown -R 1234:1234 ./gotify_data` and add `user: "1234:1234"`. Set `TZ` for the time zone. `/app/data` holds the SQLite database, uploaded images and certificates, so include it in your [backups](../backup/restic.md).

## Configuration (3.x)
Gotify 3 is configured only through environment variables. `config.yml` is removed. Convert an old file with `gotify-server migrate-config config.yml > gotify-server.env`. Any variable also accepts a `_FILE` suffix, for example `GOTIFY_DEFAULTUSER_PASS_FILE=/run/secrets/admin_pass`.

VARIABLE | DESCRIPTION
---|---
`GOTIFY_DEFAULTUSER_NAME` / `GOTIFY_DEFAULTUSER_PASS` | First admin (default `admin` / `admin`). Only applied when the database is first created
`GOTIFY_SERVER_PORT` | Listen port, default `80`
`GOTIFY_SERVER_TRUSTEDPROXIES` | Comma list of proxy IPs or CIDRs, e.g. `127.0.0.1/32,::1`
`GOTIFY_SERVER_SECURECOOKIE` | Set `true` behind HTTPS
`GOTIFY_REGISTRATION` | Allow user self-registration, default `false`
`GOTIFY_DATABASE_DIALECT` | `sqlite3` (default), `mysql` or `postgres`
`GOTIFY_DATABASE_CONNECTION` | Connection string, default `data/gotify.db`

Change the default `admin` password on first login, or create another admin and delete the default.

## Apps and Tokens
- An **application** can only send messages. A **client** receives them (the web UI, the Android app).
- Create an application in the UI, or with the API (replace the example credentials):

```bash
curl -u ADMIN_USER:ADMIN_PASSWORD https://gotify.example.com/application \
  -F "name=backups" -F "description=Backup job alerts"
```

- Gotify 3 shows a token **only once**, on creation or rotation. Rotate with `PUT /application/{id}/security`. Keep one application per sender so you can revoke one without affecting the others.

## Send a Message
```bash
curl "https://gotify.example.com/message" \
  -H "X-Gotify-Key: ${GOTIFY_APP_TOKEN}" \
  -F "title=Backup failed" \
  -F "message=borgmatic exited with status 2" \
  -F "priority=5"
```

Only `message` is required. Use the `X-Gotify-Key` header and not a `?token=` query string, because query strings end up in proxy logs. With the CLI:

COMMAND | DESCRIPTION
---|---
`gotify init` | Interactive setup of URL and token
`gotify push -t "<TITLE>" -p 10 "<MESSAGE>"` | Send a message
`echo "<MESSAGE>" \| gotify push` | Send from stdin

The CLI reads `/etc/gotify/cli.json`, `~/.config/gotify/cli.json`, `~/.gotify/cli.json` or `./cli.json` with `token` (an application token), `url` and `defaultPriority`. Flags include `--token` (or `GOTIFY_TOKEN`), `--url` and `--quiet`. Check `gotify help push` for your version.

## Priority (Android)
PRIORITY | BEHAVIOUR
---|---
`0` | No notification
`1` to `3` | Icon only
`4` to `7` | Icon and sound
`8` to `10` | Icon, sound and vibration

## Extras
Extras need a JSON body with `Content-Type: application/json`.

```bash
curl -X POST https://gotify.example.com/message \
  -H "X-Gotify-Key: ${GOTIFY_APP_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"title":"Build","message":"**passed**","priority":5,"extras":{"client::display":{"contentType":"text/markdown"},"client::notification":{"click":{"url":"https://example.com/build/42"}}}}'
```

EXTRA | EFFECT
---|---
`client::display` with `contentType` | `text/plain` (default) or `text/markdown`
`client::notification` with `click.url` | Open a URL when tapped (Android 2.0.10 and later)
`client::notification` with `bigImageUrl` | Big image (Android 2.3.0 and later)

Markdown images are fetched automatically, so use `text/plain` for untrusted text.

## Reverse Proxy
The WebSocket upgrade must pass through, and the `Host` header must be preserved for the origin check. For nginx:

```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_set_header Host $http_host;
```

If nginx terminates TLS, set `GOTIFY_SERVER_SSL_ENABLED=false` for Gotify. See [Reverse Proxy Patterns](../homelab/reverse-proxy-patterns.md).

## Not Checked
UnifiedPush support, an iOS app, the full REST reference and the steps to create client tokens in the UI were not verified here.

## See Also
- [ntfy](ntfy.md)
- [Apprise](apprise.md)
- [Notification Services](../homelab/notification-services.md)
- [Uptime Kuma](uptime-kuma.md)

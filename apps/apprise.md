# Apprise
Apprise is one library, CLI and optional API gateway that sends a notification to 100+ services (ntfy, Gotify, Discord, Slack, Telegram, Pushover, email, Matrix and more) using a single URL per service. Use it so scripts do not need a different `curl` for every chat or push service. Many tools already embed it, for example [Healthchecks](healthchecks.md).

Project: [Apprise](https://github.com/caronc/apprise)
Documentation: [Apprise docs](https://appriseit.com/), [Apprise API](https://github.com/caronc/apprise-api)

## Install
```bash
uv tool install apprise
```

Or `pip install apprise`. The install lines come from a summary of the README, so check the project page.

## CLI
```bash
apprise -t "Backup" -b "Finished OK" "ntfys://ntfy.example.com/backups"
apprise --config=/etc/apprise/config.yml --body="test"
```

OPTION | DESCRIPTION
---|---
`-b`, `--body` | Message body (read from stdin if omitted)
`-t`, `--title` | Title
`-n`, `--notification-type` | `info` (default), `success`, `warning` or `failure`
`-i`, `--input-format` | `text`, `html` or `markdown`
`-c`, `--config` | Config file or URL (repeatable)
`-g`, `--tag` | Only notify entries with this tag (repeatable)
`-a`, `--attach` | Attach a file (repeatable)
`-d`, `--dry-run` | Show what would be sent, send nothing
`-v` / `-vvvv` | Verbose output (stackable)
`-D`, `--debug` | Debug output
`-l`, `--details` | List supported services

Exit codes: `0` all sent, `1` all failed, `3` no service matched the tags, `4` partial failure. Always test a new URL with `--dry-run` and then a real send. Passwords in URLs appear in shell history and process lists, so keep URLs in a config file or environment variable.

## URL Examples
Schemes ending in `s` use TLS where the service supports it.

SERVICE | URL
---|---
ntfy | `ntfy://TOPIC/` or `ntfys://HOST/TOPIC` (self-hosted, TLS)
Gotify | `gotify://HOST/TOKEN` or `gotifys://HOST/TOKEN?priority=high`
Discord | `discord://WEBHOOK_ID/WEBHOOK_TOKEN`
Slack | `slack://TOKEN_A/TOKEN_B/TOKEN_C/CHANNEL`
Telegram | `tgram://BOT_TOKEN/CHAT_ID`
Pushover | `pover://USER_KEY@APP_TOKEN`
Email | `mailto://USER:PASSWORD@example.com`
Matrix | `matrixs://USER:PASSWORD@HOST/#ROOM_ALIAS`
Webhook | `json://HOST`

Per-service pages list every option. The ntfy, Gotify and Pushover forms above are from the services table only, so test them.

## Config Files
Apprise looks for a default config in order: `~/.apprise`, `~/.apprise.conf`, `~/.apprise.yml`, `~/.apprise.yaml`, `~/.config/apprise` and variants, then `/etc/apprise*`. Environment variables: `APPRISE_URLS`, `APPRISE_CONFIG_PATH`, `APPRISE_STORAGE_PATH`.

Text format. `tag=URL`, `#` and `;` comments, groups and includes:

```text
ops,alerts=ntfys://ntfy.example.com/ops
phone=pover://USER_KEY@APP_TOKEN
friends = user1, user2
include /etc/apprise/secrets.conf
```

YAML format:

```yaml
version: 1
urls:
  - ntfys://ntfy.example.com/ops:
      tag: ops
  - json://localhost
```

## Tags
INPUT | MEANING
---|---
`-g a -g b` | `a` OR `b`
`-g "a,b"` | `a` AND `b`
`-g all` | Every service
no `-g` | Only entries with **no** tag
`-g "2:alerts"` | Only priority-2 entries tagged `alerts`

## Apprise API
A small REST service that keeps your URLs in one place, so other containers only need to call HTTP.

```yaml
services:
  apprise:
    image: caronc/apprise:latest
    container_name: apprise
    ports:
      - "8000:8000"
    environment:
      APPRISE_STATEFUL_MODE: simple
      APPRISE_WORKER_COUNT: "1"
      APPRISE_DEFAULT_FORMAT: "text"
      TZ: Europe/London
    volumes:
      - ./config:/config
      - ./plugin:/plugin
      - ./attach:/attach
```

Pre-create the three directories. Saved configs live under `/config`, uploads under `/attach` and custom plugins under `/plugin`. The docs run the container as your user, with `--user "$(id -u):$(id -g)"`. Do not use a compose override file for production.

ENDPOINT | USE
---|---
`GET /status` | Health check
`POST /notify/` | Stateless: pass `urls`, `body`, `title`, `type`, `format`
`POST /add/{KEY}` | Save URLs (`urls`) or a config (`config` plus `format`) under a key
`POST /notify/{KEY}` | Send to everything saved under the key (`body`, `title`, `type`, `tag`, `format`)
`POST /get/{KEY}` | Fetch a saved config
`POST /del/{KEY}` | Delete a key
`GET /json/urls/{KEY}` | List the URLs saved under a key

```bash
curl -X POST -d "urls=ntfys://ntfy.example.com/ops" http://localhost:8000/add/alerts
curl -X POST -H "Content-Type: application/json" \
  -d '{"body": "Database connection failed", "type": "warning"}' \
  http://localhost:8000/notify/alerts
```

The first command is composed from the endpoint table rather than quoted from the docs. In the API, `"a,b"` means OR and `"a b"` or `"a+b"` means AND, which is the opposite of the CLI. The API is unauthenticated by default, so keep it on a private network or behind a proxy with auth. You can also use the CLI against the API with `apprise -t "Job" "apprise://localhost:8000/alerts"` (`apprises://` for HTTPS). Apprise Mobile for Android is only a companion for the API, not a notification service of its own.

## Gotchas
- URL syntax differs from [Shoutrrr](../homelab/notification-services.md#shoutrrr), so do not copy URLs between them.
- `--dry-run` sends nothing, so a "success" there does not prove credentials work.
- Auth settings for the API (`APPRISE_AUTH_REQUIRED` and friends) were not verified here.

## See Also
- [ntfy](ntfy.md)
- [Gotify](gotify.md)
- [Healthchecks](healthchecks.md)
- [Notification Services](../homelab/notification-services.md)

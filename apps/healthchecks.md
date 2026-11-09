# Healthchecks
Healthchecks monitors scheduled jobs by listening for pings. A cron job, backup or script calls a URL when it finishes, and you are alerted if the ping does not arrive on time. It catches jobs that silently stop, which uptime checks miss. Use the hosted healthchecks.io or self-host it. It can notify through email, webhooks, chat apps and push services such as [Pushover](pushover.md).

Documentation: [Healthchecks docs](https://healthchecks.io/docs/)

## Ping URLs
Each check has a UUID. Ping with `GET`, `HEAD` or `POST`.

URL | MEANING
---|---
`https://hc-ping.com/<UUID>` | Success
`https://hc-ping.com/<UUID>/start` | Job started (lets Healthchecks time it)
`https://hc-ping.com/<UUID>/fail` | Job failed
`https://hc-ping.com/<UUID>/log` | Log only, no state change
`https://hc-ping.com/<UUID>/<EXIT_STATUS>` | `0` is success, `1` to `255` is failure
`https://hc-ping.com/<PING_KEY>/<SLUG>` | Slug form, also with `/start`, `/fail`, `/log` and `/<EXIT_STATUS>`

- Slugs use `a-z`, `0-9`, hyphen and underscore. A slug that is not unique returns 409. Add `?create=1` to auto-create a check from a slug ping (off by default).
- Add `rid=<UUID>` to pair a start ping with its finish ping when jobs overlap.
- A `POST` body is stored (first 100 kB), useful for job output.
- Do not ping one check more than 5 times per minute. Responses are `200 OK` with the body `OK`.
- `rid` must be a client-generated UUID in canonical form. `?create=1` returns `201 Created` for a new check.
- Responses may carry a `Ping-Body-Limit` header with the body size limit. The body is stored only if it is UTF-8 text, and a `/log` ping shows with a Log label in Events.

## Cron and Scripts
```bash
curl -fsS -m 10 --retry 5 -o /dev/null https://hc-ping.com/YOUR-UUID
```

`-f` fails on HTTP errors, `-s -S` hide progress but show errors, `-m 10` caps each attempt and `--retry 5` retries transient errors, so a network blip does not cause a false alarm. In a crontab, ping only if the job succeeded:

```text
8 6 * * * /home/user/backup.sh && curl -fsS -m 10 --retry 5 -o /dev/null https://hc-ping.com/YOUR-UUID
```

Send the exit status, and add start and fail pings:

```bash
curl -fsS -m 10 --retry 5 -o /dev/null https://hc-ping.com/YOUR-UUID/start
/home/user/backup.sh
curl -fsS -m 10 --retry 5 -o /dev/null https://hc-ping.com/YOUR-UUID/$?
```

In a pipeline the exit status is the last command's, so use `set -o pipefail`. See [Cron](../misc/cron.md) and [Borgmatic](../backup/borgmatic.md).

## Schedules and Grace Time
- **Period and grace time:** simple schedules, "expect a ping every N, alert N after".
- **Cron expression and time zone:** for jobs that run at set times.
- **Grace time** is the extra wait before alerting, so a slow run does not page you. With start pings, grace time is also the longest allowed gap between start and success.

Set the grace time to cover the job's normal worst-case run time.

- Cron expressions have five fields. Day of week is 0 to 7 (0 and 7 are Sunday), and lists, ranges, steps and names (`JAN` to `DEC`, `MON` to `SUN`) work.
- If the server is not on UTC, set a matching time zone on the check. If pings arrive an hour out, compare with `timedatectl status`, and see recent cron runs with `journalctl --since "1 hour ago" -t CRON`.

## Management API
Base URL `https://healthchecks.io/api/v3/` (or your own `SITE_ROOT` plus `/api/v3/`). Send the project's API key in the `X-Api-Key` header. Keys belong to one project, and are read-write or read-only (created in Project Settings).

```bash
curl -fsS --header "X-Api-Key: ${HC_API_KEY}" https://healthchecks.io/api/v3/checks/
```

ENDPOINT | DESCRIPTION
---|---
`GET /checks/` | List checks
`GET /checks/<UUID>` | Get one check (a read-only key uses `unique_key` instead)
`POST /checks/` | Create a check
`POST /checks/<UUID>` | Update a check
`POST /checks/<UUID>/pause` | Pause monitoring
`POST /checks/<UUID>/resume` | Resume monitoring
`DELETE /checks/<UUID>` | Delete a check (**destructive**)
`GET /checks/<UUID>/pings/` | Recent pings (100 on free accounts, 1,000 on paid)
`GET /checks/<UUID>/flips/` | Status changes
`GET /channels/` | Integrations
`GET /badges/` | Badge URLs

- Create and update take JSON: `name`, `slug`, `tags` (space-separated), `timeout` and `grace` (60 to 31,536,000 seconds), `schedule` (cron or systemd `OnCalendar`, which overrides `timeout`), `tz`, `methods`, `manual_resume` and `channels` (`"*"` assigns all integrations).
- A `unique` array on create (`name`, `slug`, `tags`, `timeout`, `grace`) makes it an upsert: `200` for an existing match, `201` for a new check.
- A read-only key works only for list, get, flips and badges, and hides UUIDs and ping URLs.
- Keep to 100 requests a minute or you get `429`.

## Prometheus and Badges
Scrape `https://healthchecks.io/projects/<PROJECT_UUID>/metrics/<READONLY_KEY>` with `scheme: https`. The docs example uses `scrape_interval: 60s`. See [Prometheus](prometheus.md).

METRIC | MEANING
---|---
`hc_check_up` | 1 when the check is up
`hc_check_started` | Job has started
`hc_check_grace` | Check is in its grace period
`hc_check_paused` | Check is paused
`hc_tag_up`, `hc_checks_total`, `hc_checks_down_total` | Tag and total counts

Badges cover a project, a tag or a single check, in SVG, JSON or Shields.io JSON. Late counts as up by default. The `svg3`, `json3` and `shields3` variants add a separate late state. Fetch the URLs with `GET /badges/`.

## Self-host (Docker)
```bash
git clone https://github.com/healthchecks/healthchecks.git
cd healthchecks/docker
cp .env.example .env
```

Set at least `ALLOWED_HOSTS`, `DEFAULT_FROM_EMAIL`, `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `SECRET_KEY` and `SITE_ROOT` (for example `https://hc.example.com`) in `.env`, then:

```bash
docker compose up -d
docker compose run web /opt/healthchecks/manage.py createsuperuser
```

The UI is on `http://localhost:8000` (`GUNICORN_PORT` changes it). The sample stack has no TLS, so put a [reverse proxy](../homelab/reverse-proxy-patterns.md) in front that sets `X-Forwarded-For` and `X-Forwarded-Proto`. Pre-built images are `healthchecks/healthchecks:vX.Y`. The Apprise library is preinstalled in the Docker image (see [Apprise](apprise.md)). The image includes PostgreSQL and MySQL drivers. `createsuperuser` accepts `--email` and `--password` to skip the prompts. `LISTEN_IPV6=1` enables IPv6.

SETTING | DEFAULT
---|---
`SITE_ROOT` | `http://localhost:8000`
`SECRET_KEY` | Placeholder, set your own (`SECRET_KEY_FILE` takes precedence)
`DB` | `sqlite`, or `postgres` or `mysql`
`DB_NAME`, `DB_USER`, `DB_HOST`, `DB_PORT`, `DB_PASSWORD` | `hc`, then `postgres` (or `root` for MySQL), the rest empty (`DB_PASSWORD_FILE` takes precedence)
`DB_SSLMODE` | `prefer`
`EMAIL_PORT` | 587
`EMAIL_USE_TLS`, `EMAIL_USE_SSL` | True, False
`EMAIL_USE_VERIFICATION` | True
`REGISTRATION_OPEN` | True. Set to False once your account exists
`ALLOWED_HOSTS` | The domain of `SITE_ROOT`
`PING_ENDPOINT` | `SITE_ROOT` plus `/ping/` (needs the trailing slash)
`DEBUG` | True. Never leave on in production

Default Docker volumes and the status page feature were not verified.

## Notifications
Healthchecks can alert by email, webhook, SMS, chat and incident tools (PagerDuty, Splunk On-Call, Opsgenie, PagerTree). The Pushover "Emergency" priority repeats every 5 minutes until acknowledged. Run Healthchecks on a different host from the jobs it watches, or both fail together.

## See Also
- [Uptime Kuma](uptime-kuma.md) (push monitors do a similar job)
- [Pushover](pushover.md)
- [Apprise](apprise.md)
- [Prometheus](prometheus.md)
- [Cron](../misc/cron.md)

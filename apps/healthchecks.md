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

The UI is on `http://localhost:8000` (`GUNICORN_PORT` changes it). The sample stack has no TLS, so put a [reverse proxy](../homelab/reverse-proxy-patterns.md) in front that sets `X-Forwarded-For` and `X-Forwarded-Proto`. Pre-built images are `healthchecks/healthchecks:vX.Y`. The Apprise library is preinstalled in the Docker image (see [Apprise](apprise.md)). Database options (SQLite, PostgreSQL, MySQL) are on the configuration page, which was not checked here.

## Notifications
Healthchecks can alert by email, webhook, SMS, chat and incident tools (PagerDuty, Splunk On-Call, Opsgenie, PagerTree). The Pushover "Emergency" priority repeats every 5 minutes until acknowledged. Run Healthchecks on a different host from the jobs it watches, or both fail together.

## See Also
- [Uptime Kuma](uptime-kuma.md) (push monitors do a similar job)
- [Pushover](pushover.md)
- [Apprise](apprise.md)
- [Cron](../misc/cron.md)

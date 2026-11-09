# Pushover
Pushover is a hosted push notification service with a simple HTTPS API and apps for phones and desktops. It is not self-hosted, but it is reliable and has an emergency priority that repeats until you acknowledge. Use it as the "wake me up" channel for alerts from [Alertmanager](alertmanager.md), [Healthchecks](healthchecks.md) and [Uptime Kuma](uptime-kuma.md).

Documentation: [Pushover API](https://pushover.net/api)

## Cost
- The client apps are a one-time purchase per platform ($4.99 USD at the time of checking, no subscription).
- Each user can send 10,000 messages per month for free, shared across their apps. Going over returns HTTP 429. The quota resets on the 1st at 00:00 US Central Time.

## Keys
- **User key:** identifies you (shown on your Pushover dashboard).
- **API token:** one per application, created under "Create an Application/API Token". Make one per sender.

Keep both out of scripts committed to Git. Load them from an environment variable or a secrets file.

## Send a Message
```bash
curl -s https://api.pushover.net/1/messages.json \
  --data-urlencode "token=${PUSHOVER_APP_TOKEN}" \
  --data-urlencode "user=${PUSHOVER_USER_KEY}" \
  --data-urlencode "title=Backup finished" \
  --data-urlencode "message=Backup finished in 16 minutes."
```

The endpoint is `POST https://api.pushover.net/1/messages.json` over HTTPS. The body can be form-encoded or JSON. A success returns `{"status":1,"request":"..."}`. The curl command is composed from the documented parameters, not copied from the docs.

PARAMETER | DESCRIPTION
---|---
`token`, `user`, `message` | Required
`title` | Title (250 characters)
`priority` | `-2` silent, `-1` quiet, `0` normal (default), `1` high, `2` emergency
`sound` | Sound name, for example `pushover` (default), `siren`, `magic`, `none`
`url`, `url_title` | A link (512 characters) and its label (100)
`device` | Send to one device only
`html` | `1` to allow basic HTML
`monospace` | `1` for monospace text
`ttl` | Seconds until the message expires (ignored for priority 2)
`attachment` | An image, up to 5 MB, sent as multipart

The message limit is 1024 UTF-8 characters.

## Emergency Priority
Priority `2` repeats until acknowledged and needs two more parameters:

```bash
curl -s https://api.pushover.net/1/messages.json \
  --data-urlencode "token=${PUSHOVER_APP_TOKEN}" \
  --data-urlencode "user=${PUSHOVER_USER_KEY}" \
  --data-urlencode "message=Disk array degraded" \
  --data-urlencode "priority=2" \
  --data-urlencode "retry=60" \
  --data-urlencode "expire=1800"
```

`retry` is at least 30 seconds, `expire` is at most 10800 seconds (3 hours), and retries stop after 50 attempts. Use emergency sparingly or you will start ignoring it.

## Validate and Limits
COMMAND | DESCRIPTION
---|---
`POST https://api.pushover.net/1/users/validate.json` with `token` and `user` | Check a user key (`status` 1 is valid)
`GET https://api.pushover.net/1/apps/limits.json?token=<TOKEN>` | Remaining monthly quota
`GET https://api.pushover.net/1/sounds.json?token=<TOKEN>` | List sound names

The response headers `X-Limit-App-Limit`, `X-Limit-App-Remaining` and `X-Limit-App-Reset` also report usage.

## Be a Good Client
- On a 4xx response do **not** retry the same request. Repeated 4xx can get your IP blocked.
- On a 5xx or no reply, wait at least 5 seconds before retrying.
- Use at most 2 concurrent connections.

## From Apprise
`apprise -t "Title" -b "Body" "pover://USER_KEY@APP_TOKEN"`, see [Apprise](apprise.md).

## See Also
- [Healthchecks](healthchecks.md)
- [Apprise](apprise.md)
- [ntfy](ntfy.md)
- [Notification Services](../homelab/notification-services.md)

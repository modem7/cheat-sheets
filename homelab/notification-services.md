# Notification Services
How to get alerts from your homelab to your phone: which service to use, how scripts send messages, and the plain webhook APIs for Discord, Slack, Telegram and Matrix. Dedicated sheets exist for [ntfy](../apps/ntfy.md), [Gotify](../apps/gotify.md), [Apprise](../apps/apprise.md), [Pushover](../apps/pushover.md), [Healthchecks](../apps/healthchecks.md) and [msmtp](../tools/msmtp.md). Alert sources are [Alertmanager](../apps/alertmanager.md) and [Uptime Kuma](../apps/uptime-kuma.md).

## Which One
NEED | USE
---|---
Self-hosted push, publish with `curl`, no accounts for senders | [ntfy](../apps/ntfy.md)
Self-hosted push with an app and token model, a web inbox | [Gotify](../apps/gotify.md)
One send command for many services, or tools that already embed it | [Apprise](../apps/apprise.md)
Reliable hosted push with an emergency priority | [Pushover](../apps/pushover.md)
Detect cron jobs and backups that did not run | [Healthchecks](../apps/healthchecks.md)
Plain email from scripts | [msmtp](../tools/msmtp.md)
Team chat channel | Discord, Slack or Matrix webhooks (below)

## Comparison
| | ntfy | Gotify | Apprise | Pushover | Shoutrrr |
|---|---|---|---|---|---|
| What it is | Push server | Push server | Library, CLI and optional API gateway | Hosted service | Go library and CLI sender |
| Self-hostable | Yes | Yes | Yes (the API gateway) | No | Not a server |
| Mobile app | Android, iOS, F-Droid | Android | Companion for the API only | Android, iOS, desktop (paid once) | None |
| Needs a server | Optional (public ntfy.sh exists) | Yes | No (CLI) | No | No |

Apprise and Shoutrrr send **to** services, they do not deliver to a phone themselves. A topic on an open ntfy server is effectively a password, so use access control for anything private. Treat webhook URLs and bot tokens as secrets.

## Principles
- Send from one place (Alertmanager, Uptime Kuma, Healthchecks) and route there, instead of every script having its own channel.
- Use at least two independent routes, and have one send from **outside** the lab, because alerting that lives on the failing host does not alert.
- Page only for things you act on, and send the rest to a quiet channel.
- Store tokens in environment variables or secret files, never in committed scripts.
- Test the whole path regularly, for example with an always-firing Watchdog alert watched by [Healthchecks](../apps/healthchecks.md).

## Discord
Create a webhook in the channel's integration settings, then POST JSON.

```bash
curl -H "Content-Type: application/json" -X POST \
  -d '{"content":"Backup finished"}' \
  "${DISCORD_WEBHOOK_URL}"
```

- `content` is up to 2000 characters. `embeds` takes up to 10 embed objects.
- Other fields: `username`, `avatar_url`, `allowed_mentions`, `thread_name`. Add `?wait=true` to get the message back. Forum channels need `thread_id` or `thread_name`.
- At least one of `content`, `embeds`, `components`, `file` or `poll` is required. Sanitise user text and use `allowed_mentions` so a message cannot ping everyone.
- The URL is `https://discord.com/api/webhooks/<id>/<token>`. The `/api` prefix is inferred from Discord's usual API paths, so copy the URL Discord gives you.

## Slack
Create an app, turn on Incoming Webhooks and add a webhook to a channel.

```bash
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Backup finished"}' \
  "${SLACK_WEBHOOK_URL}"
```

The URL contains a secret and Slack revokes leaked ones. The payload is `text`, plus optional `blocks`. A webhook cannot override the channel, username or icon.

## Telegram
1. Message `@BotFather`, send `/newbot` and follow the steps. Save the token like a password.
2. Message your bot once, then read your chat ID with `getUpdates` (the ID is `message.chat.id`).
3. Send:

```bash
curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  --data-urlencode "chat_id=${TELEGRAM_CHAT_ID}" \
  --data-urlencode "text=Backup finished"
```

`text` is 1 to 4096 characters. `getUpdates` does not work while a webhook is set (use `deleteWebhook` first), and updates are kept for at most 24 hours. Revoke a leaked token in `@BotFather`. `parse_mode` accepts `HTML` (and others, not checked here).

## Matrix
```bash
curl -X PUT \
  -H "Authorization: Bearer ${MATRIX_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"msgtype":"m.text","body":"Backup finished"}' \
  "https://matrix.example.com/_matrix/client/v3/rooms/ROOM_ID/send/m.room.message/$(date +%s)"
```

The path is `PUT /_matrix/client/v3/rooms/{roomId}/send/{eventType}/{txnId}`. Reusing the same transaction ID returns the original result, which makes retries safe. Percent-encode the room ID (`!` and `:`). The message body format and the encoding note were not confirmed in this pass.

## Shoutrrr
A Go library and CLI for sending notifications, used by Watchtower and kured. The original `containrrr/shoutrrr` repository and the active fork `nicholas-fedor/shoutrrr` differ, and I could not confirm the original's archive status, so check which one your tool uses. URL syntax differs between versions and from Apprise.

```bash
shoutrrr send --url "SERVICE_URL" --message "Hello"
```

A Discord URL in the original is `discord://token@channel`, in the fork `discord://TOKEN@WEBHOOK_ID`. The `shoutrrr verify` subcommand was not found in the docs, so check `shoutrrr --help`. For the full list of supported services see the project's own docs.

## See Also
- [ntfy](../apps/ntfy.md)
- [Gotify](../apps/gotify.md)
- [Apprise](../apps/apprise.md)
- [Alertmanager](../apps/alertmanager.md)

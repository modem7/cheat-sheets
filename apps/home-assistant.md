# Home Assistant
Home Assistant is a self-hosted home automation platform that connects smart devices and runs local automations. This sheet covers the Container install, the Home Assistant OS `ha` command line, backups and reverse-proxy settings.

Documentation: [Home Assistant](https://www.home-assistant.io/installation/)

## Install Methods
METHOD | NOTES
---|---
Home Assistant OS | Recommended. Full appliance with apps and backups built in. Use a VM (see [Proxmox](../proxmox/proxmox-overview.md)) or a dedicated board
Container | You run the Docker image yourself. No apps (add-ons)
Supervised | Not covered here (the page was not checked)

## Container (Docker)
Needs Docker Engine 23.0.0 or later. Docker Desktop is not supported.

```yaml
services:
  homeassistant:
    image: ghcr.io/home-assistant/home-assistant:stable
    container_name: homeassistant
    restart: unless-stopped
    privileged: true
    network_mode: host
    stop_grace_period: 60s
    environment:
      TZ: Europe/London
    volumes:
      - ./config:/config
      - /run/dbus:/run/dbus:ro
```

`network_mode: host` is needed for device discovery, so Home Assistant listens on port 8123 on the host. Restart with `docker compose restart homeassistant` or from Settings, System.

## Configuration Checks
- Settings, Tools, YAML, **Check configuration** before reloading.
- A check also runs automatically on reload and restart.
- Most YAML changes apply with a reload. A new YAML integration needs a restart.
- On Home Assistant OS: `ha core check`.

## ha CLI (Home Assistant OS)
Run it from the Terminal and SSH app.

COMMAND | DESCRIPTION
---|---
`ha core check` | Validate the configuration
`ha core restart` | Restart Home Assistant Core
`ha core logs` | Show Core logs
`ha core update --backup` | Update Core after taking a backup
`ha core update --version <VERSION> --backup` | Update (or roll back) to a specific version
`ha backups new --name <NAME>` | Create a backup
`ha backups list` | List backups
`ha backups restore <SLUG>` | Restore a backup
`ha os info` / `ha os update` | Operating system info and update
`ha supervisor info` / `ha supervisor reload` | Supervisor info and reload
`ha host reboot` | Reboot the host

Only some commands were quoted from the docs, the rest come from a summary, so run `ha help` on your install to confirm.

## Automations (YAML)
Blocks use plural keys and each item names its type:

```yaml
- id: "porch_light_sunset"
  alias: Porch light at sunset
  mode: single
  triggers:
    - trigger: sun
      event: sunset
      offset: "-01:00:00"
  conditions:
    - condition: time
      after: "16:00:00"
  actions:
    - action: homeassistant.turn_on
      target:
        entity_id: light.porch
```

- Renames: `service:` became `action:` in 2024.8, and `platform:` became `trigger:` and the singular top-level keys became plural in 2024.10. Old keys still work, but do not mix old and new in one place.
- Other options: `description`, `variables`, `trigger_variables`, `max` and `max_exceeded`.
- `mode` is `single` by default (also `restart`, `queued`, `parallel`). `max` defaults to 10 and applies to `queued` and `parallel`.
- Entries in `automations.yaml` need a unique `id`, and the file must stay a list.

## Scripts and Scenes
- Script steps go under `sequence:`. Step options include `alias`, `continue_on_error: true` and `enabled: false`.
- `action: script.<NAME>` waits for the script and can return a response. `action: script.turn_on` with `target.entity_id` runs it in the background and returns nothing.
- Script fields are available as template variables, for example `{{ minutes | default(5) }}`. "Required" and "Default" in the editor are not enforced.
- Scenes in YAML are a `scene:` list with `name`, `icon` and `entities:`. Add an `id` to edit one in the UI.
- Scene actions: `scene.turn_on` (with `transition`), `scene.create` (`scene_id`, `snapshot_entities`) and `scene.reload`.

## Templates
TEMPLATE | RESULT
---|---
`{{ states('sensor.x') }}` | State as a string
`{{ states('sensor.x') \| float(0) + 5 }}` | Convert, with a default if unavailable
`{{ state_attr('light.kitchen', 'brightness') \| int(0) }}` | An attribute
`{{ is_state('light.kitchen', 'on') }}` | State check
`{{ is_state_attr('media_player.living_room', 'source', 'Spotify') }}` | Attribute check
`{{ has_value('sensor.x') }}` | True unless unknown or unavailable
`{{ now().strftime('%H:%M') }}` | Current local time (`now()` re-renders each minute)
`{{ now().weekday() }}` | Day of week, 0 is Monday
`{{ (now() - states.binary_sensor.front_door.last_changed).total_seconds() > 600 }}` | Open for over 10 minutes

Test templates in Developer Tools. It is now called **Tools**, with tabs YAML, States, Actions, Action history, Template, Events, Statistics and Assist.

## Splitting Config and Secrets
DIRECTIVE | MEANING
---|---
`!include <FILE>` | Include one file
`!include_dir_list <DIR>` | One entry per file
`!include_dir_named <DIR>` | File name becomes the key
`!include_dir_merge_list <DIR>` | Merge lists from all files
`!include_dir_merge_named <DIR>` | Merge dictionaries from all files
`!secret <NAME>` | Value from `secrets.yaml`

Directory includes read `.yaml` files only. Packages use `homeassistant: packages: !include_dir_named packages`, where the file name is the package name and must be unique. `auth_providers` must stay in `configuration.yaml`. `!secret` looks in the referencing file's folder, then up to the config folder. Do not use `!secret` in `automations.yaml` or `scripts.yaml`, because it breaks the UI editor. Keep `secrets.yaml` out of Git.

## REST and WebSocket API
Create a long-lived access token under your profile, Security, and keep it in a variable. Every request needs the Bearer header, and a missing or bad token returns 401.

```bash
curl -fsS -H "Authorization: Bearer ${HA_TOKEN}" http://<HA_HOST>:8123/api/
curl -fsS -H "Authorization: Bearer ${HA_TOKEN}" -H "Content-Type: application/json" \
  -d '{"entity_id": "light.kitchen"}' http://<HA_HOST>:8123/api/services/light/turn_on
```

ENDPOINT | DESCRIPTION
---|---
`GET /api/` | API check (needs the trailing slash)
`GET /api/states` | All entity states
`GET /api/states/<ENTITY_ID>` | One entity
`POST /api/services/<DOMAIN>/<SERVICE>` | Call an action with a JSON body
`POST /api/template` | Render a template (admin only)
`POST /api/config/core/check_config` | Check the config (admin only)

The WebSocket API is at `/api/websocket`. The server sends `auth_required`, you reply `{"type": "auth", "access_token": "..."}`, and it answers `auth_ok` or `auth_invalid`. Each command carries an increasing `id`. Commands include `subscribe_events` (`event_type`), `call_service` (`domain`, `service`, `service_data`, `target`) and `get_states`.

## MQTT and Zigbee
- MQTT needs a broker that supports MQTT v5. The Mosquitto Broker app is the easiest. Add the integration under Settings, Devices and services.
- Discovery is on by default with the prefix `homeassistant`. `action: mqtt.publish` takes `topic`, `payload` and `retain`.
- ZHA needs a Zigbee USB coordinator, and one radio cannot be shared between ZHA and Zigbee2MQTT.
- Zigbee2MQTT needs the MQTT integration and `homeassistant: enabled: true` in its own config.

## Recorder and Logger
SETTING | DEFAULT OR USE
---|---
`recorder: purge_keep_days` | 10
`recorder: auto_purge` | true, runs at 04:12
`recorder: commit_interval` | 5
`recorder: db_url` | `sqlite:////<PATH>/<DB_NAME>`, `mysql://<USER>:<PASSWORD>@<SERVER>/<DB_NAME>?charset=utf8mb4` or `postgresql://<USER>:<PASSWORD>@<SERVER>/<DB_NAME>`
`recorder: exclude:` | `domains`, `entity_globs`, `entities`, `event_types`
`logger: default: warning` | Default log level
`logger: logs: homeassistant.components.mqtt: debug` | Per-integration level

Levels: critical, fatal, error, warning, warn, info, debug, notset. `recorder.purge`, `logger.set_level` and `logger.set_default_level` are actions. Their parameters were not checked. Put a database password in `!secret`.

## Notifications
- `action: notify.send_message` targets a notify entity.
- `action: notify.persistent_notification` takes `title` and `message`.
- `action: notify.mobile_app_<DEVICE_ID>` sends to the companion app, with `message` (required) and `title`.
- See [ntfy](ntfy.md) and [Notification Services](../homelab/notification-services.md) for push options.

## Safe Mode
Settings, System, power icon, More options, then safe mode. A normal restart leaves it. It disables custom integrations and community frontend modules (from a search snippet, not a docs page). On Home Assistant OS, `ha core restart --safe-mode` is also said to work. Neither the flag nor a safe-mode file in the config folder was verified.

## Backups
- On Home Assistant OS, backups are created and stored in your configured backup locations.
- On Container, backups are in a `backups` folder inside the config directory.
- A backup holds the config folder and `ssl`. Restore needs internet access and at least 2 GB free.
- Restore from Settings, System, Backups. Copy backups off the box (see [Restic](../backup/restic.md)), and test a restore.

## Behind a Reverse Proxy
Reverse-proxy requests are blocked unless trusted. As of Home Assistant 2026.8 the "Trust X-Forwarded-For" and "Trusted proxies" options are in the UI under Settings, System, Network, and the old YAML `http:` block is migrated to the UI and should be removed. On older versions use the YAML keys `use_x_forwarded_for` and `trusted_proxies` under `http:` (the YAML example was not in the docs checked). The default port is 8123 for Container, and 80 on Home Assistant OS from 2026.8. See [Reverse Proxy Patterns](../homelab/reverse-proxy-patterns.md).

## See Also
- [Uptime Kuma](uptime-kuma.md)
- [ntfy](ntfy.md)
- [Notification Services](../homelab/notification-services.md)
- [VLANs](../homelab/vlans.md)
- [Wake on LAN](../homelab/wake-on-lan.md)

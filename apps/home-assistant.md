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
- [VLANs](../homelab/vlans.md)
- [Wake on LAN](../homelab/wake-on-lan.md)

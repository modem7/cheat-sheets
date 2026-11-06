# CrowdSec
CrowdSec is a modern, collaborative intrusion-prevention system. The **Security Engine** reads logs and detects attacks using scenarios; **bouncers** (firewall, reverse-proxy, Traefik, nginx...) enforce the resulting decisions; and a shared community blocklist pre-emptively blocks known bad IPs. It does what [[fail2ban]] does with a decoupled design, so one engine can protect many hosts and proxies.

Documentation: [CrowdSec Docs](https://docs.crowdsec.net/) · [Hub (collections)](https://app.crowdsec.net/hub)

## Install on a Host
```bash
curl -s https://install.crowdsec.net | sudo sh     # adds the package repo (read the script first)
sudo apt install crowdsec
sudo apt install crowdsec-firewall-bouncer-nftables      # or ...-iptables
sudo systemctl status crowdsec crowdsec-firewall-bouncer
```
The firewall bouncer registers itself with the local API on install. Firewall background: [[iptables]], [[ufw]].

## cscli
COMMAND | DESCRIPTION
---|---
`sudo cscli metrics` | Parsed logs, scenario hits and bouncer activity
`sudo cscli decisions list` | Active bans
`sudo cscli decisions add --ip <IP> --duration 4h --reason "manual"` | Ban an IP
`sudo cscli decisions add --range 203.0.113.0/24 --type captcha` | Ban or challenge a range
`sudo cscli decisions delete --ip <IP>` | Unban
`sudo cscli decisions delete --all` | Remove every decision
`sudo cscli alerts list` | Detected attacks
`sudo cscli alerts inspect <ID> -d` | Alert detail
`sudo cscli hub update` | Refresh the hub index
`sudo cscli hub upgrade` | Upgrade installed hub items
`sudo cscli collections list` | Installed collections
`sudo cscli collections install crowdsecurity/nginx` | Parsers and scenarios for a service
`sudo cscli collections install crowdsecurity/sshd crowdsecurity/linux` | Several at once
`sudo cscli parsers list` / `scenarios list` | Individual components
`sudo cscli bouncers list` | Registered bouncers
`sudo cscli bouncers add <NAME>` | Create an API key for a bouncer (shown once)
`sudo cscli bouncers delete <NAME>` | Revoke a bouncer
`sudo cscli machines list` | Registered engines
`sudo cscli lapi status` | Check the local API
`sudo cscli console enroll <ENROLL_KEY>` | Link to the CrowdSec Console web dashboard
`sudo cscli explain --file /var/log/auth.log --type syslog` | Debug how a log is parsed

After installing collections: `sudo systemctl reload crowdsec`.

## Acquisition (which logs to read)
`/etc/crowdsec/acquis.yaml` (or files in `/etc/crowdsec/acquis.d/`):
```yaml
filenames:
  - /var/log/auth.log
labels:
  type: syslog
---
source: journalctl
journalctl_filter:
  - "_SYSTEMD_UNIT=ssh.service"
labels:
  type: syslog
---
filenames:
  - /var/log/nginx/*.log
labels:
  type: nginx
---
source: docker
container_name:
  - traefik
labels:
  type: traefik
```
The `type` label must match what the collection's parsers expect.

## Docker Compose (engine + Traefik bouncer)
```yaml
services:
  crowdsec:
    image: crowdsecurity/crowdsec:<TAG>
    restart: unless-stopped
    environment:
      COLLECTIONS: "crowdsecurity/traefik crowdsecurity/http-cve crowdsecurity/linux"
      BOUNCER_KEY_traefik: ${CROWDSEC_BOUNCER_KEY}        # pre-registers a bouncer named "traefik"
    volumes:
      - ./crowdsec/acquis.yaml:/etc/crowdsec/acquis.yaml:ro
      - crowdsec-db:/var/lib/crowdsec/data
      - crowdsec-config:/etc/crowdsec
      - /var/run/docker.sock:/var/run/docker.sock:ro   # for the docker datasource
    networks: [proxy]

  bouncer:
    image: ghcr.io/<TRAEFIK_BOUNCER_IMAGE>:<TAG>      # e.g. a Traefik forward-auth bouncer
    restart: unless-stopped
    environment:
      CROWDSEC_BOUNCER_API_KEY: ${CROWDSEC_BOUNCER_KEY}
      CROWDSEC_AGENT_HOST: crowdsec:8080
    networks: [proxy]
volumes:
  crowdsec-db:
  crowdsec-config:
networks:
  proxy:
    external: true
```
Generate the key with `openssl rand -hex 32` and keep it in `.env` (see [[sops-age]]). Mounting the Docker socket exposes the host, so use a socket proxy if you can. Wire the bouncer into [[traefik]] through a forwardAuth middleware or the Traefik bouncer plugin, or into [[nginx]] with the nginx bouncer; details are in the bouncer's docs. Run `docker exec crowdsec cscli ...` for commands.

## Allowlist Your Own IPs
```bash
sudo cscli allowlists create home -d "trusted IPs"       # CrowdSec 1.6.8+
sudo cscli allowlists add home 192.168.1.0/24 203.0.113.10
```
Older versions: a `parsers/s02-enrich` whitelist file under `/etc/crowdsec/parsers/s02-enrich/`.

## Troubleshooting
SYMPTOM | FIX
---|---
`cscli metrics` shows no parsed logs | Check `acquis.yaml` paths and `type` label; `cscli explain`; confirm CrowdSec can read the files
Bouncer shows `last_pull` empty | Wrong API key or URL; `cscli bouncers list`, check bouncer config `api_url` and `api_key`
Banned IP still connects | Container traffic bypasses the INPUT chain; put the bouncer at the reverse proxy or the `DOCKER-USER` chain. Check `sudo nft list ruleset`
Reverse proxy sees only proxy IP | Configure trusted proxies / real-IP headers so the logged IP is the client
You blocked yourself | `sudo cscli decisions delete --ip <IP>` and add an allowlist entry
Port 8080 conflict with another service | Change `listen_uri` in `/etc/crowdsec/config.yaml` and the bouncer `api_url`

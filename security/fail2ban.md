# fail2ban
fail2ban watches log files (or the systemd journal) for repeated failures such as bad SSH logins and bans the offending IP by adding firewall rules for a set time. It is host-based and simple; for community blocklists and a modern bouncer architecture see [CrowdSec](crowdsec.md). Firewall back-ends are covered in [UFW (uncomplicated firewall)](../linux/ufw.md) and [IPTables](../linux/iptables.md).

Documentation: [fail2ban on GitHub](https://github.com/fail2ban/fail2ban) · [Wiki](https://github.com/fail2ban/fail2ban/wiki)

## Install
```bash
sudo apt install fail2ban
sudo systemctl enable --now fail2ban
```
Never edit `jail.conf` or `fail2ban.conf`; put overrides in `/etc/fail2ban/jail.local` or `/etc/fail2ban/jail.d/*.local`.

## fail2ban-client
COMMAND | DESCRIPTION
---|---
`sudo fail2ban-client status` | List active jails
`sudo fail2ban-client status sshd` | Failures, bans and banned IPs for a jail
`sudo fail2ban-client banned` | All currently banned IPs by jail
`sudo fail2ban-client set sshd banip <IP>` | Ban manually
`sudo fail2ban-client set sshd unbanip <IP>` | Unban
`sudo fail2ban-client unban --all` | Clear every ban
`sudo fail2ban-client reload` | Reload configuration
`sudo fail2ban-client reload sshd` | Reload a single jail
`sudo fail2ban-client get sshd bantime` | Read a jail setting
`sudo fail2ban-client set sshd addignoreip <IP>` | Whitelist at runtime
`sudo fail2ban-client -t` | Test the configuration
`sudo fail2ban-client ping` | Check the server is alive

## /etc/fail2ban/jail.local
```ini
[DEFAULT]
ignoreip  = 127.0.0.1/8 ::1 192.168.0.0/16 10.0.0.0/8
bantime   = 1h
findtime  = 10m
maxretry  = 5
backend   = systemd
banaction = nftables
# escalate repeat offenders
bantime.increment = true
bantime.factor    = 2
bantime.maxtime   = 5w

[sshd]
enabled = true
port    = ssh
mode    = aggressive      # also matches pre-auth failures and probes

[recidive]
enabled   = true
logpath   = /var/log/fail2ban.log
bantime   = 1w
findtime  = 1d
maxretry  = 3
```
SETTING | MEANING
---|---
`maxretry` | Failures within `findtime` that trigger a ban
`findtime` | Window in which failures are counted
`bantime` | Ban length; `-1` is permanent
`ignoreip` | IPs/CIDRs that are never banned (include your LAN and VPN, see [Tailscale](../apps/tailscale.md))
`backend` | `auto`, `systemd` (journal) or `polling`; use `systemd` on modern distros without `/var/log/auth.log`
`banaction` | Firewall action: `iptables-multiport`, `nftables`, `ufw`, ...
`logpath` | Log file to watch (not needed with `backend = systemd`)

## Custom Jail and Filter
Ban IPs that hammer a web app login (example for an [Nginx](../apps/nginx.md) access log).

`/etc/fail2ban/filter.d/myapp-auth.conf`:
```ini
[Definition]
failregex = ^<HOST> .* "POST /login HTTP/[\d.]+" 401
ignoreregex =
```
`/etc/fail2ban/jail.d/myapp.local`:
```ini
[myapp-auth]
enabled  = true
port     = http,https
filter   = myapp-auth
logpath  = /var/log/nginx/access.log
maxretry = 5
findtime = 5m
bantime  = 1h
```
Test a filter against a log before enabling it:
```bash
fail2ban-regex /var/log/nginx/access.log /etc/fail2ban/filter.d/myapp-auth.conf
fail2ban-regex --print-all-matched /var/log/nginx/access.log /etc/fail2ban/filter.d/myapp-auth.conf
fail2ban-regex systemd-journal sshd             # test a filter on the journal
```

## Docker Caveat
Published container ports bypass the INPUT chain, so the default ban rules do not protect containers. Make the action insert into `DOCKER-USER`:
```ini
[myapp-auth]
chain = DOCKER-USER
```
Behind a reverse proxy ([Traefik](../apps/traefik.md), [Nginx](../apps/nginx.md)) the log shows the proxy's IP unless real-client-IP headers are configured; fix that first or you will ban the proxy. See [Docker Networking](../docker/docker-networking.md).

## Troubleshooting
SYMPTOM | FIX
---|---
Jail doesn't start | `sudo fail2ban-client -t`; `journalctl -u fail2ban -e`; a bad `logpath` is the usual cause
`Have not found any log file for sshd jail` | Set `backend = systemd` (no `auth.log` on minimal installs)
Nothing is banned | Run `fail2ban-regex` against the log; check time zone/format; check `ignoreip`
Banned but attacker still connects | Wrong `banaction` for your firewall, or Docker traffic (see above). Check `sudo nft list ruleset` or `sudo iptables -S`
Locked yourself out | From console: `sudo fail2ban-client set sshd unbanip <IP>`, then add the IP to `ignoreip`
Bans lost on restart | Persistent by default via the sqlite DB (`/var/lib/fail2ban/fail2ban.sqlite3`); check `dbpurgeage`

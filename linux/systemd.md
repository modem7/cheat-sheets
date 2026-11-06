# systemd
`systemd` is the init system and service manager on nearly every modern Linux distribution. It starts services, runs timers, collects logs (`journald`) and applies resource and security limits. Units are plain text files; `systemctl` controls them and `journalctl` reads their logs. Short versions of the commands are in [[linux]].

Documentation: [systemd.service](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html) · [systemd.exec](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html) · [systemd.timer](https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html) · [systemd-analyze](https://www.freedesktop.org/software/systemd/man/latest/systemd-analyze.html)

> **Verification:** options and commands below come from the systemd man pages and common practice. No command was executed. Check the hardening options against your systemd version (`systemctl --version`) and test with `systemd-analyze security`.

See also: [[linux]] · [[performance-troubleshooting]] · [[selinux-apparmor]] · [[docker]]

---
## systemctl
COMMAND | DESCRIPTION
---|---
`systemctl status <UNIT>` | State, recent log lines, main PID
`sudo systemctl start\|stop\|restart <UNIT>` | Start, stop, restart now
`sudo systemctl reload <UNIT>` | Ask the service to re-read its config (needs `ExecReload=`)
`sudo systemctl try-restart <UNIT>` | Restart only if already running
`sudo systemctl enable --now <UNIT>` | Start at boot and start now
`sudo systemctl disable --now <UNIT>` | Stop and do not start at boot
`sudo systemctl mask <UNIT>` | Make a unit impossible to start (links it to `/dev/null`)
`sudo systemctl unmask <UNIT>` | Undo mask
`systemctl is-active <UNIT>` | Prints `active`, `failed`, ... (good for scripts)
`systemctl is-enabled <UNIT>` | Prints `enabled`, `disabled`, `masked`, ...
`systemctl list-units --type=service` | Loaded services
`systemctl list-units --failed` | Failed units (same as `systemctl --failed`)
`systemctl list-unit-files --state=enabled` | Units enabled at boot
`sudo systemctl reset-failed` | Clear failed state
`systemctl cat <UNIT>` | Unit file plus every drop-in, as systemd sees it
`systemctl show <UNIT> -p ExecStart -p Restart` | Specific properties
`systemctl list-dependencies <UNIT>` | What a unit pulls in
`systemctl list-dependencies --reverse <UNIT>` | What depends on a unit
`sudo systemctl daemon-reload` | Re-read unit files after any edit
`sudo systemctl edit <UNIT>` | Create or edit a drop-in override
`sudo systemctl edit --full <UNIT>` | Edit a full copy in `/etc/systemd/system/`
`sudo systemctl revert <UNIT>` | Remove overrides and go back to the packaged unit
`sudo systemctl isolate rescue.target` | Switch target (rescue mode)
`systemctl get-default` / `sudo systemctl set-default multi-user.target` | Default boot target
`sudo systemctl poweroff` / `reboot` | Shut down or reboot
`systemctl --user <CMD>` | Same, for the per-user manager

---
## Unit File Locations
PATH | PURPOSE
---|---
`/etc/systemd/system/` | Your units and overrides (highest priority)
`/etc/systemd/system/<UNIT>.d/*.conf` | Drop-in overrides
`/run/systemd/system/` | Runtime, transient units
`/usr/lib/systemd/system/` (or `/lib/systemd/system/`) | Packaged units. Do not edit
`~/.config/systemd/user/` | Per-user units

---
## A Service Unit
`/etc/systemd/system/myapp.service`:
```ini
[Unit]
Description=My app
Documentation=https://example.com/docs
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=myapp
Group=myapp
WorkingDirectory=/opt/myapp
EnvironmentFile=-/etc/myapp/env
ExecStart=/opt/myapp/bin/myapp --config /etc/myapp/config.yml
ExecReload=/bin/kill -HUP $MAINPID
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now myapp.service
systemctl status myapp.service
```

KEY | DESCRIPTION
---|---
`Type=simple` | Default. The process in `ExecStart` is the service
`Type=forking` | Process forks and the parent exits. Needs `PIDFile=` ideally
`Type=oneshot` | Runs and exits. Add `RemainAfterExit=yes` to keep it "active"
`Type=notify` | Service tells systemd when ready (`sd_notify`)
`After=` / `Before=` | Ordering only. Does not pull the other unit in
`Wants=` / `Requires=` | Pull a unit in. `Requires=` fails if the dependency fails
`EnvironmentFile=-<PATH>` | Load `KEY=value` lines. The `-` means ignore if missing
`Restart=on-failure` | Restart on non-zero exit, signal, timeout. Also `always`, `no`
`RestartSec=` | Delay before restart
`StartLimitIntervalSec=` / `StartLimitBurst=` | Give up after too many restarts (in `[Unit]`)
`TimeoutStopSec=` | Wait before SIGKILL
`ExecStartPre=` / `ExecStartPost=` / `ExecStopPost=` | Hooks around start and stop
`LimitNOFILE=65536` | Raise the open file limit
`MemoryMax=512M` / `CPUQuota=50%` / `TasksMax=200` | Resource limits (cgroups)
`StandardOutput=journal` | Default. Also `append:<FILE>` or `null`

---
## Drop-ins and Overrides
Change a packaged unit without editing it. The change survives package updates.

```bash
sudo systemctl edit nginx.service
```
This opens an editor and saves `/etc/systemd/system/nginx.service.d/override.conf`. Only list what changes:
```ini
[Service]
Restart=always
RestartSec=3
Environment=TZ=Europe/London
```
To **replace** a list option such as `ExecStart`, clear it first:
```ini
[Service]
ExecStart=
ExecStart=/usr/sbin/nginx -g 'daemon on; master_process on;'
```
Then `systemctl cat nginx` to confirm and `sudo systemctl restart nginx`. `systemctl edit` runs `daemon-reload` for you.

---
## Timers (cron replacement)
A timer activates a service of the same name. Two files:

`/etc/systemd/system/backup.service`:
```ini
[Unit]
Description=Nightly backup

[Service]
Type=oneshot
User=backup
ExecStart=/usr/local/bin/backup.sh
```
`/etc/systemd/system/backup.timer`:
```ini
[Unit]
Description=Run backup nightly

[Timer]
OnCalendar=*-*-* 02:30:00
RandomizedDelaySec=10m
Persistent=true

[Install]
WantedBy=timers.target
```
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now backup.timer
systemctl list-timers --all
journalctl -u backup.service
```
Enable the **timer**, not the service.

KEY | DESCRIPTION
---|---
`OnCalendar=daily` | Shortcuts: `hourly`, `daily`, `weekly`, `monthly`
`OnCalendar=Mon..Fri 08:00` | Weekdays at 08:00
`OnCalendar=*:0/15` | Every 15 minutes
`OnBootSec=5min` | 5 minutes after boot
`OnUnitActiveSec=1h` | 1 hour after the service last ran (monotonic)
`Persistent=true` | Run a missed job after the machine was off (only for `OnCalendar`)
`RandomizedDelaySec=` | Spread load
`AccuracySec=1s` | Default accuracy is 1 minute

COMMAND | DESCRIPTION
---|---
`systemd-analyze calendar "Mon..Fri 08:00"` | Check an expression and see the next run
`sudo systemctl start backup.service` | Run the job now to test it
`systemd-run --on-active=30m /usr/local/bin/task.sh` | One-off transient timer

---
## Transient Units: systemd-run
COMMAND | DESCRIPTION
---|---
`sudo systemd-run --unit=mytask <CMD>` | Run a command as a service, logs in the journal
`sudo systemd-run --scope -p MemoryMax=1G <CMD>` | Run in the foreground under a memory limit
`systemd-run --user --pty <CMD>` | Interactive in the user manager
`sudo systemd-run -p CPUQuota=25% -p IOWeight=50 <CMD>` | Limit CPU and I/O weight

---
## journalctl
COMMAND | DESCRIPTION
---|---
`journalctl -u <UNIT>` | One unit's logs
`journalctl -u <UNIT> -f` | Follow
`journalctl -u <UNIT> -n 100 --no-pager` | Last 100 lines
`journalctl -b` | Current boot
`journalctl -b -1` | Previous boot (needs persistent journal)
`journalctl --list-boots` | Known boots
`journalctl -p err -b` | Errors and worse this boot
`journalctl --since "2026-01-01 10:00" --until "1 hour ago"` | Time range
`journalctl -k` | Kernel messages (like `dmesg`)
`journalctl _PID=<PID>` | By PID
`journalctl _SYSTEMD_UNIT=sshd.service -o json-pretty` | Field filter, JSON output
`journalctl -o short-iso` | ISO timestamps
`journalctl -g "<REGEX>"` | Grep the messages
`journalctl --disk-usage` | Space used
`sudo journalctl --vacuum-size=500M` | Trim to a size
`sudo journalctl --vacuum-time=2weeks` | Trim by age
`sudo journalctl --rotate` | Rotate the journal files now

Persist the journal across reboots (if `/var/log/journal` does not exist):
```bash
sudo mkdir -p /var/log/journal
sudo systemctl restart systemd-journald
```
Or set `Storage=persistent` and `SystemMaxUse=1G` in `/etc/systemd/journald.conf`.

---
## Sandboxing and Hardening
Add to the `[Service]` section. Each option limits what the service can do. Test one at a time.

OPTION | EFFECT
---|---
`NoNewPrivileges=yes` | Cannot gain privileges via setuid or file capabilities
`PrivateTmp=yes` | Private `/tmp` and `/var/tmp`
`PrivateDevices=yes` | No access to physical devices
`ProtectSystem=strict` | Whole file system read-only except `/dev`, `/proc`, `/sys`. Use `full` for `/usr`, `/boot`, `/etc` only
`ProtectHome=yes` | `/home`, `/root`, `/run/user` hidden. `read-only` also works
`ReadWritePaths=/var/lib/myapp` | Exceptions to `ProtectSystem=`
`StateDirectory=myapp` | Creates `/var/lib/myapp` owned by the service user (also `CacheDirectory=`, `LogsDirectory=`, `ConfigurationDirectory=`)
`ProtectKernelTunables=yes` | `/proc/sys`, `/sys` read-only
`ProtectKernelModules=yes` | Cannot load modules
`ProtectControlGroups=yes` | cgroups read-only
`RestrictAddressFamilies=AF_INET AF_INET6 AF_UNIX` | Allowed socket families
`RestrictNamespaces=yes` | Cannot create namespaces
`CapabilityBoundingSet=CAP_NET_BIND_SERVICE` | Only these capabilities
`AmbientCapabilities=CAP_NET_BIND_SERVICE` | Bind ports below 1024 as a non-root user
`SystemCallFilter=@system-service` | Allow only a sane syscall set
`MemoryDenyWriteExecute=yes` | Breaks JIT runtimes (Java, Node). Test first
`DynamicUser=yes` | Allocate a temporary user for the service
`IPAddressDeny=any` + `IPAddressAllow=192.168.1.0/24` | Limit network peers

COMMAND | DESCRIPTION
---|---
`systemd-analyze security` | Exposure score for all services
`systemd-analyze security <UNIT>` | Per-option breakdown for one service

---
## systemd-analyze
COMMAND | DESCRIPTION
---|---
`systemd-analyze` | Total boot time
`systemd-analyze blame` | Units sorted by start time
`systemd-analyze critical-chain` | Chain that delayed boot
`systemd-analyze verify <FILE>.service` | Lint a unit file
`systemd-analyze calendar "<EXPR>"` | Test `OnCalendar` syntax
`systemd-analyze cat-config systemd/journald.conf` | Merged config with drop-ins

---
## Other Handy Tools
COMMAND | DESCRIPTION
---|---
`systemctl list-sockets` | Socket units and what they activate
`loginctl list-sessions` | Logged-in sessions
`sudo loginctl enable-linger <USER>` | Keep a user's services running after logout
`timedatectl` | Time, timezone, NTP status
`hostnamectl set-hostname <NAME>` | Set the hostname
`resolvectl status` | DNS settings per link (systemd-resolved)
`systemd-cgtop` | Live per-cgroup CPU, memory, I/O
`coredumpctl list` | Crashed processes with core dumps

## Troubleshooting a Failed Service
1. `systemctl status <UNIT>` for the exit code and last lines.
2. `journalctl -xeu <UNIT>` for full context.
3. `systemd-analyze verify /etc/systemd/system/<UNIT>` for syntax problems.
4. Run the `ExecStart` line by hand as the service user: `sudo -u <USER> <CMD>`.
5. Exit status `203/EXEC` means the binary is missing or not executable; `200/CHDIR` a missing `WorkingDirectory`; `217/USER` a missing user.
6. Failing only on boot? Check `After=` and `network-online.target`.
7. Hit the restart limit? `sudo systemctl reset-failed <UNIT>` then start again.

# journalctl
`journalctl` reads the systemd journal, the log store behind `systemd` services and the kernel. Use it to follow a service, find what happened before a crash or reboot, and keep the journal from filling the disk. See [systemd](systemd.md) for units and [Loki and Grafana Alloy](../apps/loki-alloy.md) for shipping logs elsewhere.

Documentation: [journalctl(1)](https://man7.org/linux/man-pages/man1/journalctl.1.html), [journald.conf(5)](https://man7.org/linux/man-pages/man5/journald.conf.5.html)

## Common Commands
COMMAND | DESCRIPTION
---|---
`journalctl -u <UNIT>` | Logs for one unit (repeat `-u` for several)
`journalctl -u <UNIT> -f` | Follow new entries
`journalctl -b` | Current boot only
`journalctl -b -1` | Previous boot
`journalctl --list-boots` | Boot numbers, IDs and time ranges
`journalctl -p err` | Errors and worse (`emerg`, `alert`, `crit`, `err`, `warning`, `notice`, `info`, `debug`)
`journalctl -p warning..err` | A range of priorities
`journalctl -k` | Kernel messages (like `dmesg`, current boot)
`journalctl -n 50` | Last 50 lines
`journalctl -r` | Newest first
`journalctl -g '<PATTERN>'` | Filter by regex (case-insensitive if the pattern is all lower case)
`journalctl -t <IDENTIFIER>` | Filter by syslog identifier
`journalctl -x` | Add explanatory catalogue text to entries
`journalctl --no-pager` | Plain output for scripts and piping

## Time Ranges
COMMAND | DESCRIPTION
---|---
`journalctl --since "2026-11-09 18:00:00"` | From a date and time
`journalctl --since yesterday --until today` | Keywords: `yesterday`, `today`, `tomorrow`, `now`
`journalctl --since "-1h"` | Relative time (`-1h`, `-30min`)
`journalctl -b -1 -p err -u <UNIT>` | Combine filters

## Output Formats
COMMAND | DESCRIPTION
---|---
`journalctl -o short-iso` | ISO timestamps
`journalctl -o json -n 5` | One JSON object per line
`journalctl -o json-pretty -n 1` | Readable JSON, shows every field
`journalctl -o cat` | Message text only

## Disk Use and Cleanup
COMMAND | DESCRIPTION
---|---
`journalctl --disk-usage` | Space used by all journal files
`sudo journalctl --vacuum-size=500M` | Delete **archived** files until under the size
`sudo journalctl --vacuum-time=2weeks` | Delete archived files older than this
`sudo journalctl --vacuum-files=5` | Keep only this many archived files
`sudo journalctl --rotate --vacuum-time=1d` | Archive active files first, then vacuum
`sudo journalctl --flush` | Move the journal from `/run/log/journal` to `/var/log/journal` if persistent storage is on

Vacuuming removes only archived files, so run `--rotate` first if the active file is large.

## Make the Journal Persistent
By default some distros keep the journal in memory only (`/run/log/journal`), so logs vanish on reboot. Check `Storage=` in `/usr/lib/systemd/journald.conf`. Set it in a drop-in:

```ini
# /etc/systemd/journald.conf.d/10-persistent.conf
[Journal]
Storage=persistent
SystemMaxUse=2G
MaxRetentionSec=1month
```

Then create the directory and restart the daemon:

```bash
sudo mkdir -p /var/log/journal
sudo systemctl restart systemd-journald
```

`Storage=auto` behaves like `persistent` if `/var/log/journal` exists. `SystemMaxUse` defaults to 10% of the filesystem, capped at 4G. `journalctl --user` only works with persistent storage. The directory and restart steps are the usual practice rather than text from the man page (unverified).

## See Also
- [systemd](systemd.md)
- [Loki and Grafana Alloy](../apps/loki-alloy.md)
- [Logrotate](logrotate.md)
- [Performance Troubleshooting](performance-troubleshooting.md)

# logrotate
`logrotate` rotates, compresses and removes old log files on a schedule or when they reach a size. On Debian and Ubuntu it is run daily by a systemd timer or cron, reading `/etc/logrotate.conf` and the per-application files in `/etc/logrotate.d/`. See [systemd](systemd.md) for journal-based logging, which has its own limits.

Documentation: `man logrotate`, `man logrotate.conf`

> **Verification:** options and directives were checked against the logrotate man pages on Ubuntu 24.04, and the example configuration was run (`-d` and `-f -v`) in a throwaway container on files under `/tmp`.

See also: [systemd](systemd.md) · [Linux](linux.md) · [Linux Performance Troubleshooting](performance-troubleshooting.md)

---
## Command Line
COMMAND | DESCRIPTION
---|---
`sudo logrotate -d /etc/logrotate.conf` | Debug: show what would happen, change nothing
`sudo logrotate -d /etc/logrotate.d/<APP>` | Debug one application's file
`sudo logrotate -f /etc/logrotate.conf` | Force rotation now, even if not due
`sudo logrotate -v /etc/logrotate.conf` | Rotate when due, with verbose output
`sudo logrotate -s <STATE_FILE> <CONFIG>` | Use a different state file (useful for testing)
`sudo logrotate -l <LOG_FILE> <CONFIG>` | Write messages to a file (or `syslog`)
`systemctl list-timers logrotate.timer` | Next scheduled run (systemd systems)
`cat /var/lib/logrotate/status` | State file: last rotation time per log (path varies by distribution)

`-d` implies no changes. A forced rotation really does rotate: do it on a test file first.

---
## Example Configuration
Drop a file into `/etc/logrotate.d/`:

```text
/var/log/APP/*.log {
    weekly
    rotate 4
    compress
    delaycompress
    missingok
    notifempty
    create 0640 APP_USER APP_GROUP
    sharedscripts
    postrotate
        systemctl reload APP.service > /dev/null 2>&1 || true
    endscript
}
```

---
## Common Directives
DIRECTIVE | DESCRIPTION
---|---
`daily` / `weekly` / `monthly` / `yearly` | How often to rotate
`rotate <COUNT>` | Keep this many old logs; older ones are removed
`size <SIZE>` | Rotate when larger than SIZE (for example `100M`); overrides the time interval
`maxsize <SIZE>` | Rotate when larger than SIZE even before the interval is due
`minsize <SIZE>` | Rotate at the interval only if at least SIZE
`maxage <DAYS>` | Remove rotated logs older than this
`compress` / `nocompress` | gzip rotated logs (or not)
`delaycompress` | Leave the most recent rotated log uncompressed (for programs that keep writing to it briefly)
`missingok` | No error if the log is missing
`notifempty` / `ifempty` | Skip (or rotate) empty logs
`create <MODE> <OWNER> <GROUP>` | Create a fresh log after rotation
`copytruncate` | Copy then truncate the log instead of moving it, for programs that cannot reopen logs; a few lines can be lost
`dateext` / `dateformat <FORMAT>` | Name rotated logs by date instead of a number
`olddir <DIRECTORY>` | Move rotated logs to another directory
`su <USER> <GROUP>` | Rotate as this user and group (needed when the log directory is group-writable)
`sharedscripts` | Run the scripts once for all logs matched by a pattern, not per log
`prerotate` / `postrotate` ... `endscript` | Shell commands before or after rotation
`mail <ADDRESS>` / `nomail` | Mail (or not) the log being removed

---
## Troubleshooting
SYMPTOM | FIX
---|---
"skipping ... because parent directory has insecure permissions" (unverified wording) | Add `su <USER> <GROUP>` or tighten the directory permissions
Application keeps writing to the old (rotated) file | Reload it in `postrotate`, or use `copytruncate`
Logs never rotate | Check the timer or cron runs; run `logrotate -d` and read why it says "does not need rotating"
Rotation seems to run at the wrong time | Time-based directives compare against the state file; the timer or cron job decides when logrotate runs
Config change not taking effect | Test with `-d`; a later `size` overrides an earlier `weekly` in the same block (logrotate prints a note)

---
## See Also
- [systemd](systemd.md)
- [Linux](linux.md)
- [Linux Performance Troubleshooting](performance-troubleshooting.md)

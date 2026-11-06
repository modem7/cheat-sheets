# Cron
Cron runs commands on a schedule. This sheet covers crontab syntax, the Debian/Ubuntu layout, the gotchas that make a job work in a terminal but fail under cron, overlap protection with `flock`, and how the same schedules look in systemd timers, Kubernetes CronJobs and GitHub Actions. Related: [[linux]], [[kubernetes]], [[regex]].

Documentation: `man 5 crontab`, [systemd.time(7)](https://www.freedesktop.org/software/systemd/man/latest/systemd.time.html), [Kubernetes CronJob](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/), [GitHub Actions `schedule`](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)

## Syntax
```text
# ┌───────── minute        (0-59)
# │ ┌─────── hour          (0-23)
# │ │ ┌───── day of month  (1-31)
# │ │ │ ┌─── month         (1-12 or jan-dec)
# │ │ │ │ ┌─ day of week   (0-7 or sun-sat; 0 and 7 are Sunday)
# │ │ │ │ │
  * * * * *  <COMMAND>
```

SYMBOL | MEANING
---|---
`*` | Every value
`,` | List: `1,15,30`
`-` | Range: `1-5` (Mon to Fri in the weekday field)
`/` | Step: `*/5` every 5, `10-50/10` every 10 from 10 to 50
`?` | Not valid in standard cron (it is Quartz/Spring syntax)

Rules that catch people out:
- If **both** day-of-month and day-of-week are restricted (neither is `*`), the job runs when **either** matches (OR, not AND). `0 0 1 * 1` is midnight on the 1st **and** every Monday.
- `*/N` steps restart at the start of the range, so `*/7` in the minute field runs at 0, 7, 14 ... 56, then 0 again (a 4 minute gap).
- No seconds field. For sub-minute work use a systemd timer or a loop with `sleep`.
- Times use the system local timezone. Jobs in a daylight-saving gap may be skipped or run twice, so avoid 01:00 to 03:00 local for important jobs, or run the host in UTC.

## Special Strings
STRING | EQUIVALENT
---|---
`@reboot` | Once at cron daemon start (not supported by every cron)
`@yearly` / `@annually` | `0 0 1 1 *`
`@monthly` | `0 0 1 * *`
`@weekly` | `0 0 * * 0`
`@daily` / `@midnight` | `0 0 * * *`
`@hourly` | `0 * * * *`

## crontab Command
COMMAND | DESCRIPTION
---|---
`crontab -e` | Edit your crontab (validates on save)
`crontab -l` | List your crontab
`crontab -r` | Remove your crontab with no confirmation (`-i` to prompt). `-e` and `-r` sit next to each other on the keyboard
`crontab -u <USER> -l` | Another user's crontab (root)
`crontab <FILE>` | Replace your crontab from a file
`crontab -l \| { cat; echo "0 3 * * * /usr/local/bin/backup.sh"; } \| crontab -` | Append a job from a script
`sudo crontab -e` | Root's crontab
`/etc/cron.allow` / `/etc/cron.deny` | Allow or deny list of users for `crontab`

Back up before editing in bulk: `crontab -l > crontab.bak`.

## System Cron
PATH | DESCRIPTION
---|---
`/etc/crontab` | System crontab with an extra **user** field after the schedule
`/etc/cron.d/<NAME>` | Drop-in files, same format as `/etc/crontab` (user field)
`/etc/cron.hourly/` `daily/` `weekly/` `monthly/` | Executable scripts run by `run-parts`, no schedule syntax
`/var/spool/cron/crontabs/<USER>` | Per-user crontabs on Debian (use `crontab -e`, never edit directly)

```text
# /etc/cron.d/backup: schedule, USER, command
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
MAILTO=""
30 2 * * *  root  /usr/local/bin/backup.sh >> /var/log/backup.log 2>&1
```

- Files in `/etc/cron.d` must be owned by root and not writable by group or others.
- On Debian/Ubuntu, `run-parts` and `/etc/cron.d` **skip file names containing a dot** (such as `backup.sh` or `job.conf`) and the file name must be letters, digits, `_` or `-`. A silently ignored job is almost always this. Check with `run-parts --test /etc/cron.daily`.
- Scripts in `cron.daily` and friends need the executable bit and no extension.
- The daily/weekly/monthly times are set in `/etc/crontab` (or by anacron, see below), commonly 06:25 for daily on Debian.

## Environment Gotchas
GOTCHA | FIX
---|---
Minimal `PATH` (Debian default is `/usr/bin:/bin`) | Use absolute paths or set `PATH=...` at the top of the crontab
`SHELL` is `/bin/sh` | Set `SHELL=/bin/bash` if you use bashisms
`%` is a newline | Escape as `\%` in the command, e.g. `date +\%F`. Anything after an unescaped `%` is fed to stdin
No TTY, no terminal, no `$DISPLAY`, no ssh-agent | Use key files, `-T` or `-o BatchMode=yes` for ssh, and `docker exec` without `-t`
No login profile (`~/.bashrc`, `~/.profile` not read) | Source what you need in the script, or run `bash -lc '<CMD>'`
Variable assignments are not expanded | `PATH=$PATH:/x` does not work; write the full value. `HOME`, `LOGNAME` and `SHELL` are set for you
Output is mailed to the owner | Set `MAILTO=you@example.com` or `MAILTO=""` to silence, or redirect `>> file 2>&1`
Missing trailing newline | The last line of a crontab must end with a newline, or the entry may be ignored
Wrong working directory (`$HOME`) | `cd /path && ./script` or use absolute paths
Relative times and `date` | Test with `env -i HOME="$HOME" PATH=/usr/bin:/bin /bin/sh -c '<CMD>'` to reproduce cron's environment

## Logging and Debugging
COMMAND | DESCRIPTION
---|---
`journalctl -u cron -e` | Cron daemon log on Debian/Ubuntu (`crond` on RHEL, Fedora)
`grep CRON /var/log/syslog` | Where jobs started, if rsyslog writes syslog
`systemctl status cron` | Is the daemon running
`sudo run-parts --test /etc/cron.daily` | Which scripts would run
`* * * * * /path/job.sh >> /tmp/job.log 2>&1` | Run every minute temporarily and read the log
`logger -t myjob "message"` | Write to syslog from a script

The syslog line shows that a job **started**, not whether it succeeded. Capture the output yourself and use `set -euo pipefail` in scripts. For monitoring, ping a dead-man-switch service (Healthchecks.io, Uptime Kuma push monitors) at the end of a successful run:

```bash
0 3 * * * /usr/local/bin/backup.sh && curl -fsS -m 10 --retry 3 https://hc-ping.com/<UUID> >/dev/null
```

## Preventing Overlap with flock
`flock` holds a lock file for the life of the command, so a slow run does not collide with the next one.

COMMAND | DESCRIPTION
---|---
`flock -n /var/lock/job.lock <CMD>` | Skip this run if the lock is held (exit code 1)
`flock -w 30 /var/lock/job.lock <CMD>` | Wait up to 30 seconds, then give up
`flock -n -E 0 /var/lock/job.lock <CMD>` | Exit 0 instead of 1 when skipped, so cron mail stays quiet
`flock -x -n 9 \|\| exit 0` | Inside a script after `exec 9>/var/lock/job.lock`

```text
*/5 * * * * flock -n /var/lock/sync.lock /usr/local/bin/sync.sh >> /var/log/sync.log 2>&1
```

Use a lock path writable by the job user (`/var/lock` is root-only on some systems; `/run/user/<UID>/` or `/tmp` works for users). Also consider `timeout 10m <CMD>` to kill hung jobs.

## anacron
Cron skips jobs when the machine is off. `anacron` runs them later: it records the last run date per job in `/var/spool/anacron/` and only handles daily or longer periods. It is what runs `cron.daily` on laptops and VMs that are not always on.

```text
# /etc/anacrontab: period(days) delay(min) job-id command
1    5   daily-backup   /usr/local/bin/backup.sh
7    10  weekly-report  /usr/local/bin/report.sh
@monthly 15 monthly-clean /usr/local/bin/clean.sh
```

COMMAND | DESCRIPTION
---|---
`sudo anacron -T` | Validate `/etc/anacrontab`
`sudo anacron -f -n` | Run all jobs now, ignoring timestamps and delays (testing)
`ls /var/spool/anacron` | Last-run timestamps

systemd timers do this natively with `Persistent=true`.

## systemd Timers
A timer unit starts a service unit of the same name (`backup.timer` starts `backup.service`). Benefits over cron: journal logging, dependencies, resource limits, `Persistent=` catch-up, jitter.

```ini
# /etc/systemd/system/backup.service
[Unit]
Description=Nightly backup

[Service]
Type=oneshot
ExecStart=/usr/local/bin/backup.sh
```

```ini
# /etc/systemd/system/backup.timer
[Unit]
Description=Nightly backup timer

[Timer]
OnCalendar=*-*-* 02:30:00
Persistent=true
RandomizedDelaySec=5m

[Install]
WantedBy=timers.target
```

COMMAND | DESCRIPTION
---|---
`sudo systemctl enable --now backup.timer` | Enable and start the timer (not the service)
`systemctl list-timers --all` | Next and last run times
`systemctl start backup.service` | Run the job now
`journalctl -u backup.service -e` | Job output
`systemd-analyze calendar '<EXPR>'` | Validate an expression and show the next elapse
`systemd-analyze calendar --iterations=5 '<EXPR>'` | Show the next five runs
`systemctl --user enable --now <NAME>.timer` | Per-user timer (needs `loginctl enable-linger <USER>` to run when logged out)

OnCalendar format is `DayOfWeek Year-Month-Day Hour:Minute:Second`, every part optional:

ONCALENDAR | MEANING
---|---
`minutely` `hourly` `daily` `weekly` `monthly` `yearly` | Shortcuts (`weekly` is Monday 00:00)
`*-*-* 02:30:00` | Daily at 02:30
`Mon..Fri 09:00` | Weekdays at 09:00 (normalised to `Mon..Fri *-*-* 09:00:00`)
`*:0/15` | Every 15 minutes
`*-*-01 04:00` | 1st of month at 04:00
`Sat,Sun *-*-* 12:00` | Weekend noon
`*-*-* 02:30:00 UTC` | Timezone suffix is allowed
`OnBootSec=10min` | 10 minutes after boot (monotonic timer)
`OnUnitActiveSec=1h` | 1 hour after the unit last ran

Timers are accurate to within `AccuracySec=` (default 1 minute) to batch wake-ups; set `AccuracySec=1s` if that matters.

## Kubernetes CronJob
Uses the standard five-field syntax (plus the `@` macros). See [[kubernetes]] and [[kubectl]].

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: backup
spec:
  schedule: "30 2 * * *"
  timeZone: "Europe/London"
  concurrencyPolicy: Forbid
  startingDeadlineSeconds: 300
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  jobTemplate:
    spec:
      backoffLimit: 2
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: backup
              image: <IMAGE>
              command: ["/backup.sh"]
```

- Without `spec.timeZone` (stable since Kubernetes 1.27) the schedule uses the timezone of the `kube-controller-manager`, usually UTC.
- `concurrencyPolicy`: `Allow` (default), `Forbid` (skip if previous still running), `Replace`.
- A job missed for longer than `startingDeadlineSeconds` is counted as failed and skipped.
- Do not set `CRON_TZ=` or `TZ=` inside `schedule`; use `timeZone`.

COMMAND | DESCRIPTION
---|---
`kubectl get cronjob` | List CronJobs with last schedule time
`kubectl create job --from=cronjob/<NAME> <NAME>-manual` | Trigger a run now
`kubectl patch cronjob <NAME> -p '{"spec":{"suspend":true}}'` | Pause a CronJob
`kubectl logs job/<JOB>` | Logs of a run

## GitHub Actions schedule
```yaml
on:
  schedule:
    - cron: "17 5 * * 1-5"
  workflow_dispatch:
```

- Always **UTC**. There is no timezone setting, so convert (and remember DST shifts your local time).
- Five fields only, no seconds, and no `@daily` style macros.
- Runs from the **default branch** only.
- Can be delayed under load, particularly at the top of the hour. Pick an odd minute (`17`, not `0`).
- In public repos, scheduled workflows are disabled after 60 days without repository activity. Add `workflow_dispatch` to run by hand.
- The shortest supported interval is every 5 minutes.

## Common Schedules
SCHEDULE | CRON | SYSTEMD `OnCalendar`
---|---|---
Every minute | `* * * * *` | `minutely`
Every 5 minutes | `*/5 * * * *` | `*:0/5`
Every 15 minutes | `*/15 * * * *` | `*:0/15`
Every hour | `0 * * * *` | `hourly`
Every 6 hours | `0 */6 * * *` | `0/6:00`
Daily at 02:30 | `30 2 * * *` | `*-*-* 02:30`
Weekdays at 09:00 | `0 9 * * 1-5` | `Mon..Fri 09:00`
Weekends at 10:00 | `0 10 * * 6,0` | `Sat,Sun 10:00`
Every Monday at 08:00 | `0 8 * * 1` | `Mon 08:00`
1st of month at midnight | `0 0 1 * *` | `monthly`
15th of month at 04:00 | `0 4 15 * *` | `*-*-15 04:00`
Last day of month | `0 0 28-31 * * [ "$(date -d tomorrow +\%d)" = 01 ] && <CMD>` | `*-*~1 00:00`
Quarterly (Jan, Apr, Jul, Oct 1st) | `0 0 1 1,4,7,10 *` | `quarterly`
Yearly on 1 Jan | `0 0 1 1 *` | `yearly`
At boot | `@reboot` | `OnBootSec=1min`

Cron has no "last day of month" field, so use the `date` test shown. Sanity check any expression with [crontab.guru](https://crontab.guru/) or `systemd-analyze calendar`.

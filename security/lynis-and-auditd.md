# Lynis and auditd
**Lynis** is a host security auditing scanner: it inspects a Linux system and reports warnings, suggestions and a hardening index. **auditd** is the Linux Audit daemon: it records security-relevant events (file access, commands, logins) selected by rules. Use Lynis to find what to harden and auditd to record what happens afterwards. See [Security](security.md) for the wider hardening checklist.

Project: [Lynis](https://cisofy.com/lynis/)
Documentation: `man lynis`, `man auditctl`, `man audit.rules`, `man ausearch`, `man aureport`

> **Verification:** options come from the Lynis 3.0.9 and Linux audit user-space man pages and `--help` output on Ubuntu 24.04. `lynis audit system --quick` was run in a throwaway container and wrote `/var/log/lynis.log` and `/var/log/lynis-report.dat`. auditd needs the host kernel and was **not** run: the audit commands below are from the man pages only (unverified in practice).

See also: [Security](security.md) · [fail2ban](fail2ban.md) · [CrowdSec](crowdsec.md) · [Container Scanning](container-scanning.md) · [systemd](../linux/systemd.md)

---
## Lynis
COMMAND | DESCRIPTION
---|---
`sudo lynis audit system` | Full local audit (interactive; press Enter between sections)
`sudo lynis audit system --quick` | Same without pauses
`sudo lynis audit system --warnings-only` | Run quietly, show warnings only
`sudo lynis audit system --pentest` | Non-privileged scan, points of interest for pentesting
`sudo lynis audit dockerfile <FILE>` | Analyse a Dockerfile
`sudo lynis --tests "<TEST_ID> <TEST_ID>"` | Run only specific tests
`sudo lynis --tests-from-category "<CATEGORY>"` | Run one category (see `lynis show categories`)
`sudo lynis --profile <FILE>` | Use a custom profile
`sudo lynis show commands` | List commands
`sudo lynis show categories` | List test categories (for example `security`, `performance`, `privacy`)
`sudo lynis show profiles` | Profiles in use
`sudo lynis show version` | Version
`sudo lynis update info` | Update details

Results are written to:

PATH | CONTENT
---|---
`/var/log/lynis.log` | Detailed log of every test
`/var/log/lynis-report.dat` | Machine-readable results (`warning[]`, `suggestion[]`, `hardening_index`)
`/etc/lynis/default.prf` | Default profile; override in a custom `.prf` file

Typical flow: run the audit, work through `suggestion[]` and `warning[]` lines, re-run and watch the hardening index.

```bash
sudo lynis audit system --quick
sudo grep -E '^(warning|suggestion)\[\]' /var/log/lynis-report.dat
sudo grep '^hardening_index' /var/log/lynis-report.dat
```

Distribution packages can lag the upstream release (the audit warns when the version is old). Fetch current versions from the project if you need the latest tests.

---
## auditd: Rules
Rules live in `/etc/audit/rules.d/*.rules` and are merged by `augenrules`. Load changes with `augenrules --load`.

COMMAND | DESCRIPTION
---|---
`sudo auditctl -s` | Daemon status
`sudo auditctl -l` | List loaded rules
`sudo auditctl -w <PATH> -p wa -k <KEY>` | Watch a file or directory for writes and attribute changes (`r`, `w`, `x`, `a`)
`sudo auditctl -W <PATH> -p wa -k <KEY>` | Remove that watch
`sudo auditctl -a always,exit -F arch=b64 -S <SYSCALL> -k <KEY>` | Audit a system call
`sudo auditctl -D` | Delete all rules (live only)
`sudo auditctl -e 2` | Make the configuration immutable until reboot (put last in the rules)
`sudo augenrules --check` | Check whether the rules files have changed
`sudo augenrules --load` | Rebuild `audit.rules` and load it

Example `/etc/audit/rules.d/50-homelab.rules`:

```text
-w /etc/passwd -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/ssh/sshd_config -p wa -k sshd
-a always,exit -F arch=b64 -S execve -F euid=0 -k root_commands
```

Rules set with `auditctl` are lost on reboot; files in `rules.d` persist.

---
## auditd: Searching Logs
Events are in `/var/log/audit/audit.log` (root only).

COMMAND | DESCRIPTION
---|---
`sudo ausearch -k <KEY>` | Events matching a rule key
`sudo ausearch -k <KEY> -i` | Same, with names instead of numbers
`sudo ausearch -f <PATH>` | Events for a file
`sudo ausearch -ui <UID> -ts today` | One user's events since the start of today
`sudo ausearch -m USER_LOGIN --success no -ts recent` | Recent failed logins (message type and success filters)
`sudo aureport --summary` | Summary report
`sudo aureport -au --failed --summary` | Failed authentication summary
`sudo aureport -x --summary` | Executables summary
`sudo aureport -f -i` | File access report, interpreted

---
## Troubleshooting
SYMPTOM | FIX
---|---
`Error opening /var/log/audit/audit.log` | Run as root; check the `auditd` service is running
Rules vanish after reboot | Put them in `/etc/audit/rules.d/` and run `augenrules --load`
`auditctl` rules refused | The configuration is immutable (`-e 2`); reboot to change
Huge audit log | Tune `max_log_file` and `num_logs` in `/etc/audit/auditd.conf` (see `man auditd.conf`)
Lynis keeps reporting the same suggestion | Skip it with a profile (`skip-test=<TEST_ID>` in a custom `.prf`; see the profile comments)

---
## See Also
- [Security](security.md)
- [fail2ban](fail2ban.md)
- [CrowdSec](crowdsec.md)
- [Container Scanning](container-scanning.md)

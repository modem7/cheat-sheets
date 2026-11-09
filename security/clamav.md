# ClamAV
ClamAV is an open source antivirus engine for Linux. It is most useful for scanning file shares, mail and uploads for malware that targets other systems, rather than as a full endpoint defence. This sheet also covers rkhunter and AIDE, which check for rootkits and file changes.

Documentation: [ClamAV docs](https://docs.clamav.net/)

## Install
```bash
sudo apt install clamav clamav-daemon
```

The docs list the packages `clamav`, `clamav-daemon` and `clamav-freshclam` and say you probably only need `clamav`. Install `clamav-daemon` if you want `clamd` for fast repeat scans. Service names were not on that page, so check `systemctl list-unit-files | grep -i clam` on your distribution.

## Signature Updates
COMMAND | DESCRIPTION
---|---
`sudo freshclam` | Update the signature databases once
`freshclam -d` | Run as a daemon that checks regularly
`/var/lib/clamav` | Database directory (from the Docker docs)

Run `freshclam` before the first scan, or use the packaged update service. Keep it running, because stale signatures miss new malware.

## Scanning
COMMAND | DESCRIPTION
---|---
`clamscan --recursive <DIR>` | Scan a directory (`-r` is the short form, commonly used)
`clamscan --recursive --move=<QUARANTINE_DIR> <DIR>` | Move infected files to a quarantine directory
`clamscan --log=<FILE> <DIR>` | Write a log
`clamscan --max-filesize=<N>M <DIR>` | Skip large files
`clamscan --bell <DIR>` | Sound on detection
`clamdscan <PATH>` | Scan using the running `clamd` (fast, needs the daemon)
`clamdscan --fdpass <PATH>` | Pass file descriptors, Unix socket only, not TCP

Other options such as `-i` (print only infected files) and `--exclude-dir` are widely used but were not on the pages checked, so run `clamscan --help`. Test the setup with the harmless EICAR test file from [eicar.org](https://www.eicar.org/), not real malware. `clamscan` loads the whole database on every run, so use `clamdscan` for frequent scans.

## clamd
Configure in `clamd.conf`. `LocalSocket` sets the Unix socket path. A TCP socket setting also exists but was not on the page checked. Do not expose `clamd` on the network without a firewall, because it has no authentication.

## On-Access Scanning
`clamonacc` (ClamAV 0.102 and later) scans files as they are opened, and runs as root with `clamd` already started.

SETTING | MEANING
---|---
`OnAccessIncludePath <DIR>` | Directory to watch. Recursive, and `/` is not accepted
`OnAccessExcludeUname clamav` | Do not scan files accessed by the `clamav` user
`OnAccessPrevention yes` | Block access to infected files
`sudo clamonacc` | Start it (flags include `--log`, `--foreground`, `--move`, `--copy`, `--remove`)

It defaults to notify only. It needs a kernel with fanotify (3.8 or newer): `grep FANOTIFY /boot/config-$(uname -r)`. `ScanOnAccess` applies only to ClamAV 0.101 and older.

## Docker
Image `clamav/clamav:<TAG>` (`stable`, `latest`, or a version, and `_base` has no databases):

```bash
docker run -it --rm --mount type=bind,source=<PATH>,target=/scandir clamav/clamav:stable clamscan /scandir
```

VARIABLE | MEANING
---|---
`CLAMAV_NO_CLAMD` | Do not start `clamd`
`CLAMAV_NO_FRESHCLAMD` | Do not start `freshclam`
`CLAMAV_NO_MILTERD` | Milter, off by default
`CLAMD_STARTUP_TIMEOUT` | Seconds to wait for startup (default 1800)
`FRESHCLAM_CHECKS` | Update checks per day (default 1)

Persist `/var/lib/clamav` as a volume so databases survive restarts. Config is under `/etc/clamav`, and `clamd` listens on port 3310.

## Memory
The docs recommend at least 3 GiB, and 4 GiB preferred. `clamd` uses over 1.2 GiB, peaking near 2.4 GiB while it reloads signatures. `ConcurrentDatabaseReload no` lowers the peak but blocks scans during a reload. Do not run it in a 1 GiB LXC.

## Scheduled Scan
Run `clamdscan` from cron or a systemd timer and report failures with [Healthchecks](../apps/healthchecks.md). See [Cron](../misc/cron.md) and [systemd](../linux/systemd.md). A cron example was not verified.

## rkhunter
Checks for known rootkits and suspicious changes.

COMMAND | DESCRIPTION
---|---
`sudo rkhunter --update` | Update its data files (exit 0 none, 1 error, 2 updated)
`sudo rkhunter --propupd` | Record the current file properties as the baseline. Only run on a system you trust
`sudo rkhunter --check --sk` | Run all checks without pausing for a keypress

Expect false warnings after package updates. Run `--propupd` after a verified update.

## AIDE
File integrity checker that records hashes and reports changes.

COMMAND | DESCRIPTION
---|---
`aide --init` | Build the baseline database
`aide --check` | Compare the system with the database
`aide --update` | Check, and write a new database
`aide --compare` | Compare two databases

Configure what to watch in `aide.conf`, and store the database somewhere an attacker cannot rewrite, such as read-only media or another host. Database file names are not covered in the docs read.

## Not Verified
`clamscan -r`, `-i`, `--exclude-dir`, the `TCPSocket` setting, `freshclam.conf` keys, cron examples, chkrootkit and Linux Malware Detect.

## See Also
- [Lynis and auditd](lynis-and-auditd.md)
- [Wazuh](wazuh.md)
- [Container Scanning](container-scanning.md)
- [Cron](../misc/cron.md)

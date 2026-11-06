# Backup Strategy
Overview of how to plan backups for a homelab or small server estate: the 3-2-1 rule, recovery objectives, what to back up, and a restore-testing checklist. The tool-specific sheets hold the commands; this one holds the thinking. A backup you have never restored is a hope, not a backup.

Documentation: [Backblaze: the 3-2-1 backup strategy](https://www.backblaze.com/blog/the-3-2-1-backup-strategy/) · [restic docs](https://restic.readthedocs.io/) · [BorgBackup docs](https://borgbackup.readthedocs.io/) · [borgmatic](https://torsion.org/borgmatic/)

> **Verification:** This sheet is conceptual. The tool commands live in the linked sheets, each of which has its own verification note. No command was executed.

See also: [restic](restic.md) · [BorgBackup](borg.md) · [borgmatic](borgmatic.md) · [rclone](rclone.md) · [rsync](rsync.md) · [ZFS Snapshots and Replication](zfs-snapshots-backup.md) · [Docker Volume Backup](docker-volume-backup.md) · [Database Dumps](database-dumps.md) · [Proxmox Backup and Restore](../proxmox/proxmox-backup.md) · [TrueNAS Scale](../infra/truenas-scale.md) · [Linux](../linux/linux.md) · [Docker](../docker/docker.md)

---
## The 3-2-1 Rule
RULE | MEANING
---|---
**3** copies of the data | The live data plus at least two backups
**2** different media or storage systems | A second disk, NAS or a different filesystem, so one failure mode does not take both
**1** copy off site | Another building, another provider, or cloud object storage

Common extensions:
- **3-2-1-1-0**: one copy offline or immutable (append-only, object lock, air-gapped), and **0** errors after verification.
- A snapshot on the same pool is **not** a backup. It protects against deletion and ransomware on a share, not against pool loss.
- RAID is availability, not backup. It replicates mistakes instantly.

---
## RPO and RTO
TERM | MEANING | DRIVES
---|---|---
RPO (Recovery Point Objective) | How much data you can afford to lose, expressed as time | Backup frequency
RTO (Recovery Time Objective) | How long recovery may take before it hurts | Tool and storage choice, restore speed, documentation

Examples: a nightly backup means an RPO of up to 24 hours. A 2 TB restore over a 100 Mbit/s link takes about 44 hours (`2 TB / 12.5 MB/s`), so an RTO of "a day" needs a local copy as well as the cloud one.

---
## What to Back Up
INCLUDE | NOTES
---|---
Application data and volumes | Bind mounts and named volumes, see [Docker Volume Backup](docker-volume-backup.md)
Databases | Logical dumps or a stopped/snapshotted data directory, see [Database Dumps](database-dumps.md)
Compose files, `.env` files, configs | Keep in git where possible, but secrets files need a backup too
`/etc` and service configs | Reverse proxy, DNS, firewall, systemd units
Encryption keys, passphrases, repo keys | See "Keys and credentials" below
VM and container images | Hypervisor-level, see [Proxmox Backup and Restore](../proxmox/proxmox-backup.md)
Package lists and bootstrap notes | `dpkg --get-selections`, Ansible playbooks, so a rebuild is quick

EXCLUDE | WHY
---|---
Caches, `node_modules`, `.cache`, thumbnails | Rebuildable, large
Media you can re-download | Judgement call, decide per library
`/proc`, `/sys`, `/dev`, `/run`, `/tmp` | Virtual or transient
Docker image layers | Pull them again; keep the Dockerfile and compose file instead
Live database files copied with `cp` | Inconsistent, use a dump or snapshot

### Keys and credentials
- The backup passphrase and any key file must exist **somewhere other than the backed-up host**: a password manager (for example [Bitwarden Cheat-Sheet](../tools/bitwarden.md)) plus a printed or offline copy.
- Borg: export the key with `borg key export`. restic: the password is the only key. Lose it and the repository is unreadable.
- Do not keep the only copy of the repo password inside the repo it protects.

---
## Choosing a Tool
NEED | TOOL
---|---
Deduplicated, encrypted, versioned file backups to local, SFTP or cloud | [restic](restic.md) or [BorgBackup](borg.md) (+ [borgmatic](borgmatic.md))
Mirror or sync a directory to cloud storage | [rclone](rclone.md)
Simple file mirror or hardlinked snapshots over SSH | [rsync](rsync.md)
Filesystem-level snapshots and replication | [ZFS Snapshots and Replication](zfs-snapshots-backup.md)
Docker volumes | [Docker Volume Backup](docker-volume-backup.md)
Databases | [Database Dumps](database-dumps.md), or borgmatic's native database hooks
Whole VMs | [Proxmox Backup and Restore](../proxmox/proxmox-backup.md)

`rclone sync` and `rsync --delete` mirror deletions. They are copies, not versioned backups, unless you add `--backup-dir` or `--link-dest`.

---
## Schedule and Retention (starting point)
LAYER | FREQUENCY | RETENTION
---|---|---
Local snapshots | Hourly | 24 hourly, 7 daily
Local backup repo | Daily | 7 daily, 4 weekly, 6 monthly
Off-site repo | Daily or weekly | 7 daily, 4 weekly, 12 monthly, 2 yearly
Database dumps | Before the file backup runs | 7 to 14 days on disk, the file backup keeps the history

---
## Monitoring
- Alert on **failure and on silence**. A dead timer sends no failure email. Use a dead-man's-switch such as [Healthchecks.io](https://healthchecks.io) (`curl -fsS -m 10 --retry 5 https://hc-ping.com/<UUID>`), which borgmatic supports natively, see [borgmatic](borgmatic.md).
- Log backup size and duration. A sudden size drop usually means something is not being backed up.
- Run integrity checks on a schedule, not just once (`restic check`, `borg check`, `zpool scrub`).

---
## Restore Testing Checklist
Do this at least quarterly and after every major change to the backup setup.

- [ ] Can you reach the backup from a **clean machine** with only the documented credentials (not the original host's config or keys)?
- [ ] List snapshots or archives and confirm the newest one is as recent as expected.
- [ ] Restore a **single file** to a scratch directory and compare it: `diff -r` or checksums against the live copy.
- [ ] Restore a **whole application** (volume plus database) into a throwaway Compose project and confirm it starts with the right data.
- [ ] Restore a **database dump** into a scratch instance and run a row count or `PRAGMA integrity_check`, see [Database Dumps](database-dumps.md).
- [ ] Time the restore. Compare against your RTO.
- [ ] Run the repository integrity check (`restic check --read-data-subset=5%`, `borg check --verify-data`).
- [ ] Confirm the off-site copy is restorable too, not just the local one.
- [ ] Confirm alerts fire: temporarily break a backup and check you are told.
- [ ] Write down what you learned in the runbook.

```bash
# Quick sanity restore pattern (replace the tool line with restic/borg/rclone/rsync)
SCRATCH="$(mktemp -d)"
restic restore latest --target "$SCRATCH" --include <PATH>
diff -r "$SCRATCH/<PATH>" /<PATH> && echo "restore matches"
rm -rf "$SCRATCH"
```

---
## Disaster Recovery Runbook (keep a copy off the host)
1. Where the backups are (repository URLs, bucket names, hosts).
2. Where the credentials are (password manager entry, not the secret itself in a git repo).
3. The exact commands to list and restore, tested.
4. Order of rebuild: network and DNS, storage, hypervisor or Docker, then applications, then data.
5. Who to contact and what the acceptable downtime is (RTO).

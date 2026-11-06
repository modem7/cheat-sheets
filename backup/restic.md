# restic
restic is a fast, encrypted, deduplicating backup program written in Go. One static binary, many backends (local, SFTP, S3, Backblaze B2, REST server, anything rclone supports). Every backup is a snapshot, repositories are always encrypted, and restoring is a single command.

Documentation: [restic documentation](https://restic.readthedocs.io/) · [Preparing a repository](https://restic.readthedocs.io/en/stable/030_preparing_a_new_repo.html) · [Removing snapshots](https://restic.readthedocs.io/en/stable/060_forget.html)

> **Verification:** Written from the restic documentation and experience, but **not** re-checked against the docs this session (command names, flags, repository URL forms, environment variables, the systemd units). `RESTIC_COMPRESSION` needs repository format v2 (restic 0.14+). No command was executed. Test a restore before trusting any setup.

See also: [[backup]] · [[borg]] · [[rclone]] · [[database-dumps]] · [[docker-volume-backup]] · [[linux]] · [[openssh]]

---
## Environment Variables
VARIABLE | DESCRIPTION
---|---
`RESTIC_REPOSITORY` | Repository location, replaces `-r`
`RESTIC_PASSWORD_FILE` | File containing the repository password (preferred)
`RESTIC_PASSWORD_COMMAND` | Command that prints the password, for example `pass show backup/restic`
`RESTIC_PASSWORD` | Password in the environment (visible to the process list owner, avoid)
`RESTIC_CACHE_DIR` | Cache location, default `~/.cache/restic`
`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` | S3 credentials
`B2_ACCOUNT_ID`, `B2_ACCOUNT_KEY` | Backblaze B2 credentials (application key ID and key)
`RESTIC_COMPRESSION` | `auto` (default), `max` or `off` (repository format v2)

A reusable env file (permissions `0600`, owned by the user running the backup):
```bash
# /etc/restic/env
export RESTIC_REPOSITORY=<REPOSITORY>
export RESTIC_PASSWORD_FILE=/etc/restic/password
export AWS_ACCESS_KEY_ID=<ACCESS_KEY_ID>
export AWS_SECRET_ACCESS_KEY=<SECRET_ACCESS_KEY>
```
```bash
sudo install -m 600 /dev/null /etc/restic/password   # then write the password into it
source /etc/restic/env
```

---
## Repository Backends
BACKEND | `RESTIC_REPOSITORY` VALUE
---|---
Local path | `/srv/restic-repo`
SFTP | `sftp:<USER>@<HOST>:/srv/restic-repo`
Amazon S3 | `s3:s3.amazonaws.com/<BUCKET>/<PREFIX>`
S3-compatible (MinIO, Wasabi, Backblaze S3 API) | `s3:https://<ENDPOINT>/<BUCKET>/<PREFIX>`
Backblaze B2 (native) | `b2:<BUCKET>:<PREFIX>`
REST server | `rest:https://<USER>:<PASS>@<HOST>:8000/<REPO>/`
rclone (any remote) | `rclone:<REMOTE>:<PATH>`

Notes:
- SFTP uses your normal SSH config and keys ([[openssh]]). For a non-default key or port use `-o sftp.command="ssh -p <PORT> -i <KEY> <USER>@<HOST> -s sftp"`.
- The `rclone:` backend runs `rclone serve restic` behind the scenes, so the remote must already exist in your rclone config, see [[rclone]].
- For B2, prefer a bucket-scoped application key, not the master key.

---
## Repository Setup
COMMAND | DESCRIPTION
---|---
`restic init` | Create a repository at `$RESTIC_REPOSITORY`
`restic -r <REPOSITORY> init` | Same, explicit
`restic key list` | List repository keys (passwords)
`restic key add` | Add another password
`restic key remove <KEY_ID>` | Remove a password
`restic key passwd` | Change the current password
`restic unlock` | Remove stale locks (only when no other restic process is running)
`restic cat config` | Print the repository config (a quick "can I reach and open it" test)

---
## Backup
COMMAND | DESCRIPTION
---|---
`restic backup <PATH>...` | Back up one or more paths
`restic backup --tag <TAG> <PATH>` | Add a tag, repeatable
`restic backup --exclude '*.tmp' --exclude <PATH> <PATH>` | Exclude patterns
`restic backup --exclude-file /etc/restic/excludes <PATH>` | Exclude patterns from a file
`restic backup --exclude-caches <PATH>` | Skip directories containing `CACHEDIR.TAG`
`restic backup --one-file-system <PATH>` | Do not cross filesystem boundaries
`restic backup --files-from /etc/restic/includes` | Read the path list from a file
`restic backup --dry-run -v <PATH>` | Show what would be added without writing
`restic backup --host <NAME> <PATH>` | Override the recorded hostname (keeps snapshots grouped when the host name changes)
`restic backup --stdin --stdin-filename <NAME>` | Back up data piped on stdin (for example a database dump)
`restic backup --limit-upload 5000 <PATH>` | Limit upload speed in KiB/s

Example, a database dump streamed straight into a snapshot (no temp file), see [[database-dumps]]:
```bash
pg_dump -Fc <DATABASE> | restic backup --stdin --stdin-filename <DATABASE>.dump --tag db
```

---
## Inspect and Verify
COMMAND | DESCRIPTION
---|---
`restic snapshots` | List snapshots
`restic snapshots --tag <TAG> --host <HOST>` | Filter
`restic snapshots --group-by host,paths` | Group the listing
`restic ls latest` | List files in the latest snapshot
`restic ls <SNAPSHOT_ID> <PATH>` | List a path in a snapshot
`restic find '<PATTERN>'` | Find a file across snapshots
`restic diff <ID1> <ID2>` | Compare two snapshots
`restic stats` | Repository size statistics
`restic stats --mode raw-data` | Actual stored size after dedup and compression
`restic check` | Verify repository structure and indexes
`restic check --read-data` | Read and verify **all** pack data (slow, downloads everything from remote)
`restic check --read-data-subset=10%` | Verify a random 10 percent of pack data
`restic check --read-data-subset=1/5` | Verify the first fifth, use `2/5`, `3/5`... on other days to cover all of it

Run `restic check` weekly and a data-subset check regularly. A remote repository bills for the bytes downloaded by `--read-data`.

---
## Restore
COMMAND | DESCRIPTION
---|---
`restic restore latest --target <DIR>` | Restore the latest snapshot into a directory
`restic restore <SNAPSHOT_ID> --target <DIR>` | Restore a specific snapshot
`restic restore latest --target <DIR> --include <PATH>` | Restore only matching paths
`restic restore latest --target <DIR> --exclude <PATTERN>` | Restore everything except
`restic restore latest --target <DIR> --host <HOST> --path <PATH>` | `latest` limited to a host and path
`restic restore latest --target <DIR> --verify` | Re-read restored files and compare to the snapshot
`restic dump latest <FILE_PATH>` | Print one file to stdout
`restic dump latest <DIR_PATH> --archive tar > dir.tar` | Archive a directory from a snapshot
`restic mount <MOUNTPOINT>` | Browse snapshots as a FUSE filesystem (stays in the foreground, Ctrl-C to unmount)

Restoring a database dump that was stored through stdin:
```bash
restic dump latest <DATABASE>.dump | pg_restore -d <DATABASE> --clean --if-exists
```

---
## Retention: forget and prune
`forget` removes snapshot references. `prune` deletes the data nobody references any more. `forget --prune` does both.

COMMAND | DESCRIPTION
---|---
`restic forget <SNAPSHOT_ID>` | Forget one snapshot
`restic forget --keep-last 5` | Keep the 5 most recent
`restic forget --keep-hourly 24 --keep-daily 7 --keep-weekly 4 --keep-monthly 12 --keep-yearly 2` | Typical policy
`restic forget --keep-within 30d` | Keep everything from the last 30 days
`restic forget --keep-tag <TAG>` | Never forget snapshots with this tag
`restic forget --group-by host,paths --keep-daily 7` | Apply the policy per host and path set (the default grouping)
`restic forget --dry-run --keep-daily 7 --keep-weekly 4` | **Preview** what would be removed
`restic forget --keep-daily 7 --keep-weekly 4 --keep-monthly 12 --prune` | Apply and delete unreferenced data
`restic prune` | Delete unreferenced data only
`restic prune --max-unused 5%` | Tolerate some unused data to save repacking work

Always run with `--dry-run` first when changing a policy.

---
## Copy Between Repositories
COMMAND | DESCRIPTION
---|---
`restic copy --from-repo <SRC_REPOSITORY> --from-password-file <FILE> latest` | Copy the latest snapshot into the current (`-r`) repository
`restic copy --from-repo <SRC_REPOSITORY> --from-password-file <FILE>` | Copy all snapshots

Use this to keep an off-site repository without backing up twice. For the best deduplication initialise the new repository with `restic init --from-repo <SRC> --copy-chunker-params`.

---
## Scheduled Backup with systemd
`/etc/systemd/system/restic-backup.service`:
```ini
[Unit]
Description=restic backup
Wants=network-online.target
After=network-online.target

[Service]
Type=oneshot
EnvironmentFile=/etc/restic/env.conf
ExecStart=/usr/bin/restic backup --exclude-file=/etc/restic/excludes --one-file-system /etc /home /srv
ExecStartPost=/usr/bin/restic forget --keep-daily 7 --keep-weekly 4 --keep-monthly 12 --prune
```

`/etc/restic/env.conf` uses plain `KEY=value` lines (systemd `EnvironmentFile` syntax, no `export`):
```ini
RESTIC_REPOSITORY=<REPOSITORY>
RESTIC_PASSWORD_FILE=/etc/restic/password
```

`/etc/systemd/system/restic-backup.timer`:
```ini
[Unit]
Description=Nightly restic backup

[Timer]
OnCalendar=*-*-* 02:30:00
RandomizedDelaySec=15m
Persistent=true

[Install]
WantedBy=timers.target
```
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now restic-backup.timer
systemctl list-timers restic-backup.timer
journalctl -u restic-backup.service -n 50
```

With cron and a dead-man's switch:
```bash
30 2 * * * . /etc/restic/env && restic backup /srv && curl -fsS -m 10 --retry 5 https://hc-ping.com/<UUID> >/dev/null
```

---
## Gotchas
- **The password is the key.** Lose it and the data is gone. Store it outside the backed-up host, see [[backup]].
- `restic unlock` while another backup is genuinely running can corrupt nothing but will break its lock. Check with `pgrep restic` first.
- Snapshots are grouped by host and paths. Changing the hostname or the backed-up path set creates a new group and breaks "latest" and the keep policies. Use `--host` to pin the name.
- Backing up a live database directory yields an inconsistent copy. Dump first, see [[database-dumps]].
- Ransomware on the source can use the repo credentials to delete the backups. For a hardened target use an append-only [REST server](https://github.com/restic/rest-server) (`--append-only`) or object lock on the bucket, and run `forget`/`prune` from a separate trusted host.

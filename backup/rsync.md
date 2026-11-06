# rsync
rsync copies files locally or over SSH and transfers only the differences. It is the classic tool for mirroring directories and, with `--link-dest`, for space-efficient hardlinked point-in-time backups. Remember that `--delete` makes the destination a mirror of the source, deletions included.

Documentation: [rsync man page](https://download.samba.org/pub/rsync/rsync.1) · [rsync homepage](https://rsync.samba.org/)

> **Verification:** Flags and behaviour below are standard rsync usage written from knowledge and were **not** re-checked against the manual this session. `--mkpath` needs rsync 3.2.3 or newer. No command was executed. Dry-run everything with `-n` first.

See also: [[backup]] · [[rclone]] · [[restic]] · [[borg]] · [[openssh]] · [[linux]] · [[nfs]]

---
## Core Flags
FLAG | DESCRIPTION
---|---
`-a` | Archive: recursive, symlinks, permissions, times, group, owner, devices (`-rlptgoD`)
`-v` | Verbose
`-h` | Human-readable sizes
`-n`, `--dry-run` | Show what would happen, change nothing
`-i`, `--itemize-changes` | One line per file saying what changes
`--info=progress2` | Overall progress
`--stats` | Summary statistics
`-z` | Compress in transit (useful on slow links, wasteful for already-compressed data or fast LAN)
`-H` | Preserve hard links
`-A` | Preserve ACLs
`-X` | Preserve extended attributes
`--numeric-ids` | Do not map user and group names, keep raw IDs (use for backups and restores)
`--partial` | Keep partially transferred files so a resumed transfer continues
`-P` | `--partial --progress`
`-c`, `--checksum` | Compare by checksum, not size and time (slow)
`-x`, `--one-file-system` | Do not cross filesystems
`--exclude '<PATTERN>'` | Exclude
`--exclude-from <FILE>` | Exclude list from file
`--include '<PATTERN>'` | Include (order matters, put before the excludes)
`--bwlimit=<KBPS>` | Bandwidth limit in KiB/s
`--mkpath` | Create missing destination directories (3.2.3+)
`--remove-source-files` | Delete source files after a successful transfer (like a move)

A solid default for a filesystem backup:
```bash
rsync -aHAX --numeric-ids --info=progress2 -h /srv/ /mnt/backup/srv/
```

---
## Trailing Slash Rules
SOURCE | RESULT
---|---
`rsync -a /srv/app /backup/` | Creates `/backup/app`, copies the **directory itself**
`rsync -a /srv/app/ /backup/` | Copies the **contents** of `app` into `/backup/`
`rsync -a /srv/app/ /backup/app/` | Contents into `/backup/app/` (usual mirror form)

Only the **source** trailing slash matters. The destination slash does not change behaviour. When in doubt, add `-n -i`.

---
## --delete Safely
FLAG | DESCRIPTION
---|---
`--delete` | Remove destination files that are absent from the source
`--delete-after` | Delete after the transfer completes (safer if interrupted)
`--delete-excluded` | Also delete excluded files at the destination
`--max-delete=<N>` | Refuse to delete more than N files
`--backup --backup-dir=<DIR> --suffix=<SUFFIX>` | Move overwritten or deleted files aside instead of losing them
`--ignore-errors` | Delete even if there are I/O errors (avoid)

Safe pattern:
```bash
# 1. Preview deletions
rsync -aHAXn --delete -i /srv/data/ /mnt/backup/data/ | grep '^\*deleting'

# 2. Real run with guard rails and a dated holding area
rsync -aHAX --numeric-ids --delete-after --max-delete=100 \
  --backup --backup-dir=/mnt/backup/deleted/$(date +%F) \
  /srv/data/ /mnt/backup/data/
```
Never run `--delete` from a source that might be empty or unmounted. Check first: `mountpoint -q /srv/data || exit 1`.

---
## Over SSH
COMMAND | DESCRIPTION
---|---
`rsync -aHAXz /srv/ <USER>@<HOST>:/backup/srv/` | Push
`rsync -aHAXz <USER>@<HOST>:/srv/ /backup/srv/` | Pull
`rsync -aHAX -e 'ssh -p <PORT> -i <KEY>' /srv/ <USER>@<HOST>:/backup/srv/` | Custom port and key
`rsync -aHAX --rsync-path='sudo rsync' <USER>@<HOST>:/etc/ /backup/etc/` | Run the remote rsync with sudo (needs passwordless sudo for rsync)
`rsync -aHAX -e 'ssh -o BatchMode=yes' ...` | Fail instead of prompting, for cron

Use a dedicated key and restrict it in `authorized_keys` on the target, see [[openssh]]. Example forced command, for a pull-only backup account using `rrsync` (shipped with rsync, path may differ):
```
command="/usr/bin/rrsync -ro /srv",restrict ssh-ed25519 AAAA... backup@<HOST>
```

---
## Hardlinked Snapshots with --link-dest
Each run is a full-looking directory, but unchanged files are hardlinks to the previous snapshot, so they cost no extra space.

```bash
#!/usr/bin/env bash
set -euo pipefail
SRC=/srv/data/
DEST=/mnt/backup/snapshots
NOW=$(date +%F_%H%M%S)

mkdir -p "$DEST"
rsync -aHAX --numeric-ids --delete \
  --link-dest="$DEST/latest" \
  "$SRC" "$DEST/$NOW.incomplete/"

mv "$DEST/$NOW.incomplete" "$DEST/$NOW"
ln -sfn "$NOW" "$DEST/latest"

# Retention: delete snapshots older than 30 days
find "$DEST" -maxdepth 1 -type d -name '20*' -mtime +30 -exec rm -rf {} +
```
- `--link-dest` must be a path that exists at run time. On the very first run rsync warns that it does not exist and copies everything. That is expected.
- The `.incomplete` rename means `latest` never points at a half-finished snapshot.
- The destination must be a filesystem that supports hardlinks (not FAT/exFAT). Deleting an old snapshot is safe, the data lives on in the newer ones that link to it.
- Measure space with one `du` call over all snapshots, `du -sh "$DEST"/20*`: `du` counts a hardlinked file only once per invocation, so the later snapshots show only their unique data.

Restore from a snapshot:
```bash
rsync -aHAXn -i /mnt/backup/snapshots/2026-01-15_020000/ /srv/data/      # preview
rsync -aHAX --numeric-ids /mnt/backup/snapshots/2026-01-15_020000/ /srv/data/
```
Add `--delete` to the restore only if you want the target to match the snapshot exactly.

---
## Verify
```bash
rsync -aHAXn --checksum -i /srv/data/ /mnt/backup/data/    # lists any differences, changes nothing
diff -rq /srv/data /mnt/backup/data
```

---
## Scheduling
Cron:
```bash
30 2 * * * /usr/local/bin/rsync-snapshot.sh >> /var/log/rsync-snapshot.log 2>&1
```
For systemd timers (with `Persistent=true` to catch missed runs) see the unit examples in [[restic]] or [[rclone]].

Exit codes worth handling: `0` success, `23` partial transfer due to an error, `24` source files vanished during the transfer (normal on a live system, often safe to treat as success).

---
## Gotchas
- rsync mirrors **file contents**, not consistency. A live database directory copy is unusable, dump first, see [[database-dumps]].
- Without encryption or history, a mirror propagates ransomware and accidental deletes on the next run. Keep `--backup-dir` or snapshots.
- NFS or SMB destinations can drop ownership and permissions. Prefer SSH to a real filesystem for faithful backups, see [[nfs]].

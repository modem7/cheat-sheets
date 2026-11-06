# rclone
rclone is "rsync for cloud storage": it copies, syncs, mounts and encrypts across 70+ providers (S3, B2, Google Drive, OneDrive, SFTP, WebDAV, local disk). It is a file mirroring tool, not a versioned backup tool, so use `--backup-dir` or a real backup program ([restic](restic.md), [BorgBackup](borg.md)) when you need history.

Documentation: [rclone docs](https://rclone.org/docs/) · [Commands](https://rclone.org/commands/) · [Filtering](https://rclone.org/filtering/) · [Crypt](https://rclone.org/crypt/) · [Bisync](https://rclone.org/bisync/)

> **Verification:** Only the bisync status (no longer labelled beta, `--resync` required on the first run) was checked against rclone.org. All other commands and flags are standard rclone usage written from knowledge and were **not** re-checked this session. No command was executed. Always dry-run `sync` first.

See also: [Backup Strategy](backup.md) · [restic](restic.md) · [rsync](rsync.md) · [Docker Volume Backup](docker-volume-backup.md) · [OpenSSH Cheat-Sheet](../tools/openssh.md) · [Linux](../linux/linux.md) · [Mount](../linux/mount.md)

---
## Remotes and Config
COMMAND | DESCRIPTION
---|---
`rclone config` | Interactive remote setup
`rclone config file` | Where the config file lives (default `~/.config/rclone/rclone.conf`)
`rclone config show` | Print the config (contains secrets)
`rclone listremotes` | List configured remotes
`rclone about <REMOTE>:` | Quota and usage
`rclone lsd <REMOTE>:` | List top-level directories
`rclone ls <REMOTE>:<PATH>` | List files with sizes
`rclone lsf <REMOTE>:<PATH>` | Machine-friendly listing
`rclone tree <REMOTE>:<PATH>` | Tree view
`rclone size <REMOTE>:<PATH>` | Total size and object count
`rclone obscure <PASSWORD>` | Obscure a password for the config file (not encryption)
`rclone version` | Version

The config file holds credentials: `chmod 600`, back it up with the other secrets (see [Backup Strategy](backup.md)). It can be encrypted with `rclone config` -> "Set configuration password", then supply `RCLONE_CONFIG_PASS` or `--password-command`.

Remotes without a config file, from the environment:
```bash
export RCLONE_CONFIG_B2_TYPE=b2
export RCLONE_CONFIG_B2_ACCOUNT=<KEY_ID>
export RCLONE_CONFIG_B2_KEY=<APPLICATION_KEY>
rclone lsd B2:
```

Example S3-compatible remote in `rclone.conf`:
```ini
[s3]
type = s3
provider = Other
access_key_id = <ACCESS_KEY_ID>
secret_access_key = <SECRET_ACCESS_KEY>
endpoint = https://<ENDPOINT>
```

---
## copy, sync, move
COMMAND | DESCRIPTION
---|---
`rclone copy <SRC> <DEST>` | Copy new and changed files. **Never deletes** at the destination
`rclone sync <SRC> <DEST>` | Make DEST identical to SRC. **Deletes** extra files at DEST
`rclone move <SRC> <DEST>` | Copy then delete the source files
`rclone copyto <SRC_FILE> <DEST_FILE>` | Copy one file with a rename
`rclone moveto <SRC> <DEST>` | Move and rename
`rclone bisync <PATH1> <PATH2> --resync` | Two-way sync, the **first** run needs `--resync`
`rclone bisync <PATH1> <PATH2>` | Later two-way runs
`rclone deletefile <REMOTE>:<FILE>` | Delete one file
`rclone purge <REMOTE>:<PATH>` | Delete the path and all contents (no filters)
`rclone mkdir <REMOTE>:<PATH>` | Create a directory

Remember: `rclone sync` is one-way and destructive on the destination. The direction is `SRC DEST`. Check twice.

### Safe sync routine
```bash
# 1. Preview. Nothing is changed.
rclone sync /srv/data <REMOTE>:<BUCKET>/data --dry-run -v

# 2. Real run with guard rails.
rclone sync /srv/data <REMOTE>:<BUCKET>/data \
  --max-delete 50 \
  --backup-dir <REMOTE>:<BUCKET>/archive/$(date +%F) \
  --log-file /var/log/rclone-data.log --log-level INFO \
  --stats-one-line

# 3. Verify. Compares sizes and hashes, reports differences.
rclone check /srv/data <REMOTE>:<BUCKET>/data --one-way
```
`--max-delete N` aborts if more than N deletions would happen. `--backup-dir` moves overwritten and deleted files into a dated archive, giving cheap versioning. It must be on the same remote as the destination and outside the destination path.

---
## Common Flags
FLAG | DESCRIPTION
---|---
`-n`, `--dry-run` | Show what would be done
`-v`, `-vv` | More logging
`-P`, `--progress` | Live progress
`--log-file <FILE>` / `--log-level INFO\|DEBUG\|NOTICE\|ERROR` | Logging to a file
`--stats-one-line` | Compact stats lines for logs
`--transfers <N>` | Parallel file transfers (default 4)
`--checkers <N>` | Parallel checkers (default 8)
`--fast-list` | Fewer API calls on S3, B2 and Drive, uses more memory
`--checksum` | Compare by hash instead of modification time and size
`--size-only` | Compare by size only
`--update` | Skip files that are newer on the destination
`--ignore-existing` | Skip files that already exist on the destination
`--immutable` | Fail if an existing file would be modified
`--track-renames` | Detect renamed files and rename instead of re-uploading
`--max-delete <N>` | Abort if too many deletions
`--backup-dir <DIR>` / `--suffix <SUFFIX>` | Keep replaced and deleted files
`--bwlimit 10M` | Bandwidth limit (bytes per second units, `10M` = 10 MiB/s)
`--bwlimit "08:00,512k 18:00,off"` | Timetable
`--retries <N>` / `--low-level-retries <N>` | Retry behaviour
`--min-age 15m` / `--max-age 7d` | Only files older or newer than this
`--order-by size,descending` | Transfer order
`--drive-use-trash=false` | Google Drive: delete permanently instead of trashing
`--s3-no-check-bucket` | S3: skip bucket existence checks (for restricted keys)
`--config <FILE>` | Use a different config file

`--bwlimit` can be changed live on a running `rclone` that has `--rc` enabled, or with `SIGUSR2` to toggle.

---
## Filters
Patterns use `**` for any path depth and a leading `/` to anchor at the root of the transfer. Rules apply in order, first match wins.

FLAG | DESCRIPTION
---|---
`--exclude '*.tmp'` | Exclude matches
`--exclude '/cache/**'` | Exclude a directory tree
`--include '*.jpg'` | Include matches (an `--include` makes everything else excluded unless you add `--exclude`)
`--exclude-from <FILE>` / `--include-from <FILE>` | Patterns from a file
`--filter '- *.tmp' --filter '+ *.jpg' --filter '- *'` | Ordered include/exclude rules
`--filter-from <FILE>` | Ordered rules from a file
`--exclude-if-present .nobackup` | Skip directories containing a marker file
`--files-from <FILE>` | Exact list of paths to transfer
`--min-size 1M` / `--max-size 5G` | Size filters
`--delete-excluded` | With `sync`, also delete excluded files from the destination (dangerous)

Test filters before running:
```bash
rclone ls /srv/data --filter-from /etc/rclone/filters.txt
```

---
## Crypt (client-side encryption)
A crypt remote wraps another remote and encrypts file contents and, optionally, names.

```ini
[secret]
type = crypt
remote = <REMOTE>:<BUCKET>/encrypted
filename_encryption = standard
directory_name_encryption = true
password = <OBSCURED_PASSWORD>
password2 = <OBSCURED_SALT>
```
Create it with `rclone config` (it generates and obscures the passwords) rather than hand-editing.

COMMAND | DESCRIPTION
---|---
`rclone sync /srv/data secret:data` | Upload encrypted
`rclone copy secret:data /tmp/restore` | Download and decrypt
`rclone cryptcheck /srv/data secret:data` | Verify local files against the encrypted remote without downloading
`rclone cryptdecode secret: <ENCRYPTED_NAME>` | Decode an encrypted filename

**Back up the crypt passwords and `rclone.conf` separately.** Without them the data is unrecoverable. Obscured is not encrypted: anyone with the config file can decrypt.

---
## Mount and Serve
COMMAND | DESCRIPTION
---|---
`rclone mount <REMOTE>:<PATH> /mnt/<NAME> --vfs-cache-mode full` | FUSE mount, full read and write caching
`rclone mount <REMOTE>: /mnt/<NAME> --read-only --daemon` | Read-only, in the background
`fusermount3 -u /mnt/<NAME>` | Unmount (or `umount`)
`rclone serve sftp <REMOTE>:<PATH> --addr :2022` | Expose a remote over SFTP
`rclone serve webdav <REMOTE>:<PATH> --addr :8080` | Expose over WebDAV
`rclone serve restic <REMOTE>:<PATH>` | restic REST backend, see [restic](restic.md)
`rclone ncdu <REMOTE>:` | Interactive disk usage

Mount flags that matter: `--vfs-cache-mode full`, `--vfs-cache-max-size 20G`, `--dir-cache-time 72h`, `--allow-other` (needs `user_allow_other` in `/etc/fuse.conf`). Mounts are fine for browsing and light access. Do not put a database directory on one.

---
## Scheduled Sync with systemd
`/etc/systemd/system/rclone-backup.service`:
```ini
[Unit]
Description=rclone sync to offsite
Wants=network-online.target
After=network-online.target

[Service]
Type=oneshot
Environment=RCLONE_CONFIG=/etc/rclone/rclone.conf
ExecStart=/usr/bin/rclone sync /srv/data <REMOTE>:<BUCKET>/data --max-delete 100 --backup-dir <REMOTE>:<BUCKET>/archive --log-file /var/log/rclone-backup.log --log-level INFO
```
`/etc/systemd/system/rclone-backup.timer`:
```ini
[Unit]
Description=Daily rclone sync

[Timer]
OnCalendar=*-*-* 03:30:00
Persistent=true

[Install]
WantedBy=timers.target
```
```bash
sudo systemctl daemon-reload && sudo systemctl enable --now rclone-backup.timer
```

---
## Gotchas
- `sync` direction and trailing slashes: rclone treats `src` and `src/` the same (unlike [rsync](rsync.md)); it always syncs the **contents** of the source into the destination.
- A `sync` from an **empty or unmounted** source deletes everything at the destination. Guard with `--max-delete`, or check the source mount first (`findmnt /mnt/data || exit 1`).
- Provider rate limits (Google Drive, OneDrive) may need `--tpslimit` and fewer `--transfers`, and for Drive your own client ID.
- `rclone mount` and `copy` run as the user whose `rclone.conf` they read. Under systemd, set `RCLONE_CONFIG` explicitly.
- Copying a live database file gives an inconsistent copy. Dump first, see [Database Dumps](database-dumps.md).

# BorgBackup
Borg is a deduplicating, compressing, authenticated-encryption backup program. Repositories hold many archives, and each archive is a point-in-time backup. This sheet uses the **Borg 1.4** syntax (`REPO::ARCHIVE`), which is what most distributions and the [borgmatic](borgmatic.md) Docker image ship. Borg 2 is still beta and changes the syntax (see the end of this sheet). Day-to-day scheduling is easier with [borgmatic](borgmatic.md).

Documentation: [Borg docs](https://borgbackup.readthedocs.io/) · [Quick start](https://borgbackup.readthedocs.io/en/stable/quickstart.html) · [Usage](https://borgbackup.readthedocs.io/en/stable/usage.html)

> **Verification:** The Borg 2 renames and its beta status were checked against the Borg changelog. The Borg 1.4 command syntax below is standard and long-stable but was **not** re-checked against the docs this session, and neither was the `authorized_keys` form. No command was executed.

See also: [Backup Strategy](backup.md) · [borgmatic](borgmatic.md) · [restic](restic.md) · [rsync](rsync.md) · [OpenSSH Cheat-Sheet](../tools/openssh.md) · [Linux](../linux/linux.md)

---
## Environment Variables
VARIABLE | DESCRIPTION
---|---
`BORG_REPO` | Default repository, so `REPO` can be omitted
`BORG_PASSPHRASE` | Passphrase (visible in the environment, avoid on shared hosts)
`BORG_PASSCOMMAND` | Command that prints the passphrase, for example `cat /etc/borg/passphrase`
`BORG_RSH` | SSH command, for example `ssh -i /root/.ssh/borg_ed25519 -o StrictHostKeyChecking=yes`
`BORG_REMOTE_PATH` | Borg binary name on the server, for example `borg1` on rsync.net
`BORG_CACHE_DIR` | Chunk cache location, default `~/.cache/borg`
`BORG_BASE_DIR` | Move config, cache and keys to one tree

Repository forms: `/path/to/repo`, `ssh://<USER>@<HOST>:<PORT>/./path/to/repo` (relative to the home), `ssh://<USER>@<HOST>/path/to/repo` (absolute), or the older `<USER>@<HOST>:path`.

---
## Create a Repository
COMMAND | DESCRIPTION
---|---
`borg init --encryption=repokey-blake2 <REPO>` | Key stored in the repository, protected by the passphrase (common choice)
`borg init --encryption=keyfile-blake2 <REPO>` | Key stored in `~/.config/borg/keys`, **you must back it up**
`borg init --encryption=authenticated-blake2 <REPO>` | Integrity only, no encryption
`borg init --encryption=none <REPO>` | No encryption or authentication
`borg key export <REPO> <FILE>` | Export the key (store it outside the host, with the passphrase)
`borg key export --paper <REPO>` | Printable key backup
`borg key change-passphrase <REPO>` | Change the passphrase

With `repokey`, losing the passphrase loses the data, and anybody with repo write access and the passphrase can read it. Export the key anyway.

---
## Create Backups
COMMAND | DESCRIPTION
---|---
`borg create --stats --progress <REPO>::<NAME> <PATH>...` | Create an archive
`borg create --stats --compression zstd,3 <REPO>::<NAME> <PATH>` | With zstd level 3 (also `lz4`, `zlib,6`, `lzma,6`, `auto,lz4`)
`borg create --list --filter=AME <REPO>::<NAME> <PATH>` | List added (A), modified (M) and error (E) files
`borg create --dry-run --list <REPO>::<NAME> <PATH>` | Show what would be backed up
`borg create --exclude '*.tmp' --exclude <PATH> <REPO>::<NAME> <PATH>` | Exclude
`borg create --exclude-from <FILE> <REPO>::<NAME> <PATH>` | Exclude patterns from a file
`borg create --exclude-caches --exclude-if-present .nobackup <REPO>::<NAME> <PATH>` | Skip cache dirs and dirs holding a marker file
`borg create --one-file-system <REPO>::<NAME> <PATH>` | Stay on one filesystem
`borg create --stdin-name <FILE> <REPO>::<NAME> -` | Back up stdin as a single file

Archive name placeholders: `{hostname}`, `{user}`, `{now}`, `{utcnow}`, `{fqdn}`. Example:
```bash
export BORG_REPO=ssh://<USER>@<HOST>/./borg-repo
export BORG_PASSCOMMAND='cat /etc/borg/passphrase'

borg create --stats --compression auto,zstd \
  --exclude-caches --exclude '/home/*/.cache' \
  '::{hostname}-{now:%Y-%m-%dT%H:%M:%S}' /etc /home /srv
```
With `BORG_REPO` set, `::NAME` refers to that repo.

---
## Prune and Compact
`prune` removes archives per a retention policy. In Borg 1.2 and later the space is only returned by `compact`.

COMMAND | DESCRIPTION
---|---
`borg prune --list --dry-run --keep-daily 7 --keep-weekly 4 --keep-monthly 6 <REPO>` | **Preview** a prune
`borg prune --list --keep-daily 7 --keep-weekly 4 --keep-monthly 6 --keep-yearly 1 <REPO>` | Prune
`borg prune --glob-archives '<HOST>-*' --keep-daily 7 <REPO>` | Only archives with a name prefix (needed when several hosts share a repo)
`borg compact <REPO>` | Free the space of deleted archives
`borg delete <REPO>::<NAME>` | Delete one archive (then compact)
`borg delete --dry-run --list <REPO>` | Preview a whole-repo delete (without `<NAME>` it deletes the repository, check the dry run)

Other `--keep-*` options: `--keep-within 3d`, `--keep-last N`, `--keep-hourly N`.

---
## Inspect, Verify, Browse
COMMAND | DESCRIPTION
---|---
`borg list <REPO>` | List archives
`borg list <REPO>::<NAME>` | List files in an archive
`borg list --short <REPO>` | Archive names only
`borg info <REPO>` | Repository size and dedup statistics
`borg info <REPO>::<NAME>` | Archive details
`borg diff <REPO>::<A> <B>` | Compare two archives
`borg check <REPO>` | Repository and archive consistency
`borg check --verify-data <REPO>` | Also decrypt and verify every chunk (slow, reads everything)
`borg check --repository-only <REPO>` | Quick repository check
`borg check --repair <REPO>` | Attempt repair (back up the repo first, read the docs)
`borg mount <REPO>::<NAME> <MOUNTPOINT>` | Browse an archive with FUSE (needs `python3-llfuse` or `pyfuse3`)
`borg mount <REPO> <MOUNTPOINT>` | Mount all archives
`borg umount <MOUNTPOINT>` | Unmount
`borg break-lock <REPO>` | Remove a stale lock (only if no borg process is running)

---
## Restore
`extract` writes into the **current directory**, so `cd` to the target first. Paths are stored without the leading slash.

```bash
mkdir /tmp/restore && cd /tmp/restore
borg extract --list <REPO>::<NAME> home/<USER>/documents
borg extract --dry-run --list <REPO>::<NAME>          # preview a full restore
borg extract --strip-components 2 <REPO>::<NAME> srv/app/data
borg export-tar <REPO>::<NAME> - | tar -tf -          # stream an archive as tar
```

Quick verification after a restore: compare with `diff -r /tmp/restore/home/<USER>/documents /home/<USER>/documents`.

---
## Remote Repository over SSH
- Install the same major Borg version on both ends.
- Use a dedicated SSH key and restrict it on the server in `~/.ssh/authorized_keys`:

```
command="borg serve --restrict-to-path /srv/borg/<HOST> --append-only",restrict ssh-ed25519 AAAA... backup@<HOST>
```

`--append-only` stops a compromised client from deleting history. Run `prune` and `compact` from a trusted admin machine with a different key. Without `--append-only`, a client can destroy its own backups.

---
## Hook-style Wrapper Script
For anything beyond a one-off, use [borgmatic](borgmatic.md). A minimal script if you want plain Borg:
```bash
#!/usr/bin/env bash
set -euo pipefail
export BORG_REPO=ssh://<USER>@<HOST>/./borg-repo
export BORG_PASSCOMMAND='cat /etc/borg/passphrase'

borg create --stats --compression auto,zstd '::{hostname}-{now:%Y-%m-%dT%H:%M:%S}' /etc /srv
borg prune --list --glob-archives '{hostname}-*' --keep-daily 7 --keep-weekly 4 --keep-monthly 6
borg compact
borg check --repository-only
curl -fsS -m 10 --retry 5 https://hc-ping.com/<UUID> >/dev/null
```

---
## Borg 2 Differences (beta at the time of writing)
Borg 2 is beta and its documentation says not to use it for production. Borg 1.4 repositories are not compatible and need `borg transfer`.

BORG 1.4 | BORG 2
---|---
`borg init` | `borg repo-create`
`borg list <REPO>` | `borg repo-list`
`borg info <REPO>` | `borg repo-info`
`borg create <REPO>::<NAME> ...` | `borg -r <REPO> create <NAME> ...` (or `BORG_REPO`)
Archive selected by `<REPO>::<NAME>` | Archive selected by name or `aid:<hash>`

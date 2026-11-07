# SnapRAID
SnapRAID is a snapshot parity tool for arrays of mostly static files, such as media libraries. Data disks stay independent filesystems, one or more parity disks protect them, and parity is only updated when you run `snapraid sync`, so it is closer to a backup than to live RAID. Pair it with [mergerfs](mergerfs.md) to present the disks as one pool.

Documentation: [SnapRAID manual](https://www.snapraid.it/manual) · [FAQ](https://www.snapraid.it/faq)
Project: [SnapRAID](https://www.snapraid.it/)

> **Verification:** commands, options and configuration directives were checked against the `snapraid` man page in Ubuntu 24.04. No array was built or recovered. SnapRAID is not a backup of deleted or overwritten files after a `sync`, and it does not protect against losing more disks than you have parity disks.

## How It Works
POINT | MEANING
---|---
Parity is a snapshot | Changes since the last `sync` are not protected
Each data disk keeps its own filesystem | Any one disk can be read on its own
1 parity disk survives 1 disk failure | `2-parity` survives two, and so on
Parity disk must be as large as the largest data disk | Plus room for filesystem overhead
Content file lists every file and checksum | Keep several copies on different disks
Best for large, rarely changing files | Poor fit for databases and VM images

## Configuration
`/etc/snapraid.conf`:

```text
parity /mnt/parity1/snapraid.parity

content /var/snapraid/snapraid.content
content /mnt/disk1/snapraid.content
content /mnt/disk2/snapraid.content

data d1 /mnt/disk1/
data d2 /mnt/disk2/
data d3 /mnt/disk3/

exclude *.unrecoverable
exclude /lost+found/
exclude /tmp/
```

DIRECTIVE | PURPOSE
---|---
`parity FILE` | Parity file; `2-parity`, `3-parity` add more
`content FILE` | Content (metadata) file; list at least one more than the number of parity disks
`data NAME DIR` | A data disk mount point; keep the name stable
`exclude PATTERN` / `include PATTERN` | Filter files
`nohidden` | Ignore hidden files
`autosave GIGABYTES` | Save the content file during long syncs
`pool DIR` | Directory for the read-only `pool` view
`smartctl DISK OPTIONS` | Custom `smartctl` command for USB or RAID controllers (use `%s` for the device)

## Daily Commands
COMMAND | DESCRIPTION
---|---
`snapraid status` | Array summary: scrub age, error counts, parity fill
`snapraid diff` | List changes since the last sync; exit code 2 means a sync is needed
`snapraid sync` | Update parity for new and changed files (can be interrupted and resumed)
`snapraid scrub` | Verify about 8% of the oldest data and parity against checksums
`snapraid scrub -p 5` | Scrub a different percentage
`snapraid scrub -p new` | Scrub only blocks not yet scrubbed
`snapraid scrub -p bad` | Re-check blocks marked bad
`snapraid smart` | SMART report for all disks (uses `smartctl`)
`snapraid up` / `snapraid down` | Spin disks up or down
`snapraid -d d1 down` | Spin down one data disk
`snapraid dup` | List files that are duplicates by content
`snapraid pool` | Build a read-only pool of symlinks in the configured `pool` directory
`snapraid touch` | Give files with a zero sub-second timestamp a random one (helps move detection)
`snapraid -c <CONFIG_FILE> sync` | Use a different configuration file

Always run `snapraid diff` before `sync`: if many files have been removed, stop and find out why before the parity is overwritten.

## Recovery
COMMAND | DESCRIPTION
---|---
`snapraid check` | Verify all files and parity against the last sync (read-only)
`snapraid check -a` | Check file data only, ignore parity (faster)
`snapraid fix` | Revert all files and parity to the state of the last sync
`snapraid -d d1 -l fix.log fix` | Rebuild one failed data disk onto a replacement mounted at the same path, with a log
`snapraid -e fix` | Fix only blocks marked bad by sync or scrub
`snapraid -m fix` | Restore files deleted since the last sync
`snapraid -f <DIR_OR_PATTERN> fix` | Restore a directory or pattern
`snapraid -i <DIR> check` | Use files from another directory (for example moved-out files) during recovery

`fix` unconditionally reverts changes made since the last sync. Files that cannot be recovered are renamed with the `.unrecoverable` extension.

Replacing a failed data disk:

```bash
# 1. mount the new, empty disk at the old mount point (for example /mnt/disk1)
# 2. rebuild it, logging to a file
snapraid -d d1 -l ~/snapraid-fix.log fix
# 3. check the result
snapraid -d d1 -a check
# 4. then bring parity back in step
snapraid sync
```

## Automation
Run `diff`, then `sync` and a partial `scrub` from cron or a systemd timer, and alert on failure. Do not run `sync` blindly: guard it with a threshold on deleted files.

```bash
#!/usr/bin/env bash
set -euo pipefail
snapraid diff > /tmp/snapraid-diff.txt || [ $? -eq 2 ]
REMOVED=$(grep -c '^remove ' /tmp/snapraid-diff.txt || true)  # line format of 'diff' output: unverified, check yours
if [ "$REMOVED" -gt 100 ]; then
  echo "Too many removed files ($REMOVED): not syncing" >&2
  exit 1
fi
snapraid sync
snapraid scrub -p 5 -o 30
```

The `-o 30` option limits scrubbing to blocks older than 30 days. Several community scripts add pre-checks and notifications; the threshold idea above is the important part.

## Troubleshooting
SYMPTOM | FIX
---|---
`sync` refuses with an empty or missing disk | A data disk is not mounted; mount it, do not use `--force-empty` until sure
Content file warnings | Keep content copies on several disks; check each path in `snapraid.conf`
Parity file too large for its disk | The parity disk needs to be at least as large as the largest data disk
Many files show as `copied` or `updated` after a move | Run `snapraid touch` once, then sync
Disk errors during scrub | `snapraid smart`, then `snapraid -e fix`; replace the disk if errors repeat
Files changed since last sync | They are not protected: run `snapraid sync`

## See Also
- [mergerfs](mergerfs.md)
- [Storage and Filesystems](storage-and-filesystems.md)
- [RAID with mdadm](raid-mdadm.md)
- [Backup Strategy](../backup/backup.md)

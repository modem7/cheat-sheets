# ZFS Snapshots and Replication
ZFS snapshots are instant, read-only, point-in-time views of a dataset. `zfs send` and `zfs receive` replicate them (fully or incrementally) to another pool or host, and Sanoid and Syncoid automate the snapshot schedule and the replication. Snapshots on the same pool protect against mistakes, not pool loss, so replicate to a second system. See [[backup]] for the 3-2-1 reasoning.

Documentation: [OpenZFS zfs-snapshot](https://openzfs.github.io/openzfs-docs/man/master/8/zfs-snapshot.8.html) · [zfs-send](https://openzfs.github.io/openzfs-docs/man/master/8/zfs-send.8.html) · [Sanoid and Syncoid](https://github.com/jimsalterjrs/sanoid) · [Syncoid wiki](https://github.com/jimsalterjrs/sanoid/wiki/Syncoid)

> **Verification:** Sanoid template keys, `process_children_only`, `recursive = yes|zfs`, and the Syncoid options `--no-sync-snap`, `--sendoptions`, `--recvoptions`, `--no-privilege-elevation`, `--sshkey`, `--exclude-datasets` and `--create-bookmark` (needs `--no-sync-snap`) were checked against the Sanoid repository and wiki. The raw `zfs`/`zpool` commands and the sanoid CLI flags were **not** re-checked against the man pages. No command was executed. Use `-n` dry runs and test on a scratch dataset first.

See also: [[backup]] · [[truenas-scale]] (replication tasks in the UI) · [[proxmox-storage]] · [[rsync]] · [[openssh]] · [[linux]]

---
## Snapshots
COMMAND | DESCRIPTION
---|---
`zfs snapshot <POOL>/<DATASET>@<NAME>` | Snapshot one dataset
`zfs snapshot -r <POOL>/<DATASET>@<NAME>` | Atomic recursive snapshot of a dataset and its children
`zfs snapshot <POOL>/<DATASET>@$(date +%F_%H%M)` | Date-stamped name
`zfs list -t snapshot` | List all snapshots
`zfs list -t snapshot -r <POOL>/<DATASET> -o name,used,refer,creation` | One dataset, with sizes
`zfs list -t snapshot -s creation -r <POOL>/<DATASET>` | Oldest first
`zfs diff <POOL>/<DATASET>@<NAME>` | What changed since a snapshot
`zfs destroy -nv <POOL>/<DATASET>@<NAME>` | **Dry run** of a destroy
`zfs destroy <POOL>/<DATASET>@<NAME>` | Destroy a snapshot
`zfs destroy -nv <POOL>/<DATASET>@<OLDEST>%<NEWEST>` | Dry-run destroying a range of snapshots
`zfs hold <TAG> <POOL>/<DATASET>@<NAME>` | Prevent a snapshot being destroyed
`zfs release <TAG> <POOL>/<DATASET>@<NAME>` | Remove the hold
`zfs holds <POOL>/<DATASET>@<NAME>` | List holds

---
## Restore and Roll Back
COMMAND | DESCRIPTION
---|---
`ls /<MOUNTPOINT>/.zfs/snapshot/<NAME>/` | Browse and copy single files out of a snapshot (hidden directory)
`zfs set snapdir=visible <POOL>/<DATASET>` | Make `.zfs` visible in listings
`zfs clone <POOL>/<DATASET>@<NAME> <POOL>/<CLONE>` | Writable copy of a snapshot, for testing a restore
`zfs rollback <POOL>/<DATASET>@<NAME>` | Roll back to the **most recent** snapshot
`zfs rollback -r <POOL>/<DATASET>@<NAME>` | Roll back to an older snapshot, **destroying newer ones**

Rollback discards everything written since the snapshot. For a single file, copy it out of `.zfs/snapshot` instead.

---
## Send and Receive
COMMAND | DESCRIPTION
---|---
`zfs send -nv <POOL>/<DATASET>@<SNAP>` | **Dry run**: print the stream size, send nothing
`zfs send <POOL>/<DATASET>@<SNAP> \| zfs receive <TARGET_POOL>/<DATASET>` | Full copy to a local pool
`zfs send <POOL>/<DATASET>@<SNAP> \| ssh <USER>@<HOST> zfs receive <TARGET_POOL>/<DATASET>` | Full copy to a remote host
`zfs send -i @<OLD> <POOL>/<DATASET>@<NEW> \| ssh <USER>@<HOST> zfs receive <TARGET_POOL>/<DATASET>` | Incremental between two snapshots
`zfs send -I @<OLD> <POOL>/<DATASET>@<NEW> \| ...` | Incremental including all intermediate snapshots
`zfs send -R <POOL>/<DATASET>@<SNAP> \| ...` | Replication stream: dataset, children, properties and snapshots
`zfs send -w <POOL>/<DATASET>@<SNAP> \| ...` | **Raw** send of an encrypted dataset: stays encrypted, the target never sees the key
`zfs send -c ... ` | Send blocks as stored compressed
`zfs receive -u ...` | Do not mount the received dataset
`zfs receive -F ...` | Force rollback of the target to the latest common snapshot (can destroy newer target data)
`zfs receive -s ...` | Save partial state if interrupted, so it can be resumed
`zfs get -H -o value receive_resume_token <TARGET>` | Read the resume token after an interrupted receive
`zfs send -t <TOKEN> \| ssh <USER>@<HOST> zfs receive -s <TARGET>` | Resume the interrupted transfer

Notes:
- An incremental send requires the **target to still have the `@<OLD>` snapshot**. Never delete the last common snapshot on both sides, or you must resend fully.
- A received dataset on a backup pool is normally set read-only: `zfs set readonly=on <TARGET_POOL>/<DATASET>`.
- Insert `pv` into the pipe for progress, and `mbuffer` for steadier throughput on long links.
- With raw sends of encrypted datasets, incremental sends keep working, but the target cannot be mounted without the key.

Verify after replication:
```bash
zfs list -t snapshot -r <TARGET_POOL>/<DATASET> | tail
zpool scrub <TARGET_POOL> && zpool status <TARGET_POOL>
```

---
## Sanoid (snapshot policy)
Sanoid takes and prunes snapshots from a policy file, run every minute (or every 15) from cron or a systemd timer. On Debian and Ubuntu it is packaged as `sanoid`.

`/etc/sanoid/sanoid.conf`:
```ini
[<POOL>/data]
        use_template = production
        recursive = yes

[<POOL>/vm]
        use_template = production
        recursive = zfs

[<POOL>/backup]
        use_template = backup
        process_children_only = yes
        recursive = yes

[template_production]
        frequently = 0
        hourly = 24
        daily = 7
        weekly = 4
        monthly = 6
        yearly = 0
        autosnap = yes
        autoprune = yes

[template_backup]
        # Replication target: keep snapshots that syncoid brings in, do not create new ones
        autosnap = no
        autoprune = yes
        hourly = 36
        daily = 30
        monthly = 12
```

KEY | DESCRIPTION
---|---
`recursive = yes` | Apply to child datasets, snapshotting each one separately
`recursive = zfs` | Apply to children using one atomic recursive ZFS snapshot
`process_children_only = yes` | Snapshot the children but not the parent dataset itself
`use_template = <NAME>` | Inherit from `[template_<NAME>]`
`autosnap` / `autoprune` | Take and prune snapshots
`frequently`, `hourly`, `daily`, `weekly`, `monthly`, `yearly` | How many of each to keep

COMMAND | DESCRIPTION
---|---
`sanoid --cron` | Take and prune per the config (what the timer runs)
`sanoid --take-snapshots --verbose` | Take snapshots only
`sanoid --prune-snapshots --verbose` | Prune only
`sanoid --monitor-snapshots` | Nagios-style check that snapshots are recent
`sanoid --monitor-health` | Pool health check
`sanoid --configdir <DIR>` | Use another config directory
`sanoid --cron --readonly --verbose` | Preview without changes (check `--help` on your version)

Debian ships a systemd `sanoid.timer`. Enable it with `sudo systemctl enable --now sanoid.timer`.

---
## Syncoid (replication)
Syncoid wraps `zfs send`/`receive` with snapshot management, incremental detection and resume support. Run it from the **backup** host in pull mode, or from the source in push mode.

COMMAND | DESCRIPTION
---|---
`syncoid <POOL>/data <BACKUP_POOL>/data` | Local replication
`syncoid <USER>@<HOST>:<POOL>/data <BACKUP_POOL>/data` | Pull from a remote host
`syncoid <POOL>/data <USER>@<HOST>:<BACKUP_POOL>/data` | Push to a remote host
`syncoid -r <POOL>/data <BACKUP_POOL>/data` | Recursive: include child datasets
`syncoid --no-sync-snap <SRC> <DEST>` | Only use existing (Sanoid) snapshots, create no `syncoid_*` ones
`syncoid --no-sync-snap --create-bookmark <SRC> <DEST>` | Also create a bookmark on the source
`syncoid --sendoptions=w <SRC> <DEST>` | Raw send for encrypted datasets
`syncoid --recvoptions=u <SRC> <DEST>` | Pass options to `zfs receive`
`syncoid --exclude-datasets='<REGEX>' -r <SRC> <DEST>` | Skip child datasets matching a regex
`syncoid --sshkey=<KEY> <SRC> <DEST>` | Specific SSH key
`syncoid --no-privilege-elevation <SRC> <DEST>` | Do not use `sudo`, rely on `zfs allow` permissions
`syncoid --quiet <SRC> <DEST>` | Quiet, for cron

Typical hardened pull setup: create a non-root user on the source with `zfs allow`, give the backup host a dedicated SSH key for it, and run `syncoid` from the backup host so a compromised source cannot reach the backups.
```bash
# On the source, delegate only what syncoid needs (verify the permission set for your version)
sudo zfs allow -u <USER> send,snapshot,hold <POOL>/data
# On the backup host
sudo zfs allow -u <USER> receive,create,mount,mountpoint <BACKUP_POOL>
```

systemd timer for a nightly pull (`/etc/systemd/system/syncoid-data.service` and `.timer`):
```ini
[Unit]
Description=Replicate data dataset with syncoid
Wants=network-online.target
After=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/sbin/syncoid --no-sync-snap --quiet <USER>@<HOST>:<POOL>/data <BACKUP_POOL>/data
```
```ini
[Unit]
Description=Nightly syncoid

[Timer]
OnCalendar=*-*-* 03:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

---
## Gotchas
- `zfs receive -F` can destroy newer data on the target. Use `-nv` first and know what you are overwriting.
- Syncoid with `--no-sync-snap` replicates only what Sanoid created, make sure Sanoid runs on the source and pruning on the target does not remove the last common snapshot.
- Keep snapshots small in number on pools with heavy churn: each holds blocks. Check `zfs list -t snapshot -o name,used`.
- A snapshot of a running database is crash-consistent at best. Quiesce or dump first, see [[database-dumps]].
- Test restores: clone a replicated snapshot (`zfs clone`) and mount it, then compare, see the checklist in [[backup]].

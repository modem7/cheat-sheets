# ZFS
ZFS is a combined filesystem and volume manager: disks are grouped into pools (`zpool`), and datasets and volumes (`zfs`) are carved out of them with checksumming, compression and snapshots built in. Use this sheet for pool health and day-to-day dataset management; snapshots and replication are in [ZFS Snapshots and Replication](../backup/zfs-snapshots-backup.md).

Documentation: [OpenZFS documentation](https://openzfs.github.io/openzfs-docs/) · [zpool man pages](https://openzfs.github.io/openzfs-docs/man/master/8/zpool.8.html) · [zfs man pages](https://openzfs.github.io/openzfs-docs/man/master/8/zfs.8.html)

> **Verification:** subcommands and options were checked against the `zpool` and `zfs` man pages shipped in Ubuntu 24.04 (`zfsutils-linux`). No pool was created, so output and behaviour on real hardware are unverified.

## Pool Health
COMMAND | DESCRIPTION
---|---
`zpool status` | Pool state, vdev layout, scrub and resilver progress
`zpool status -x` | Only pools with problems
`zpool status -v` | Include files with permanent errors
`zpool list` | Size, allocation, fragmentation and health per pool
`zpool iostat -v <POOL> 5` | Per-vdev I/O every 5 seconds
`zpool history <POOL>` | Commands previously run on the pool
`zpool get health <POOL>` | Single property
`zpool clear <POOL>` | Clear error counters after fixing the cause

## Scrub and Trim
COMMAND | DESCRIPTION
---|---
`zpool scrub <POOL>` | Read and verify every block; repairs from redundancy
`zpool scrub -p <POOL>` | Pause a running scrub
`zpool scrub -s <POOL>` | Stop a scrub
`zpool trim <POOL>` | Manually TRIM free space on SSDs
`zpool set autotrim=on <POOL>` | TRIM continuously

## Create and Change Pools
Use stable `/dev/disk/by-id/` paths, never `/dev/sdX`. `ashift=12` aligns to 4 KiB sectors and cannot be changed afterwards.

COMMAND | DESCRIPTION
---|---
`zpool create -o ashift=12 <POOL> mirror <DISK1> <DISK2>` | New mirrored pool
`zpool create -o ashift=12 <POOL> raidz2 <DISK1> <DISK2> <DISK3> <DISK4>` | New RAIDZ2 pool
`zpool add <POOL> mirror <DISK1> <DISK2>` | Add a vdev (permanent for most vdev types; check with `-n` first)
`zpool add -n <POOL> mirror <DISK1> <DISK2>` | Dry run: show the resulting layout
`zpool attach <POOL> <EXISTING_DISK> <NEW_DISK>` | Add a disk to a mirror
`zpool detach <POOL> <DISK>` | Remove a disk from a mirror
`zpool replace <POOL> <OLD_DISK> <NEW_DISK>` | Replace a failed or smaller disk
`zpool offline <POOL> <DISK>` / `zpool online <POOL> <DISK>` | Take a disk out of or back into service
`zpool export <POOL>` | Cleanly detach a pool before moving disks
`zpool import` | List importable pools
`zpool import -d /dev/disk/by-id <POOL>` | Import using stable device names
`zpool destroy <POOL>` | **Destroys the pool and its data**

## Datasets
COMMAND | DESCRIPTION
---|---
`zfs list` | Datasets with used, available and mountpoint
`zfs list -o space` | Space accounting: snapshots, children, reservations
`zfs list -t all -r <POOL>` | Datasets, volumes and snapshots
`zfs create <POOL>/<DATASET>` | New dataset (mounted at `/<POOL>/<DATASET>` by default)
`zfs create -p <POOL>/<PARENT>/<DATASET>` | Create missing parents too
`zfs create -V 20G <POOL>/<VOLUME>` | Block volume (zvol) of fixed size
`zfs rename <POOL>/<OLD> <POOL>/<NEW>` | Rename a dataset
`zfs destroy <POOL>/<DATASET>` | **Deletes the dataset and its data**
`zfs destroy -r <POOL>/<DATASET>` | **Also deletes children and snapshots**
`zfs mount -a` | Mount all datasets
`zfs unmount <POOL>/<DATASET>` | Unmount one dataset

## Properties
COMMAND | DESCRIPTION
---|---
`zfs get all <POOL>/<DATASET>` | Every property with its source
`zfs get compressratio <POOL>/<DATASET>` | Compression achieved
`zfs set compression=lz4 <POOL>/<DATASET>` | Enable lz4 compression for new writes
`zfs set atime=off <POOL>/<DATASET>` | Stop updating access times
`zfs set quota=500G <POOL>/<DATASET>` | Cap space used by a dataset and its children
`zfs set reservation=100G <POOL>/<DATASET>` | Guarantee space
`zfs set recordsize=1M <POOL>/<DATASET>` | Block size for large sequential files
`zfs set mountpoint=/srv/data <POOL>/<DATASET>` | Change the mount path
`zfs inherit compression <POOL>/<DATASET>` | Revert a property to the inherited value

## Encryption
COMMAND | DESCRIPTION
---|---
`zfs create -o encryption=on -o keyformat=passphrase <POOL>/<DATASET>` | New encrypted dataset (prompts for a passphrase)
`zfs load-key <POOL>/<DATASET>` | Load the key after a reboot or import
`zfs load-key -a` | Load keys for all encrypted datasets
`zfs mount <POOL>/<DATASET>` | Mount once the key is loaded
`zfs unmount <POOL>/<DATASET>` then `zfs unload-key <POOL>/<DATASET>` | Lock the dataset again

Encryption can only be set at creation. Back up the passphrase or key file separately: without it the data is unrecoverable.

## Snapshots
Full coverage in [ZFS Snapshots and Replication](../backup/zfs-snapshots-backup.md). The basics:

```bash
zfs snapshot -r POOL/DATASET@before-upgrade
zfs list -t snapshot -r POOL/DATASET
zfs rollback POOL/DATASET@before-upgrade
```

## Troubleshooting
SYMPTOM | FIX
---|---
Pool shows `DEGRADED` | `zpool status -v`, then `zpool replace` the failed disk and watch the resilver
Pool missing after reboot | `zpool import`, then `zpool import <POOL>`; check cables and `by-id` names
`cannot import ... pool may be in use` | Export it on the other host first, or `zpool import -f <POOL>` only when sure it is not in use elsewhere
Checksum errors on one disk | Run `zpool scrub`, check `smartctl -a` for that disk, replace if errors recur
Dataset full but data deleted | Snapshots hold the space: `zfs list -t snapshot -o name,used`

## See Also
- [ZFS Snapshots and Replication](../backup/zfs-snapshots-backup.md)
- [Storage and Filesystems](storage-and-filesystems.md)
- [Proxmox Storage](../proxmox/proxmox-storage.md)
- [TrueNAS Scale](../infra/truenas-scale.md)
- [RAID with mdadm](raid-mdadm.md)

# Btrfs
Btrfs is a copy-on-write Linux filesystem with built-in subvolumes, snapshots, checksums, compression, multi-device RAID profiles and send/receive replication. Use it for snapshotting root and data volumes, or as a single-host alternative to ZFS that ships in the mainline kernel.

Documentation: [Btrfs documentation](https://btrfs.readthedocs.io/en/latest/) · [btrfs(8) manual pages](https://btrfs.readthedocs.io/en/latest/btrfs.html)
Project: [btrfs-progs](https://github.com/kdave/btrfs-progs)

> **Verification:** subcommands and options were checked against the btrfs-progs 6.6.3 man pages in Ubuntu 24.04. No filesystem was created or mounted. Commands marked destructive delete or overwrite data. RAID5 and RAID6 profiles are documented upstream as having known problems: avoid them for data you care about.

## Create and Mount
COMMAND | DESCRIPTION
---|---
`sudo mkfs.btrfs -L <LABEL> /dev/<DEVICE>` | **Formats the device.** Single-device filesystem
`sudo mkfs.btrfs -L <LABEL> -d raid1 -m raid1 /dev/<DEV1> /dev/<DEV2>` | **Formats both devices.** Mirror data and metadata
`sudo mkfs.btrfs -d single -m raid1 /dev/<DEV1> /dev/<DEV2>` | Data spread without redundancy, metadata mirrored
`sudo mount /dev/<DEVICE> /mnt/data` | Mount (any device of a multi-device filesystem works)
`sudo mount -o compress=zstd,noatime /dev/<DEVICE> /mnt/data` | Compression and no access-time updates
`sudo mount -o subvol=<NAME> /dev/<DEVICE> /mnt/data` | Mount a subvolume by name
`sudo btrfs filesystem label /mnt/data <NEWLABEL>` | Change the label

`/etc/fstab` entry:

```text
UUID=FILESYSTEM_UUID /mnt/data btrfs defaults,noatime,compress=zstd,subvol=@data 0 0
```

Find the UUID with `lsblk -f` (see [Storage and Filesystems](storage-and-filesystems.md)).

## Subvolumes
A subvolume looks like a directory but can be snapshotted, mounted and sent separately.

COMMAND | DESCRIPTION
---|---
`sudo btrfs subvolume create /mnt/data/<NAME>` | New subvolume
`sudo btrfs subvolume list /mnt/data` | List subvolumes with IDs
`sudo btrfs subvolume show /mnt/data/<NAME>` | Details, including UUID and snapshots
`sudo btrfs subvolume delete /mnt/data/<NAME>` | **Deletes the subvolume and its data**
`sudo btrfs subvolume get-default /mnt/data` | Default subvolume mounted when none is named
`sudo btrfs subvolume set-default <ID> /mnt/data` | Change the default subvolume
`sudo btrfs subvolume sync /mnt/data` | Wait for deleted subvolumes to be cleaned up

A common layout uses top-level subvolumes such as `@` (root), `@home` and `@snapshots`, each mounted with `subvol=`.

## Snapshots
COMMAND | DESCRIPTION
---|---
`sudo btrfs subvolume snapshot /mnt/data/<NAME> /mnt/data/.snapshots/<NAME>-$(date +%F)` | Writable snapshot
`sudo btrfs subvolume snapshot -r /mnt/data/<NAME> /mnt/data/.snapshots/<NAME>-$(date +%F)` | Read-only snapshot (needed for `send`)
`sudo btrfs subvolume delete /mnt/data/.snapshots/<SNAPSHOT>` | **Deletes a snapshot**
`cp -a --reflink=always <FILE> <COPY>` | Instant copy sharing blocks (same filesystem only)

To roll back, move or `mv` the broken subvolume away and snapshot the good one into its place, or use `set-default` and remount. Tools such as Snapper or btrbk automate retention (not covered here).

## Send and Receive
Replicate read-only snapshots to another Btrfs filesystem or file.

```bash
# full send
sudo btrfs send /mnt/data/.snapshots/SNAP1 | sudo btrfs receive /mnt/backup

# incremental: send only the difference from a snapshot both sides already have
sudo btrfs send -p /mnt/data/.snapshots/SNAP1 /mnt/data/.snapshots/SNAP2 | sudo btrfs receive /mnt/backup

# to a remote host
sudo btrfs send /mnt/data/.snapshots/SNAP1 | ssh <USER>@<HOST> 'sudo btrfs receive /mnt/backup'
```

COMMAND | DESCRIPTION
---|---
`btrfs send -p <PARENT> <SNAPSHOT>` | Incremental stream against a parent present on both sides
`btrfs send -f <FILE> <SNAPSHOT>` | Write the stream to a file
`btrfs receive -f <FILE> <DIR>` | Read a stream from a file

## Scrub, Balance and Space
COMMAND | DESCRIPTION
---|---
`sudo btrfs scrub start /mnt/data` | Verify checksums and repair from redundancy (runs in the background)
`sudo btrfs scrub start -B /mnt/data` | Run in the foreground
`sudo btrfs scrub status /mnt/data` | Progress and error counts
`sudo btrfs scrub cancel /mnt/data` / `resume /mnt/data` | Stop and continue
`sudo btrfs filesystem usage /mnt/data` | Real allocation: data, metadata, unallocated space
`sudo btrfs filesystem df /mnt/data` | Per-type usage
`sudo btrfs filesystem show` | Filesystems and member devices
`sudo btrfs balance start -dusage=50 /mnt/data` | Compact data chunks that are under 50% full
`sudo btrfs balance start -musage=50 /mnt/data` | Same for metadata chunks
`sudo btrfs balance status /mnt/data` | Progress
`sudo btrfs balance cancel /mnt/data` | Stop a balance
`sudo btrfs filesystem defragment -r /mnt/data/<DIR>` | Defragment (breaks block sharing with snapshots; use sparingly)

`df` is unreliable on Btrfs: use `btrfs filesystem usage`. A full filesystem with free data space usually means no unallocated space for new metadata chunks: a filtered `balance` frees it.

## Devices and RAID
COMMAND | DESCRIPTION
---|---
`sudo btrfs device add /dev/<DEVICE> /mnt/data` | Add a device
`sudo btrfs device remove /dev/<DEVICE> /mnt/data` | Remove a device (data is migrated off first)
`sudo btrfs device stats /mnt/data` | Per-device error counters
`sudo btrfs device scan` | Register devices after boot or hotplug
`sudo btrfs replace start /dev/<OLD> /dev/<NEW> /mnt/data` | Replace a device in place
`sudo btrfs replace status /mnt/data` | Progress
`sudo btrfs filesystem resize max /mnt/data` | Grow to fill the device after enlarging it
`sudo btrfs filesystem resize -10G /mnt/data` | Shrink by 10 GiB
`sudo btrfs balance start -dconvert=raid1 -mconvert=raid1 /mnt/data` | Convert profiles (for example single to RAID1)

## Quotas
COMMAND | DESCRIPTION
---|---
`sudo btrfs quota enable /mnt/data` | Enable quota groups (adds overhead with many snapshots)
`sudo btrfs qgroup show /mnt/data` | Usage per quota group
`sudo btrfs qgroup limit 100G /mnt/data/<NAME>` | Limit a subvolume
`sudo btrfs qgroup limit none /mnt/data/<NAME>` | Remove the limit

## Copy-on-Write and Databases
COMMAND | DESCRIPTION
---|---
`chattr +C /mnt/data/<EMPTY_DIR>` | Disable copy-on-write for new files in an empty directory (databases, VM images); also disables checksums and compression for them
`lsattr -d /mnt/data/<DIR>` | Check the `C` attribute

Setting `+C` on a file that already has data does not change existing extents.

## Repair and Recovery
COMMAND | DESCRIPTION
---|---
`sudo btrfs check /dev/<DEVICE>` | Read-only check of an **unmounted** filesystem
`sudo btrfs check --repair /dev/<DEVICE>` | **Last resort, can make things worse:** back up first and read the upstream warning
`sudo btrfs restore /dev/<DEVICE> /mnt/recovery` | Copy files off an unmountable filesystem without writing to it
`sudo dmesg \| grep -i btrfs` | Kernel messages

## Troubleshooting
SYMPTOM | FIX
---|---
`No space left on device` but `df` shows free space | `btrfs filesystem usage`; run `balance start -dusage=20` to free chunks
Checksum errors in `dmesg` | `btrfs scrub start`, `btrfs device stats`; check the disk with `smartctl`
Slow after many snapshots | Reduce snapshot count; avoid quotas if unneeded
Cannot mount degraded RAID1 | `mount -o degraded`, then `btrfs replace` the missing device
Snapshots missing space after delete | Deletion is asynchronous: `btrfs subvolume sync`

## See Also
- [Storage and Filesystems](storage-and-filesystems.md)
- [LVM](lvm.md)
- [RAID with mdadm](raid-mdadm.md)
- [Mount](mount.md)
- [Backup Strategy](../backup/backup.md)
- [Proxmox Storage](../proxmox/proxmox-storage.md)

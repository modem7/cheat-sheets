# mergerfs
mergerfs is a FUSE union filesystem that presents several disks or directories as one mount point, while each disk keeps its own filesystem and can be read on its own. It is the usual way to pool mismatched disks in a media server, often together with [SnapRAID](snapraid.md) for parity.

Documentation: [mergerfs README](https://github.com/trapexit/mergerfs#readme) · [mergerfs docs](https://trapexit.github.io/mergerfs/)
Project: [mergerfs on GitHub](https://github.com/trapexit/mergerfs)

> **Verification:** options and policy names were checked against the `mergerfs` man page of version 2.33.5 (Ubuntu 24.04 package). Current upstream releases (2.40 and later) have changed some defaults and renamed options, so check the documentation for your installed version (`mergerfs -V`). No pool was mounted on real disks. Prefer the upstream release packages over the distribution one for new installs.

## Concepts
TERM | MEANING
---|---
Branch | One source directory or disk in the pool
Policy | Rule that picks which branch a function (create, search, action) uses
`create` policy | Chooses the branch for new files; the main setting to tune
`mfs` | Most free space: spreads new files to the emptiest disk
`ff` | First found: fills disks in listed order
`lfs` / `lus` | Least free space / least used space
`rand` | Random branch
`ep*` (`epmfs`, `epff`, ...) | Path preserving: only branches where the parent directory already exists

## Mount
COMMAND | DESCRIPTION
---|---
`mergerfs -o allow_other,use_ino,category.create=mfs /mnt/disk1:/mnt/disk2:/mnt/disk3 /mnt/pool` | Mount three disks as one
`mergerfs -o allow_other,use_ino,category.create=mfs '/mnt/disk*' /mnt/pool` | Use a glob; quote it so mergerfs expands it
`mergerfs -V` | Version
`fusermount -u /mnt/pool` | Unmount (or `sudo umount /mnt/pool`)
`mount \| grep mergerfs` | Show the pool and its options

Permanent mount in `/etc/fstab`:

```text
/mnt/disk* /mnt/pool fuse.mergerfs allow_other,use_ino,cache.files=off,dropcacheonclose=true,category.create=mfs,minfreespace=50G,fsname=pool 0 0
```

## Common Options
OPTION | PURPOSE
---|---
`allow_other` | Let users other than the mounting user see the pool (required for services)
`use_ino` | mergerfs supplies inode numbers (recommended)
`category.create=mfs` | Policy for creating files
`category.search=ff` / `category.action=epall` | Policies for lookups and for actions such as `chmod`
`func.FUNC=POLICY` | Override one function, for example `func.getattr=newest`
`minfreespace=SIZE` | Skip branches with less free space than this when creating files
`moveonenospc=true` | On a full disk, move the file to another branch and retry
`cache.files=off` / `partial` / `full` | Page cache mode; `off` is safest, `partial` allows `mmap`
`dropcacheonclose=true` | Avoid double caching
`fsname=NAME` | Name shown in `df` and `mount`
`statfs=base` / `full` | How free space is reported
`ignorepponrename=true` | Ignore path preservation on rename

Options are evaluated in order, so put `category.*` before `func.*` overrides.

## Branch Modes
Append a mode to a branch with `=`:

```text
/mnt/disk1=RW:/mnt/disk2=RW:/mnt/archive=NC
```

MODE | MEANING
---|---
`RW` | Read and write (default)
`RO` | Read-only branch, never chosen for creation or action
`NC` | No create: files can be read and changed but new files are not created there

## Runtime Control
mergerfs exposes extended attributes on the pool. The `.mergerfs` pseudo file is marked deprecated in the 2.33.5 man page, so check the documentation of your version for the current interface.

COMMAND | DESCRIPTION
---|---
`getfattr -d -m mergerfs /mnt/pool/.mergerfs` | List runtime settings (needs `attr` package)
`setfattr -n user.mergerfs.category.create -v epmfs /mnt/pool/.mergerfs` | Change a setting without remounting
`getfattr -n user.mergerfs.basepath /mnt/pool/<FILE>` | Which disk holds a file

Key names follow the man page; the `getfattr` and `setfattr` commands themselves are from the `attr` package and were not run against a pool here (unverified). Test on a scratch pool first.

## Typical Media Server Layout
```text
/mnt/disk1  /mnt/disk2  /mnt/disk3   # data disks, each its own filesystem
/mnt/parity1                          # SnapRAID parity disk
/mnt/pool                             # mergerfs pool of the data disks, used by Plex, Jellyfin and the arr apps
```

Point the containers and apps at `/mnt/pool`, not the individual disks. Keep downloads and the library in the same pool so moves are fast renames; see [Docker-Compose](../docker/docker-compose.md) for bind mounts.

## Troubleshooting
SYMPTOM | FIX
---|---
Services cannot see the pool | Add `allow_other`, and `user_allow_other` in `/etc/fuse.conf`
New files always land on one disk | `category.create` is `ff` or an `ep*` policy; use `mfs`, and check `minfreespace`
`No space left on device` with space on another disk | Use `moveonenospc=true` or a non-path-preserving create policy
`mmap` errors (some databases and apps) | Use `cache.files=partial` or `full`
Pool empty after boot | Mount the disks first, then the pool; systemd mount ordering options are not covered here (unverified)

## See Also
- [SnapRAID](snapraid.md)
- [Storage and Filesystems](storage-and-filesystems.md)
- [Mount](mount.md)
- [Disk Usage](disk-usage.md)
- [Hardware Inspection](hardware-inspection.md)
- [NFS](nfs.md)
- [Docker-Compose](../docker/docker-compose.md)

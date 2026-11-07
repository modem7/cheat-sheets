# XFS
**XFS** is a high-performance journalling file system, the default on RHEL and its derivatives and common for large volumes and media storage. It grows online but cannot be shrunk. Volume management is in [LVM](lvm.md), mounting in [Mount](mount.md) and the wider picture in [Storage and Filesystems](storage-and-filesystems.md).

Documentation: [XFS man pages (xfsprogs)](https://man7.org/linux/man-pages/man8/xfs_growfs.8.html) · `man xfs`, `man xfs_repair`, `man xfs_quota`, `man xfsdump`

> **Verification:** options were checked against the `xfsprogs` and `xfsdump` man pages and `--help` output on Ubuntu 24.04 (xfsdump 3.1.11) in a throwaway container. No command was run against a real file system. Creating, repairing and zeroing logs can destroy data: check the device name first and back up.

See also: [LVM](lvm.md) · [RAID with mdadm](raid-mdadm.md) · [Storage and Filesystems](storage-and-filesystems.md) · [Mount](mount.md) · [Linux](linux.md)

---
## Create
COMMAND | DESCRIPTION
---|---
`sudo mkfs.xfs <DEVICE>` | Format (destroys existing data; refuses if a file system is already present)
`sudo mkfs.xfs -f <DEVICE>` | Force overwrite of an existing file system
`sudo mkfs.xfs -L <LABEL> <DEVICE>` | Set a label
`sudo mkfs.xfs -m reflink=1 <DEVICE>` | Enable reflink copies (see the man page for the default on your version)
`sudo mkfs.xfs -d su=<STRIPE_UNIT>,sw=<DATA_DISKS> <DEVICE>` | Align to RAID stripe geometry
`sudo mkfs.xfs -i maxpct=<PERCENT> <DEVICE>` | Cap the share of space used for inodes

Example `/etc/fstab` line (use the UUID from `blkid`):

```text
UUID=<UUID>  /srv/data  xfs  defaults,nofail  0  0
```

---
## Inspect
COMMAND | DESCRIPTION
---|---
`xfs_info <MOUNTPOINT>` | Geometry: block size, allocation groups, log, features
`sudo xfs_info <DEVICE>` | Same, for an unmounted device
`df -hT <MOUNTPOINT>` | Space used and free
`sudo xfs_db -r <DEVICE>` | Read-only debugger for an unmounted file system (`-r` read-only)
`sudo xfs_bmap -v <FILE>` | Extent map of a file (fragmentation)
`sudo xfs_logprint <DEVICE>` | Dump the journal of an unmounted file system

---
## Grow
XFS grows only. The underlying block device must already be larger, for example after `lvextend` ([LVM](lvm.md)).

COMMAND | DESCRIPTION
---|---
`sudo xfs_growfs <MOUNTPOINT>` | Grow the data section to fill the device (works mounted)
`sudo xfs_growfs -n <MOUNTPOINT>` | Show the resulting geometry without changing anything
`sudo xfs_growfs -D <BLOCKS> <MOUNTPOINT>` | Grow to a given number of file-system blocks
`sudo lvextend -r -l +100%FREE <VG>/<LV>` | Extend an LV and grow the file system in one go

---
## Check and Repair
Run repairs on an **unmounted** file system. Back up first where possible.

COMMAND | DESCRIPTION
---|---
`sudo xfs_repair -n <DEVICE>` | Dry run: report damage, change nothing
`sudo xfs_repair <DEVICE>` | Repair
`sudo xfs_repair -v <DEVICE>` | Repair with verbose output
`sudo xfs_repair -L <DEVICE>` | Zero the log first; last resort, may lose recent changes
`sudo xfs_repair -f <IMAGE_FILE>` | Repair an image file rather than a device
`sudo xfs_repair -m <MEGABYTES> <DEVICE>` | Limit memory use
`sudo xfs_metadump <DEVICE> <FILE>` | Dump metadata only (for bug reports); `xfs_mdrestore` restores it

If `xfs_repair` reports a dirty log, mount and unmount once to replay it, and only use `-L` if the mount fails.

```bash
sudo mount <DEVICE> /mnt && sudo umount /mnt
sudo xfs_repair -n <DEVICE>
```

---
## Label, UUID and Features
COMMAND | DESCRIPTION
---|---
`sudo xfs_admin -l <DEVICE>` | Print the label
`sudo xfs_admin -L <LABEL> <DEVICE>` | Set the label (unmounted)
`sudo xfs_admin -u <DEVICE>` | Print the UUID
`sudo xfs_admin -U generate <DEVICE>` | Generate a new UUID (needed after cloning a disk, to mount both)
`sudo xfs_admin -U nil <DEVICE>` | Clear the UUID
`sudo xfs_admin -O bigtime=1 <DEVICE>` | Upgrade a feature on an unmounted V5 file system (see the `xfs_admin` man page for supported features)

Use `xfs_admin` only on unmounted file systems. On kernels that support online label changes, `xfs_io -c label` works on a mounted file system (`man xfs_io`; not run here).

---
## Quotas
Enable at mount time with `uquota` (user), `gquota` (group) or `pquota` (project); changing these options needs an unmount and remount.

```text
UUID=<UUID>  /srv/data  xfs  defaults,uquota,pquota  0  0
```

COMMAND | DESCRIPTION
---|---
`sudo xfs_quota -x -c 'state' <MOUNTPOINT>` | Show quota state
`sudo xfs_quota -x -c 'report -h' <MOUNTPOINT>` | Human-readable usage report
`sudo xfs_quota -x -c 'limit bsoft=<SOFT> bhard=<HARD> <USER>' <MOUNTPOINT>` | Set block limits for a user (for example `5g` and `6g`)
`sudo xfs_quota -x -c 'limit -g bsoft=<SOFT> bhard=<HARD> <GROUP>' <MOUNTPOINT>` | Group limit
`sudo xfs_quota -x -c 'quota -h <USER>' <MOUNTPOINT>` | One user's usage
`sudo xfs_quota -x -c 'report -p -h' <MOUNTPOINT>` | Project report

Project (directory) quotas need entries in `/etc/projects` and `/etc/projid`:

```bash
echo '<PROJECT_ID>:<DIRECTORY>' | sudo tee -a /etc/projects
echo '<PROJECT_NAME>:<PROJECT_ID>' | sudo tee -a /etc/projid
sudo xfs_quota -x -c 'project -s <PROJECT_NAME>' <MOUNTPOINT>
sudo xfs_quota -x -c 'limit -p bhard=<HARD> <PROJECT_NAME>' <MOUNTPOINT>
```

---
## Backup with xfsdump
`xfsdump` dumps a **mounted** XFS file system; levels 0 to 9 give incremental dumps. Each dump is recorded in an inventory under `/var/lib/xfsdump`.

COMMAND | DESCRIPTION
---|---
`sudo xfsdump -l 0 -L <SESSION_LABEL> -M <MEDIA_LABEL> -f <DUMP_FILE> <MOUNTPOINT>` | Full (level 0) dump to a file
`sudo xfsdump -l 1 -L <SESSION_LABEL> -M <MEDIA_LABEL> -f <DUMP_FILE> <MOUNTPOINT>` | Incremental since the last lower-level dump
`sudo xfsdump -I` | Show the dump inventory
`sudo xfsrestore -t -f <DUMP_FILE>` | List contents only
`sudo xfsrestore -f <DUMP_FILE> <DESTINATION>` | Restore everything
`sudo xfsrestore -f <DUMP_FILE> -s <SUBTREE> <DESTINATION>` | Restore one subtree
`sudo xfsrestore -r -f <DUMP_FILE> <DESTINATION>` | Cumulative restore of an incremental series, oldest first
`sudo xfsrestore -i -f <DUMP_FILE> <DESTINATION>` | Interactive browse and select

Add `-F` to skip prompts in scripts.

---
## Freeze and Defragment
COMMAND | DESCRIPTION
---|---
`sudo xfs_freeze -f <MOUNTPOINT>` | Freeze writes (for a storage-level snapshot)
`sudo xfs_freeze -u <MOUNTPOINT>` | Unfreeze
`sudo xfs_fsr -v <MOUNTPOINT>` | Defragment (reorganise extents) while mounted
`sudo xfs_fsr -t <SECONDS> <MOUNTPOINT>` | Stop after a time limit
`sudo fstrim -v <MOUNTPOINT>` | Discard unused blocks on SSDs

LVM snapshots and most hypervisor snapshots freeze the file system for you; you rarely need `xfs_freeze` by hand.

---
## Troubleshooting
SYMPTOM | FIX
---|---
`mount: wrong fs type` or `Structure needs cleaning` | Run `xfs_repair -n` on the unmounted device, then repair
`xfs_repair` says the log is dirty | Mount and unmount to replay it; use `-L` only if the mount fails
Cannot mount a cloned disk: duplicate UUID | `mount -o nouuid <DEVICE> <DIR>` or `xfs_admin -U generate <DEVICE>`
`No space left on device` with free space showing | Check inodes with `df -i`; check quotas with `xfs_quota`
`xfs_growfs` reports nothing to grow | Extend the partition or LV first, then re-run
Want to shrink | Not supported: back up with `xfsdump`, recreate smaller, restore

---
## See Also
- [LVM](lvm.md)
- [RAID with mdadm](raid-mdadm.md)
- [Storage and Filesystems](storage-and-filesystems.md)
- [Mount](mount.md)

# LVM
The **Logical Volume Manager** adds a layer between disks and file systems. Physical volumes (PV) are pooled into volume groups (VG), and logical volumes (LV) are carved out of the pool. LVs can be grown online, snapshotted and moved between disks. Used by default on many Ubuntu server and RHEL installs, and by Proxmox ([Proxmox Storage](../proxmox/proxmox-storage.md)).

Documentation: [Red Hat LVM guide](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/configuring_and_managing_logical_volumes/index) · `man lvm`, `man lvcreate`, `man lvextend`

> **Verification:** commands follow the LVM man pages and the Red Hat guide. No command was executed. Test on a spare disk first. Resizing and shrinking can destroy data: back up before you start.

See also: [Storage and Filesystems](storage-and-filesystems.md) · [RAID with mdadm](raid-mdadm.md) · [Mount](mount.md) · [Linux](linux.md)

---
## Concepts
TERM | MEANING
---|---
PV | Physical volume: a disk or partition initialised for LVM
VG | Volume group: pool of one or more PVs
LV | Logical volume: a block device (`/dev/<VG>/<LV>`) that you format and mount
PE | Physical extent: allocation unit, 4 MiB by default
Thin pool | An LV that holds many thin (over-provisioned) LVs

Layout: **disk → PV → VG → LV → file system**.

---
## Inspect
COMMAND | DESCRIPTION
---|---
`sudo pvs` / `vgs` / `lvs` | One-line summaries
`sudo pvdisplay` / `vgdisplay` / `lvdisplay` | Full details
`sudo lvs -a -o +devices` | Include hidden LVs and which PV they sit on
`sudo pvs -o +pv_used` | Used space per PV
`lsblk -f` | Block device tree with file systems
`sudo vgs -o +vg_free_count,vg_extent_size` | Free extents

---
## Create
```bash
sudo pvcreate /dev/sdb /dev/sdc
sudo vgcreate vg_data /dev/sdb /dev/sdc
sudo lvcreate -L 100G -n lv_media vg_data
sudo mkfs.ext4 /dev/vg_data/lv_media
sudo mkdir -p /srv/media
sudo mount /dev/vg_data/lv_media /srv/media
```
COMMAND | DESCRIPTION
---|---
`sudo lvcreate -L 50G -n <LV> <VG>` | Fixed size
`sudo lvcreate -l 100%FREE -n <LV> <VG>` | All remaining space
`sudo lvcreate -l 50%VG -n <LV> <VG>` | Percentage of the whole VG
`sudo lvcreate -L 100G -i 2 -I 64 -n <LV> <VG>` | Striped across 2 PVs
`sudo lvcreate --type raid1 -m 1 -L 100G -n <LV> <VG>` | LVM-managed mirror (RAID1)

Add to `/etc/fstab` using the UUID (`blkid /dev/<VG>/<LV>`) or the `/dev/mapper/<VG>-<LV>` path:
```
/dev/mapper/vg_data-lv_media  /srv/media  ext4  defaults,nofail  0  2
```

---
## Extend Online
Grow a file system without unmounting.

```bash
# Add a new disk to the VG (if the VG has no free space)
sudo pvcreate /dev/sdd
sudo vgextend vg_data /dev/sdd

# Grow the LV and the file system in one step
sudo lvextend -r -L +50G /dev/vg_data/lv_media
# or use all free space
sudo lvextend -r -l +100%FREE /dev/vg_data/lv_media
```
`-r` (`--resizefs`) calls the right tool for the file system (`resize2fs`, `xfs_growfs`). Manual equivalents:

FILE SYSTEM | COMMAND
---|---
ext4 | `sudo resize2fs /dev/<VG>/<LV>`
XFS | `sudo xfs_growfs <MOUNTPOINT>` (takes the mount point, not the device)
Btrfs | `sudo btrfs filesystem resize max <MOUNTPOINT>`

**Disk got bigger** (VM disk resized): `sudo pvresize /dev/sdb`, then extend the LV as above. If the PV is on a partition, grow the partition first (`growpart /dev/sda 3` from `cloud-guest-utils`).

**Ubuntu Server default install** often leaves the root LV at half the disk:
```bash
sudo lvextend -r -l +100%FREE /dev/ubuntu-vg/ubuntu-lv
```

---
## Shrink (ext4 only, offline)
XFS cannot shrink. For ext4:
```bash
sudo umount /srv/media
sudo e2fsck -f /dev/vg_data/lv_media
sudo lvreduce -r -L 40G /dev/vg_data/lv_media
sudo mount /srv/media
```
`-r` shrinks the file system first, then the LV. Never run `lvreduce` below the data size.

---
## Move Data Off a Disk
```bash
sudo pvmove /dev/sdb               # move all extents to other PVs in the VG
sudo vgreduce vg_data /dev/sdb     # remove the empty PV from the VG
sudo pvremove /dev/sdb             # wipe the LVM label
```
`pvmove` works online and can be resumed with `pvmove` after an interruption.

---
## Snapshots
Copy-on-write snapshots give a point-in-time view, useful for consistent backups.

COMMAND | DESCRIPTION
---|---
`sudo lvcreate -s -L 5G -n snap_media /dev/vg_data/lv_media` | Classic snapshot, 5 GB for changes
`sudo mount -o ro /dev/vg_data/snap_media /mnt/snap` | Mount it read-only (add `nouuid` for XFS)
`sudo lvs` | Check `Data%`. At 100% the snapshot is invalid
`sudo lvextend -L +2G /dev/vg_data/snap_media` | Give a snapshot more room
`sudo lvconvert --merge /dev/vg_data/snap_media` | Roll the origin back to the snapshot (needs the origin to be unmounted, otherwise runs at next activation)
`sudo lvremove /dev/vg_data/snap_media` | Delete the snapshot

Remove snapshots when finished: an old snapshot slows writes to the origin.

Backup pattern:
```bash
sudo lvcreate -s -L 5G -n snap /dev/vg_data/lv_media
sudo mount -o ro /dev/vg_data/snap /mnt/snap
rsync -a /mnt/snap/ <BACKUP-TARGET>/
sudo umount /mnt/snap && sudo lvremove -y /dev/vg_data/snap
```

---
## Thin Provisioning
One pool, many volumes that only use space as it is written. Snapshots are cheap and need no preset size.

```bash
sudo lvcreate -L 500G --thinpool tpool vg_data
sudo lvcreate -V 200G --thin -n lv_vm1 vg_data/tpool
sudo lvcreate -V 200G --thin -n lv_vm2 vg_data/tpool     # over-provisioned: 400G of 500G, can exceed
sudo lvcreate -s -n lv_vm1_snap vg_data/lv_vm1           # thin snapshot, no size
```
COMMAND | DESCRIPTION
---|---
`sudo lvs -o +data_percent,metadata_percent` | Pool and metadata usage. **Watch both**
`sudo lvextend -L +100G vg_data/tpool` | Grow the pool data
`sudo lvextend --poolmetadatasize +1G vg_data/tpool` | Grow pool metadata
`sudo lvchange -ay -K vg_data/lv_vm1_snap` | Activate a thin snapshot (they are skipped by default)

A full thin pool freezes or corrupts the volumes. Do not over-provision without monitoring. Proxmox uses `local-lvm` as a thin pool ([Proxmox Storage](../proxmox/proxmox-storage.md)).

---
## Rename, Remove, Repair
COMMAND | DESCRIPTION
---|---
`sudo lvrename <VG> <OLD> <NEW>` | Rename an LV
`sudo vgrename <OLD> <NEW>` | Rename a VG (update fstab and the boot config)
`sudo lvremove /dev/<VG>/<LV>` | Delete an LV
`sudo vgremove <VG>` | Delete an empty VG
`sudo pvremove /dev/sdX` | Remove LVM label from a disk
`sudo vgchange -ay` | Activate all VGs
`sudo vgscan` / `lvscan` / `pvscan` | Rescan for LVM devices
`sudo vgcfgbackup` | Save metadata to `/etc/lvm/backup/`
`sudo vgcfgrestore <VG>` | Restore metadata from `/etc/lvm/archive/`
`sudo vgimport <VG>` / `vgexport <VG>` | Move a VG between machines

## Notes
- LVM metadata backups live in `/etc/lvm/backup` and `/etc/lvm/archive`. Copy them off the machine.
- LVM is not redundancy. Use [RAID with mdadm](raid-mdadm.md) underneath, or `--type raid1`, or ZFS or Btrfs for that.
- Add `nofail` to non-root mounts so a missing disk does not drop boot to emergency mode.

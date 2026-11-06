# Storage and Filesystems
Partitioning, creating file systems, checking disk health and measuring disk speed on Linux. Mounting is covered in [[mount]]; volume management in [[lvm]] and software RAID in [[raid-mdadm]].

Documentation: [smartmontools](https://www.smartmontools.org/wiki/TocDoc) · [fio](https://fio.readthedocs.io/en/latest/fio_doc.html) · [Btrfs docs](https://btrfs.readthedocs.io/en/latest/)

> **Verification:** commands follow the man pages and common practice. No command was executed. `mkfs`, `parted`, `wipefs` and `fio` write tests destroy data on the target. Check the device name with `lsblk` every time.

See also: [[lvm]] · [[raid-mdadm]] · [[mount]] · [[nfs]] · [[performance-troubleshooting]] · [[linux]]

---
## Identify Disks
COMMAND | DESCRIPTION
---|---
`lsblk -f` | Disks, partitions, file systems, UUIDs, mount points
`lsblk -o NAME,SIZE,TYPE,MODEL,SERIAL,ROTA` | Model and serial (`ROTA=1` is a spinning disk)
`sudo blkid` | UUIDs and file system types
`sudo fdisk -l` | Partition tables of all disks
`ls -l /dev/disk/by-id/` | Stable names. Use these in scripts and ZFS/RAID setups
`sudo smartctl --scan` | Disks smartctl can see
`df -hT` / `df -i` | Space and inodes per file system

---
## Partition
Use GPT on anything new. `parted` and `sgdisk` are scriptable; `fdisk` and `cfdisk` are interactive.

```bash
sudo parted /dev/sdb --script mklabel gpt mkpart data ext4 1MiB 100%
sudo parted /dev/sdb print
```
COMMAND | DESCRIPTION
---|---
`sudo fdisk /dev/sdb` | Interactive: `g` new GPT, `n` new partition, `t` type, `w` write
`sudo cfdisk /dev/sdb` | Menu-driven
`sudo sgdisk -n 1:0:0 -t 1:8300 /dev/sdb` | One Linux partition using the whole disk
`sudo sgdisk -t 1:8e00 /dev/sdb` | Set type to Linux LVM
`sudo sgdisk -t 1:fd00 /dev/sdb` | Set type to Linux RAID
`sudo sgdisk -Z /dev/sdb` | Destroy GPT and MBR structures
`sudo partprobe /dev/sdb` | Make the kernel re-read the table
`sudo wipefs -a /dev/sdb` | Remove all file system and RAID signatures
`sudo growpart /dev/sda 1` | Grow a partition into new space (`cloud-guest-utils`)

---
## Create File Systems
COMMAND | DESCRIPTION
---|---
`sudo mkfs.ext4 -L data /dev/sdb1` | ext4 with a label
`sudo mkfs.xfs -L data /dev/sdb1` | XFS (add `-f` to overwrite)
`sudo mkfs.btrfs -L data /dev/sdb1` | Btrfs
`sudo mkfs.vfat -F 32 /dev/sdb1` | FAT32 (USB sticks, EFI partition)
`sudo mkfs.exfat /dev/sdb1` | exFAT (needs `exfatprogs`)
`sudo mkswap /dev/sdb2 && sudo swapon /dev/sdb2` | Swap partition
`sudo tune2fs -m 1 /dev/sdb1` | Lower ext4 root-reserved blocks from 5% to 1% on a data disk
`sudo e2label /dev/sdb1 data` / `sudo xfs_admin -L data /dev/sdb1` | Change a label

Mount permanently with the UUID from `blkid`:
```
UUID=<UUID>  /srv/data  ext4  defaults,nofail  0  2
```
Test it with `sudo mount -a` before rebooting. Details in [[mount]].

---
## Choosing a File System
FS | GOOD FOR | NOTES
---|---|---
ext4 | General purpose, root disks | Mature, can shrink and grow
XFS | Large files, big arrays, RHEL default | Grow only, cannot shrink
Btrfs | Snapshots, checksums, compression | Built-in RAID1 and RAID10 are fine; RAID5/6 is not recommended
ZFS | Pools, snapshots, send/receive | Out of tree on Linux. See [[proxmox-storage]]
FAT32 / exFAT | Removable media, EFI | No permissions or journaling

---
## Check and Repair
Unmount first (or boot rescue media for the root file system).

COMMAND | DESCRIPTION
---|---
`sudo fsck -f /dev/sdb1` | Check and repair ext4 (add `-n` to check only)
`sudo e2fsck -fy /dev/sdb1` | ext4, answer yes to all repairs
`sudo xfs_repair /dev/sdb1` | XFS repair (`-n` to dry run)
`sudo btrfs check /dev/sdb1` | Btrfs read-only check. `--repair` is a last resort
`sudo btrfs scrub start -B /mnt/data` | Verify checksums on a mounted Btrfs
`sudo dumpe2fs -h /dev/sdb1` | ext4 superblock info
`sudo xfs_info /mnt/data` | XFS geometry

---
## Btrfs Basics
COMMAND | DESCRIPTION
---|---
`sudo btrfs subvolume create /mnt/data/@docs` | Create a subvolume
`sudo btrfs subvolume list /mnt/data` | List subvolumes
`sudo btrfs subvolume snapshot -r /mnt/data/@docs /mnt/data/@docs-snap` | Read-only snapshot
`sudo btrfs subvolume delete /mnt/data/@docs-snap` | Delete a snapshot
`sudo btrfs filesystem usage /mnt/data` | Real space use (plain `df` misleads on Btrfs)
`sudo btrfs device add /dev/sdc /mnt/data` | Add a disk to the pool
`sudo btrfs balance start -dusage=50 /mnt/data` | Rebalance data chunks that are under 50% full

Mount option for transparent compression: `compress=zstd`.

---
## SMART Health (smartmontools)
```bash
sudo apt install smartmontools
```
COMMAND | DESCRIPTION
---|---
`sudo smartctl -H /dev/sdb` | Overall verdict (`PASSED` is not a guarantee)
`sudo smartctl -a /dev/sdb` | Full report
`sudo smartctl -x /dev/sdb` | Everything, including error logs
`sudo smartctl -t short /dev/sdb` | Short self-test (about 2 minutes)
`sudo smartctl -t long /dev/sdb` | Extended self-test (hours, runs in the background)
`sudo smartctl -l selftest /dev/sdb` | Self-test results
`sudo smartctl -a -d sat /dev/sdb` | Disk behind a USB or SATA bridge
`sudo smartctl -a /dev/nvme0` | NVMe disk
`sudo nvme smart-log /dev/nvme0` | NVMe health with `nvme-cli`

Attributes worth watching on SATA disks:

ATTRIBUTE | MEANING
---|---
`Reallocated_Sector_Ct` (5) | Bad sectors remapped. Rising means the disk is failing
`Current_Pending_Sector` (197) | Sectors waiting to be remapped. Not zero is a warning
`Offline_Uncorrectable` (198) | Unreadable sectors
`UDMA_CRC_Error_Count` (199) | Cable or connector problem
`Temperature_Celsius` (194) | Keep under about 50 C
`Percentage Used`, `Media and Data Integrity Errors` | NVMe wear and errors

Monitor with the `smartd` daemon. In `/etc/smartd.conf`:
```
DEVICESCAN -a -o on -S on -n standby,q -s (S/../.././02|L/../../6/03) -m admin@example.com
```
Then `sudo systemctl enable --now smartmontools` (Debian/Ubuntu) or `smartd` (RHEL).

---
## Performance: iostat and iotop
Part of `sysstat` (`sudo apt install sysstat`).

COMMAND | DESCRIPTION
---|---
`iostat -xz 1` | Per-disk utilisation, latency and queue each second
`iostat -xz 1 -p sdb` | One disk and its partitions
`sudo iotop -oPa` | Processes doing I/O, accumulated
`pidstat -d 1` | Per-process disk I/O
`vmstat 1` | `wa` column is CPU time waiting on I/O
`sudo hdparm -tT /dev/sdb` | Quick sequential read test of a hard disk
`dd if=/dev/zero of=/srv/data/test bs=1M count=1024 oflag=direct status=progress` | Crude write test. Delete the file afterwards

Read `iostat -x`: `r_await` / `w_await` are average latency in ms, `aqu-sz` is the queue depth, `%util` near 100 on a spinning disk means saturated (not a reliable signal on NVMe).

---
## Benchmark with fio
Test on a file on the file system you care about, not on a raw device that holds data.

COMMAND | DESCRIPTION
---|---
`fio --name=seqwrite --filename=/srv/data/fio.tmp --rw=write --bs=1M --size=2G --direct=1 --ioengine=libaio --iodepth=16` | Sequential write throughput
`fio --name=seqread --filename=/srv/data/fio.tmp --rw=read --bs=1M --size=2G --direct=1 --ioengine=libaio --iodepth=16` | Sequential read throughput
`fio --name=randread --filename=/srv/data/fio.tmp --rw=randread --bs=4k --size=2G --direct=1 --ioengine=libaio --iodepth=32 --runtime=60 --time_based` | Random 4k read IOPS
`fio --name=randrw --filename=/srv/data/fio.tmp --rw=randrw --rwmixread=70 --bs=4k --size=2G --direct=1 --ioengine=libaio --iodepth=32 --runtime=60 --time_based` | Mixed 70/30 workload
`fio --name=fsync --filename=/srv/data/fio.tmp --rw=write --bs=4k --size=256M --fsync=1` | Sync write latency (what databases and etcd feel)
`rm /srv/data/fio.tmp` | Clean up

---
## Space Problems
COMMAND | DESCRIPTION
---|---
`sudo du -xh --max-depth=1 / \| sort -h \| tail` | Biggest directories on the root file system
`sudo ncdu -x /` | Interactive usage browser
`df -i` | Out of inodes with free space left? Many tiny files
`sudo lsof +L1` | Deleted files still held open by a process
`sudo journalctl --vacuum-size=500M` | Shrink the journal ([[systemd]])
`sudo fstrim -av` | Trim SSDs (a timer `fstrim.timer` normally does this weekly)

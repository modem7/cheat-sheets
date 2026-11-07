# RAID with mdadm
`mdadm` manages Linux software RAID (the `md` driver). It builds arrays from whole disks or partitions, watches their health and rebuilds after a disk fails. RAID protects against disk failure only; it is **not a backup**.

Documentation: [Linux RAID wiki](https://raid.wiki.kernel.org/) · `man mdadm`, `man mdadm.conf`

> **Verification:** commands follow the mdadm man page and the Linux RAID wiki. No command was executed. Most of these commands change or destroy disks. Run them on spare disks first and double check device names with `lsblk`.

See also: [LVM](lvm.md) · [Storage and Filesystems](storage-and-filesystems.md) · [XFS](xfs.md) · [Mount](mount.md) · [Linux](linux.md)

---
## RAID Levels
LEVEL | MIN DISKS | SURVIVES | USABLE | NOTES
---|---|---|---|---
RAID 0 | 2 | Nothing | All | Striping, speed only
RAID 1 | 2 | N-1 failures | One disk | Mirror
RAID 5 | 3 | 1 failure | N-1 | Parity. Risky on large disks (long rebuild)
RAID 6 | 4 | 2 failures | N-2 | Double parity
RAID 10 | 4 | 1 per mirror | N/2 | Stripe of mirrors, fast rebuild

---
## Inspect
COMMAND | DESCRIPTION
---|---
`cat /proc/mdstat` | Live state of all arrays and rebuild progress
`sudo mdadm --detail /dev/md0` | Array details, state, failed devices
`sudo mdadm --examine /dev/sdb1` | Superblock on a member disk
`sudo mdadm --detail --scan` | Array lines for `mdadm.conf`
`lsblk -f` | Arrays under their disks
`watch -n 2 cat /proc/mdstat` | Follow a rebuild

State flags in `/proc/mdstat`: `[UU]` all members up, `[U_]` one missing, `(F)` failed, `(S)` spare, `recovery` or `resync` with a percentage.

---
## Create an Array
```bash
# RAID 1 from two partitions
sudo mdadm --create /dev/md0 --level=1 --raid-devices=2 /dev/sdb1 /dev/sdc1

# RAID 5 with a hot spare
sudo mdadm --create /dev/md0 --level=5 --raid-devices=3 --spare-devices=1 \
  /dev/sdb1 /dev/sdc1 /dev/sdd1 /dev/sde1

# RAID 10
sudo mdadm --create /dev/md0 --level=10 --raid-devices=4 /dev/sd[b-e]1
```
Then format, mount and persist:
```bash
sudo mkfs.ext4 /dev/md0
sudo mkdir -p /srv/data
sudo mount /dev/md0 /srv/data

# Save the config (Debian/Ubuntu)
sudo mdadm --detail --scan | sudo tee -a /etc/mdadm/mdadm.conf
sudo update-initramfs -u

# fstab with UUID from: blkid /dev/md0
echo 'UUID=<UUID>  /srv/data  ext4  defaults,nofail  0  2' | sudo tee -a /etc/fstab
```
On RHEL the config file is `/etc/mdadm.conf` and the initramfs command is `dracut -f`.

The array syncs in the background and can be used straight away. Check progress in `/proc/mdstat`.

---
## Monitor
Email on events (set `MAILADDR` in `mdadm.conf`):
```
MAILADDR admin@example.com
```
COMMAND | DESCRIPTION
---|---
`sudo mdadm --monitor --scan --daemonise --mail=<ADDRESS>` | Run the monitor by hand
`sudo systemctl status mdmonitor` | Monitor service on RHEL (`mdadm` on Debian/Ubuntu)
`sudo mdadm --monitor --scan --oneshot --test` | Send a test alert for each array
`cat /sys/block/md0/md/mismatch_cnt` | Mismatches found by the last scrub
`echo check \| sudo tee /sys/block/md0/md/sync_action` | Start a scrub (read and compare)
`echo repair \| sudo tee /sys/block/md0/md/sync_action` | Scrub and fix mismatches

Debian runs a monthly scrub (`/usr/share/mdadm/checkarray`). Also watch the disks with SMART, see [Storage and Filesystems](storage-and-filesystems.md).

---
## Replace a Failed Disk
1. Identify the failed member:
```bash
cat /proc/mdstat
sudo mdadm --detail /dev/md0
```
2. If it is not already marked failed, fail and remove it:
```bash
sudo mdadm /dev/md0 --fail /dev/sdc1
sudo mdadm /dev/md0 --remove /dev/sdc1
```
3. Physically replace the disk. Confirm the new device name with `lsblk` and `smartctl -i`.
4. Copy the partition table from a healthy member to the new disk, then randomise the GUID:
```bash
sudo sfdisk -d /dev/sdb | sudo sfdisk /dev/sdc       # MBR or GPT dump and restore
sudo sgdisk -G /dev/sdc                               # new GUIDs (GPT)
```
Or use `sgdisk -R=/dev/sdc /dev/sdb` (replicate, careful with the argument order: the target is the `-R` value).
5. Add it to the array and watch the rebuild:
```bash
sudo mdadm /dev/md0 --add /dev/sdc1
watch cat /proc/mdstat
```
6. Update `mdadm.conf` if anything changed and, on a boot array, reinstall the bootloader on the new disk (`sudo grub-install /dev/sdc`).

A hot spare (`--add` on a healthy array) takes over automatically.

---
## Manage Arrays
COMMAND | DESCRIPTION
---|---
`sudo mdadm --add /dev/md0 /dev/sdX1` | Add a disk (spare if the array is healthy)
`sudo mdadm --grow /dev/md0 --raid-devices=4` | Add a disk to RAID 5/6 and reshape
`sudo mdadm --grow /dev/md0 --size=max` | Use bigger member disks after all are replaced
`sudo mdadm --stop /dev/md0` | Stop an array (unmount first)
`sudo mdadm --assemble --scan` | Assemble every array found
`sudo mdadm --assemble /dev/md0 /dev/sdb1 /dev/sdc1` | Assemble one by hand
`sudo mdadm --assemble --force /dev/md0 <DEVICES>` | Force assembly of a degraded array (last resort)
`sudo mdadm --zero-superblock /dev/sdb1` | Wipe RAID metadata from a former member
`sudo mdadm --readonly /dev/md0` | Mark read-only

After `--grow`, grow the file system too (`resize2fs /dev/md0` or `xfs_growfs`). With LVM on top, `pvresize /dev/md0` first ([LVM](lvm.md)).

## Delete an Array
```bash
sudo umount /srv/data
sudo mdadm --stop /dev/md0
sudo mdadm --zero-superblock /dev/sdb1 /dev/sdc1
# remove its line from /etc/mdadm/mdadm.conf and /etc/fstab, then:
sudo update-initramfs -u
```

## Notes
- An array renamed to `md127` after reboot means `mdadm.conf` is missing or stale. Re-run the `--detail --scan` step and rebuild the initramfs.
- Replace disks in an ageing RAID 5 one at a time and check SMART on the survivors first. A second failure during rebuild loses the array.
- Use whole-disk arrays only if you are sure no other tool will write a partition table to them. Partitions that are slightly smaller than the disk make it easier to use a replacement of a different make.

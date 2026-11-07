# NAS Operating Systems Compared
A short comparison of the NAS platforms covered in this repository: TrueNAS Community Edition, Unraid, OpenMediaVault and UniFi NAS. Use it to pick one; the linked sheets hold the commands.

See also: [TrueNAS Community Edition](truenas-community-edition.md) · [Unraid](unraid.md) · [OpenMediaVault](openmediavault.md) · [UniFi NAS](unifi-nas.md) · [RAID with mdadm](../linux/raid-mdadm.md) · [Storage and Filesystems](../linux/storage-and-filesystems.md) · [Backup Strategy](../backup/backup.md)

## Comparison
TOPIC | TRUENAS CE | UNRAID | OPENMEDIAVAULT | UNIFI NAS
---|---|---|---|---
Base | Debian | Slackware-style, runs from USB flash | Debian | Appliance firmware (UniFi OS)
Pool model | ZFS pools (stripe, mirror, RAIDZ1-3, dRAID) | Parity array of single-disk filesystems plus pools | Whatever Debian supports: ext4, XFS, Btrfs, mdadm RAID, plugins | RAID 1/5/6/10 groups in pools
Mixed disk sizes | Poor within a vdev | Good (parity disk must be the largest) | Depends on layout | Same size within a group
Expansion | RAIDZ expansion, one disk at a time | Add a disk to the array | Depends on layout | Rebuild takes hours
App model | Docker-based apps, Compose YAML, KVM VMs | Docker via Community Applications, KVM VMs | Docker through omv-extras plugins | None documented
Shell access | Supported shell, UI-only config | Root SSH | Full Debian | Not documented
Licence and cost | Free; Enterprise is separate | Paid licence (Starter, Unleashed, Lifetime) | Free | Hardware purchase
Best fit | Data integrity, snapshots, replication | Mixed disks and media servers | Light, flexible NAS on any hardware | Simple managed storage in a UniFi network

Figures are as documented in the individual sheets; items marked unverified there are unverified here.

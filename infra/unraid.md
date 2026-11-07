# Unraid
Unraid is a commercial NAS and virtualisation OS that runs from a licensed USB flash drive. It pools mixed-size disks in a parity array and runs Docker containers and KVM virtual machines.

Documentation: [Unraid Docs](https://docs.unraid.net/)
Project: [Unraid](https://unraid.net/)

See also: [TrueNAS Community Edition](truenas-community-edition.md) · [OpenMediaVault](openmediavault.md) · [UniFi NAS](unifi-nas.md) · [NAS Operating Systems Compared](nas-os-comparison.md) · [RAID with mdadm](../linux/raid-mdadm.md) · [NFS](../linux/nfs.md) · [Docker](../docker/docker.md) · [Docker Compose](../docker/docker-compose.md) · [Backup Strategy](../backup/backup.md)

## Version and Licence
FACT | DETAIL
---|---
Latest stable | 7.3.4 (2026-10-22); 7.4.0 is a release candidate
Licence tiers | Starter (6 devices), Unleashed (unlimited), Lifetime; 30-day trial without a card
Updates | A purchase includes one year of updates; an optional paid extension renews them, and you keep your version without it
Boot device | USB flash drive with a unique GUID; the licence is tied to the GUID
Flash replacement | **Tools > Registration > Replace Key** (limited to once per 12 months)

## Install
1. Write the flash with the Unraid USB Creator (manual: FAT32, label `UNRAID`).
2. Boot the server from it and open the web UI.
3. Assign parity and data disks, optionally a cache pool, then start the array.
4. Back up the flash drive before every OS update.

## Storage Model
AREA | DETAIL
---|---
Array | 1 or 2 parity disks plus data disks; each data disk is its own filesystem (XFS default, BTRFS or ZFS selectable)
Parity rule | Parity must be at least as large as the largest data disk
Pools | BTRFS (default), ZFS (6.12+) or XFS (single device); used for cache, appdata, VMs
Mover | Moves files between pool and array on a schedule (array and pool only)
User shares | `/mnt/user/<SHARE>` merges all disks; disk shares at `/mnt/diskN` (off by default); pools at `/mnt/<POOL>`
Allocation | High-water (recommended), most-free, fill-up; split level overrides minimum free space
Added disks | Data disks added to a parity array are cleared first, then formatted

Never copy or move between a user share and a disk share in the same operation (data loss risk).

## Shares and Access
- Root has web UI and SSH access but cannot use SMB, NFS or FTP. Share users have no SSH or web UI.
- Shares can be exported over SMB and NFS. Per-share security modes (Secure, Private, Public) are unverified here.

## Docker, Apps and VMs
- Docker uses the Docker tab; templates come from the Community Applications plugin. Appdata lives in the `appdata` share.
- Unraid does not natively support Docker Compose (a community plugin exists; unverified).
- VMs use libvirt and QEMU. Passthrough bindings are stored in `/boot/config/vfio-pci.cfg`. The boot USB cannot be passed through.

## Backups
- Parity protects against disk failure only; it is not a backup. Use [restic](../backup/restic.md), [rsync](../backup/rsync.md) or [rclone](../backup/rclone.md) to another machine.
- Unraid Connect can back up the flash (latest copy only; excludes passwords and WireGuard keys).
- ZFS pools support snapshots (not checked in detail).

## Updates
COMMAND | DESCRIPTION
---|---
**Tools > Update OS** | Install the latest release (back up flash first)
**Tools > Downgrade OS** | Roll back, or manually move `bz*` files into `previous/` (upgraded ZFS pools can block rollback)
**Tools > New Config** | Rebuild array assignments; not for rebuilding a failed disk. Undo by renaming `config/super.old` to `super.dat`
**Settings > Scheduler** | Schedule parity checks

## CLI
COMMAND | DESCRIPTION
---|---
`smartctl -a /dev/sdX` | SMART report
`hdparm` | Drive settings
`powerdown` | Clean shutdown (documented on the CLI page; a forum post reports a deprecation warning, unverified)
`unraid-api status` | Unraid API service (7.x); subcommands `start`, `stop`, `restart`, `logs`, `config`, `apikey`, `sso`, `report` are documented. `status` is unverified
`tail /var/log/syslog` | System log (lives in RAM)

Not found in the docs, so omitted: `mdcmd`, a `mover` command and a diagnostics CLI. Capture diagnostics from the web UI.

## Gotchas
SYMPTOM | FIX
---|---
Parity check starts after boot | Caused by an unclean shutdown (power loss, open SSH session, flash failure); non-correcting by default
Array refuses to start | Device count is over the licence limit
Disk larger than parity | Use the documented parity swap procedure

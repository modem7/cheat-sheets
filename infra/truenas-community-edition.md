# TrueNAS Community Edition
TrueNAS Community Edition (formerly TrueNAS SCALE) is a Debian-based, open source NAS platform with ZFS, Docker-based apps and KVM virtual machines. Searches for "TrueNAS SCALE" land here.

Documentation: [TrueNAS Documentation Hub](https://www.truenas.com/docs/) · [Community Edition 25.10 docs](https://www.truenas.com/docs/scale/25.10/)
Project: [TrueNAS](https://www.truenas.com/)

## Naming and Releases
FACT | DETAIL
---|---
Rename | SCALE became "TrueNAS Community Edition" with 25.04 "Fangtooth" (April 2025)
Latest stable | 25.10 "Goldeye" (25.10.8 on 2026-11-05); 26 and 27 are pre-release, with no codenames
Version scheme | `YY.MM`, roughly April and October releases
Enterprise | Separate licensed and supported product on the same code base, adding HA and support
CORE | FreeBSD edition, no longer under active development
Docs URLs | Still under `/docs/scale/` (for example `/docs/scale/25.10/`)
Minimum hardware | 2-core x86_64, 8 GB RAM, 16 GB SSD boot device, two identical data disks

See also: [NAS Operating Systems Compared](nas-os-comparison.md) · [Unraid](unraid.md) · [OpenMediaVault](openmediavault.md) · [UniFi NAS](unifi-nas.md) · [ZFS Snapshots and Replication](../backup/zfs-snapshots-backup.md) · [NFS](../linux/nfs.md) · [Docker](../docker/docker.md) · [Proxmox Storage](../proxmox/proxmox-storage.md)

---
## Install and First Setup
1. Write the ISO to a USB drive and install to a dedicated boot device (SSD).
2. Create the admin user in the installer (`truenas_admin` is the default name). Root login is deprecated.
3. Use an HBA or a RAID card in passthrough/JBOD mode, never hardware RAID. ECC RAM is recommended.
4. Create a pool, then one dataset per share or app.

## Pool Layouts
LAYOUT | NOTES
---|---
Stripe | No redundancy
Mirror | Two or more disks, any one can fail
RAIDZ1 / RAIDZ2 / RAIDZ3 | One, two or three parity disks per vdev
dRAID1 to dRAID3 | Distributed spares, for large pools
RAIDZ expansion | Add disks to a RAIDZ vdev one at a time (docs credit 24.10 with introducing it)

## UI Paths (25.10)
TASK | PATH
---|---
Shell | **System Settings > Shell**
Update | **System > Update**
Boot environments | **System > Boot Environment**
Save config | **System > Advanced Settings > Manage Configuration** (tick Export Password Secret Seed)
Periodic snapshots | **Data Protection > Periodic Snapshot Tasks**
Replication | **Data Protection > Replication Tasks**
Cloud sync | **Data Protection > Cloud Sync Tasks** (unverified)
Custom app | **Apps > Discover > Custom App**, or the menu **Install via YAML** for a Docker Compose file
Scrub | Weekly scrub is created automatically per pool; **Scrub Now** on the Storage Health widget

## ACME Certificates
1. Create DNS credentials (**Credentials > Certificates > ACME DNS-Authenticators > Add**).
2. Create a signing request (**Certificate Signing Requests > Add**).
3. Set the email address for your current user (root: system email).
4. On the CSR, use the menu **Create ACME Certificate**.
5. Switch the GUI certificate (**System > General Settings > GUI > Settings > GUI SSL Certificate**).

In 25.10 the Certificate Authority feature was removed (CSRs and imports remain).

## ZFS Commands
Run from a shell (**System Settings > Shell**, or SSH once enabled for the user). Standard OpenZFS commands; not individually checked against TrueNAS docs (unverified on 25.10).

COMMAND | DESCRIPTION
---|---
`zpool status` | Pool health and any errors
`zpool list` | Pool capacity
`zpool status -x` | Only report unhealthy pools
`zpool scrub <POOL>` | Start a scrub
`zfs list` | Datasets and usage
`zfs list -t snapshot` | Snapshots
`zfs snapshot <POOL>/<DATASET>@<NAME>` | Create a snapshot
`zfs rollback <POOL>/<DATASET>@<NAME>` | Roll back to a snapshot (discards newer changes)
`zfs destroy <POOL>/<DATASET>@<NAME>` | Delete a snapshot (data loss)
`zfs get compressratio <POOL>/<DATASET>` | Compression ratio
`zpool iostat -v 5` | Live per-disk I/O

## Middleware CLI
COMMAND | DESCRIPTION
---|---
`midclt call system.version` | Installed version (the `system.version` method exists in API v25.10; exact `midclt call` form unverified)
`cli` | TrueNAS CLI, exit with `quit` (older CLI reference; unverified on 25.10)

Only the web UI and API are supported for configuration changes. Installing packages with `apt` or running a separate Docker install can break the system.

## Disk Health
COMMAND | DESCRIPTION
---|---
`lsblk -o NAME,SIZE,MODEL,SERIAL` | Map devices to serial numbers
`smartctl -a /dev/sdX` | Full SMART report
`smartctl -t short /dev/sdX` | Start a short self-test
`sensors` | Temperatures

In 25.10 the SMART test scheduler UI was removed; existing tests became cron tasks and smartmontools remains installed.

## Good Practice
- Keep a scrub schedule (monthly) and SMART tests (weekly short, monthly long).
- Snapshots are not backups. Replicate to another machine or offsite.
- Do not fill a pool above about 80%.
- Use a dataset per share or app so you can snapshot and set quotas separately.

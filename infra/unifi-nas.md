# UniFi NAS
UniFi NAS (the UNAS line) is Ubiquiti's network storage range, managed through UniFi OS and the UniFi Drive application. It is an appliance: shares, RAID and backups, but no documented shell, containers or VMs.

Documentation: [UniFi Help Center](https://help.ui.com/) · [Tech Specs](https://techspecs.ui.com/)
Project: [Ubiquiti Store](https://store.ui.com/us/en/category/all-unifi-nas)

See also: [TrueNAS Community Edition](truenas-community-edition.md) · [Unraid](unraid.md) · [OpenMediaVault](openmediavault.md) · [NAS Operating Systems Compared](nas-os-comparison.md) · [NFS](../linux/nfs.md) · [rsync](../backup/rsync.md) · [Backup Strategy](../backup/backup.md) · [VLANs](../homelab/vlans.md)

## Models
MODEL | BAYS | NOTES
---|---|---
UNAS 2 | 2 x 3.5" HDD | 2.5 GbE; RAID 1 only
UNAS 4 | 4 | 2 NVMe cache slots, 2.5 GbE
UNAS Pro | 7 (HDD or SSD) | 10G SFP+ plus 1 GbE, needs UniFi Drive 1.16.0 or later; formerly called "UniFi NAS Pro"
UNAS Pro 4 | 4 | 2 NVMe cache slots, 10G
UNAS Pro 8 | 8 | 2 M.2 NVMe, 16 GB RAM, 10G
Enterprise NAS | 16 | Dual 25G

Prices vary by store and region; check the store. CPU and RAM for the smaller models are not documented in what was read.

## Storage
FACT | DETAIL
---|---
Pool setup | **Settings > Control Plane > Storage > Create Storage Pool**
Hierarchy | A pool holds RAID groups; a group needs same-size drives of one type (no HDD and SSD mix)
RAID levels | RAID 1 (UNAS 2), RAID 5, RAID 6, RAID 10 (one group per pool)
Groups per pool | One on UNAS 2, UNAS 4 and Pro 4; several on UNAS Pro and Pro 8
Hot spare | An odd drive count leaves the last drive as spare; a global hot spare is UNAS Pro only
Encryption | Per pool, with its own key; losing the key means permanent loss of access
Filesystem | Ubiquiti articles say both Btrfs and ZFS; unresolved, so treat as unverified
Snapshots | Opt-in per Personal or Shared Drive; schedule and retention not documented

## Shares and Access
- Personal drives (per user) and Shared drives (**UniFi Drive > All Files**).
- Access by Site Manager, the UniFi Endpoint app, SMB (optional AD), NFS (Linux) and the local web UI by IP.
- WebDAV, iSCSI and FTP are not listed.
- Whether a UniFi OS console is required is not stated; the docs assume UniFi OS and a UI account.

## Backups
DESTINATION | NOTES
---|---
Another UNAS, SMB/CIFS | Network targets
Google Drive, OneDrive, Dropbox | Cloud drives
S3, Backblaze B2, Wasabi | Object storage
rsync | Pull or serve
Local USB | exFAT, FAT32 or ext4

## SSH and CLI
- No UNAS shell is documented. The only SSH step in the UNAS articles targets the gateway, enabled at **Control Plane > Console > Advanced > SSH**.
- Ubiquiti says not to use SSH unless support asks. Containers, VMs, package installs and a CLI are not documented (treat as not possible).

## Gotchas
- Restoring pools needs all drives from all earlier pools, plus a UI account backup.
- Adding or replacing drives triggers a rebuild that takes hours.
- Firmware update steps and config backup are not documented here (unverified).

## See Also
- [UniFi](../unifi/unifi.md)
- [UniFi Backups and Migration](../unifi/unifi-backups.md)

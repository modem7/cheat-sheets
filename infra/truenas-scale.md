# TrueNAS Scale
TrueNAS SCALE is a Debian-based open source NAS platform with ZFS, apps and VMs.

Documentation: [TrueNAS Docs](https://www.truenas.com/docs/scale/)

---
## ACME Certificates
1. Create DNS Credentials (**Credentials > Certificates > ACME DNS-Authenticators**)
2. Create Signing Request (CSR)
3. Configure the email address for your current user (in case of root, info)
4. Create the ACME Certificate from the CSR
5. Switch the Admin Certificate (**System > General > GUI > Settings**)

---
## ZFS Commands
Run from a shell (**System > Shell**, or SSH).

COMMAND | DESCRIPTION
---|---
`zpool status` | Pool health and any errors
`zpool list` | Pool capacity
`zpool status -x` | Only report unhealthy pools
`zpool scrub <POOL>` | Start a scrub
`zfs list` | Datasets and usage
`zfs list -t snapshot` | Snapshots
`zfs snapshot <POOL>/<DATASET>@<NAME>` | Create a snapshot
`zfs rollback <POOL>/<DATASET>@<NAME>` | Roll back to a snapshot
`zfs destroy <POOL>/<DATASET>@<NAME>` | Delete a snapshot
`zfs get compressratio <POOL>/<DATASET>` | Compression ratio
`zpool iostat -v 5` | Live per-disk I/O

## Disk Health
COMMAND | DESCRIPTION
---|---
`lsblk -o NAME,SIZE,MODEL,SERIAL` | Map devices to serial numbers
`smartctl -a /dev/sdX` | Full SMART report
`smartctl -t short /dev/sdX` | Start a short self-test
`sensors` | Temperatures

## Good Practice
- Keep a scrub schedule (monthly) and SMART tests (weekly short, monthly long).
- Snapshots are not backups. Replicate to another machine or offsite.
- Do not fill a pool above about 80%.
- Use a dataset per share or app so you can snapshot and set quotas separately.

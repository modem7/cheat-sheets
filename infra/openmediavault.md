# OpenMediaVault
OpenMediaVault (OMV) is a free, Debian-based NAS operating system with a web UI for disks, file systems, shares and services, extended by plugins such as omv-extras.

Documentation: [OpenMediaVault Docs](https://docs.openmediavault.org/en/stable/)
Project: [OpenMediaVault](https://www.openmediavault.org/) · [omv-extras installer](https://github.com/OpenMediaVault-Plugin-Developers/installScript)

See also: [TrueNAS Community Edition](truenas-community-edition.md) · [Unraid](unraid.md) · [UniFi NAS](unifi-nas.md) · [NAS Operating Systems Compared](nas-os-comparison.md) · [RAID with mdadm](../linux/raid-mdadm.md) · [LVM](../linux/lvm.md) · [NFS](../linux/nfs.md) · [Docker Compose](../docker/docker-compose.md) · [rsync](../backup/rsync.md) · [NUT (Network UPS Tools)](../homelab/nut-ups.md)

## Version and Install
FACT | DETAIL
---|---
Current line | OMV 8 "Synchrony" on Debian 13 (changelog entry 8.6.1-1, 2026-10-30)
Previous line | OMV 7 "Sandworm" on Debian 12; end-of-life date unverified
Install methods | ISO to a dedicated drive (recommended on x86); USB stick, SD card or existing Debian install (the ARM route)
Not supported | LXC and other containers
Default web login | `admin` / `openmediavault` (change it straight away)

First steps from the install docs: note the IP on the console login screen, disable root SSH under **Services > SSH**, and create a non-privileged user in the `_ssh` and `sudo` groups.

## Storage and Shares
AREA | DETAIL
---|---
Docs sections | Disks (power, wipe), SMART (settings, scheduled tests), RAID (overview, grow), Filesystems, Shared Folders (permissions, ACLs)
Service docs | Samba, FTP, NFS, SSH, rsync (jobs and server)
RAID, ZFS, LVM, mergerfs, SnapRAID | Via plugins and mdadm; levels and plugin names not verified here (unverified)
Mount paths | `/srv/dev-disk-by-uuid-<UUID>` style (unverified)

## omv-extras and Docker
omv-extras is installed with a script from the plugin developers' GitHub (pipes a download into a root shell, so read it first). The command is on the installer page; the compose plugin and Portainer steps are not verified here (unverified).

## CLI
COMMAND | DESCRIPTION
---|---
`omv-upgrade` | Upgrade packages (run after an ISO install)
`omv-release-upgrade` | Move to the next release (referenced in the changelog; not found in the docs)
`omv-salt deploy run <MODULE>` | Re-deploy one configuration module, for example `nginx`, `samba`, `nfs`, `ssh`, `fstab`
`omv-salt stage run prepare` / `omv-salt stage run deploy` | Prepare and deploy all modules
`omv-env list` / `omv-env get <NAME>` / `omv-env set <NAME> <VALUE>` | Environment variables kept in `/etc/default/openmediavault`
`omv-firstaid` | Console recovery menu (exists in source; not in the docs)

## Configuration Locations
PATH | CONTENT
---|---
`/etc/openmediavault/config.xml` | The configuration database
`/srv/salt/omv/deploy` | Salt deploy modules
`/etc/default/openmediavault` | `omv-env` variables

To change fstab mount options, edit the `<fstab>` entries in `config.xml`, run `omv-salt deploy run fstab`, then reboot.

## Gotchas
- Salt deploys regenerate service config files, so hand edits to generated files may be overwritten (inferred, unverified).
- Not found in the official docs: backup, snapshot and update-management plugin details, the pending-changes banner and boot-media wear guidance.

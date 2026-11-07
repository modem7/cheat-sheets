# Proxmox Storage
Storage definitions live in `/etc/pve/storage.cfg` and are managed with `pvesm`. Default install: `local` (directory `/var/lib/vz`, ISOs, templates, backups) and `local-lvm` (LVM-thin, VM and container disks). ZFS installs get `local-zfs` instead.

Documentation: [Storage](https://pve.proxmox.com/pve-docs/chapter-pvesm.html) · [pvesm(1)](https://pve.proxmox.com/pve-docs/pvesm.1.html)

> **Verification:** `pvesm add dir`, `add nfs`, `add pbs`, `scan nfs`, `set`, `remove` and the default storage layout were checked against the docs. The `zfspool`, `lvmthin`, `cifs` and `zfs`/`lvs` examples, the ARC limit and the Ceph notes were **not** verified against the docs. No command was executed.

See also: [Proxmox VE Overview and Install](proxmox-overview.md) · [Proxmox Backup and Restore](proxmox-backup.md) · [Proxmox qm and pct](proxmox-qm-pct.md) · [NFS](../linux/nfs.md) · [TrueNAS Community Edition](../infra/truenas-community-edition.md) (ZFS and NFS server side)

---
## pvesm
COMMAND | DESCRIPTION
---|---
`pvesm status` | All storages, type, usage
`pvesm list <STORAGE>` | Volumes in a storage
`pvesm list <STORAGE> --content backup` | Only backups
`pvesm scan nfs <SERVER>` | List exports on an NFS server
`pvesm set <STORAGE> --content images,rootdir` | Change allowed content types
`pvesm remove <STORAGE>` | Remove the definition only (data is **not** deleted)
`pvesm path <VOLID>` | Filesystem path of a volume
`pvesm alloc <STORAGE> <VMID> <NAME> <SIZE>` | Allocate a volume
`pvesm free <VOLID>` | Delete a volume

Content types: `images` (VM disks), `rootdir` (container disks), `vztmpl` (templates), `iso`, `backup`, `snippets`.

---
## Add Storage
COMMAND | DESCRIPTION
---|---
`pvesm add dir <STORAGE> --path /mnt/<DIR> --content backup,iso,vztmpl` | Directory
`pvesm add nfs <STORAGE> --server <SERVER> --export /<EXPORT> --content images,backup` | NFS share
`pvesm add cifs <STORAGE> --server <SERVER> --share <SHARE> --username <USER> --password <PASS> --content backup` | SMB/CIFS share
`pvesm add zfspool <STORAGE> --pool <POOL>/<DATASET> --content images,rootdir --sparse 1` | ZFS pool or dataset
`pvesm add lvmthin <STORAGE> --vgname <VG> --thinpool <POOL> --content images,rootdir` | LVM-thin
`pvesm add pbs <STORAGE> --server <PBS-HOST> --datastore <DATASTORE> --username <USER>@pbs --fingerprint <SHA256> --password <PASS>` | Proxmox Backup Server ([Proxmox Backup and Restore](proxmox-backup.md))

For a directory on a separate disk: partition, `mkfs.ext4`, mount via `/etc/fstab` (use the UUID), then add as `dir`. Add `is_mountpoint 1` on the storage to stop Proxmox writing into the empty mount point if the disk is missing.

---
## Which Type
TYPE | SNAPSHOTS | SHARED | NOTES
---|---|---|---
Directory (qcow2) | yes | no | Simple, any filesystem
LVM-thin | yes | no | Default `local-lvm`, fast, thin provisioned
ZFS | yes | no | Checksums, compression, replication ([Proxmox Clustering and HA](proxmox-cluster-ha.md))
NFS | yes (qcow2) | yes | Easy shared storage, see [NFS](../linux/nfs.md)
CIFS | yes (qcow2) | yes | Mainly for backups and ISOs
Ceph RBD | yes | yes | Hyper-converged, needs 3+ nodes
Lightbits (plugin) | yes (crash-consistent) | yes | NVMe/TCP block storage, third-party plugin, PVE 9.x, see [Lightbits SDS](#lightbits-sds-nvmetcp)
PBS | n/a | yes | Backups only

Snapshot support depends on disk format: raw disks on plain directory storage cannot snapshot, qcow2 can.

---
## LVM-thin
COMMAND | DESCRIPTION
---|---
`lvs` | Logical volumes and thin pool usage (watch `Data%` and `Meta%`)
`vgs` / `pvs` | Volume groups / physical volumes
`lvdisplay pve/data` | Thin pool detail
`lvextend -L +10G pve/data` | Grow the thin pool (free space in the VG needed)

A full thin pool freezes guests. Monitor `Data%` and do not over-commit heavily.

---
## ZFS
COMMAND | DESCRIPTION
---|---
`zpool status` | Pool health
`zpool list` / `zfs list` | Capacity, datasets and zvols
`zpool scrub <POOL>` | Start a scrub
`zfs list -t snapshot` | Snapshots
`zpool import <POOL>` | Import after a disk move or reinstall
`zpool create -o ashift=12 <POOL> mirror /dev/disk/by-id/<DISK1> /dev/disk/by-id/<DISK2>` | New mirrored pool (use stable `by-id` paths)
`cat /sys/module/zfs/parameters/zfs_arc_max` | Current ARC limit in bytes (0 = default)

Limit ARC (default can use up to about half of RAM) in `/etc/modprobe.d/zfs.conf`:
```
options zfs zfs_arc_max=8589934592
```
Then run `update-initramfs -u -k all` and reboot. More ZFS commands in [TrueNAS Community Edition](../infra/truenas-community-edition.md).

---
## Ceph (overview)
Hyper-converged shared storage built into PVE: each node runs MON, MGR and OSD daemons, VMs use RBD pools. Needs at least 3 nodes, a dedicated fast network (10 GbE or more is the usual advice) and one OSD per disk.

COMMAND | DESCRIPTION
---|---
`pveceph install` | Install Ceph packages on a node
`pveceph init --network <CIDR>` | Initialise Ceph config (once per cluster)
`pveceph mon create` / `pveceph mgr create` | Create monitor and manager on a node
`pveceph osd create /dev/<DISK>` | Create an OSD from a disk
`pveceph pool create <POOL> --add_storages` | Create a pool and add it as storage
`ceph -s` | Cluster health
`ceph osd tree` | OSDs and hosts

Not verified against the docs. Read the [Ceph chapter](https://pve.proxmox.com/pve-docs/chapter-pveceph.html) before building a cluster.

---
## Lightbits SDS (NVMe/TCP)
Lightbits (LightOS) is software-defined block storage served over NVMe/TCP. It is not built into PVE: the community-supported `pve-lightbits` plugin adds a `lightbits` storage type, and each VM disk becomes one Lightbits volume (`vm-<VMID>-<VMGENID>-disk-<N>`). It is shared storage, so live migration moves no disk data.

Plugin: [LightBitsLabs/pve-lightbits](https://github.com/LightBitsLabs/pve-lightbits) · [Lightbits docs](https://documentation.lightbitslabs.com/lightbits-plug-ins/proxmox-installation)

Requirements (per the plugin README): PVE 9.x, LightOS 3.x, Perl 5.36 or newer, kernel 5.0 or newer with `nvme_tcp`, and the `nvme-cli` and `discovery-client` packages. Network ports to the Lightbits cluster: 443 (REST API), 4420 (NVMe/TCP I/O) and 8009 (discovery). Only NVMe/TCP is supported.

**Install** on every node: clone the repository and run its installer (`scripts/install.sh`). It installs the module, pulls in `nvme-cli` and `discovery-client` if missing and restarts the PVE daemons. Re-run it to upgrade. The uninstaller refuses to run while `lightbits` storage entries exist, so remove them first with `pvesm remove`.

OPTION | DESCRIPTION
---|---
`lb_api_host` | Required. Comma-separated `<HOST>:443` list of Lightbits API endpoints
`lb_jwt` | Required. API token, kept in `/etc/pve/priv/storage/<STORAGE>.pw`
`lb_nvme_host` | `<HOST>:4420` list used to seed `discovery-client`
`lb_project` | Lightbits project (default `default`)
`lb_replica_count` | Replicas per volume (default `1`; the README suggests `3` on three or more nodes)
`lb_owner_id` | Ownership label (default: node hostname). Set one value cluster-wide
`lb_subsys_nqn` | Subsystem NQN. Fetched from the API unless pinned here
`lb_fingerprint` | SHA-256 certificate pin (a list is accepted for rotation)
`lb_ssl_verify` / `lb_ca_file` | TLS verification (default off) and the CA file used when it is on
`content images` | VM disks (the only content type in the README examples)
`shared 1` | Needed on a multi-node cluster

Add the storage from the CLI with `pvesm add lightbits <STORAGE>` plus the options above. The GUI "Add Storage" dialog does not list this type. Change settings later with `pvesm set <STORAGE> <OPTION> <VALUE>`.

COMMAND | DESCRIPTION
---|---
`pvesm status` | Storage state and capacity
`pvesm list <STORAGE>` | Lightbits volumes the plugin manages
`pvesm config <STORAGE>` | Stored options for the storage
`nvme list` | NVMe devices the node sees
`cat /etc/nvme/hostnqn` | Host NQN (must be allowed on the Lightbits side)
`systemctl status discovery-client` | Discovery service state
`lsmod \| grep nvme_tcp` | Kernel module loaded
`nc -zv <HOST> 4420` / `nc -zv <HOST> 8009` | Check I/O and discovery ports are reachable
`journalctl -u pvestatd -n 50` | Plugin errors reported by the status daemon
`lbcli create jwt` | Create a new token when `lb_jwt` has expired (run against the Lightbits cluster)

Behaviour to know about:
- Snapshots and native rollback work but are crash-consistent. A snapshot cannot be attached, and backup or clone from a snapshot is not supported. Deleting a disk deletes its snapshots.
- Only full clones work, not linked clones. Resize is grow-only.
- Live migration (`qm migrate <VMID> <NODE> --online`) and HA restart on another node work.
- The plugin writes `/etc/discovery-client/discovery.d/lightbits-<STORAGE>.conf` and symlinks volumes under `/dev/lightbits/<STORAGE>/`. It only manages volumes it labelled itself.

**Not verified.** Facts come from a read of the plugin README and Lightbits docs, not from running it. The installer path was taken from a search snippet, and the literal `pvesm add` example was not captured, so check the README for the exact syntax. The Lightbits product page mentions PVE 8.x, the README says 9.x. Check the README for current versions.

---
## Check Free Space and Clean Up
COMMAND | DESCRIPTION
---|---
`df -h /var/lib/vz` | Space on `local`
`du -sh /var/lib/vz/dump/*` | Backup sizes
`journalctl --vacuum-size=500M` | Trim the journal
`apt clean` | Clear the package cache

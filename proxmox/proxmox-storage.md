# Proxmox Storage
Storage definitions live in `/etc/pve/storage.cfg` and are managed with `pvesm`. Default install: `local` (directory `/var/lib/vz`, ISOs, templates, backups) and `local-lvm` (LVM-thin, VM and container disks). ZFS installs get `local-zfs` instead.

Documentation: [Storage](https://pve.proxmox.com/pve-docs/chapter-pvesm.html) · [pvesm(1)](https://pve.proxmox.com/pve-docs/pvesm.1.html)

> **Verification:** `pvesm add dir`, `add nfs`, `add pbs`, `scan nfs`, `set`, `remove` and the default storage layout were checked against the docs. The `zfspool`, `lvmthin`, `cifs` and `zfs`/`lvs` examples, the ARC limit and the Ceph notes were **not** verified against the docs. The LVM, BTRFS, iSCSI, CephFS, RBD, ZFS over iSCSI and ESXi sections were read in the [storage chapter](https://pve.proxmox.com/pve-docs/chapter-pvesm.html) (PVE 9.2 docs). Gaps are marked *(unverified)*. No command was executed.

See also: [Proxmox VE Overview and Install](proxmox-overview.md) · [Proxmox Backup and Restore](proxmox-backup.md) · [Proxmox qm and pct](proxmox-qm-pct.md) · [Proxmox Disk Image Formats](proxmox-disk-formats.md) · [NFS](../linux/nfs.md) · [TrueNAS Community Edition](../infra/truenas-community-edition.md) (ZFS and NFS server side)

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

## Content Types
The **Content** drop-down in the Add Storage dialog maps to the `content` option (comma-separated).

GUI NAME | `content` VALUE | USED FOR
---|---|---
Disk image | `images` | VM disks
ISO image | `iso` | Installer ISOs
Container template | `vztmpl` | LXC templates (`pveam`)
Backup | `backup` | `vzdump` archives and [PBS](proxmox-backup.md)
Container | `rootdir` | Container root disks and mount points
Snippets | `snippets` | Cloud-init and hook files, see [Proxmox Cloud-Init](proxmox-cloud-init.md)
Import | `import` | Import sources for the import wizard, such as VMs from [ESXi](#esxi-import) (what else it accepts is *unverified*)

Not every storage type offers every content type. The drop-down only lists what the selected type supports, for example:

TYPE | CONTENT TYPES
---|---
LVM, RBD | `images`, `rootdir`
iSCSI | `images`, `none`
CephFS | `vztmpl`, `iso`, `backup`, `snippets`
ZFS over iSCSI | `images`
ESXi | `import`

`none` is for storage you only use as a base for another, such as an iSCSI LUN under LVM. Change the list later with `pvesm set <STORAGE> --content images,rootdir`. Content types for the other storage types are in the [storage chapter](https://pve.proxmox.com/pve-docs/chapter-pvesm.html) (not re-checked here).

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
`pvesm add lvm <STORAGE> --vgname <VG> --content images,rootdir` | LVM volume group ([LVM](#lvm-thick))
`pvesm add iscsi <STORAGE> --portal <HOST[:PORT]> --target <TARGET> --content none` | iSCSI target ([iSCSI](#iscsi))
`pvesm add cephfs <STORAGE> --monhost "<MON1> <MON2> <MON3>" --fs-name <FS> --content backup --username <USER> --keyring <FILE>` | CephFS ([CephFS and RBD](#cephfs-and-rbd))
`pvesm add rbd <STORAGE> --monhost "<MON1> <MON2> <MON3>" --pool <POOL> --content images --username <USER> --keyring <FILE>` | RBD pool, for an external Ceph cluster ([CephFS and RBD](#cephfs-and-rbd))

For a directory on a separate disk: partition, `mkfs.ext4`, mount via `/etc/fstab` (use the UUID), then add as `dir`. Add `is_mountpoint 1` on the storage to stop Proxmox writing into the empty mount point if the disk is missing.

---
## Which Type
TYPE | SNAPSHOTS | SHARED | NOTES
---|---|---|---
Directory (qcow2) | yes | no | Simple, any filesystem
LVM | yes (volume chains, tech preview) | no (can be shared over iSCSI or FC) | Thick provisioned block storage, see [LVM](#lvm-thick)
LVM-thin | yes | no | Default `local-lvm`, fast, thin provisioned
BTRFS | yes | no | File storage, **technology preview**, see [BTRFS](#btrfs)
ZFS | yes | no | Checksums, compression, replication ([Proxmox Clustering and HA](proxmox-cluster-ha.md))
NFS | yes (qcow2) | yes | Easy shared storage, see [NFS](../linux/nfs.md)
CIFS | yes (qcow2) | yes | Mainly for backups and ISOs
iSCSI | no | yes | Raw LUNs, normally with LVM on top, see [iSCSI](#iscsi)
CephFS | yes (not guaranteed stable) | yes | File storage for ISOs, templates, backups and snippets, see [CephFS and RBD](#cephfs-and-rbd)
Ceph RBD | yes (and clones) | yes | Hyper-converged, needs 3+ nodes. Also usable against an external cluster
ZFS over iSCSI | yes (no clones) | yes | A remote ZFS box serving zvols over iSCSI, see [ZFS over iSCSI](#zfs-over-iscsi)
ESXi | n/a | n/a | Import source for migrating VMs, not a place to run guests, see [ESXi Import](#esxi-import)
Lightbits (plugin) | yes (crash-consistent) | yes | NVMe/TCP block storage, third-party plugin, PVE 9.x, see [Lightbits SDS](#lightbits-sds-nvmetcp)
PBS | n/a | yes | Backups only

Snapshot support depends on disk format: raw disks on plain directory storage cannot snapshot, qcow2 can. See [Proxmox Disk Image Formats](proxmox-disk-formats.md) for raw, qcow2 and VMDK.

---
## LVM (Thick)
Block storage on a volume group, with each VM disk a full-size logical volume. Content types are `images` and `rootdir`.

OPTION | DESCRIPTION
---|---
`vgname` | Volume group to use
`base` | Volume activated first. The docs mention it only for remote iSCSI volumes
`saferemove` | Zero data when a volume is deleted
`snapshot-as-volume-chain` | Snapshots as volume chains (technology preview), see [Snapshots as Volume Chain](#snapshots-as-volume-chain)

COMMAND | DESCRIPTION
---|---
`pvesm add lvm <STORAGE> --vgname <VG>` | Add an existing volume group
`pvesm add lvm <STORAGE> --vgname <VG> --snapshot-as-volume-chain 1` | Same, with volume-chain snapshots
`vgs` / `lvs` | Groups and volumes

The docs mark LVM as not shared by itself. To share it, put it on an LUN every node can see ([iSCSI](#iscsi)), but no full walkthrough was found *(unverified)*.

---
## Snapshots as Volume Chain
The **Snapshots as Volume-Chain** checkbox (storage option `snapshot-as-volume-chain`) gives thick LVM storage real VM snapshots. Each snapshot is a thick logical volume holding only the differences from the volume behind it, and taking a snapshot starts a new volume backed by the last. It uses qcow2 only to layer the chain, and the PVE storage layer does the snapshot work, not qcow2's internal snapshots.

The docs say this avoids the I/O penalty and the dangerous out-of-space behaviour of native LVM snapshots, and that it works on block storage such as iSCSI and FC SANs, with cluster-wide locking when the storage is shared.

TOPIC | DETAIL
---|---
Status | **Technology preview**. Introduced in PVE 9.0 and still a preview in 9.1 and 9.2. The roadmap plans to take it out of preview for LVM (thick), Directory, NFS and CIFS
Option | `--snapshot-as-volume-chain <boolean>`, default `0`, on `pvesm add` and `pvesm set`
Scope | Only affects **newly created** disks, and cannot be turned off while a qcow2 image exists on the storage (9.1 notes)
TPM | 9.1: offline snapshots of VMs with TPM state (machine version 10 or later). 9.2: live snapshots with TPM state, but the top-most snapshot cannot be removed while the VM runs

COMMAND | DESCRIPTION
---|---
`pvesm set <STORAGE> --snapshot-as-volume-chain 1` | Turn it on for new disks
`pvesm config <STORAGE>` | Check the stored option

Caveats:
- Each snapshot uses its full size unless the backing storage is thin provisioned and passes through discard.
- LVM still has no linked clones.
- The roadmap says migrating VMs that have snapshots on local volume-chain storage is blocked.
- The docs do not say how existing raw disks, backup, clone or move-disk behave, or how much overhead qcow2 adds. The idea that only new disks become qcow2 is inferred *(unverified)*.
- The **Preallocation** setting shown in the same dialog is documented (`off`, `metadata`, `falloc`, `full`) only for raw and qcow2 images on file-based storage, so how it applies here is *(unverified)*.

---
## BTRFS
File-based storage on a BTRFS filesystem. The docs mark it as a **technology preview** and show only a `storage.cfg` example, not a `pvesm add` command.

```text
btrfs: <STORAGE>
        path /mnt/<BTRFS_MOUNT>
        content rootdir,images
        is_mountpoint 1
```

Snapshots are supported, and storage is not shared. Treat it as unsuitable for anything you cannot rebuild.

---
## iSCSI
Raw LUNs from an iSCSI target. The LUNs are not managed per guest, so the usual pattern is `content none` on the iSCSI storage with [LVM](#lvm-thick) on top. Content types are `images` and `none`. Table 10 of the docs says no snapshots, though the summary table says "volume chains", so the per-backend table is trusted here.

COMMAND | DESCRIPTION
---|---
`pvesm scan iscsi <HOST[:PORT]>` | List targets on a portal
`pvesm add iscsi <STORAGE> --portal <HOST[:PORT]> --target <TARGET> --content none` | Add the target
`pvesm list <STORAGE>` | List LUNs

`iscsiadm` is only mentioned in the docs, without commands, so low-level session commands are not covered here *(unverified)*.

---
## CephFS and RBD
Both talk to a Ceph cluster, either one built with `pveceph` ([Ceph (overview)](#ceph-overview)) or an external one.

TYPE | CONTENT | KEY OPTIONS
---|---|---
`cephfs` | `vztmpl`, `iso`, `backup`, `snippets` | `monhost`, `fs-name`, `username`, `subdir`, `path`, `fuse`
`rbd` | `images`, `rootdir` | `monhost`, `pool`, `username`, `krbd`, `keyring`

COMMAND | DESCRIPTION
---|---
`pveceph fs create --pg_num 128 --add-storage` | Create a CephFS and add it as storage
`pvesm add cephfs <STORAGE> --monhost "<MON1> <MON2> <MON3>" --fs-name <FS> --content backup --username <USER> --keyring <FILE>` | External CephFS
`pvesm add rbd <STORAGE> --monhost "<MON1> <MON2> <MON3>" --pool <POOL> --content images --username <USER> --keyring <FILE>` | External RBD pool

The `keyring` file is copied to `/etc/pve/priv/ceph/<STORAGE>.keyring` for RBD, and the CephFS secret lives at `/etc/pve/priv/ceph/<STORAGE>.secret`. Set `krbd 1` to use the kernel RBD client instead of librbd. CephFS snapshots exist, but the docs do not guarantee they are stable.

---
## ZFS over iSCSI
Proxmox creates a zvol per disk on a remote ZFS server and attaches it over iSCSI. It is the `zfs` storage type, and not to be confused with `zfspool` for local ZFS. The remote host needs an iSCSI target provider and SSH access from every PVE node. Content is `images`. Snapshots work, clones do not.

OPTION | DESCRIPTION
---|---
`pool` | Pool or dataset on the remote host
`portal` / `target` | iSCSI portal and target name
`iscsiprovider` | `comstar`, `istgt`, `iet` or `LIO`
`comstar_tg` / `comstar_hg` | COMSTAR target group and host group
`lio_tpg` | LIO target portal group
`blocksize` | zvol block size
`sparse` | Thin provision zvols
`nowritecache` | Disable the write cache

Set up passwordless SSH from each node first:

```bash
mkdir /etc/pve/priv/zfs
ssh-keygen -f /etc/pve/priv/zfs/192.0.2.1_id_rsa
ssh-copy-id -i /etc/pve/priv/zfs/192.0.2.1_id_rsa.pub root@192.0.2.1
```

The key file name starts with the portal address. The docs give `storage.cfg` examples for each provider but no `pvesm add zfs` command *(unverified)*. `blocksize` and `sparse` are also documented for the local `zfspool` type.

---
## ESXi Import
The `esxi` type connects Proxmox to an ESXi host or vCenter so you can import its VMs. It is for migration, not for running guests. The import wizard is GUI-only, tech preview, added during the 8.2 cycle, and was tested with ESXi 6.5 to 8.0.

OPTION | DESCRIPTION
---|---
`server` | ESXi host
`username` / `password` | Credentials
`skip-cert-verification` | Accept a self-signed certificate
`content import` | Import content type

The docs have no `pvesm add esxi` example, so add it from **Datacenter > Storage > Add > ESXi** *(unverified from the CLI)*. Whether `qm importdisk` applies is not addressed there. Migration context is in [Hypervisor Comparison](../infra/hypervisor-comparison.md).

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

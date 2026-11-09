# Proxmox Disk Image Formats
Which format a VM disk uses (raw, qcow2 or VMDK), when to choose each, and the disk options that go with them. Storage types and content types are in [Proxmox Storage](proxmox-storage.md), and the `qm` commands in [Proxmox qm and pct](proxmox-qm-pct.md).

Documentation: [Virtual Machines](https://pve.proxmox.com/pve-docs/chapter-qm.html) · [Storage](https://pve.proxmox.com/pve-docs/chapter-pvesm.html) · [qm(1)](https://pve.proxmox.com/pve-docs/qm.1.html) · [qemu-img](https://www.qemu.org/docs/master/tools/qemu-img.html)

> **Verification:** the format guidance and options were read in the PVE docs (partly, the first 100k characters of the VM chapter and `qm.1`). The `qemu-img` commands were run locally with qemu-img 10.2.1. Gaps are marked *(unverified)*.

## The Formats
FORMAT | SNAPSHOTS | THIN PROVISIONING | NOTES
---|---|---|---
raw | no (by itself) | no | Simplest, "up to 10% faster" per the docs. Snapshots then come from the storage layer (ZFS, LVM-thin, Ceph)
qcow2 | yes | yes | Copy-on-write file format. Gives snapshots, linked clones and thin provisioning on file-based storage
VMDK | no | n/a | Only worth it to import or export disks to other hypervisors

On file storage (directory, NFS, CIFS) snapshots and clones need qcow2. Raw on plain directory storage cannot snapshot.

## Which Storage Allows Which
STORAGE | FORMATS
---|---
Directory | raw, qcow2, VMDK (and `subvol` for containers)
NFS, CIFS | raw, qcow2, VMDK
ZFS | raw (zvols), `subvol` for containers
LVM, RBD | raw. LVM can also hold qcow2 with the `snapshot-as-volume-chain` storage option (technology preview, PVE 9.0 and later)

Storages that present block devices (LVM, ZFS, Ceph) need the raw format, so the choice only exists on file-based storage.

## When to Use Which
SITUATION | CHOOSE
---|---
Local ZFS, LVM-thin or Ceph | raw. The storage already does thin provisioning and snapshots
Directory, NFS or CIFS and you want snapshots or linked clones | qcow2
Directory or NFS and you want maximum speed, no snapshots | raw
Moving a VM to or from VMware or another hypervisor | VMDK, then convert to qcow2 or raw once imported
Big disk on network storage | qcow2 with preallocation `off`, so it does not write metadata up front
Templates you will linked-clone | qcow2 (the original must be a read-only template, and cannot be deleted while clones exist)

Internal qcow2 snapshots block a running VM and are slow, worst on NFS. Use raw on storage that has native snapshots where you can.

## Choose the Format
COMMAND | DESCRIPTION
---|---
`qm disk import <VMID> <FILE> <STORAGE> --format qcow2` | Import a disk image as a given format (`qcow2`, `raw` or `vmdk`)
`qm disk move <VMID> scsi0 <STORAGE> --format raw --delete 1` | Move a disk to another storage and convert it. `--format` applies only when moving to a **different** storage
`qm set <VMID> --scsi0 <STORAGE>:32,format=qcow2` | New disk with a format *(`format=` on `qm set` not confirmed in the docs read)*

## qemu-img
COMMAND | DESCRIPTION
---|---
`qemu-img create -f qcow2 <FILE> 100M` | New qcow2 image
`qemu-img create -f raw <FILE> 100M` | New raw image (sparse, no disk used until written)
`qemu-img create -f qcow2 -o preallocation=metadata <FILE> 100M` | qcow2 with metadata preallocated
`qemu-img create -f qcow2 -b <BASE> -F qcow2 <FILE>` | Child image backed by a base (what linked clones are)
`qemu-img convert -p -f raw -O qcow2 <IN> <OUT>` | Convert raw to qcow2 with progress
`qemu-img convert -f qcow2 -O raw <IN> <OUT>` | Convert qcow2 to raw
`qemu-img info <FILE>` | Format, virtual and on-disk size, backing file

Converting does not change the VM config. Import the result with `qm disk import`, or see the shrink workflow in [Proxmox qm and pct](proxmox-qm-pct.md).

## Preallocation
Applies to raw and qcow2 images on file-based storage only. The default is `metadata`, which has no effect on raw. Set it to `off` for big qcow2 disks on network storage. The full value list (`off`, `metadata`, `falloc`, `full`) is from the `qemu-img` side and was not seen in full in the PVE docs *(partly unverified)*.

## Disk Options That Go With It
OPTION | NOTE
---|---
`discard=on` | Pass TRIM through so thin storage can reclaim space. Needed for thin provisioning to shrink
`iothread=1` | Dedicated I/O thread. Needs VirtIO SCSI single or VirtIO Block
`ssd=1` | SSD emulation. Not supported on VirtIO Block
cache | Default is **No cache** (`none`). Other modes were not read in full *(unverified)*
`aio=native\|threads\|io_uring` | I/O mode. The default was not confirmed

VirtIO SCSI single is recommended for performance and has been the default for new Linux VMs since PVE 7.3.

## See Also
- [Proxmox Storage](proxmox-storage.md)
- [Proxmox qm and pct](proxmox-qm-pct.md)
- [Proxmox Backup and Restore](proxmox-backup.md)
- [Proxmox VE Overview and Install](proxmox-overview.md)

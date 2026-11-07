# Hypervisors Compared
A short comparison of the hypervisors covered in this repository: Proxmox VE, VMware ESXi and XCP-ng. Use it to choose a platform for a homelab.

See also: [Proxmox VE Overview and Install](../proxmox/proxmox-overview.md) · [Proxmox Storage](../proxmox/proxmox-storage.md) · [VMware ESXi](esxi.md) · [XCP-ng](xcp-ng.md) · [NAS Operating Systems Compared](nas-os-comparison.md)

## Comparison
TOPIC | PROXMOX VE | VMWARE ESXI | XCP-NG
---|---|---|---
Base | Debian, KVM and LXC | Proprietary VMkernel | Xen, CentOS-derived dom0
Management | Web UI, API, clustering built in | Host Client; vCenter for clusters | Xen Orchestra
Licence | Open source, optional support subscription | Broadcom; free edition is ESXi 8.0 U3e with limits | Open source, Vates support optional
Storage | ZFS, LVM, Ceph, NFS, iSCSI | VMFS, NFS, vSAN | EXT, LVM, NFS, iSCSI, XOSTOR
CLI | `qm`, `pct`, `pvesh` | `esxcli`, `vim-cmd` (unverified) | `xe`
Best fit | General homelab | Existing VMware estates | Xen shops wanting open source

Hyper-V (Windows) and Incus (containers and VMs) are alternatives not covered by a sheet here. For plain KVM on a Linux host see [libvirt and KVM](../linux/libvirt-kvm.md); for desktop virtualisation see [VirtualBox](../tools/virtualbox.md).

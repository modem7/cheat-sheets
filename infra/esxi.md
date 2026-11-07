# VMware ESXi
VMware ESXi is Broadcom's bare-metal hypervisor, managed by the Host Client web UI or by vCenter. Many homelabs have moved to [Proxmox VE](../proxmox/proxmox-overview.md) or [XCP-ng](xcp-ng.md) since the Broadcom takeover.

Documentation: [Broadcom TechDocs](https://techdocs.broadcom.com/) · [Free ESXi KB 399823](https://knowledge.broadcom.com/external/article/399823)

See also: [Hypervisors Compared](hypervisor-comparison.md) · [XCP-ng](xcp-ng.md) · [Proxmox VE Overview and Install](../proxmox/proxmox-overview.md) · [Proxmox Storage](../proxmox/proxmox-storage.md) · [NFS](../linux/nfs.md)

## Versions and Licensing
FACT | DETAIL
---|---
Versions | 9.1 (9.1.1.0), 9.0 and 8.0 (U3k) listed by endoflife.date (third party); the product is called "ESX" in 9.x (inferred)
Free edition | Broadcom KB: free vSphere Hypervisor is ESXi 8.0 U3e, limited to 2 physical CPUs and 8 vCPU per VM, no vCenter, vMotion, HA or backup APIs, no support
Download | Broadcom Support Portal, Free Software Downloads; still offered in Nov 2026 is unverified
Free ESXi 9 | Not found
Boot media | ESXi 8.0 needs a boot disk of at least 32 GB; SD or USB-only boot is being deprecated
Edition names | Not verified

## CLI
Commands below come from a third-party backup guide (NAKIVO), not Broadcom docs, so all are unverified. Enable SSH from the Host Client or DCUI first.

COMMAND | DESCRIPTION
---|---
`vim-cmd hostsvc/firmware/sync_config` | Flush config to disk (unverified)
`vim-cmd hostsvc/firmware/backup_config` | Create a config backup bundle in `/scratch/downloads` (unverified)
`vim-cmd hostsvc/firmware/restore_config` | Restore a bundle, host in maintenance mode, then reboots (unverified)
`esxcli system maintenanceMode set --enable yes` | Enter maintenance mode (unverified; `no` to leave)

`esxcli`, `vmkfstools`, `esxtop`, PowerCLI and `govc` were not checked against Broadcom docs, so they are omitted.

## Migrate to Proxmox
Proxmox VE 8 or later has an ESXi import (**Datacenter > Storage > Add > ESXi**, then **Import** on the VM). Tested with ESXi 6.5 to 8.0; power the source VM off. vSAN and encrypted disks cannot be imported, snapshots slow it, and importing through vCenter is much slower. See [Migrate to Proxmox VE](https://pve.proxmox.com/wiki/Migrate_to_Proxmox_VE).

# XCP-ng
XCP-ng is an open source, Xen-based hypervisor forked from XenServer, hosted by the Linux Foundation and backed by Vates. It is managed from Xen Orchestra.

Documentation: [XCP-ng Docs](https://docs.xcp-ng.org/) · [Xen Orchestra Docs](https://docs.xen-orchestra.com/)
Project: [XCP-ng](https://xcp-ng.org/)

See also: [Hypervisors Compared](hypervisor-comparison.md) · [VMware ESXi](esxi.md) · [Proxmox VE Overview and Install](../proxmox/proxmox-overview.md) · [NFS](../linux/nfs.md)

## Release and Requirements
FACT | DETAIL
---|---
Current | 8.3 LTS (released 2024-10-07, supported to 2028-11-30); 8.2 is end-of-life; 9.0 announced without a date
Requirements | 64-bit x86 with VT-x or AMD-V plus SLAT; 2 GB RAM minimum (8 GB or more recommended); 46 GB disk minimum
Install | USB ISO or netinstall ISO; EXT storage recommended; USB and SD installs discouraged

## Storage
Supported SR types: local EXT, local LVM, NFS, File (use with caution), iSCSI, HBA and XOSTOR. ZFS and Ceph are provided as-is. Snapshots use VHD; removing one triggers a coalesce, with a chain limit of 30.

## CLI
COMMAND | DESCRIPTION
---|---
`xe vm-list` | List VMs (`--minimal`, `params=` supported)
`xe help` | List xe commands
`xe sr-create` | Create a storage repository
`xe host-disable` / `xe host-enable` | Take a host out of, and back into, service for updates
`xe host-evacuate` | Move VMs off a host
`xe task-list` | Show running tasks
`xe-toolstack-restart` | Restart the toolstack without a reboot
`yum update` | Update the host (update the pool master first)
`xe pool-dump-database file-name=<FILE>` | Back up the pool database
`xe pool-restore-database file-name=<FILE> dry-run=true` | Test a restore

Update from SSH, not xsconsole or a VNC console, and disable third-party repositories first.

## Xen Orchestra
Backups: rolling snapshots, full and incremental backups, replication and mirroring, to S3, NFS and SMB targets. It also imports from ESXi. Free versus paid features and the Lite edition were not verified (unverified).

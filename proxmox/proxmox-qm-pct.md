# Proxmox qm and pct
`qm` manages KVM virtual machines, `pct` manages LXC containers. Run on a PVE node as root. `<VMID>` and `<CTID>` share one ID space per cluster.

Documentation: [qm(1)](https://pve.proxmox.com/pve-docs/qm.1.html) · [pct(1)](https://pve.proxmox.com/pve-docs/pct.1.html)

> **Verification:** all `qm` commands, including `qm disk import`, `qm disk move`, `qm disk resize`, `qm guest exec`, `qm showcmd` and `qm monitor`, were checked against the qm docs. The `pct` subcommands (`create`, `set`, `resize`, `snapshot`, `move-volume`, `fsck`, `migrate --restart`) were **not** verified against the docs and no command was executed. Run `pct help <SUBCOMMAND>` to confirm.

See also: [[proxmox-overview]] · [[proxmox-storage]] · [[proxmox-cloud-init]] · [[proxmox-troubleshooting]]

---
## qm: Virtual Machines
COMMAND | DESCRIPTION
---|---
`qm list` | List VMs on this node
`qm status <VMID>` | Running state
`qm config <VMID>` | Show config
`qm start <VMID>` | Start
`qm shutdown <VMID>` | Graceful ACPI shutdown
`qm stop <VMID>` | Hard stop
`qm reboot <VMID>` / `qm reset <VMID>` | Graceful reboot / hard reset
`qm suspend <VMID>` / `qm resume <VMID>` | Pause / resume
`qm create <VMID> --name <NAME> --memory 2048 --cores 2 --net0 virtio,bridge=vmbr0` | Create an empty VM
`qm set <VMID> --memory 4096 --cores 4` | Change resources
`qm set <VMID> --onboot 1` | Start at boot
`qm set <VMID> --agent enabled=1` | Enable QEMU guest agent (install it in the guest too)
`qm clone <VMID> <NEWID> --name <NAME> --full` | Full clone (omit `--full` for a linked clone from a template)
`qm template <VMID>` | Convert a VM to a template
`qm destroy <VMID> --purge` | Delete VM and remove it from jobs
`qm snapshot <VMID> <NAME>` | Snapshot
`qm listsnapshot <VMID>` | List snapshots
`qm rollback <VMID> <NAME>` | Roll back
`qm delsnapshot <VMID> <NAME>` | Delete a snapshot
`qm unlock <VMID>` | Clear a stuck lock
`qm terminal <VMID>` | Serial console (needs a serial port, `-serial0 socket`)
`qm monitor <VMID>` | QEMU monitor
`qm showcmd <VMID> --pretty` | Show the kvm command line
`qm migrate <VMID> <TARGET> --online` | Live migrate in a cluster ([[proxmox-cluster-ha]])

### Guest agent
COMMAND | DESCRIPTION
---|---
`qm agent <VMID> ping` | Check the agent responds
`qm guest exec <VMID> -- <CMD> <ARGS>` | Run a command in the guest
`qm guest cmd <VMID> network-get-interfaces` | Guest NIC info

### Disks
COMMAND | DESCRIPTION
---|---
`qm set <VMID> --scsi1 <STORAGE>:32` | Add a new 32 GiB disk
`qm disk import <VMID> <FILE> <STORAGE>` | Import a disk image (`qm importdisk` is the older alias)
`qm disk move <VMID> scsi0 <STORAGE> --delete 1` | Move a disk to another storage (`qm move-disk` alias)
`qm disk resize <VMID> scsi0 +5G` | Grow a disk (`qm resize` alias)
`qm set <VMID> --delete unused0` | Remove an unused disk entry
`qm rescan` | Re-scan storage and fix up unused volumes

### Resize a disk
Grow in the GUI or with `qm disk resize <VMID> scsi0 +5G`. Then grow the partition and filesystem inside the guest (`growpart`, `resize2fs` or `xfs_growfs`).

### Shrink a disk (manual, risky)
> Take a backup first ([[proxmox-backup]]). Proxmox cannot shrink disks. Shrink the filesystem and partition inside the guest first, otherwise data is lost.

1. Convert qcow2 to raw
```
qemu-img convert vm-<VMID>.qcow2 vm-<VMID>.raw
```
2. Shrink the disk
```
qemu-img resize -f raw --shrink vm-<VMID>.raw 10G
```
3. Convert back to qcow2
```
qemu-img convert -p -O qcow2 vm-<VMID>.raw vm-<VMID>.qcow2
```
Applies to file-based storage (directory, NFS). For LVM or ZFS volumes, shrink the volume itself with `lvreduce` or `zfs set volsize`, which is not covered here.

---
## pct: LXC Containers
COMMAND | DESCRIPTION
---|---
`pct list` | List containers
`pct status <CTID>` | Running state
`pct config <CTID>` | Show config
`pct create <CTID> <STORAGE>:vztmpl/<TEMPLATE> --hostname <NAME> --unprivileged 1 --net0 name=eth0,bridge=vmbr0,ip=dhcp --rootfs <STORAGE>:8` | Create from a downloaded template (`pveam download`)
`pct start <CTID>` / `pct shutdown <CTID>` / `pct stop <CTID>` | Start, graceful, hard stop
`pct enter <CTID>` | Shell into a container from the host
`pct exec <CTID> -- <CMD>` | Run a command in a container
`pct push <CTID> <LOCAL> <REMOTE>` | Copy a file in
`pct pull <CTID> <REMOTE> <LOCAL>` | Copy a file out
`pct set <CTID> --memory 1024 --cores 2` | Change resources
`pct set <CTID> --features nesting=1,keyctl=1` | Enable nesting (needed for [[docker]] in LXC)
`pct set <CTID> --mp0 <STORAGE>:8,mp=/data` | Add a mount point volume
`pct set <CTID> --mp0 /host/path,mp=/mnt/path` | Bind mount a host directory
`pct resize <CTID> rootfs +4G` | Grow the root disk
`pct snapshot <CTID> <NAME>` / `pct rollback <CTID> <NAME>` | Snapshot and roll back
`pct clone <CTID> <NEWID> --hostname <NAME>` | Clone
`pct template <CTID>` | Convert to a template
`pct destroy <CTID> --purge` | Delete
`pct unlock <CTID>` | Clear a stuck lock
`pct fsck <CTID>` | Check the root filesystem (container stopped)
`pct migrate <CTID> <TARGET> --restart` | Migrate (containers restart, no live migration)
`pct restore <CTID> <ARCHIVE> --storage <STORAGE>` | Restore from a vzdump archive

### Unprivileged containers and bind mounts
Unprivileged containers map container UID 0 to host UID 100000. A bind-mounted host directory must be owned by the mapped IDs (for example `chown -R 100000:100000 <DIR>`) or you need custom `lxc.idmap` entries. Sharing an NFS export into a container is usually easiest by mounting it on the host first, see [[nfs]] and [[proxmox-storage]].

---
## Container Templates
COMMAND | DESCRIPTION
---|---
`pveam update` | Refresh the template index
`pveam available --section system` | List OS templates
`pveam download local <TEMPLATE>` | Download to `local` storage
`pveam list local` | Downloaded templates
`pveam remove <STORAGE>:vztmpl/<TEMPLATE>` | Delete a template

General Linux commands inside guests: [[linux]].

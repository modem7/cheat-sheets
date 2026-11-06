# Proxmox
Proxmox VE is an open source virtualisation platform (KVM virtual machines and LXC containers) with a web UI, clustering and ZFS/Ceph storage.

Documentation: [Proxmox VE Docs](https://pve.proxmox.com/pve-docs/)

---
## VM and Container Commands
COMMAND | DESCRIPTION
---|---
`qm list` | List VMs
`qm start <VMID>` / `qm shutdown <VMID>` / `qm stop <VMID>` | Start, graceful shutdown, hard stop
`qm config <VMID>` | Show VM config
`qm set <VMID> --memory 4096 --cores 4` | Change resources
`qm clone <VMID> <NEWID> --name <NAME> --full` | Full clone
`qm template <VMID>` | Convert a VM to a template
`qm snapshot <VMID> <NAME>` / `qm rollback <VMID> <NAME>` | Snapshot and roll back
`qm unlock <VMID>` | Clear a stuck lock
`qm terminal <VMID>` | Serial console
`pct list` | List LXC containers
`pct enter <CTID>` | Shell into a container
`pct exec <CTID> -- <CMD>` | Run a command in a container
`pct push <CTID> <LOCAL> <REMOTE>` | Copy a file in

## Backups and Storage
COMMAND | DESCRIPTION
---|---
`vzdump <VMID> --storage <STORAGE> --mode snapshot --compress zstd` | Back up a guest
`qmrestore <ARCHIVE> <VMID> --storage <STORAGE>` | Restore a VM
`pct restore <CTID> <ARCHIVE> --storage <STORAGE>` | Restore a container
`pvesm status` | Storage status
`pvesm list <STORAGE>` | Volumes in a storage

## Cluster and Host
COMMAND | DESCRIPTION
---|---
`pvecm status` | Cluster and quorum state
`pvecm nodes` | Cluster members
`pveversion -v` | Versions
`pveam update && pveam available` | Container templates
`journalctl -u pveproxy -f` | Web UI logs
`systemctl restart pveproxy pvedaemon` | Restart the UI services
`zpool status` | ZFS health, see [[truenas-scale]] for more ZFS

---
## ACME Certificates

1. datacenter -> acme -> add account
2. datacenter -> acme -> add challenge plugin
3. node -> certificates -> acme -> use account
4. node -> certificates -> acme -> add certs
5. node -> certificates -> acme -> order certificates now

CLI form:
```bash
pvenode acme account register default <EMAIL>
pvenode config set --acme domains=pve.example.com
pvenode acme cert order
```

---
## Resize Disk

### Increase disk size
Increase disk size in the GUI or with the following command
```
qm resize 100 virtio0 +5G
```
Then grow the partition and filesystem inside the guest (`growpart`, `resize2fs` or `xfs_growfs`).

### Decrease disk size
> Before decreasing disk sizes in Proxmox, you should take a backup!
Shrink the filesystem and partition inside the guest first, otherwise data is lost.
1. Convert qcow2 to raw
```
qemu-img convert vm-100.qcow2 vm-100.raw
```
2. Shrink the disk
```
qemu-img resize -f raw --shrink vm-100.raw 10G
```
3. Convert back to qcow2
```
qemu-img convert -p -O qcow2 vm-100.raw vm-100.qcow2
```

---
## Cloud-Init Template (quick recipe)
```bash
qm create 9000 --name ubuntu-template --memory 2048 --net0 virtio,bridge=vmbr0
qm importdisk 9000 jammy-server-cloudimg-amd64.img local-lvm
qm set 9000 --scsihw virtio-scsi-pci --scsi0 local-lvm:vm-9000-disk-0 --ide2 local-lvm:cloudinit --boot c --bootdisk scsi0 --serial0 socket --vga serial0
qm template 9000
```

---
## Further information

More examples and tutorials regarding Proxmox can be found in the link list below:

- Ansible playbook that automates Linux VM updates running on Proxmox (including snapshots): [TheDatabaseMe - update_proxmox_vm](https://github.com/thedatabaseme/update_proxmox_vm)
- Manage Proxmox VM templates with Packer: [Use Packer to build Proxmox images](https://thedatabaseme.de/2022/10/16/what-a-golden-boy-use-packer-to-build-proxmox-images/)

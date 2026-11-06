# Proxmox Cloud-Init Templates
Build a VM template from a cloud image once, then clone it and let cloud-init set user, SSH key, hostname and network on first boot.

Documentation: [Cloud-Init Support](https://pve.proxmox.com/pve-docs/chapter-qm.html#qm_cloud_init)

> **Verification:** `qm disk import` (alias `qm importdisk`), `import-from=`, `ciuser`, `cipassword`, `sshkeys`, `ipconfig0` and `qm cloudinit dump` were checked against the qm docs. No command was executed. The docs example spells the key option `--sshkey` in prose, the property is `sshkeys` (a file path works with `--sshkeys`). Image URLs change, check the distro site.

See also: [Proxmox qm and pct](proxmox-qm-pct.md) · [Proxmox Storage](proxmox-storage.md) · [Terraform](../tools/terraform.md) · [Ansible Cheat-Sheet](../tools/ansible.md)

---
## Build a Template
Example with an Ubuntu cloud image, template ID `9000`, storage `local-lvm`:
```bash
wget https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img
qm create 9000 --name ubuntu-template --memory 2048 --cores 2 --net0 virtio,bridge=vmbr0
qm disk import 9000 noble-server-cloudimg-amd64.img local-lvm
qm set 9000 --scsihw virtio-scsi-pci --scsi0 local-lvm:vm-9000-disk-0
qm set 9000 --ide2 local-lvm:cloudinit
qm set 9000 --boot order=scsi0
qm set 9000 --serial0 socket --vga serial0
qm set 9000 --agent enabled=1
qm template 9000
```
On current versions the import can be done in one step: `qm set 9000 --scsi0 local-lvm:0,import-from=/path/to/image.img`.

The older form (from the previous version of this sheet) is: `qm importdisk 9000 jammy-server-cloudimg-amd64.img local-lvm`, then `--boot c --bootdisk scsi0`. That still works but `--boot order=` is current.

The guest agent only works if `qemu-guest-agent` is in the image. Install it with a cloud-init snippet or customise the image (for example with `virt-customize --install qemu-guest-agent -a <IMAGE>`).

---
## Cloud-Init Settings
COMMAND | DESCRIPTION
---|---
`qm set <VMID> --ciuser <USER>` | Default user
`qm set <VMID> --cipassword <PASS>` | Password (prefer SSH keys)
`qm set <VMID> --sshkeys ~/.ssh/id_ed25519.pub` | Authorised key(s), from a file
`qm set <VMID> --ipconfig0 ip=dhcp` | DHCP
`qm set <VMID> --ipconfig0 ip=<IP>/24,gw=<GATEWAY>` | Static address
`qm set <VMID> --nameserver <DNS> --searchdomain <DOMAIN>` | DNS
`qm set <VMID> --ciupgrade 1` | Upgrade packages on first boot
`qm cloudinit update <VMID>` | Regenerate the cloud-init drive
`qm cloudinit dump <VMID> user` | Show generated user-data (also `network`, `meta`)

Changing settings on a running VM needs `qm cloudinit update` (or a stop and start), and the guest only applies them on first boot unless cleaned.

---
## Clone and Boot
```bash
qm clone 9000 <NEWID> --name <NAME> --full
qm set <NEWID> --ciuser <USER> --sshkeys ~/.ssh/id_ed25519.pub --ipconfig0 ip=dhcp
qm disk resize <NEWID> scsi0 +20G
qm start <NEWID>
```
Linked clones (omit `--full`) are quick but depend on the template.

## Custom User-Data
Put a cloud-init file on a storage with the `snippets` content type (for example `local`: `/var/lib/vz/snippets/<NAME>.yml`) and attach it:
```bash
qm set <VMID> --cicustom "user=local:snippets/<NAME>.yml"
```
Custom user-data replaces the generated user part, so include users and keys in it.

---
## Automation
- [Terraform](../tools/terraform.md) with a Proxmox provider can clone this template and fill cloud-init fields.
- [Ansible Cheat-Sheet](../tools/ansible.md) can configure the VM after boot.
- Packer can build the template itself, see [Proxmox VE Overview and Install](proxmox-overview.md) for links.

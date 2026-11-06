# Proxmox VM Template and Clone
Build an Ubuntu cloud-init template once, clone it into new VMs in seconds, resize the disk, and configure each VM with Ansible.

Documentation: [Proxmox Cloud-Init Support](https://pve.proxmox.com/pve-docs/chapter-qm.html#qm_cloud_init) · [qm(1)](https://pve.proxmox.com/pve-docs/qm.1.html)

## Goal
`qm clone` produces a running Ubuntu VM with your user, SSH key, hostname and IP set automatically, ready for an Ansible run.

## Prerequisites
- A Proxmox VE node with a storage that holds VM disks (`local-lvm` below) and a bridge (`vmbr0`) ([Proxmox VE Overview and Install](../proxmox/proxmox-overview.md), [Proxmox Storage](../proxmox/proxmox-storage.md))
- Shell access on the node (`root`), and an SSH key on your workstation
- Free VMIDs: `9000` for the template, `120` for the first clone
- For the guest agent: `libguestfs-tools` on the node (`apt install libguestfs-tools`) if you customise the image

## Steps
### 1. Download and prepare the image
```bash
cd /var/lib/vz/template
wget https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img
sudo virt-customize -a noble-server-cloudimg-amd64.img --install qemu-guest-agent
```
Skip `virt-customize` if you install the agent through cloud-init user-data instead ([Proxmox Cloud-Init Templates](../proxmox/proxmox-cloud-init.md)).

### 2. Create the template VM
```bash
qm create 9000 --name ubuntu-2404-template --memory 2048 --cores 2 \
  --net0 virtio,bridge=vmbr0 --scsihw virtio-scsi-pci --ostype l26
qm set 9000 --scsi0 local-lvm:0,import-from=/var/lib/vz/template/noble-server-cloudimg-amd64.img
qm set 9000 --ide2 local-lvm:cloudinit
qm set 9000 --boot order=scsi0
qm set 9000 --serial0 socket --vga serial0
qm set 9000 --agent enabled=1
```
`--scsi0 <STORAGE>:0,import-from=` imports the image in one step on current Proxmox VE. On older releases use `qm importdisk` and attach the resulting disk ([Proxmox qm and pct](../proxmox/proxmox-qm-pct.md)).

### 3. Set the cloud-init defaults and convert to a template
```bash
qm set 9000 --ciuser <USER> --sshkeys ~/.ssh/id_ed25519.pub
qm set 9000 --ipconfig0 ip=dhcp
qm template 9000
```
`--sshkeys` takes a path to a file on the node: copy your public key there first. Avoid `--cipassword`; use keys.

### 4. Clone
```bash
qm clone 9000 120 --name web01 --full
qm set 120 --ipconfig0 ip=192.0.2.120/24,gw=192.0.2.1 --nameserver 192.0.2.53 --searchdomain example.com
qm set 120 --memory 4096 --cores 4
```
`--full` makes an independent copy. Without it you get a fast linked clone that depends on the template and cannot be removed while clones exist.

### 5. Resize the disk, then start
```bash
qm disk resize 120 scsi0 +30G
qm start 120
```
The cloud image grows its root partition and filesystem on first boot (`growpart`). The disk can only grow, never shrink.

### 6. Check the guest
```bash
qm agent 120 ping                       # exits 0 once the guest agent responds
qm guest cmd 120 network-get-interfaces # IPs reported by the guest
ssh <USER>@192.0.2.120
df -h /
```
After changing cloud-init values on an existing clone run `qm cloudinit update 120` (the guest applies them only on the next boot of a fresh instance). `qm cloudinit dump 120 user` shows what the guest receives.

### 7. Provision with Ansible
Inventory `inventory.ini`:
```ini
[web]
web01 ansible_host=192.0.2.120 ansible_user=<USER>
```
```bash
ansible -i inventory.ini web -m ping
ansible-playbook -i inventory.ini site.yml --check --diff
ansible-playbook -i inventory.ini site.yml
```
Apply the hardening steps from [New Server Checklist](new-server-checklist.md) as a role, so every clone ends up identical ([Ansible Cheat-Sheet](../tools/ansible.md), [Ansible-Playbook Cheat-Sheet](../tools/ansible-playbook.md)).

### 8. Optional: back up and protect
Add the VM to a backup job (`vzdump`) and start it on boot: `qm set 120 --onboot 1` ([Proxmox Backup and Restore](../proxmox/proxmox-backup.md)). Allow only the needed ports in [Proxmox Firewall](../proxmox/proxmox-firewall.md).

## Verify
```bash
qm status 120                      # status: running
qm config 120 | grep -E 'scsi0|ipconfig0|agent'
ssh <USER>@192.0.2.120 'hostname; lsblk; cloud-init status'
```
`cloud-init status` should report `done`. Check the logs in `/var/log/cloud-init.log` if not.

## Rollback / Cleanup
- Remove a clone: `qm stop 120 && qm destroy 120 --purge`.
- Rebuild the template: remove it with `qm destroy 9000` (only after all linked clones are gone) and repeat steps 1 to 3.
- Delete the downloaded image: `rm /var/lib/vz/template/noble-server-cloudimg-amd64.img`.
- Clones that all share one template SSH key and machine-id behave oddly if you boot the template itself before converting it. Never start the template before `qm template`.

## Related Sheets
- [Proxmox Cloud-Init Templates](../proxmox/proxmox-cloud-init.md) · [Proxmox qm and pct](../proxmox/proxmox-qm-pct.md) · [Proxmox Storage](../proxmox/proxmox-storage.md) · [Proxmox Networking](../proxmox/proxmox-networking.md)
- [Proxmox Backup and Restore](../proxmox/proxmox-backup.md) · [Proxmox Firewall](../proxmox/proxmox-firewall.md) · [Proxmox Troubleshooting and One-Liners](../proxmox/proxmox-troubleshooting.md) · [Proxmox VE Overview and Install](../proxmox/proxmox-overview.md)
- [Ansible Cheat-Sheet](../tools/ansible.md) · [Ansible-Playbook Cheat-Sheet](../tools/ansible-playbook.md) · [Terraform](../tools/terraform.md) · [OpenSSH Cheat-Sheet](../tools/openssh.md)
- [New Server Checklist](new-server-checklist.md) · [K3s Cluster from Scratch](k3s-cluster-from-scratch.md)
- [Backup Strategy](../backup/backup.md) · [VLANs](../homelab/vlans.md) · [Bash](../scripting/bash.md) · [CI/CD Overview](../cicd/cicd.md)

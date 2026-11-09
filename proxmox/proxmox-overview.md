# Proxmox VE Overview and Install
Proxmox VE is an open source virtualisation platform (KVM virtual machines and LXC containers) based on Debian, with a web UI, clustering, ZFS and Ceph. PVE 9.x is based on Debian 13 (trixie), PVE 8.x on Debian 12 (bookworm).

Documentation: [Proxmox VE Docs](https://pve.proxmox.com/pve-docs/) · [Package Repositories](https://pve.proxmox.com/wiki/Package_Repositories)

> **Verification:** repository, upgrade and certificate details were read against the official docs (PVE 9.2 era). No command on this sheet was executed. Not verified: `pvenode acme` option names, `pveam` details. Check `man` pages on your node before relying on them.

Other sheets in this section: [Proxmox qm and pct](proxmox-qm-pct.md) · [Proxmox Storage](proxmox-storage.md) · [Proxmox Disk Image Formats](proxmox-disk-formats.md) · [Proxmox Networking](proxmox-networking.md) · [Proxmox Backup and Restore](proxmox-backup.md) · [Proxmox Clustering and HA](proxmox-cluster-ha.md) · [Proxmox Cloud-Init Templates](proxmox-cloud-init.md) · [Proxmox GPU and PCIe Passthrough](proxmox-passthrough.md) · [Proxmox Users, Permissions, API Tokens and pvesh](proxmox-access-api.md) · [Proxmox Firewall](proxmox-firewall.md) · [Proxmox Troubleshooting and One-Liners](proxmox-troubleshooting.md)

---
## First Run
1. Install from the ISO, then open `https://<NODE-IP>:8006` (log in as `root`, realm *Linux PAM*).
2. Fix repositories (below), then update.
3. Check the hostname resolves to the node IP: `hostname --ip-address` (see [Proxmox Troubleshooting and One-Liners](proxmox-troubleshooting.md)).
4. Optional: ACME certificate, backup job, firewall ([Proxmox Firewall](proxmox-firewall.md)).

COMMAND | DESCRIPTION
---|---
`pveversion` | Short PVE version
`pveversion -v` | All package versions
`hostname --ip-address` | Must return the node's real IP, not `127.0.0.1`
`pvesm status` | Storages (see [Proxmox Storage](proxmox-storage.md))
`pveam update && pveam available --section system` | Refresh and list LXC templates
`pveam download <STORAGE> <TEMPLATE>` | Download a template (for example `local`)

---
## Repositories Without a Subscription

### PVE 9 (trixie, deb822 `.sources` format)
Disable the enterprise repositories (they return 401 without a subscription):
```
/etc/apt/sources.list.d/pve-enterprise.sources
/etc/apt/sources.list.d/ceph.sources
```
Set `Enabled: false` in each file, or delete them. Then create `/etc/apt/sources.list.d/proxmox.sources`:
```
Types: deb
URIs: http://download.proxmox.com/debian/pve
Suites: trixie
Components: pve-no-subscription
Signed-By: /usr/share/keyrings/proxmox-archive-keyring.gpg
```
The Ceph repository has its own `no-subscription` component, see the wiki page above for the current release name.

### PVE 8 (bookworm, one-line format)
```
deb http://download.proxmox.com/debian/pve bookworm pve-no-subscription
```
Put it in `/etc/apt/sources.list` (or a file in `/etc/apt/sources.list.d/`) and comment out the line in `pve-enterprise.list`.

The no-subscription repository is not recommended for production. It is fine for a home lab.

COMMAND | DESCRIPTION
---|---
`apt modernize-sources` | Convert old `.list` files to `.sources` (Debian 13)

---
## Updates
COMMAND | DESCRIPTION
---|---
`apt update` | Refresh package lists
`apt dist-upgrade` | Upgrade PVE (use this or `apt full-upgrade`, not plain `apt upgrade`)
`pve8to9 --full` | Pre-upgrade checker for 8 to 9 (run until it is clean)
`reboot` | Needed after a kernel update

Major upgrade guide: [Upgrade from 8 to 9](https://pve.proxmox.com/wiki/Upgrade_from_8_to_9). In a cluster, upgrade one node at a time and migrate guests off it first ([Proxmox Clustering and HA](proxmox-cluster-ha.md)). Take backups first ([Proxmox Backup and Restore](proxmox-backup.md)).

---
## ACME Certificates
GUI:
1. Datacenter -> ACME -> add account
2. Datacenter -> ACME -> add challenge plugin (for DNS challenges)
3. Node -> Certificates -> ACME -> select account and add domain
4. Node -> Certificates -> ACME -> order certificates now

CLI form:
```bash
pvenode acme account register default <EMAIL>
pvenode config set --acme domains=<FQDN>
pvenode acme cert order
```
For a comparable flow on another platform, see [TrueNAS Community Edition](../infra/truenas-community-edition.md). Compare hypervisors in [Hypervisors Compared](../infra/hypervisor-comparison.md).

---
## Useful Host Basics
COMMAND | DESCRIPTION
---|---
`pvesh get /version` | API version
`pvesh get /nodes` | Nodes and status
`pvenode config get` | Node options
`systemctl status pveproxy pvedaemon pvestatd` | Core service state
`ssh root@<NODE>` | Shell access, general Linux tips in [Linux](../linux/linux.md)

---
## Further information
- Ansible playbook that automates Linux VM updates running on Proxmox (including snapshots): [TheDatabaseMe - update_proxmox_vm](https://github.com/thedatabaseme/update_proxmox_vm). See also [Ansible Cheat-Sheet](../tools/ansible.md).
- Manage Proxmox VM templates with Packer: [Use Packer to build Proxmox images](https://thedatabaseme.de/2022/10/16/what-a-golden-boy-use-packer-to-build-proxmox-images/)
- Provision with [Terraform](../tools/terraform.md) using a Proxmox provider (not covered here).
- Running Docker: prefer a VM, or an LXC with nesting enabled, see [Docker](../docker/docker.md).

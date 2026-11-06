# Proxmox Troubleshooting and One-Liners
Quick checks, logs and recovery steps for a PVE node or cluster.

Documentation: [Proxmox VE Admin Guide](https://pve.proxmox.com/pve-docs/pve-admin-guide.html) · [Package Repositories](https://pve.proxmox.com/wiki/Package_Repositories)

> **Verification:** `pveversion -v`, `qm unlock`, `pvecm updatecerts`, `pvecm delnode`, `pvecm expected` and the node removal steps were checked against the docs. **Not verified against the docs:** `pct` subcommands, `systemctl restart pve-cluster`, the `/etc/pve` read-only note, `qm stop --skiplock`, `/etc/hosts` fixes and the service and log names below (they come from common practice). No command was executed. Back up before destructive recovery steps ([Proxmox Backup and Restore](proxmox-backup.md)).

See also: [Proxmox VE Overview and Install](proxmox-overview.md) · [Proxmox Clustering and HA](proxmox-cluster-ha.md) · [Proxmox Networking](proxmox-networking.md) · [Proxmox Storage](proxmox-storage.md) · [Linux](../linux/linux.md) · [tmux](../tools/tmux.md)

---
## Versions and Health
COMMAND | DESCRIPTION
---|---
`pveversion` | PVE version
`pveversion -v` | All component versions (include in bug reports)
`uname -r` | Running kernel
`pvesh get /cluster/resources` | Everything the cluster knows about
`pvecm status` | Quorum and votes
`pvesm status` | Storage state
`zpool status -x` | ZFS health (only problems)
`smartctl -a /dev/<DISK>` | Disk SMART data
`df -h && free -h` | Space and memory
`uptime` | Load average

---
## Services and Logs
COMMAND | DESCRIPTION
---|---
`systemctl status pveproxy pvedaemon pvestatd pve-cluster` | Core services
`systemctl restart pveproxy pvedaemon` | Restart web UI and API
`systemctl restart pvestatd` | Fix grey question marks on guests and storage
`systemctl restart pve-cluster` | Restart pmxcfs (`/etc/pve`)
`systemctl restart corosync` | Restart cluster membership
`journalctl -u pveproxy -f` | Web UI logs
`journalctl -u pve-cluster -u corosync -b` | Cluster logs since boot
`journalctl -b -p err` | Errors since boot
`journalctl -k \| grep -i -e error -e fail` | Kernel errors
`tail -f /var/log/pve/tasks/active` | Running tasks
`ls /var/log/pve/tasks/` | Task logs

---
## Locks and Stuck Guests
A failed backup, migration or snapshot can leave a lock.

COMMAND | DESCRIPTION
---|---
`qm unlock <VMID>` | Remove a VM lock
`pct unlock <CTID>` | Remove a container lock
`qm stop <VMID> --skiplock` | Force stop a locked VM
`qm config <VMID> \| grep lock` | See the lock reason
`ps aux \| grep "kvm -id <VMID>"` | Find the process if `qm stop` hangs
`kill -9 <PID>` | Last resort for a hung VM process (may corrupt the disk)
`rm /var/lock/qemu-server/lock-<VMID>.conf` | Stale local lock file

Check that no backup or migration is really still running (`Tasks` in the GUI) before unlocking.

---
## Remove a Node from a Cluster
See [Proxmox Clustering and HA](proxmox-cluster-ha.md) for the full procedure. Short form on a **remaining** node, with the dead node powered off:
```bash
pvecm delnode <NODE>
rm -r /etc/pve/nodes/<NODE>
```
Remove its key from `/etc/pve/priv/authorized_keys` too. Reinstall the old node before reusing it.

## Cluster Without Quorum
`/etc/pve` is read-only and guests cannot be started.

COMMAND | DESCRIPTION
---|---
`pvecm status` | Check votes
`pvecm expected 1` | **Emergency:** force quorum on a lone node, undo by restoring the other nodes
`systemctl restart corosync pve-cluster` | After network fixes

Fix the network or add a QDevice instead of forcing quorum whenever you can.

---
## Web UI and SSH Problems
COMMAND | DESCRIPTION
---|---
`pvecm updatecerts --force` | Rebuild node certificates and SSH keys
`hostname --ip-address` | Must not be `127.0.0.1`, fix `/etc/hosts`
`cat /etc/hosts` | Needs `<IP> <FQDN> <HOSTNAME>` for this node
`ss -tlnp \| grep 8006` | Is `pveproxy` listening
`curl -k https://localhost:8006` | Local test, see [curl](../tools/curl.md)
`pve-firewall stop` | Rule out the firewall ([Proxmox Firewall](proxmox-firewall.md))

---
## Repository and Update Errors
- `401 Unauthorized` on `enterprise.proxmox.com`: you have no subscription, disable the enterprise repositories and add the no-subscription one ([Proxmox VE Overview and Install](proxmox-overview.md)).
- `Release file ... not valid yet` or a time error: fix the clock (`timedatectl`, NTP).
- Partial upgrade breakage: `apt update && apt dist-upgrade`, then `dpkg --configure -a`.

## Guest Problems
COMMAND | DESCRIPTION
---|---
`qm showcmd <VMID> --pretty` | See the exact KVM command line
`qm terminal <VMID>` | Serial console
`qm agent <VMID> ping` | Guest agent reachable
`qm rescan` | Fix missing disks after storage changes
`pct enter <CTID>` | Shell into a container
`pct config <CTID>` | Container config
`journalctl -b \| grep -i <VMID>` | Related host logs

Boot a VM from an ISO or live disk to repair it. The storage and disk details are on [Proxmox Storage](proxmox-storage.md) and [Proxmox qm and pct](proxmox-qm-pct.md).

---
## Handy One-Liners
COMMAND | DESCRIPTION
---|---
`qm list \| awk 'NR>1 && $3=="running" {print $1}'` | IDs of running VMs
`for v in $(qm list \| awk 'NR>1 {print $1}'); do qm snapshot $v pre-update; done` | Snapshot all VMs
`pvesh get /cluster/resources --type vm --output-format json \| jq -r '.[].name'` | Guest names ([jq](../tools/jq.md))
`pveam update && pveam available --section system` | Refresh the template list
`ls /etc/pve/qemu-server/ /etc/pve/lxc/` | Guest configs on this node
`cat /etc/pve/storage.cfg` | Storage definitions
`apt list --upgradable` | Pending updates
`last reboot \| head` | Reboot history
`pveperf` | Quick CPU, disk and DNS performance test

Run long jobs inside [tmux](../tools/tmux.md) so an SSH drop does not kill them.

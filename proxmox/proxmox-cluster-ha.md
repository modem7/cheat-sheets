# Proxmox Clustering and HA
A PVE cluster shares configuration through `/etc/pve` (pmxcfs) and uses corosync for membership and quorum. Guests can be migrated, replicated and restarted automatically (HA).

Documentation: [Cluster Manager](https://pve.proxmox.com/pve-docs/chapter-pvecm.html) · [High Availability](https://pve.proxmox.com/pve-docs/chapter-ha-manager.html) · [Storage Replication](https://pve.proxmox.com/pve-docs/chapter-pvesr.html)

> **Verification:** `pvecm` commands, node removal procedure, QDevice setup, `ha-manager` commands, `qm migrate --online` and `pvesr create-local-job` were checked against the docs. **Not verified:** `pct migrate --restart`, `pvesr status`, `pvesr list`, and the `/etc/pve` read-only behaviour without quorum (stated from experience). No command was executed. In PVE 9, HA groups were replaced by HA node-affinity rules, so older group-based guides differ.

See also: [[proxmox-networking]] · [[proxmox-storage]] · [[proxmox-backup]] · [[proxmox-troubleshooting]] · [[proxmox-firewall]]

---
## Requirements
- Same major PVE version on all nodes, all nodes resolvable by name.
- A stable low-latency network for corosync, ideally a dedicated NIC or VLAN, ideally with a second link.
- A new node must have **no guests** when joining (IDs would clash).
- Do not change a node's hostname or IP after joining without reading the docs.
- Open ports: corosync UDP 5405-5412, SSH 22, web/API 8006 ([[proxmox-firewall]]).

---
## Create and Join
COMMAND | DESCRIPTION
---|---
`pvecm create <CLUSTERNAME>` | Create a cluster on the first node
`pvecm create <CLUSTERNAME> --link0 <IP>` | Pick the corosync network address
`pvecm add <EXISTING-NODE-IP>` | On the new node: join (asks for the root@pam password of the existing node)
`pvecm add <EXISTING-NODE-IP> --link0 <NEW-NODE-IP>` | Join and set the corosync address
`pvecm status` | Quorum, votes, cluster name
`pvecm nodes` | Members and node IDs
`pvecm updatecerts` | Re-sync certificates and SSH known hosts

---
## Quorum
A cluster needs more than half the votes to be quorate. Without quorum `/etc/pve` becomes read-only and guests cannot be started or changed (running guests keep running).

COMMAND | DESCRIPTION
---|---
`pvecm expected 1` | **Emergency only:** lower expected votes so a lone node regains quorum
`pvecm status` | Check `Quorate: Yes`

Two-node clusters lose quorum when either node is down. Add a QDevice (third vote) or a third node.

### QDevice
An external tie-breaker (a small VM, a Raspberry Pi, any Debian box not in the cluster).

COMMAND | DESCRIPTION
---|---
`apt install corosync-qnetd` | On the external host
`apt install corosync-qdevice` | On **every** cluster node
`pvecm qdevice setup <QDEVICE-IP>` | On one cluster node, sets it up everywhere
`pvecm qdevice remove` | Remove the QDevice
`pvecm status` | Shows the extra vote

Setup needs root SSH from the cluster to the QDevice host. Do not run the QDevice on a guest that lives in the same cluster.

---
## Remove a Node
1. Migrate or back up guests, then power the node off and **never boot it again on the same network** with its old identity (reinstall it).
2. If a QDevice exists, remove it first. Remove the node from HA rules.
3. On a remaining node:
```bash
pvecm nodes
pvecm delnode <NODE>
```
4. Clean up leftovers on a remaining node:
```bash
rm -r /etc/pve/nodes/<NODE>
# also remove its key from /etc/pve/priv/authorized_keys
```
5. `pvecm status` to confirm votes.

---
## Migration
COMMAND | DESCRIPTION
---|---
`qm migrate <VMID> <TARGET> --online` | Live migrate a VM (shared storage, or add `--with-local-disks`)
`qm migrate <VMID> <TARGET>` | Offline migrate
`pct migrate <CTID> <TARGET> --restart` | Containers restart on the target
`ha-manager crm-command relocate vm:<VMID> <TARGET>` | HA-managed move

Live migration needs compatible CPUs. Use a common CPU type (for example `x86-64-v2-AES`) instead of `host` in mixed clusters. Live migration traffic uses ports 60000-60050 on the migration network.

---
## Storage Replication
Asynchronous replication of guest disks between nodes (ZFS local storage only), giving fast recovery without shared storage. Interval defaults to every 15 minutes.

COMMAND | DESCRIPTION
---|---
`pvesr create-local-job <VMID>-0 <TARGET> --schedule "*/15"` | Create a job (job ID is `<VMID>-<N>`)
`pvesr list` | List jobs
`pvesr status` | Job state
`pvesr delete <VMID>-0` | Delete a job
`pvesr schedule-now <VMID>-0` | Run now

Replication works on ZFS ([[proxmox-storage]]). On failover you can lose up to one interval of data.

---
## High Availability
Needs 3 or more voting nodes (or 2 plus QDevice) and storage reachable from the nodes (shared, or replicated ZFS).

COMMAND | DESCRIPTION
---|---
`ha-manager status` | CRM and LRM state, managed resources
`ha-manager add vm:<VMID> --state started` | Make a VM HA managed
`ha-manager add ct:<CTID> --state started` | Same for a container
`ha-manager set vm:<VMID> --state stopped` | Request a state
`ha-manager remove vm:<VMID>` | Stop managing
`ha-manager config` | List resources
`ha-manager crm-command relocate vm:<VMID> <NODE>` | Move (stops, then starts on the target)
`ha-manager crm-command migrate vm:<VMID> <NODE>` | Live migration when possible

States: `started`, `stopped`, `disabled`, `ignored`. Fenced nodes reboot via the hardware watchdog, so test failover before relying on it. PVE 9 uses HA node-affinity rules in place of groups, see the docs.

---
## Tips
- Take backups before any cluster change ([[proxmox-backup]]).
- Keep SSH between nodes working (`pvecm updatecerts` repairs known_hosts).
- Automate node maintenance with [[ansible]].

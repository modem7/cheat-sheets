# Proxmox Backup and Restore
`vzdump` backs up VMs and containers to any storage with `backup` content, or to Proxmox Backup Server (PBS). Jobs are set under Datacenter -> Backup.

Documentation: [Backup and Restore](https://pve.proxmox.com/pve-docs/chapter-vzdump.html) · [PBS docs](https://pbs.proxmox.com/docs/) · [PBS client](https://pbs.proxmox.com/docs/backup-client.html)

> **Verification:** `vzdump` modes and options, `--prune-backups`, `/etc/vzdump.conf`, the `proxmox-backup-client` syntax, and the PBS garbage collection command were checked against the docs. The `proxmox-backup-manager` commands for datastore, prune-job and verify-job creation were **not** verified, nor were `datastore list`, `garbage-collection status`, `versions`, `vzdump --exclude`, `--mailto`, `qmrestore --unique`, or restoring from a PBS volume ID in the form shown. No command was executed. Always test a restore.

See also: [Proxmox Storage](proxmox-storage.md) · [Proxmox qm and pct](proxmox-qm-pct.md) · [Proxmox Clustering and HA](proxmox-cluster-ha.md) · [Proxmox Troubleshooting and One-Liners](proxmox-troubleshooting.md) · [TrueNAS Community Edition](../infra/truenas-community-edition.md) (offsite replication target)

---
## vzdump
COMMAND | DESCRIPTION
---|---
`vzdump <VMID> --storage <STORAGE> --mode snapshot --compress zstd` | Back up one guest
`vzdump <VMID1> <VMID2> --storage <STORAGE>` | Several guests
`vzdump --all --storage <STORAGE>` | Everything on this node
`vzdump --all --exclude <VMID> --storage <STORAGE>` | Everything except some guests
`vzdump <VMID> --storage <STORAGE> --prune-backups keep-last=3,keep-daily=7,keep-weekly=4` | Back up and prune old ones
`vzdump <VMID> --storage <STORAGE> --notes-template '{{guestname}} on {{node}}'` | Custom notes (`{{cluster}}`, `{{guestname}}`, `{{node}}`, `{{vmid}}`)
`vzdump <VMID> --mailto <EMAIL> --mailnotification failure` | Mail on failure

Modes: `snapshot` (default, guest keeps running), `suspend`, `stop`. Compression: `zstd` is usually the best choice, others are `lzo`, `gzip`.

Defaults for ad-hoc runs go in `/etc/vzdump.conf`, as `key: value` lines:
```
storage: <STORAGE>
compress: zstd
```

---
## Restore
COMMAND | DESCRIPTION
---|---
`qmrestore <ARCHIVE> <VMID> --storage <STORAGE>` | Restore a VM
`qmrestore <ARCHIVE> <VMID> --storage <STORAGE> --unique 1` | Restore as a copy with new MAC addresses
`pct restore <CTID> <ARCHIVE> --storage <STORAGE>` | Restore a container
`pvesm list <STORAGE> --content backup` | Find archives (and PBS volume IDs)
`qmrestore <STORAGE>:backup/vm/<VMID>/<TIMESTAMP> <NEWVMID>` | Restore from a PBS storage volume ID

Use a new ID to restore beside the original. Restoring over an existing ID overwrites it. The GUI **Restore** button on a backup does the same.

---
## Retention
Prune options (job settings, `vzdump --prune-backups`, or on the storage with `--prune-backups`):

OPTION | MEANING
---|---
`keep-last=<N>` | Keep the newest N
`keep-hourly=<N>` | Keep one per hour for N hours
`keep-daily=<N>` | One per day for N days
`keep-weekly=<N>` | One per week
`keep-monthly=<N>` | One per month
`keep-yearly=<N>` | One per year
`keep-all=1` | Disable pruning

Follow the 3-2-1 rule: three copies, two media, one offsite.

---
## Proxmox Backup Server
PBS stores deduplicated, incremental, optionally encrypted backups in datastores. Install it on its own machine (or VM, ideally not on the same disks it protects).

### Connect PVE to PBS
1. On PBS create a datastore, a user (or API token) and give it the `DatastoreBackup` role on `/datastore/<NAME>`.
2. Get the certificate fingerprint: PBS dashboard -> Show Fingerprint.
3. On PVE add the storage:
```bash
pvesm add pbs <STORAGE> --server <PBS-HOST> --datastore <DATASTORE> \
  --username <USER>@pbs --fingerprint <SHA256> --password <PASS>
```
Then `vzdump <VMID> --storage <STORAGE>` or select it in a backup job. PVE can also set a client-side encryption key in the storage options. Store that key safely, without it backups are unreadable.

### PBS maintenance
COMMAND | DESCRIPTION
---|---
`proxmox-backup-manager datastore list` | List datastores
`proxmox-backup-manager garbage-collection start <DATASTORE>` | Reclaim space from pruned chunks
`proxmox-backup-manager garbage-collection status <DATASTORE>` | GC state
`proxmox-backup-manager versions` | Installed versions

Prune, garbage collection, verify and sync jobs are normally scheduled in the PBS GUI (Datastore -> Prune & GC, Verify Jobs, Sync Jobs). Pruning only marks chunks, **garbage collection frees space**.

### proxmox-backup-client (back up a plain Linux host)
```bash
export PBS_REPOSITORY='<USER>@pbs@<PBS-HOST>:<DATASTORE>'
export PBS_FINGERPRINT='<SHA256>'
proxmox-backup-client backup root.pxar:/ --exclude /proc --exclude /sys
```
COMMAND | DESCRIPTION
---|---
`proxmox-backup-client snapshot list` | List snapshots in the repository
`proxmox-backup-client restore host/<NAME>/<TIME> root.pxar /restore/path` | Restore an archive
`proxmox-backup-client prune host/<NAME> --keep-daily 7 --keep-weekly 4` | Prune a group
`proxmox-backup-client key create` | Create an encryption key

The password comes from `PBS_PASSWORD` or a prompt. General host tooling: [Linux](../linux/linux.md).

---
## Tips
- Back up before major changes and upgrades ([Proxmox VE Overview and Install](proxmox-overview.md)).
- Snapshot-mode backups of VMs get consistent filesystems only with the guest agent enabled.
- Exclude disks you do not need with `backup=0` on that disk (`qm set <VMID> --scsi1 <STORAGE>:vm-<VMID>-disk-1,backup=0`).
- Automate guest updates with snapshots using [Ansible Cheat-Sheet](../tools/ansible.md).

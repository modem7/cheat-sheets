# Ceph
Ceph is a distributed storage system that provides block (RBD), file (CephFS) and object (RGW) storage from commodity servers, with data replicated across hosts. In a homelab it usually appears as hyper-converged storage on a [Proxmox cluster](../proxmox/proxmox-cluster-ha.md). It needs several nodes and a fast network, and is overkill for a single box, where [ZFS](zfs.md) is simpler.

Documentation: [Ceph docs](https://docs.ceph.com/en/latest/) (the `latest` docs are a development version, so pick your release), [Proxmox Ceph guide](https://pve.proxmox.com/wiki/Deploy_Hyper-Converged_Ceph_Cluster)

## Sizing and Requirements
- At least three servers, preferably identical (Proxmox guidance). Three or five monitors are typical, and three are needed for quorum.
- A network of 10 Gbps or faster for Ceph traffic (Proxmox guidance). A separate cluster network (`--cluster-network`) helps.
- Each OSD (one per disk) needs about 4 GiB of RAM by default, and Proxmox suggests at least 8 GiB per OSD to be comfortable.
- Pools keep 3 copies (`size 3`). Setting `size` to 2 or `min_size` to 1 in production risks data loss.
- Time must be in sync across nodes, see [chrony](chrony.md).

## Deploy with cephadm
Needs Python 3.9 or later, systemd, Podman or Docker, time sync, LVM2 and SSH.

COMMAND | DESCRIPTION
---|---
`cephadm bootstrap --mon-ip <MON_IP>` | Create the first monitor and manager, and write `/etc/ceph/ceph.conf` and the admin keyring
`cephadm bootstrap --mon-ip <MON_IP> --single-host-defaults` | Single-host test cluster (size 2, not for production)
`cephadm shell -- ceph -s` | Run a Ceph command inside the cephadm shell
`ceph orch host label add <HOST> _admin` | Give a host the admin keyring
`ceph orch apply osd --all-available-devices` | Create OSDs on every unused disk (**wipes them**)

Bootstrap turns on memory auto-tuning at 0.7 of host RAM. On converged hosts lower it with `ceph config set mgr mgr/cephadm/autotune_memory_target_ratio 0.2`. The `ceph orch host add` syntax was not checked here, so see the cephadm host-management page.

## Status and Health
COMMAND | DESCRIPTION
---|---
`ceph -s` / `ceph status` | Cluster state at a glance
`ceph health detail` | Why the cluster is not `HEALTH_OK`
`ceph df` | Space by pool
`ceph osd tree` | OSDs by host (standard command, not checked in this pass)
`ceph health mute <CODE> 1w` | Silence a warning for a week
`ceph osd set <FLAG>` / `ceph osd unset <FLAG>` | Set or clear flags such as `noout` (use `noout` during planned maintenance)

## Pools
COMMAND | DESCRIPTION
---|---
`ceph osd pool create <POOL>` | Create a replicated pool (the default `pg_num` of 32 is unsuitable for most systems)
`ceph osd pool ls detail` | List pools with settings
`ceph osd pool set <POOL> size 3` / `min_size 2` | Replica count and minimum for I/O
`ceph osd pool get <POOL> <KEY>` | Read a setting
`ceph osd pool application enable <POOL> rbd` | Tag the pool use (`rbd`, `cephfs`, `rgw`)
`ceph osd pool set-quota <POOL> max_bytes <BYTES>` | Cap a pool's size
`ceph osd pool delete` | **Destroys data**; needs `mon_allow_pool_delete`

## CephFS
COMMAND | DESCRIPTION
---|---
`ceph fs volume create <VOLUME>` | Create a file system, with its pools and MDS
`ceph fs volume ls` / `ceph fs volume info <VOLUME>` | List and inspect
`ceph fs subvolume create <VOLUME> <SUBVOL>` | Create a subvolume
`ceph fs volume rm <VOLUME> --yes-i-really-mean-it` | **Delete** a file system

## Proxmox pveceph
Proxmox wraps Ceph in `pveceph`, and the web UI exposes the same steps. Quoted from the Proxmox wiki:

```bash
pveceph install
pveceph init --network <CEPH_NETWORK_CIDR>
pveceph mon create
pveceph mgr create
```

Further commands from a summary of that page (confirm with `pveceph help`): `pveceph osd create /dev/sdX`, `pveceph pool create <POOL> --add_storages`, `pveceph mds create`, `pveceph fs create --pg_num 128 --add-storage`. Proxmox defaults are 128 placement groups, size 3 and min_size 2.

## Common Health Warnings
CODE | MEANING AND FIX
---|---
`MON_DOWN` | A monitor is down. A majority must be up
`MON_CLOCK_SKEW` | Clocks differ. Fix time sync with [chrony](chrony.md)
`MON_DISK_LOW` | Monitor disk is under 30% free (`mon_data_avail_warn`)
`MGR_DOWN` | No manager, so the dashboard will not work
`OSD_DOWN` | Check the host, the daemon and the network. Logs are in `/var/log/ceph/`
`OSD_NEARFULL`, `OSD_BACKFILLFULL`, `OSD_FULL` | Disks filling up. Check `ceph df` and add capacity
`POOL_FULL` | A pool hit its quota. Raise it with `ceph osd pool set-quota`
`POOL_APP_NOT_ENABLED` | Run `ceph osd pool application enable` (or `rbd pool init`)
`OSDMAP_FLAGS` | A flag such as `noout` is set. Clear with `ceph osd unset <FLAG>`
`AUTH_INSECURE_GLOBAL_ID_RECLAIM` | Update clients, then `ceph config set mon auth_allow_insecure_global_id_reclaim false`

RBD (`rbd`) and RGW commands were not checked in this pass, so see the Ceph docs for those.

## See Also
- [Proxmox Cluster and HA](../proxmox/proxmox-cluster-ha.md)
- [Proxmox Storage](../proxmox/proxmox-storage.md)
- [ZFS](zfs.md)
- [Storage and Filesystems](storage-and-filesystems.md)

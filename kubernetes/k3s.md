# K3S
Lightweight [Kubernetes](kubernetes.md). Production ready, easy to install, half the memory, all in a binary less than 100 MB.

Project Homepage: [K3s.io](https://www.k3s.io/)
Documentation: [K3s Documentation](https://docs.k3s.io/)

---
## Installation
To install k3s, you can follow different approaches.

**K3s with external DB ([Install K3S in High Availability Mode](k3s-install-ha-externaldb.md))** - Set up an HA K3s cluster backed by an external datastore such as MySQL, PostgreSQL, or etcd.

**K3s with embedded DB ([Install K3S in High Availability Mode with an embedded Database](k3s-install-ha-embeddeddb.md))** - Set up an HA K3s cluster that leverages a built-in distributed database.

**K3s single node** ([K3S Single-Node Installation](k3s-install-single.md)) - Set up K3s as a single node installation.

---
## What is Bundled
COMPONENT | DEFAULT | DISABLE WITH
---|---|---
Ingress | [Traefik](../apps/traefik.md) | `--disable traefik`
Service load balancer | ServiceLB (klipper) | `--disable servicelb`
Storage | local-path-provisioner | `--disable local-storage` (use [Longhorn](../apps/longhorn.md))
Metrics | metrics-server | `--disable metrics-server`
CNI | Flannel | `--flannel-backend=none` (to install Cilium/Calico)
DNS | CoreDNS, see [Kubernetes DNS](kubernetes-dns.md) | n/a

Make flags permanent in `/etc/rancher/k3s/config.yaml`:
```yaml
write-kubeconfig-mode: "0644"
tls-san:
  - k3s.example.com
disable:
  - traefik
```

## Manage K3S
### Management on Server Nodes
`k3s kubectl`

### Download Kube Config
`/etc/rancher/k3s/k3s.yaml`

Replace `127.0.0.1` with the server address when using it remotely.

COMMAND | DESCRIPTION
---|---
`sudo systemctl status k3s` / `k3s-agent` | Service state on server / agent
`sudo journalctl -u k3s -f` | Logs
`sudo k3s kubectl get nodes -o wide` | Nodes
`sudo cat /var/lib/rancher/k3s/server/node-token` | Join token
`sudo k3s check-config` | Check kernel requirements
`kubectl label node <NODE> node-role.kubernetes.io/worker=worker` | Label a worker so `get nodes` shows its role
`sudo k3s crictl ps` | Containers via the embedded runtime
`sudo k3s crictl images` | Images on the node
`/usr/local/bin/k3s-killall.sh` | Stop everything on the node
`/usr/local/bin/k3s-uninstall.sh` | Uninstall a server

## Private Registry
`/etc/rancher/k3s/registries.yaml`
```yaml
mirrors:
  docker.io:
    endpoint:
      - "https://registry.example.com"
configs:
  "registry.example.com":
    auth:
      username: <USER>
      password: <PASSWORD>
```
Restart K3s after editing.

## Upgrades
- Manual: re-run the install script with `INSTALL_K3S_VERSION=<VERSION>` (servers first, then agents).
- Automated: install the `system-upgrade-controller` and apply `Plan` resources.

## Database Backups

### etcd snapshots
Stored in `/var/lib/rancher/k3s/server/db/snapshots`.

COMMAND | DESCRIPTION
---|---
`sudo k3s etcd-snapshot save --name <NAME>` | Take a snapshot now
`sudo k3s etcd-snapshot ls` | List snapshots
`sudo k3s server --cluster-reset --cluster-reset-restore-path=<SNAPSHOT>` | Restore (stop K3s on all servers first)

Scheduled snapshots are on by default every 12 hours (`etcd-snapshot-schedule-cron`, `etcd-snapshot-retention`). Single-node installs use SQLite: back up `/var/lib/rancher/k3s/server/db/`.

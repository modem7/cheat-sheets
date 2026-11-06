# K3S Single-Node Installation
Install a single-server [[k3s]] cluster. For high availability see [[k3s-install-ha-embeddeddb]] or [[k3s-install-ha-externaldb]].

Documentation: [K3s Quick-Start](https://docs.k3s.io/quick-start)

## Requirements
- Linux host with 1 CPU / 512 MB RAM minimum (2 CPU / 2 GB recommended)
- Ports open between nodes: `6443/tcp` (API), `8472/udp` (flannel VXLAN), `10250/tcp` (kubelet)
- Hostname unique per node

## Install the Server
```bash
curl -sfL https://get.k3s.io | sh -
```
Pin a version:
```bash
curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION=v1.31.4+k3s1 sh -
```
Disable the bundled Traefik or ServiceLB if you bring your own:
```bash
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--disable traefik --disable servicelb" sh -
```

## Verify
```bash
sudo systemctl status k3s
sudo k3s kubectl get nodes
```

## Use kubectl Without sudo
```bash
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown "$USER": ~/.kube/config
chmod 600 ~/.kube/config
```
To use it from another machine, copy the file and replace `127.0.0.1` in `server:` with the server's IP or DNS name.

## Add an Agent (Worker) Node
Get the token on the server:
```bash
sudo cat /var/lib/rancher/k3s/server/node-token
```
Run on the worker:
```bash
curl -sfL https://get.k3s.io | K3S_URL=https://<SERVER-IP>:6443 K3S_TOKEN=<TOKEN> sh -
```

## Useful Paths
PATH | DESCRIPTION
---|---
`/etc/rancher/k3s/k3s.yaml` | Kubeconfig
`/etc/rancher/k3s/config.yaml` | Server config (flags as YAML keys)
`/var/lib/rancher/k3s/server/manifests/` | Manifests here are auto-applied
`/var/lib/rancher/k3s/server/node-token` | Join token
`/var/lib/rancher/k3s/server/db/` | SQLite datastore (single node)

## Maintenance
COMMAND | DESCRIPTION
---|---
`sudo journalctl -u k3s -f` | Server logs
`sudo k3s etcd-snapshot save` | Snapshot (embedded etcd only)
`sudo systemctl restart k3s` | Restart
`/usr/local/bin/k3s-killall.sh` | Stop all K3s processes and containers
`/usr/local/bin/k3s-uninstall.sh` | Uninstall server
`/usr/local/bin/k3s-agent-uninstall.sh` | Uninstall agent

## Upgrade
Re-run the install script with a newer `INSTALL_K3S_VERSION` (or none for latest stable). For clusters, use the `system-upgrade-controller`.

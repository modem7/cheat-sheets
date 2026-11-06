# Longhorn
Longhorn is a lightweight, reliable and easy-to-use distributed block storage system for **Kubernetes ([[kubernetes]])**.

Project Homepage: [Longhorn Homepage](https://longhorn.io)
Documentation: [Longhorn Docs](https://longhorn.io/docs/)

---
## Prerequisites
Each node needs `open-iscsi` and an NFS client (for RWX volumes):
```bash
sudo apt install -y open-iscsi nfs-common
sudo systemctl enable --now iscsid
```
Check the cluster with the official script:
```bash
curl -sSfL https://raw.githubusercontent.com/longhorn/longhorn/v1.7.2/scripts/environment_check.sh | bash
```
(Replace the version with the one you are installing.)

## Install with Helm ([[helm]])
```bash
helm repo add longhorn https://charts.longhorn.io
helm repo update
helm install longhorn longhorn/longhorn -n longhorn-system --create-namespace
kubectl -n longhorn-system get pods
```

## Access the UI
```bash
kubectl -n longhorn-system port-forward svc/longhorn-frontend 8080:80
```
The UI has no authentication by default. Protect any Ingress with basic auth or an auth proxy.

## StorageClass
COMMAND | DESCRIPTION
---|---
`kubectl get storageclass` | `longhorn` is installed and can be the default
`kubectl patch storageclass longhorn -p '{"metadata":{"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'` | Make it the default
`kubectl patch storageclass local-path -p '{"metadata":{"annotations":{"storageclass.kubernetes.io/is-default-class":"false"}}}'` | Unset the K3s default ([[k3s]])

Example claim:
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data
spec:
  accessModes: [ReadWriteOnce]
  storageClassName: longhorn
  resources:
    requests:
      storage: 5Gi
```

## Operations
- **Replicas**: default is 3 per volume. Set 2 on small clusters via a custom StorageClass (`numberOfReplicas: "2"`).
- **Snapshots and backups**: configure a backup target (S3 or NFS) in **Settings > General**, then add recurring jobs.
- **Draining a node**: use the UI **Node > Disable scheduling / Evict** before maintenance.
- **Volume stuck attaching**: check `kubectl -n longhorn-system get volumes.longhorn.io` and instance-manager pod logs.

# Rancher
**Rancher**, the open-source multi-cluster orchestration platform, lets operations teams deploy, manage and secure enterprise **Kubernetes ([[kubernetes]])**.

Project Homepage: [Rancher Homepage](https://www.rancher.com)
Documentation: [Rancher Docs](https://ranchermanager.docs.rancher.com)

---
## Install on Kubernetes with Helm
Needs cert-manager first ([[cert-manager]]), and a hostname that resolves to the cluster ([[helm]], [[k3s]]).
```bash
helm repo add rancher-stable https://releases.rancher.com/server-charts/stable
helm repo update
helm install cert-manager oci://quay.io/jetstack/charts/cert-manager -n cert-manager --create-namespace --set crds.enabled=true
helm install rancher rancher-stable/rancher -n cattle-system --create-namespace \
  --set hostname=rancher.example.com \
  --set bootstrapPassword=<PASSWORD> \
  --set replicas=3
kubectl -n cattle-system rollout status deploy/rancher
```
Rancher must be installed on a Rancher-supported Kubernetes version. Check the support matrix before picking your K3s/RKE2 version.

## Quick Test Install (Docker)
```bash
docker run -d --restart=unless-stopped --privileged -p 80:80 -p 443:443 rancher/rancher:latest
docker logs <CONTAINER> 2>&1 | grep "Bootstrap Password:"
```
For testing only.

## Reset the Admin Password
```bash
kubectl -n cattle-system exec $(kubectl -n cattle-system get pods -l app=rancher --no-headers | head -1 | awk '{print $1}') -c rancher -- reset-password
```

## Remove Installation
```
kubectl delete validatingwebhookconfiguration rancher.cattle.io
kubectl delete mutatingwebhookconfiguration rancher.cattle.io
```
Then uninstall the chart and clean up leftover `cattle-*` namespaces with the official [rancher-cleanup](https://github.com/rancher/rancher-cleanup) job:
```bash
helm uninstall rancher -n cattle-system
```

## Useful kubectl
COMMAND | DESCRIPTION
---|---
`kubectl -n cattle-system get pods` | Rancher pods
`kubectl -n cattle-system logs -l app=rancher -f` | Rancher logs
`kubectl get settings.management.cattle.io server-version` | Installed Rancher version

# K3s Cluster from Scratch
Build a K3s cluster starting with one node, then grow it to three servers (HA with embedded etcd) plus agents, reach it with `kubectl`, and add ingress with TLS, persistent storage, GitOps and monitoring.

Documentation: [K3s docs](https://docs.k3s.io/) · [HA embedded etcd](https://docs.k3s.io/datastore/ha-embedded) · [Requirements](https://docs.k3s.io/installation/requirements)

## Goal
A working cluster with `kubectl` access from your workstation, HTTPS ingress with automatic certificates, replicated storage, Argo CD and a metrics stack.

## Prerequisites
- Three Ubuntu 24.04 hosts, 2 CPU / 2 GB RAM or more each: `k3s-1` (`192.0.2.11`), `k3s-2` (`192.0.2.12`), `k3s-3` (`192.0.2.13`), prepared as in [[new-server-checklist]] (or cloned with [[proxmox-vm-template-and-clone]]); a fixed address or DNS name for the API, `k3s.example.com` (`192.0.2.10`, a virtual IP, load balancer or DNS round-robin)
- Unique hostnames, synchronised clocks, no swap issues
- Ports between nodes: `6443/tcp` (API), `10250/tcp` (kubelet), `8472/udp` (flannel VXLAN), and for embedded etcd `2379-2380/tcp` between servers
- `kubectl` and `helm` on your workstation ([[kubectl]], [[helm]])

A single node is fine to start. Skip the server join steps if you only want one.

## Steps
### 1. First server
Use `--cluster-init` from the start if you may want HA later. A default single-node install uses SQLite; K3s can migrate it to embedded etcd by restarting with `--cluster-init`, but starting with it is simpler ([[k3s-install-ha-embeddeddb]]):
```bash
curl -sfL https://get.k3s.io | K3S_TOKEN=<SECRET> sh -s - server \
  --cluster-init \
  --tls-san k3s.example.com --tls-san 192.0.2.10
sudo k3s kubectl get nodes
```
For a plain single node without HA: `curl -sfL https://get.k3s.io | sh -` ([[k3s-install-single]]). K3s bundles Traefik (ingress), ServiceLB, CoreDNS, metrics-server and the local-path storage provisioner. Add `--disable traefik` to the install command if you bring your own ingress ([[k3s]]).

### 2. Join more servers (HA)
```bash
curl -sfL https://get.k3s.io | K3S_TOKEN=<SECRET> sh -s - server \
  --server https://192.0.2.11:6443 \
  --tls-san k3s.example.com --tls-san 192.0.2.10
```
Use an **odd** number of servers (3 or 5) so etcd keeps quorum: three servers tolerate one failure. Servers also run workloads unless you taint them.

### 3. Add agents (workers), optional
```bash
curl -sfL https://get.k3s.io | K3S_URL=https://k3s.example.com:6443 K3S_TOKEN=<SECRET> sh -s - agent
```
The token is also in `/var/lib/rancher/k3s/server/node-token` on a server. Keep it secret.

### 4. kubectl from your workstation
```bash
mkdir -p ~/.kube
scp <USER>@192.0.2.11:/etc/rancher/k3s/k3s.yaml ~/.kube/k3s.yaml     # may need sudo cp on the server first
sed -i 's#https://127.0.0.1:6443#https://k3s.example.com:6443#' ~/.kube/k3s.yaml
chmod 600 ~/.kube/k3s.yaml
export KUBECONFIG=~/.kube/k3s.yaml
kubectl get nodes -o wide
```
The `--tls-san` flags in steps 1 and 2 are what make the API certificate valid for `k3s.example.com`. Without them you get `x509: certificate is valid for ... not ...` ([[tls-troubleshooting]]). The file is readable by root only on the server, so copy it via an account with sudo.

### 5. Ingress (Traefik, bundled)
Check that the bundled Traefik is running, then publish a test app:
```bash
kubectl -n kube-system get pods,svc -l app.kubernetes.io/name=traefik
kubectl create deployment hello --image=nginx:1.27 --port=80
kubectl expose deployment hello --port=80
kubectl create ingress hello --class=traefik --rule="hello.example.com/*=hello:80"
curl -H 'Host: hello.example.com' http://192.0.2.11/
```
Point `hello.example.com` (DNS) at the node or VIP. See [[traefik]] and [[kubernetes]].

### 6. TLS with cert-manager
```bash
helm repo add jetstack https://charts.jetstack.io && helm repo update
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager --create-namespace --set crds.enabled=true
kubectl -n cert-manager get pods
```
Then create a staging `ClusterIssuer` (HTTP-01 against the `traefik` class), request a certificate by annotating the Ingress with `cert-manager.io/cluster-issuer`, and switch to the production issuer when it works ([[cert-manager]]).

### 7. Persistent storage with Longhorn
K3s ships `local-path`, which is not replicated. For replicated volumes install Longhorn after meeting its node prerequisites:
```bash
# on every node
sudo apt install -y nfs-common open-iscsi
sudo systemctl enable --now iscsid
# from the workstation
helm repo add longhorn https://charts.longhorn.io && helm repo update
helm install longhorn longhorn/longhorn -n longhorn-system --create-namespace
kubectl -n longhorn-system get pods
kubectl get storageclass
```
Run Longhorn's preflight check first (`longhornctl check preflight`, see the install docs) and open the UI with a port-forward. Details and the default-StorageClass choice are in [[longhorn]].

### 8. GitOps with Argo CD
```bash
kubectl create namespace argocd
kubectl apply -n argocd --server-side --force-conflicts \
  -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl -n argocd get pods
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d; echo
kubectl -n argocd port-forward svc/argocd-server 8080:443
```
Pin a release tag instead of `stable` for reproducible installs. Then declare your apps in Git ([[argocd]]).

### 9. Monitoring pointers
- Metrics and dashboards: the `kube-prometheus-stack` Helm chart from `https://prometheus-community.github.io/helm-charts` installs Prometheus, Alertmanager, Grafana and node exporters in one release ([[prometheus]], [[grafana]]).
- Day-to-day: `kubectl top nodes` (metrics-server is bundled), and [[k9s]] for a terminal UI.
- Cluster DNS problems: [[kubernetes-dns]], [[dns-troubleshooting]].

## Verify
```bash
kubectl get nodes -o wide                 # all Ready
kubectl get pods -A                       # nothing stuck in Pending or CrashLoopBackOff
kubectl get --raw='/readyz?verbose' | tail -n 3
sudo k3s kubectl get nodes                # on a server, bypassing your kubeconfig
curl -sI https://hello.example.com | head -n 1
```
For HA, reboot or stop one server (`sudo systemctl stop k3s`), confirm `kubectl get nodes` through the VIP still works, then start it again.

## Rollback / Cleanup
```bash
sudo /usr/local/bin/k3s-uninstall.sh          # on servers
sudo /usr/local/bin/k3s-agent-uninstall.sh    # on agents
```
These remove K3s and its data on that node, including etcd and local volumes. Drain and delete a node first when removing it from a live cluster: `kubectl drain <NODE> --ignore-daemonsets --delete-emptydir-data && kubectl delete node <NODE>`. Remove one Helm release with `helm uninstall <RELEASE> -n <NAMESPACE>` (CRDs and PVCs can remain; check before deleting). Back up `/var/lib/rancher/k3s/server/db/snapshots` or use `k3s etcd-snapshot save` before upgrades.

## Related Sheets
- [[k3s]] · [[k3s-install-single]] · [[k3s-install-ha-embeddeddb]] · [[k3s-install-ha-externaldb]]
- [[kubectl]] · [[kubernetes]] · [[kubernetes-automation]] · [[k9s]] · [[kind]] · [[helm]]
- [[traefik]] · [[cert-manager]] · [[longhorn]] · [[argocd]] · [[prometheus]] · [[grafana]] · [[rancher]]
- [[new-server-checklist]] · [[proxmox-vm-template-and-clone]] · [[tls-troubleshooting]] · [[dns-troubleshooting]]

# Kubectl
Kubectl is a command line tool for communicating with a Kubernetes ([[kubernetes]]) cluster's control plane, using the Kubernetes API.

Documentation: [Kubectl Reference](https://kubernetes.io/docs/reference/kubectl/)

---
## Installation

### On Windows (PowerShell)
Install Kubectl with **Chocolatey** ([[chocolatey]]):
```powershell
choco install kubernetes-cli
```

### On Linux
> [!INFO] Installing on WSL2
> On WSL2 you can install Docker Desktop ([[docker-desktop]]) on Windows and enable its WSL integration, which provides kubectl inside the distro. See [[wsl]].

1. Download the latest release
```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
```

2. Install Kubectl
```bash
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```
Use `linux/arm64` in the URL on ARM machines. kubectl is supported within one minor version of the cluster's API server.

### On macOS
Install Kubectl with **Homebrew ([[homebrew]])**:
```zsh
brew install kubernetes-cli
```

### Shell Completion and Alias
```bash
source <(kubectl completion bash)   # zsh: source <(kubectl completion zsh)
alias k=kubectl
complete -o default -F __start_kubectl k
```

---
## Config Management

### Multiple Config Files

**On Windows (PowerShell)**
```powershell
$env:KUBECONFIG = "$HOME/.kube/config;$HOME/.kube/cluster-a.yaml;$HOME/.kube/cluster-b.yaml"
```

**On Linux / macOS**
```bash
export KUBECONFIG=~/.kube/config:~/.kube/cluster-a.yaml:~/.kube/cluster-b.yaml
```

Merge them into one file:
```bash
KUBECONFIG=~/.kube/config:~/.kube/new.yaml kubectl config view --flatten > /tmp/merged && mv /tmp/merged ~/.kube/config
```

### Contexts
COMMAND | DESCRIPTION
---|---
`kubectl config get-contexts` | List contexts
`kubectl config current-context` | Show the active context
`kubectl config use-context <CONTEXT>` | Switch cluster
`kubectl config set-context --current --namespace=<NS>` | Set the default namespace for this context
`kubectl config view --minify` | Show only the active context's config

[kubectx and kubens](https://github.com/ahmetb/kubectx) make switching faster. See also [[k9s]].

---
## Commands

### Networking

Connect to services using the Kubernetes internal DNS name (see [[kubernetes-dns]]):
`<service-name>.<namespace>.svc.cluster.local`

COMMAND | DESCRIPTION
---|---
`kubectl run tmp-shell --rm -it --image nicolaka/netshoot -- /bin/bash` | Throwaway troubleshooting pod with network tools
`kubectl port-forward svc/<SERVICE> 8080:80` | Forward local 8080 to a service port
`kubectl port-forward pod/<POD> 8080:80` | Forward to a pod
`kubectl get svc,ingress -A` | List services and ingresses

### Containers

COMMAND | DESCRIPTION
---|---
`kubectl rollout restart deploy <DEPLOYMENT>` | Restart a deployment with a rolling update (preferred)
`kubectl scale deploy <DEPLOYMENT> --replicas=0` | Stop all pods (set back to 1 or more to start)
`kubectl exec -it <POD> -- <COMMAND>` | Run a command in a pod
`kubectl exec -it <POD> -c <CONTAINER> -- /bin/bash` | Shell into a specific container (use `/bin/sh` if there is no bash)
`kubectl cp <POD>:/path/file ./file` | Copy a file out of a pod
`kubectl debug -it <POD> --image=busybox --target=<CONTAINER>` | Attach an ephemeral debug container

### Config and Cluster Management
COMMAND | DESCRIPTION
---|---
`kubectl cluster-info` | Display endpoint information about the control plane and services
`kubectl config view` | Get the kubeconfig
`kubectl version` | Client and server versions
`kubectl get nodes -o wide` | List nodes with IPs and versions
`kubectl top nodes` / `kubectl top pods -A` | CPU and memory use (needs metrics-server)
`kubectl api-resources` | List all resource types and their short names
`kubectl explain pod.spec.containers` | Built-in field documentation
`kubectl cordon <NODE>` | Mark a node unschedulable
`kubectl drain <NODE> --ignore-daemonsets --delete-emptydir-data` | Evict pods before maintenance
`kubectl uncordon <NODE>` | Make the node schedulable again

### Resource Management
COMMAND | DESCRIPTION
---|---
`kubectl get all --all-namespaces` | List common workload resources in all namespaces (not literally every resource type)
`kubectl get <RESOURCE> -n <NS> -o wide` | List with more columns
`kubectl get <RESOURCE> <NAME> -o yaml` | Show the full manifest
`kubectl describe <RESOURCE> <NAME>` | Details and recent events
`kubectl apply -f <FILE-OR-DIR>` | Create or update from manifests
`kubectl apply -k <DIR>` | Apply a kustomize directory
`kubectl diff -f <FILE>` | Show what an apply would change
`kubectl edit <RESOURCE> <NAME>` | Edit live in your editor
`kubectl delete -f <FILE>` | Delete what a manifest defines
`kubectl delete <RESOURCE> <NAME> --grace-period=0 --force` | Force the deletion of a resource (last resort)
`kubectl create deploy web --image=nginx --dry-run=client -o yaml` | Generate a manifest without creating anything
`kubectl label <RESOURCE> <NAME> key=value` | Add a label
`kubectl get pods -l app=web` | Select by label
`kubectl rollout status deploy <DEPLOYMENT>` | Watch a rollout
`kubectl rollout undo deploy <DEPLOYMENT>` | Roll back

### Output Formatting
COMMAND | DESCRIPTION
---|---
`-o wide` | Extra columns
`-o yaml` / `-o json` | Full object
`-o name` | Only `resource/name`
`-o jsonpath='{.items[*].metadata.name}'` | Extract fields
`-o custom-columns=NAME:.metadata.name,IMAGE:.spec.containers[*].image` | Custom table
`--sort-by=.metadata.creationTimestamp` | Sort the list
`-w` | Watch for changes

### Secrets
```bash
kubectl get secret <NAME> -o jsonpath='{.data.password}' | base64 -d
kubectl create secret generic <NAME> --from-literal=password=<VALUE>
kubectl create secret tls <NAME> --cert=tls.crt --key=tls.key
```

---
## List of Kubernetes Resources "Short Names"
Run `kubectl api-resources` for the list on your cluster.

Short Name | Long Name
---|---
`cm`|`configmaps`
`cj`|`cronjobs`
`crd`|`customresourcedefinitions`
`csr`|`certificatesigningrequests`
`ds`|`daemonsets`
`deploy`|`deployments`
`ep`|`endpoints`
`ev`|`events`
`hpa`|`horizontalpodautoscalers`
`ing`|`ingresses`
`limits`|`limitranges`
`netpol`|`networkpolicies`
`ns`|`namespaces`
`no`|`nodes`
`pvc`|`persistentvolumeclaims`
`pv`|`persistentvolumes`
`po`|`pods`
`pdb`|`poddisruptionbudgets`
`quota`|`resourcequotas`
`rs`|`replicasets`
`rc`|`replicationcontrollers`
`sa`|`serviceaccounts`
`sc`|`storageclasses`
`sts`|`statefulsets`
`svc`|`services`

`cs` (componentstatuses) is deprecated and `psp` (podsecuritypolicies) was removed in Kubernetes 1.25.

---
## Logs and Troubleshooting

### Logs
COMMAND | DESCRIPTION
---|---
`kubectl logs <POD>` | Pod logs
`kubectl logs -f <POD>` | Follow
`kubectl logs <POD> -c <CONTAINER>` | A specific container
`kubectl logs <POD> --previous` | Logs of the last crashed container
`kubectl logs -l app=web --tail=100` | Logs from all pods matching a label
`kubectl get events -A --sort-by=.lastTimestamp` | Recent cluster events
`kubectl describe pod <POD>` | Why a pod is Pending or crashing (see Events)

### MySQL Client
```bash
kubectl run -it --rm --image=mysql:8 --restart=Never mysql-client -- mysql -u USERNAME -h HOSTNAME -p
```
See [[mariadb]].

### PostgreSQL Client
```bash
kubectl run -it --rm --image=postgres:16 --restart=Never psql-client -- psql -U USERNAME -h HOSTNAME -d DBNAME
```
See [[postgres]].

### Networking
```bash
kubectl run -it --rm --image=nicolaka/netshoot netshoot -- /bin/bash
```

### Common Pod States
STATE | MEANING
---|---
`Pending` | Not scheduled: no resources, taint or unbound PVC. See `describe pod`
`ImagePullBackOff` | Wrong image name or tag, or missing registry credentials
`CrashLoopBackOff` | Container keeps exiting. Check `logs --previous`
`OOMKilled` | Exceeded its memory limit
`Terminating` (stuck) | Finalizers or an unreachable node. See below

---
## Resources stuck in Terminating state

### Namespaces
1. Save the namespace in a `YOUR-NAMESPACE.json` file.
```bash
kubectl get ns YOUR-NAMESPACE -o json > YOUR-NAMESPACE.json
```

2. Edit `YOUR-NAMESPACE.json` and remove the entries in the `finalizers` list (`spec.finalizers`).

3. Update the namespace.
```bash
kubectl replace --raw "/api/v1/namespaces/YOUR-NAMESPACE/finalize" -f ./YOUR-NAMESPACE.json
```
First check what is blocking deletion: `kubectl api-resources --verbs=list --namespaced -o name | xargs -n1 kubectl get -n YOUR-NAMESPACE --ignore-not-found`.

### Other Resources
```bash
kubectl patch <RESOURCE> <NAME> -p '{"metadata":{"finalizers":null}}' --type=merge
```

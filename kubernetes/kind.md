# Kind

Using the Kind project, you can easily deploy a Kubernetes cluster on top of Docker. Kind starts separate containers that act as the Kubernetes nodes. This document gives some examples, plus a link to an Ansible ([Ansible Cheat-Sheet](../tools/ansible.md)) playbook that can do the cluster creation and deletion for you. It only covers the basics; for more detail see the [official Kind documentation](https://kind.sigs.k8s.io/docs/user/quick-start/).

Kind is ideal for a local development environment or a build pipeline run.

## Installation

Kind needs a container engine such as [Docker](../docker/docker.md) (Podman also works).

### On Linux
Download the release binary for your platform. Check the [releases page](https://github.com/kubernetes-sigs/kind/releases) for the current version and replace `<VERSION>`:

```bash
curl -Lo ./kind https://kind.sigs.k8s.io/dl/<VERSION>/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```
Use `kind-linux-arm64` on ARM.

### On macOS
```bash
brew install kind
```
See [Homebrew](../macos/homebrew.md).

### On Windows
```powershell
choco install kind
```
See [Chocolatey](../windows/chocolatey.md).

## Cluster management

### Cluster creation

For a quick single-node cluster:

```bash
kind create cluster
kind create cluster --name dev --image kindest/node:<NODE-VERSION>
```
Node image tags per Kind release are listed in the release notes. Use `kindest/node:<VERSION>` to pick the Kubernetes version.

For more control, provide a configuration file. Example:

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: testcluster
# 1 control plane node and 2 workers
nodes:
# the control plane node config
- role: control-plane
# the two workers
- role: worker
- role: worker
```

Create the cluster:

```bash
kind create cluster --config kind-cluster-config.yaml
```
```
Creating cluster "testcluster" ...
Ensuring node image (kindest/node:v1.25.2)
Preparing nodes
Writing configuration
Starting control-plane
Installing CNI
Installing StorageClass
Joining worker nodes

Set kubectl context to "kind-testcluster"
You can now use your cluster with:
kubectl cluster-info --context kind-testcluster
```
(The node version shown depends on your Kind release.)

Check the Docker containers:

```bash
docker ps -a
```
```
CONTAINER ID IMAGE COMMAND CREATED STATUS PORTS NAMES
ac14d8c7a3c9 kindest/node:v1.25.2 "/usr/local/bin/entr..." 2 minutes ago Up About a minute testcluster-worker2
096dd4bf1718 kindest/node:v1.25.2 "/usr/local/bin/entr..." 2 minutes ago Up About a minute 127.0.0.1:42319->6443/tcp testcluster-control-plane
e1ae2d701394 kindest/node:v1.25.2 "/usr/local/bin/entr..." 2 minutes ago Up About a minute testcluster-worker
```

### Expose Ports (Ingress)
Map host ports to the control-plane node in the config so an ingress controller is reachable on `localhost`:

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
```
The Kind ingress guide installs ingress-nginx with a Kind-specific manifest (see the official docs for the current URL). Services of type `NodePort` can be reached the same way with extra port mappings.

### Interacting with your cluster

You may have several Kind clusters at once. List them:

```bash
kind get clusters
```
```
kind
kind-2
```

After creation, the kubectl context is switched to the new cluster automatically (named `kind-<NAME>`). Switch with [kubectx](https://github.com/ahmetb/kubectx), `kubectl config use-context kind-<NAME>` ([Kubectl](kubectl.md)), or pass `--context` to a command.

COMMAND | DESCRIPTION
---|---
`kind get nodes --name <NAME>` | List the node containers
`kind get kubeconfig --name <NAME>` | Print the kubeconfig
`kind export kubeconfig --name <NAME>` | Write the cluster into your kubeconfig
`kind load docker-image <IMAGE> --name <NAME>` | Load a local image into the nodes (no registry needed)
`kind export logs ./logs --name <NAME>` | Collect logs for debugging
`kubectl cluster-info --context kind-<NAME>` | Check the cluster

### Cluster deletion

Kind also removes the cluster from your kubeconfig, so you don't have to.

```bash
kind delete cluster --name testcluster
kind delete clusters --all
```

## Limitations
- Nodes are containers, so there is no real VM isolation and `LoadBalancer` services stay `<pending>` unless you add something like MetalLB.
- Images pulled on the host are not visible to the cluster; use `kind load docker-image`.
- Clusters do not survive a Docker data wipe, and restarting Docker or the host can leave the control plane needing a moment to recover.

## Further information

- Creating an Ansible playbook to manage Kind clusters: [Lightweight Kubernetes cluster using Kind and Ansible](https://thedatabaseme.de/2022/04/22/lightweight-kubernetes-cluster-using-kind-and-ansible/)
- Alternatives: [K3S](k3s.md) on a VM, or minikube.

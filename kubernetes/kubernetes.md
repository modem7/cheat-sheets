# Kubernetes
Kubernetes (K8s) is an open source system for automating deployment, scaling and management of containerised applications.

Documentation: [Kubernetes Docs](https://kubernetes.io/docs/)

Related sheets: [[kubectl]], [[k3s]], [[k9s]], [[kind]], [[helm]], [[kubernetes-dns]], [[kubernetes-automation]]

## Core Concepts
OBJECT | DESCRIPTION
---|---
Pod | Smallest deployable unit: one or more containers sharing network and storage
ReplicaSet | Keeps a set number of identical Pods running
Deployment | Manages ReplicaSets, rolling updates and rollbacks for stateless apps
StatefulSet | Pods with stable identity and storage (databases)
DaemonSet | One Pod per node (log shippers, agents)
Job / CronJob | Run-to-completion tasks, optionally on a schedule
Service | Stable virtual IP and DNS name in front of Pods (`ClusterIP`, `NodePort`, `LoadBalancer`)
Ingress / Gateway | HTTP(S) routing into the cluster
ConfigMap / Secret | Configuration and sensitive data injected into Pods
PersistentVolume / PVC | Storage and the claim for it
Namespace | Logical partition of cluster resources
NetworkPolicy | Firewall rules between Pods
ServiceAccount / Role / RoleBinding | Identity and RBAC permissions

## Control Plane and Node Components
COMPONENT | ROLE
---|---
`kube-apiserver` | Front door of the cluster, every request goes through it
`etcd` | Key-value store holding all cluster state
`kube-scheduler` | Assigns Pods to nodes
`kube-controller-manager` | Runs controllers that reconcile desired and actual state
`kubelet` | Node agent that runs and monitors Pods
`kube-proxy` | Implements Service networking on each node
Container runtime | containerd or CRI-O

## Everyday Commands
See [[kubectl]] for the full list.

COMMAND | DESCRIPTION
---|---
`kubectl get nodes -o wide` | Nodes with IPs and versions
`kubectl get pods -A` | Pods in all namespaces
`kubectl describe pod <POD>` | Details and events (first stop for debugging)
`kubectl logs <POD> -f` | Follow logs
`kubectl exec -it <POD> -- sh` | Shell into a Pod
`kubectl apply -f <FILE>` | Create or update from a manifest
`kubectl rollout undo deployment/<NAME>` | Roll back a Deployment

## Minimal Deployment and Service
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: web
          image: nginx:1.27
          ports:
            - containerPort: 80
          resources:
            requests: { cpu: 50m, memory: 64Mi }
            limits: { memory: 128Mi }
          readinessProbe:
            httpGet: { path: /, port: 80 }
---
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  selector:
    app: web
  ports:
    - port: 80
      targetPort: 80
```

## Debugging Flow
1. `kubectl get pods` — status: `Pending`, `CrashLoopBackOff`, `ImagePullBackOff`?
2. `kubectl describe pod <POD>` — read the **Events** at the bottom.
3. `kubectl logs <POD> --previous` — logs from the last crashed container.
4. `kubectl get events --sort-by=.lastTimestamp` — cluster-wide recent events.
5. `kubectl debug -it <POD> --image=busybox --target=<CONTAINER>` — ephemeral debug container.
6. `kubectl get endpoints <SERVICE>` — empty means the selector matches no ready Pods.

STATUS | USUAL CAUSE
---|---
`Pending` | No node fits (resources, taints, unbound PVC)
`ImagePullBackOff` | Wrong image name/tag or missing registry credentials
`CrashLoopBackOff` | App exits on start. Check `logs --previous`
`OOMKilled` | Memory limit too low
`CreateContainerConfigError` | Missing ConfigMap or Secret

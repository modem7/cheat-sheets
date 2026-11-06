# Kubernetes DNS
Cluster DNS is served by CoreDNS in the `kube-system` namespace ([[kubernetes]], [[k3s]]).

## Names Inside the Cluster
NAME | RESOLVES TO
---|---
`<SERVICE>` | Service in the same namespace
`<SERVICE>.<NAMESPACE>` | Service in another namespace
`<SERVICE>.<NAMESPACE>.svc.cluster.local` | Fully qualified service name
`<POD-IP-DASHED>.<NAMESPACE>.pod.cluster.local` | A Pod by IP (e.g. `10-1-2-3`)
`<POD>.<HEADLESS-SVC>.<NAMESPACE>.svc.cluster.local` | StatefulSet Pod via a headless Service

## Debugging
COMMAND | DESCRIPTION
---|---
`kubectl run dns-test --rm -it --image=busybox:1.36 --restart=Never -- nslookup kubernetes.default` | Test cluster DNS from a Pod
`kubectl run dns-test --rm -it --image=nicolaka/netshoot --restart=Never -- dig +short <SERVICE>.<NS>.svc.cluster.local` | Query with dig
`kubectl -n kube-system get pods -l k8s-app=kube-dns` | CoreDNS pods
`kubectl -n kube-system logs -l k8s-app=kube-dns` | CoreDNS logs
`kubectl -n kube-system get svc kube-dns` | The cluster DNS IP
`kubectl exec <POD> -- cat /etc/resolv.conf` | What a Pod uses (`ndots:5` is the default)
`kubectl -n kube-system rollout restart deployment coredns` | Restart CoreDNS

## Custom DNS Settings

### Edit coredns config map

Add entry to the `Corefile: |` section of the `configmap/coredns` in section **kube-system**.

```yml
.:53 {
  # ...
}
import /etc/coredns/custom/*.server
```

### Add new config map

Example for local DNS server using the **clcreative.home** zone.

```yml
apiVersion: v1
kind: ConfigMap
metadata:
  name: coredns-custom
  namespace: kube-system
data:
  clcreative.server: |
    clcreative.home:53 {
      forward . 10.20.0.10
    }
```
This `coredns-custom` ConfigMap and the `import` line work out of the box on K3s. Restart CoreDNS afterwards.

### Static host records
```yaml
data:
  hosts.override: |
    hosts {
      10.0.0.5 nas.home
      fallthrough
    }
```

## Per-Pod DNS
```yaml
spec:
  dnsPolicy: ClusterFirst        # default
  dnsConfig:
    options:
      - name: ndots
        value: "2"               # fewer search-domain lookups for external names
```
Other policies: `Default` (node resolver), `None` (use only `dnsConfig`), `ClusterFirstWithHostNet`.

## Common Problems
SYMPTOM | CAUSE
---|---
External names slow or time out | `ndots:5` search expansion, UDP drops. Use FQDNs with a trailing dot, or lower `ndots`
Names fail on some nodes only | CNI or node firewall blocking UDP/TCP 53 between nodes
Split-DNS names fail | Forward the zone in CoreDNS as shown above
`SERVFAIL` on external lookups | Upstream resolver unreachable from the node (`/etc/resolv.conf` on the node)

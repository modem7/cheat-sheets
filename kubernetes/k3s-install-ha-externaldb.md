# Install K3S in High Availability Mode
HA K3s ([[k3s]]) with an external datastore. For the built-in alternative see [[k3s-install-ha-embeddeddb]].

## Install Database
Install MariaDB ([[mariadb]]) (or MySQL, PostgreSQL, etcd) on a separate, ideally replicated, host. Create the database first:
```sql
CREATE DATABASE k3s;
CREATE USER 'k3s'@'%' IDENTIFIED BY '<PASSWORD>';
GRANT ALL ON k3s.* TO 'k3s'@'%';
```
## Install Servers
```bash
curl -sfL https://get.k3s.io | sh -s - server \
--token=YOUR-SECRET \
--datastore-endpoint='mysql://user:pass@tcp(ipaddress:3306)/dbname' \
--node-taint CriticalAddonsOnly=true:NoExecute \
--tls-san your-dns-name --tls-san your-lb-ip-address
```
Run the same command on each server node. PostgreSQL uses `postgres://user:pass@host:5432/dbname`.

### Node-Taint
By default, server nodes will be schedulable and thus your workloads can get launched on them. If you wish to have a dedicated control plane where no user workloads will run, you can use taints. The node-taint parameter will allow you to configure nodes with taints, for example `--node-taint CriticalAddonsOnly=true:NoExecute`.

### SSL Certificates
To avoid certificate errors in such a configuration, you should install the server with the `--tls-san YOUR_IP_OR_HOSTNAME_HERE` option. This option adds an additional hostname or IP as a Subject Alternative Name in the TLS cert, and it can be specified multiple times if you would like to access via both the IP and the hostname.

## Get a registered Address
Agents and `kubectl` need one stable address for the API on `6443/tcp`. Options:

OPTION | NOTES
---|---
DNS round-robin | Simplest, no health checks
Load balancer (HAProxy, nginx stream, hardware) | Health-checks servers, see below
Virtual IP (keepalived or kube-vip) | Floating IP shared between servers

HAProxy example:
```
frontend k3s_api
    bind *:6443
    mode tcp
    default_backend k3s_servers
backend k3s_servers
    mode tcp
    balance roundrobin
    option tcp-check
    server s1 10.0.0.11:6443 check
    server s2 10.0.0.12:6443 check
    server s3 10.0.0.13:6443 check
```

## Install Agents
  
```bash
curl -sfL https://get.k3s.io | sh -s - agent \
--server https://your-lb-ip-address:6443 \
--token YOUR-SECRET
```

## Verify
```bash
sudo k3s kubectl get nodes -o wide
```
The datastore is a single point of failure unless it is replicated itself, and it needs regular backups.

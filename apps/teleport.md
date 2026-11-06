# Teleport
Teleport is an open source identity-aware access proxy for SSH servers, Kubernetes, databases, web apps and Windows desktops, with short-lived certificates, SSO and audit logging.

Project Homepage: [goteleport.com](https://goteleport.com)
Documentation: [Teleport Docs](https://goteleport.com/docs/)

---
## Adding nodes
Add another node with roles `tctl nodes add --roles=<node,app,kube,proxy,...> --ttl=1h`

## Users
COMMAND | DESCRIPTION
---|---
`tctl users add <USER> --roles=access,editor --logins=root,ubuntu` | Create a user and print the invite link
`tctl users ls` | List users
`tctl users rm <USER>` | Delete a user
`tctl users reset <USER>` | Reset a user's credentials
`tctl get roles` | List roles

## Client (tsh)
COMMAND | DESCRIPTION
---|---
`tsh login --proxy=teleport.example.com --user=<USER>` | Log in (starts an SSO flow if configured)
`tsh status` | Current login and certificate TTL
`tsh ls` | List reachable SSH nodes
`tsh ssh <USER>@<NODE>` | SSH to a node
`tsh scp <FILE> <USER>@<NODE>:<PATH>` | Copy files
`tsh kube ls` / `tsh kube login <CLUSTER>` | List and log in to Kubernetes clusters
`tsh db ls` / `tsh db connect <DB>` | Databases
`tsh apps ls` | Registered web apps
`tsh logout` | Remove credentials

## Server (tctl and teleport)
COMMAND | DESCRIPTION
---|---
`tctl status` | Cluster status and CA fingerprints
`tctl nodes ls` | Registered nodes
`tctl tokens add --type=node --ttl=1h` | Create a join token
`tctl tokens ls` | Active tokens
`teleport configure -o file > /etc/teleport.yaml` | Generate a base config
`sudo systemctl restart teleport` | Restart the service
`tctl lock --user=<USER> --message="reason"` | Lock a user out immediately

## Joining a Node
```bash
sudo teleport node configure --token=<TOKEN> --proxy=teleport.example.com:443 --output=file:///etc/teleport.yaml
sudo systemctl enable --now teleport
```

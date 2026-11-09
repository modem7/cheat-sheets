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

## Sessions and Recordings
COMMAND | DESCRIPTION
---|---
`tsh ls <KEY>=<VALUE>` | List nodes by label (labels are a positional argument, not `--labels`)
`tsh ls --search=<TEXT>` | Filter nodes by text
`tsh recordings ls` | List session recordings (`--last`, `--limit`)
`tsh play <SESSION_ID>` | Replay a recorded session (`--speed`, `--skip-idle-time`)
`tsh recordings export <SESSION_ID>` | Export a recording

## Access Requests
`tsh request create --roles=<ROLE> --reason="<REASON>"` asks for temporary elevated access. Other flags: `--resource`, `--reviewers`, `--max-duration`, `--request-ttl`, `--session-ttl`, `--nowait`. Community Edition can only request roles through the CLI.

## Use Teleport as a Bastion
Nodes open a reverse SSH tunnel to the Proxy, so they need no inbound SSH. Clients reach the Proxy on port 443 (TLS routing) or 3080. The upstream guide keeps port 22 open only during setup and recommends closing it afterwards. This is an alternative to a [bastion host](../recipes/ssh-bastion-lxc.md).

COMMAND | DESCRIPTION
---|---
`tsh ssh -J <JUMPHOST> <USER>@<NODE>` | Use a jump host (`-J` is a global flag)
`tsh proxy ssh <USER>@<NODE>` | Proxy an SSH connection for another client
`tsh config >> ~/.ssh/config` | Let the plain OpenSSH client reach nodes (generates a `ProxyCommand` using `tsh proxy ssh`)

Documentation: [tsh reference](https://goteleport.com/docs/reference/cli/tsh/) · [Server access getting started](https://goteleport.com/docs/enroll-resources/server-access/getting-started/)

## Licence
Community Edition binaries from v16 onwards are under a commercial licence, free for companies with fewer than 100 employees and under $10M annual revenue. The source is AGPL-3.0, and earlier releases stay Apache 2.0. Check [the feature matrix](https://goteleport.com/docs/feature-matrix/) before relying on it.

## Joining a Node
```bash
sudo teleport node configure --token=<TOKEN> --proxy=teleport.example.com:443 --output=file:///etc/teleport.yaml
sudo systemctl enable --now teleport
```

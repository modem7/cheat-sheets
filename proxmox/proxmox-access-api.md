# Proxmox Users, Permissions, API Tokens and pvesh
Access control is built from users, groups, roles, realms and ACL entries on paths such as `/vms/<VMID>`. `pveum` manages them, `pvesh` calls the REST API from the shell, and API tokens let scripts authenticate without a password.

Documentation: [User Management](https://pve.proxmox.com/pve-docs/chapter-pveum.html) · [pveum(1)](https://pve.proxmox.com/pve-docs/pveum.1.html) · [API Viewer](https://pve.proxmox.com/pve-docs/api-viewer/)

> **Verification:** ACL syntax, `pveum role add --privs`, token creation, the `PVEAPIToken` header, realm sync and TFA unlock were checked against the docs. The docs show single-dash forms (`-user`, `-role`), double-dash forms also work. **Not verified:** `pveum user list`, `pveum acl list` output formats, `pvesh` examples beyond the API viewer paths. No command was executed.

See also: [[proxmox-overview]] · [[proxmox-firewall]] · [[proxmox-troubleshooting]] · [[curl]] · [[jq]] · [[terraform]] · [[ansible]]

---
## Users and Realms
Users are `<NAME>@<REALM>`. Realms: `pam` (Linux accounts on the node, including `root`), `pve` (Proxmox's own user database), plus LDAP, Active Directory and OpenID Connect.

COMMAND | DESCRIPTION
---|---
`pveum user list` | List users
`pveum user add <USER>@pve --password <PASS>` | Create a user in the `pve` realm
`pveum user add <USER>@pve --email <EMAIL> --comment "<TEXT>"` | With details
`pveum passwd <USER>@pve` | Change a password
`pveum user delete <USER>@pve` | Delete
`pveum group add <GROUP>` | Create a group
`pveum user modify <USER>@pve --groups <GROUP>` | Add a user to a group
`pveum realm list` | Authentication realms
`pveum realm sync <REALM>` | Sync LDAP or AD users
`pveum user tfa unlock <USER>@<REALM>` | Unlock a user locked out by failed TFA

---
## Roles and ACLs
Built-in roles include `Administrator`, `PVEAdmin`, `PVEVMAdmin`, `PVEVMUser`, `PVEAuditor`, `PVEDatastoreUser`, `PVEPoolAdmin` and `NoAccess`.

COMMAND | DESCRIPTION
---|---
`pveum role list` | Roles and their privileges
`pveum role add <ROLE> --privs "VM.Audit VM.PowerMgmt"` | Custom role
`pveum acl list` | Current ACL entries
`pveum acl modify /vms/<VMID> --users <USER>@pve --roles PVEVMUser` | Grant a role on one VM
`pveum acl modify /pool/<POOL> --groups <GROUP> --roles PVEVMAdmin` | Grant on a pool
`pveum acl modify / --users <USER>@pve --roles PVEAuditor` | Read-only everywhere
`pveum acl delete /vms/<VMID> --users <USER>@pve --roles PVEVMUser` | Remove an entry
`pveum user permissions <USER>@pve` | Effective permissions

Permissions inherit down the path tree (`/`, `/vms`, `/storage/<ID>`, `/nodes/<NODE>`, `/pool/<POOL>`). Use pools to group guests for a team.

---
## API Tokens
Tokens belong to a user and act with that user's permissions (or a subset). **The secret is displayed once.**

COMMAND | DESCRIPTION
---|---
`pveum user token add <USER>@pve <TOKENID> --privsep 1` | Token with separate privileges (needs its own ACL)
`pveum user token add <USER>@pve <TOKENID> --privsep 0` | Token with the same rights as the user
`pveum user token list <USER>@pve` | List tokens
`pveum user token remove <USER>@pve <TOKENID>` | Delete
`pveum acl modify /vms --tokens '<USER>@pve!<TOKENID>' --roles PVEAuditor` | Grant a privilege-separated token a role

Use it with [[curl]]:
```bash
curl -s -k \
  -H 'Authorization: PVEAPIToken=<USER>@<REALM>!<TOKENID>=<SECRET>' \
  https://<NODE>:8006/api2/json/nodes | jq .
```
Use `-k` only for self-signed certificates, prefer a trusted certificate ([[proxmox-overview]]). Tools such as [[terraform]] providers and [[ansible]] collections take the same user, token ID and secret.

---
## pvesh
`pvesh` talks to the local API as root and mirrors the REST tree: `get`, `create` (POST), `set` (PUT), `delete`, `ls`, `usage`.

COMMAND | DESCRIPTION
---|---
`pvesh ls /nodes` | Browse the tree
`pvesh get /version` | PVE version
`pvesh get /cluster/resources --type vm` | All VMs and containers in the cluster
`pvesh get /cluster/resources --output-format json \| jq .` | JSON output for scripts
`pvesh get /nodes/<NODE>/status` | CPU, memory, uptime
`pvesh get /nodes/<NODE>/qemu/<VMID>/status/current` | VM state
`pvesh create /nodes/<NODE>/qemu/<VMID>/status/start` | Start a VM
`pvesh create /nodes/<NODE>/qemu/<VMID>/snapshot --snapname <NAME>` | Snapshot
`pvesh set /nodes/<NODE>/qemu/<VMID>/config --memory 4096` | Change config
`pvesh get /nodes/<NODE>/hardware/pci --pci-class-blacklist ""` | PCI devices
`pvesh usage /nodes/<NODE>/qemu/<VMID>/config -v` | Show parameters of an endpoint

The [API Viewer](https://pve.proxmox.com/pve-docs/api-viewer/) lists every path and parameter. API paths mirror the CLI, so `qm` and `pct` options map directly ([[proxmox-qm-pct]]).

---
## Security Notes
- Do not use `root@pam` for automation, make a dedicated user and token with the least privileges.
- Enable TFA for admin users (Datacenter -> Permissions -> Two Factor).
- Restrict port 8006 with the firewall ([[proxmox-firewall]]) or put the UI behind [[wireguard]].

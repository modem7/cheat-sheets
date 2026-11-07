# Hetzner Cloud
Hetzner Cloud is low-cost European VPS hosting that suits a homelab: hourly-billed servers, private networks, firewalls, volumes, snapshots and backups, all scriptable with the `hcloud` CLI. Also covers Storage Box and Object Storage for backups.

Documentation: [Hetzner Docs](https://docs.hetzner.com/) · [hcloud CLI manual](https://github.com/hetznercloud/cli/tree/main/docs/reference/manual) · [Terraform hcloud provider](https://registry.terraform.io/providers/hetznercloud/hcloud/latest) (see [Terraform](../../tools/terraform.md))
Project: [hetznercloud/cli](https://github.com/hetznercloud/cli)

> **Verification:** `hcloud` syntax was checked against the CLI's manual pages in the GitHub repository (November 2026). The CLI was not installed or run. Items marked *(unverified)* were not confirmed. The Hetzner billing FAQ is dated 2020, so re-check prices on the Hetzner site.

## Services a Self-Hoster Uses
NEED | SERVICE | NOTES
---|---|---
Virtual machine | Cloud Server | Billed hourly with a monthly cap
Private network | Network | Subnets per network zone
Firewall | Cloud Firewall | Applied to servers or label selectors
Extra disk | Volume | Attach to one server at a time
Static address | Primary IP, Floating IP | Floating IPs move between servers
Backups | Backups (20% surcharge) and snapshots | See billing below
Off-site backup target | Storage Box | SFTP, SCP, rsync, Borg, SMB, WebDAV
S3 storage | Object Storage | S3-compatible buckets
DNS | `hcloud zone` commands | See DNS below

## Authentication and Contexts
Create an API token in the Cloud Console (project, Security, API tokens). Treat it as a secret.

COMMAND | DESCRIPTION
---|---
`hcloud context create <NAME>` | Create a context (prompts for the token)
`hcloud context create --token-from-env <NAME>` | Create a context using the `HCLOUD_TOKEN` environment variable
`hcloud context list` | List contexts
`hcloud context use <NAME>` | Switch context (one per Hetzner project)
`hcloud context active` | Show the active context

`HCLOUD_TOKEN` is the documented token variable. `HCLOUD_CONTEXT` is inferred from how the CLI names options and is *unverified*.

## Servers
COMMAND | DESCRIPTION
---|---
`hcloud server-type list` | List server types
`hcloud location list` | List locations
`hcloud image list` | List images
`hcloud server create --name <NAME> --type <TYPE> --image <IMAGE>` | Create a server
`hcloud server create --name <NAME> --type <TYPE> --image <IMAGE> --location <LOCATION> --ssh-key <KEY> --firewall <FIREWALL> --network <NETWORK> --label <KEY>=<VALUE> --user-data-from-file <FILE>` | Create with options (flags are repeatable, `-` reads stdin)
`hcloud server list` | List servers (`-l <SELECTOR>` filters by label)
`hcloud server describe <SERVER>` | Show details
`hcloud server ssh <SERVER>` | SSH in (`-p <PORT>`, or `-- <COMMAND>`)
`hcloud server reboot <SERVER>` | Reboot
`hcloud server shutdown <SERVER>` | Graceful shutdown
`hcloud server poweroff <SERVER>` | Hard power off (billing continues)
`hcloud server rebuild --image <IMAGE> <SERVER>` | Reinstall the server from an image (destroys its disk contents)
`hcloud server enable-protection <SERVER> delete rebuild` | Block accidental deletion and rebuilds
`hcloud server delete <SERVER>` | Delete the server (destroys its data)

Cloud-init user data is passed with `--user-data-from-file`. See [Proxmox Cloud-Init Templates](../../proxmox/proxmox-cloud-init.md) for the format.

## SSH Keys
COMMAND | DESCRIPTION
---|---
`hcloud ssh-key create --name <NAME> --public-key-from-file ~/.ssh/id_ed25519.pub` | Upload a public key
`hcloud ssh-key create --name <NAME> --public-key <KEY>` | Upload from a string

## Firewalls
COMMAND | DESCRIPTION
---|---
`hcloud firewall create --name <NAME>` | Create a firewall (flag *unverified*, the page was not read)
`hcloud firewall add-rule --direction in --source-ips 203.0.113.10/32 --protocol tcp --port 22 <FIREWALL>` | Allow SSH from one address
`hcloud firewall add-rule --direction out --destination-ips <CIDR> --protocol tcp --port 443 <FIREWALL>` | Outbound rule (uses `--destination-ips`)
`hcloud firewall apply-to-resource --type server --server <SERVER> <FIREWALL>` | Apply to one server
`hcloud firewall apply-to-resource --type label_selector -l <SELECTOR> <FIREWALL>` | Apply to every server matching a label

Once any firewall is attached, inbound traffic not matched by a rule is dropped. The label selector syntax is *unverified*; the CLI accepts `-l` or `--selector`.

## Networks, Volumes and IPs
COMMAND | DESCRIPTION
---|---
`hcloud network create --name <NAME> --ip-range 10.0.0.0/16` | Create a private network
`hcloud network add-subnet --type cloud --network-zone eu-central --ip-range 10.0.1.0/24 <NETWORK>` | Add a subnet
`hcloud volume create --name <NAME> --size <GB> --server <SERVER> --format ext4 --automount` | Create and attach a volume
`hcloud volume attach --server <SERVER> --automount <VOLUME>` | Attach an existing volume
`hcloud primary-ip create --type ipv4 --name <NAME>` | Reserve a primary IP
`hcloud floating-ip create --type ipv4 --server <SERVER>` | Create a floating IP (or `--home-location <LOCATION>`)
`hcloud load-balancer create --name <NAME> --type <TYPE>` | Create a load balancer

## Snapshots and Backups
COMMAND | DESCRIPTION
---|---
`hcloud server create-image --type snapshot --description <TEXT> <SERVER>` | Take a snapshot
`hcloud server create-image --type backup --description <TEXT> <SERVER>` | Create a backup image (requires backups enabled)
`hcloud server enable-backup <SERVER>` | Enable automatic backups (20% of the server price)
`hcloud image list --type snapshot` | List snapshots (the `--type` filter is *unverified*)

Backups and snapshots live in the same Hetzner project and data centre provider as the server, so they are not an off-site copy. Use [restic](../../backup/restic.md) or [BorgBackup](../../backup/borg.md) to a Storage Box or another provider.

## Storage Box and Object Storage
STORAGE BOX ACCESS | PORT
---|---
FTP / FTPS | 21
SFTP / SCP | 22
SSH (SFTP, SCP, rsync, BorgBackup) | 23
SMB | 445
WebDAV over HTTPS | 443

Ports 23, 445 and 443 must be enabled in the console first. Source: [Storage Box access](https://docs.hetzner.com/storage/storage-box/access/access-overview). Borg and rsync use the SSH service on port 23 (see [BorgBackup](../../backup/borg.md) and [rsync](../../backup/rsync.md)).

Object Storage is S3-compatible with endpoints of the form `https://<BUCKET>.<LOCATION>.your-objectstorage.com`, where the location is `fsn1`, `nbg1` or `hel1`. Source: [Object Storage overview](https://docs.hetzner.com/storage/object-storage/overview). Client examples (`aws`, `s3cmd`, [rclone](../../backup/rclone.md)) were not found in the official page.

## DNS
The `hcloud` CLI has a `hcloud zone` command group for DNS zones and records. Hetzner announced that the older DNS Console and its API shut down in May 2026 and that DNS moves to the Cloud Console (*unverified, from a search snippet; see the [migration guide](https://docs.hetzner.com/networking/dns/migration-to-hetzner-console/process)*). Check `hcloud zone --help` for the current subcommands.

## Billing and Pitfalls
PITFALL | DETAIL
---|---
Hourly billing, monthly cap | You pay by the hour up to a monthly maximum per server ([billing FAQ](https://docs.hetzner.com/cloud/billing/faq/), dated 2020)
Powered-off servers still billed | Delete the server (after taking a snapshot) to stop charges
Backups cost 20% of the server price | Per server, on top of the server price
Snapshots are billed per GB | They accrue until deleted
Traffic allowance | Each plan includes traffic, with overage charged per TB; amounts *(unverified, no official source found)*
Unattached IPs and volumes | Still billed
Exposed API token | A project token controls every resource in the project; keep one per tool and revoke on leak

## See Also
- [Cloud-Provider Comparison](cloud-provider-comparison.md)
- [What is Cloud-Computing?](../what-is-cloud-computing.md)
- [Terraform](../../tools/terraform.md)
- [restic](../../backup/restic.md)
- [BorgBackup](../../backup/borg.md)
- [rsync](../../backup/rsync.md)

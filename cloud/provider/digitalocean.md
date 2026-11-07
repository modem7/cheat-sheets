# DigitalOcean
DigitalOcean offers simple, predictably priced Droplets (VPS), Spaces object storage, cloud firewalls, DNS and managed Kubernetes. Covers the `doctl` CLI and the billing details that matter for a homelab.

Documentation: [doctl reference](https://docs.digitalocean.com/reference/doctl/reference/) · [Droplet pricing](https://docs.digitalocean.com/products/droplets/details/pricing/) · [Spaces pricing](https://docs.digitalocean.com/products/spaces/details/pricing/) · [Terraform DigitalOcean provider](https://registry.terraform.io/providers/digitalocean/digitalocean/latest) (see [Terraform](../../tools/terraform.md))
Project: [digitalocean/doctl](https://github.com/digitalocean/doctl)

> **Verification:** `doctl` syntax and pricing were checked against the DigitalOcean docs and the doctl README (November 2026). The CLI was not installed or run. Items marked *(unverified)* were not confirmed.

## Services a Self-Hoster Uses
NEED | SERVICE | NOTES
---|---|---
Virtual machine | Droplet | Billed per second
Firewall | Cloud Firewall | Applied by Droplet or tag
Extra disk | Volume | Block storage
Object storage | Spaces | S3-compatible
Snapshots and backups | Snapshots, Backups | Backups are a percentage surcharge
DNS | Domains | Free DNS hosting for domains you point at DigitalOcean
Kubernetes | DOKS | See `doctl kubernetes` below
Container registry | DOCR | `doctl registry login`

## Authentication
Create a personal access token in the control panel (API, Tokens). Treat it as a secret.

COMMAND | DESCRIPTION
---|---
`doctl auth init` | Authenticate (prompts for the token)
`doctl auth init --context <NAME>` | Save the token under a named context
`doctl auth list` | List contexts
`doctl auth switch --context <NAME>` | Switch context
`doctl account get` | Show account details and limits
`export DIGITALOCEAN_ACCESS_TOKEN=<TOKEN>` | Token via environment (applies to the default context only)

## Droplets
COMMAND | DESCRIPTION
---|---
`doctl compute droplet create <NAME> --region <REGION> --size <SIZE> --image <IMAGE>` | Create a Droplet
`doctl compute droplet create <NAME> --region <REGION> --size <SIZE> --image <IMAGE> --ssh-keys <KEY_ID_OR_FINGERPRINT> --vpc-uuid <VPC_ID> --tag-name <TAG> --user-data-file <FILE> --enable-backups` | Create with options
`doctl compute droplet list` | List Droplets
`doctl compute ssh <DROPLET>` | SSH in
`doctl compute droplet delete <ID_OR_NAME>` | Delete a Droplet (destroys its data)
`doctl compute size list` | List sizes *(unverified)*
`doctl compute region list` | List regions *(unverified)*

## Snapshots
COMMAND | DESCRIPTION
---|---
`doctl compute droplet-action snapshot <DROPLET_ID> --snapshot-name <NAME>` | Snapshot a Droplet
`--enable-backups` (on create) | Weekly automatic backups

Snapshots and backups stay in DigitalOcean, so they are not an off-site copy. Use [restic](../../backup/restic.md) or [BorgBackup](../../backup/borg.md) elsewhere too.

## Firewalls
COMMAND | DESCRIPTION
---|---
`doctl compute firewall create --name <NAME> --inbound-rules "protocol:tcp,ports:22,address:203.0.113.10/32" --outbound-rules "protocol:tcp,ports:443,address:0.0.0.0/0" --tag-names <TAG>` | Create a firewall applied to tagged Droplets (use `--droplet-ids` to target Droplets directly)
`doctl compute firewall list` | List firewalls *(unverified)*

Rules are a comma-separated list of `key:value` pairs. A Droplet source uses `droplet_id:` in place of `address:`.

## Volumes and DNS
COMMAND | DESCRIPTION
---|---
`doctl compute volume create <NAME> --region <REGION> --size 10GiB` | Create a volume
`doctl compute domain create example.com --ip-address <IP>` | Add a domain
`doctl compute domain records create example.com --record-type A --record-name @ --record-data <IP>` | Add a record

## Spaces
`doctl` has no commands for objects; `doctl spaces keys` manages access keys only. Use an S3 client with the endpoint `https://<REGION>.digitaloceanspaces.com` (see [rclone](../../backup/rclone.md), [restic](../../backup/restic.md) or the AWS CLI with `--endpoint-url`). Source: [Spaces and AWS SDKs](https://docs.digitalocean.com/products/spaces/how-to/use-aws-sdks/). Prefer per-bucket keys over full-access keys *(unverified)*.

## Kubernetes and Registry
COMMAND | DESCRIPTION
---|---
`doctl kubernetes cluster kubeconfig save <CLUSTER>` | Merge the cluster's kubeconfig (see [Kubectl](../../kubernetes/kubectl.md))
`doctl registry login` | Log Docker in to the DigitalOcean registry

## Billing and Pitfalls
PITFALL | DETAIL
---|---
Per-second billing, monthly cap | 60 second minimum, capped at 672 hours per month ([pricing](https://docs.digitalocean.com/products/droplets/details/pricing/))
Powered-off Droplets still billed | Destroy the Droplet (after a snapshot) to stop charges
Backups | Weekly is 20% of the Droplet price, daily is 30% ([backups pricing](https://docs.digitalocean.com/products/backups/details/pricing/))
Spaces | $5 per month includes 250 GiB storage and 1,024 GiB outbound transfer, shared across buckets; overage $0.02 per GiB storage and $0.01 per GiB transfer ([Spaces pricing](https://docs.digitalocean.com/products/spaces/details/pricing/))
Snapshots | Billed per GB until deleted *(unverified rate)*
Token scope | A full-access token controls the whole team; create scoped tokens and revoke on leak

## See Also
- [Cloud-Provider Comparison](cloud-provider-comparison.md)
- [What is Cloud-Computing?](../what-is-cloud-computing.md)
- [Terraform](../../tools/terraform.md)
- [restic](../../backup/restic.md)
- [rclone](../../backup/rclone.md)

# Google Cloud
Google Cloud from a self-hoster's point of view: the free e2-micro VM, Cloud Storage for backups, firewall rules, Cloud DNS, service accounts and budgets. For generic CLI usage see [gcloud (Google Cloud CLI)](../../tools/gcloud.md); to compare providers see [Cloud-Provider Comparison](cloud-provider-comparison.md).

Documentation: [gcloud reference](https://cloud.google.com/sdk/gcloud/reference) · [Free Tier features](https://docs.cloud.google.com/free/docs/free-cloud-features) · [Terraform Google provider](https://registry.terraform.io/providers/hashicorp/google/latest) (see [Terraform](../../tools/terraform.md))

> **Verification:** flags were checked against the gcloud reference pages and free-tier terms against the Google Cloud Free Tier page (November 2026). No command was run against a project. Items marked *(unverified)* were not confirmed.

## Services a Self-Hoster Uses
NEED | SERVICE | NOTES
---|---|---
Virtual machine | Compute Engine | One free e2-micro, see below
Object storage | Cloud Storage | Backups, static files
Firewall | VPC firewall rules | Applied by network tag or service account
Disk snapshots | Snapshot schedules | Resource policy attached to a disk
DNS | Cloud DNS | Managed zones are billed monthly
Containers without servers | Cloud Run | Scales to zero
Access control | IAM and service accounts | Avoid downloaded keys where possible
Cost control | Billing budgets | Alerts only, they do not stop spending

## Free Tier
Source: [Free Tier features](https://docs.cloud.google.com/free/docs/free-cloud-features). Google can change terms with 30 days' notice and a billing account is required.

PRODUCT | FREE USAGE
---|---
Compute Engine | 1 non-preemptible `e2-micro` per month in `us-west1`, `us-central1` or `us-east1`
Persistent disk | 30 GB-months standard disk
Network egress | 1 GB per month from North America (excluding China and Australia)
Cloud Storage | 5 GB regional storage (US regions), 5,000 Class A and 50,000 Class B operations, 100 GB egress
Cloud Run | 2 million requests, 360,000 GB-seconds, 180,000 vCPU-seconds, 1 GB egress

New accounts may also receive trial credit; check the current offer on the [Free Program page](https://cloud.google.com/free).

## Compute Engine
COMMAND | DESCRIPTION
---|---
`gcloud compute instances create <NAME> --machine-type e2-micro --image-family <FAMILY> --image-project <PROJECT> --zone <ZONE> --tags <TAG>` | Create a VM (list families with `gcloud compute images list`)
`gcloud compute instances list` | List VMs
`gcloud compute instances stop <NAME> --zone <ZONE>` | Stop a VM
`gcloud compute instances delete <NAME> --zone <ZONE>` | Delete a VM (data on boot disk is deleted by default)
`gcloud compute ssh <NAME> --zone <ZONE>` | SSH in (see [gcloud (Google Cloud CLI)](../../tools/gcloud.md#compute))

## Firewall
COMMAND | DESCRIPTION
---|---
`gcloud compute firewall-rules create <NAME> --allow tcp:22 --source-ranges 203.0.113.10/32 --target-tags <TAG> --direction INGRESS` | Allow SSH from one address to tagged VMs
`gcloud compute firewall-rules list` | List rules

The default network ships with rules that allow SSH and RDP from anywhere. Delete or narrow them, or use a VPN such as [WireGuard](../../apps/wireguard.md) or [Tailscale](../../apps/tailscale.md).

## Snapshots
COMMAND | DESCRIPTION
---|---
`gcloud compute disks snapshot <DISK> --zone <ZONE>` | One-off snapshot
`gcloud compute resource-policies create snapshot-schedule <NAME> --region <REGION> --daily-schedule --start-time 03:00 --max-retention-days 7 --on-source-disk-delete keep-auto-snapshots` | Daily schedule with retention (attach it to a disk afterwards; the attach command is *(unverified)*)

## Cloud Storage
COMMAND | DESCRIPTION
---|---
`gcloud storage buckets create gs://<BUCKET> --location <LOCATION> --default-storage-class <CLASS> --uniform-bucket-level-access --public-access-prevention` | Create a private bucket
`gcloud storage cp <FILE> gs://<BUCKET>/` | Copy to a bucket
`gcloud storage rsync <DIR> gs://<BUCKET>/<PREFIX>` | Sync a directory (add `--delete-unmatched-destination-objects` only to mirror deletions, *flag unverified*)
`gcloud storage buckets update gs://<BUCKET> --lifecycle-file lifecycle.json` | Apply lifecycle rules

Lifecycle rule moving objects to Archive after 90 days and deleting after a year (`lifecycle.json`, format from the Cloud Storage lifecycle docs):

```json
{
  "rule": [
    {
      "action": { "type": "SetStorageClass", "storageClass": "ARCHIVE" },
      "condition": { "age": 90 }
    },
    {
      "action": { "type": "Delete" },
      "condition": { "age": 365 }
    }
  ]
}
```

Classes are `STANDARD`, `NEARLINE`, `COLDLINE` and `ARCHIVE`. Use a bucket with [restic](../../backup/restic.md) or [rclone](../../backup/rclone.md).

## Service Accounts and IAM
COMMAND | DESCRIPTION
---|---
`gcloud iam service-accounts create <NAME> --display-name <TEXT>` | Create a service account
`gcloud projects add-iam-policy-binding <PROJECT_ID> --member serviceAccount:<NAME>@<PROJECT_ID>.iam.gserviceaccount.com --role <ROLE>` | Grant a project role (*command unverified here, see the [gcloud (Google Cloud CLI)](../../tools/gcloud.md) sheet*)
`gcloud iam service-accounts keys create key.json --iam-account <NAME>@<PROJECT_ID>.iam.gserviceaccount.com` | Download a key file (a long-lived secret, avoid where possible)
`gcloud auth list` | Show active accounts

Prefer attaching a service account to the VM, or workload identity federation for CI, over key files. Never commit `key.json`.

## DNS
COMMAND | DESCRIPTION
---|---
`gcloud dns managed-zones create <ZONE_NAME> --dns-name example.com. --description <TEXT>` | Create a zone (note the trailing dot)
`gcloud dns record-sets create www.example.com. --zone <ZONE_NAME> --type A --rrdatas 203.0.113.10 --ttl 300` | Add a record

## Cloud Run
COMMAND | DESCRIPTION
---|---
`gcloud run deploy <SERVICE> --image <IMAGE> --region <REGION> --no-allow-unauthenticated` | Deploy a container privately (use `--allow-unauthenticated` for a public service)

## Budgets
COMMAND | DESCRIPTION
---|---
`gcloud billing budgets create --billing-account <BILLING_ACCOUNT_ID> --display-name <NAME> --budget-amount 10GBP --threshold-rule percent=0.5 --threshold-rule percent=1.0` | Alert at 50% and 100% of a budget (amount format *unverified*)

Budgets alert but do not cap spending.

## Pitfalls
PITFALL | DETAIL
---|---
Free VM is region-locked | Only the three US regions qualify, so latency from Europe is high
Wrong zone or class | An `e2-small` or a disk in another region is billed in full
Static external IPs | Charges apply for reserved or in-use addresses; rates *(unverified, the pricing page did not render)*
Egress | Only 1 GB per month is free from the VM, then charged per GB
Service account keys | Leaked keys give full access to their roles
Budgets | Alert only, no automatic stop

## See Also
- [gcloud (Google Cloud CLI)](../../tools/gcloud.md)
- [Cloud-Provider Comparison](cloud-provider-comparison.md)
- [What is Cloud-Computing?](../what-is-cloud-computing.md)
- [Terraform](../../tools/terraform.md)
- [restic](../../backup/restic.md)

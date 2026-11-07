# Oracle Cloud
Oracle Cloud Infrastructure (OCI) and its Always Free tier, the most generous free allowance for a homelab VPS. Covers the free resources, the idle-reclamation and capacity pitfalls, and the key `oci` CLI commands.

Documentation: [Always Free resources](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm) · [OCI CLI reference](https://docs.oracle.com/en-us/iaas/tools/oci-cli/latest/oci_cli_docs/cmdref/) · [S3 compatibility API](https://docs.oracle.com/en-us/iaas/Content/Object/Tasks/s3compatibleapi.htm) · [Terraform OCI provider](https://registry.terraform.io/providers/oracle/oci/latest) (see [Terraform](../../tools/terraform.md))

> **Verification:** the free-tier limits, idle policy and `compute instance launch` flags were checked against the Oracle docs (November 2026). Only the flags listed for `launch` were checked; other `oci` commands below are marked *(unverified syntax)*. No command was run against an account. Oracle changes the Always Free allowance, so re-read the first link before relying on a number.

## Always Free Resources
RESOURCE | ALWAYS FREE ALLOWANCE
---|---
Arm (Ampere A1) compute | 2 OCPU and 12 GB memory in total (1,500 OCPU-hours and 9,000 GB-hours per month)
AMD compute | Up to 2 `VM.Standard.E2.1.Micro` instances, each 1/8 OCPU and 1 GB
Block volume | 200 GB in total plus 5 backups (minimum boot volume 47 GB on the Compute page, 50 GB on the Block Volume page, not reconciled)
Object Storage | 20 GB on an Always Free-only account, or 10 GB each of Standard, Infrequent Access and Archive on a paid or trial account
Autonomous Database | 2 databases, each 1 OCPU and 20 GB
Load balancing | 1 flexible load balancer (10 Mbps) and 1 network load balancer
Networking | 2 VCNs and 10 TB per month outbound data

Always Free compute and Autonomous Database can only be created in your **home region**, chosen at sign-up and not changeable.

## Pitfalls
PITFALL | DETAIL
---|---
Idle reclamation | A compute instance is idle if, over 7 days, the 95th-percentile CPU is under 20%, network is under 20% and memory is under 20% (memory applies to A1 shapes only). Oracle may reclaim idle Always Free instances, so keep a light workload running
Out of host capacity | A temporary shortage, common for A1. Try another availability domain, a smaller shape, or retry later
Upgrading to Pay As You Go | Always Free resources stay free; only usage above the limits is charged. It often makes capacity easier to obtain
Home region | Cannot be changed. Choose it deliberately when signing up
S3 signing | The S3 compatibility API accepts SigV4 only
Tokens and keys | The API signing key and the Customer Secret Key are secrets, never commit them

## OCI CLI
Install and authenticate with a config file or a browser session.

COMMAND | DESCRIPTION
---|---
`oci setup config` | Interactive setup of `~/.oci/config` and an API signing key *(unverified syntax)*
`oci session authenticate` | Browser-based login that creates a short-lived session token *(unverified syntax)*
`oci iam region list` | List regions *(unverified syntax)*
`oci compute instance list --compartment-id <COMPARTMENT_OCID>` | List instances *(unverified syntax)*

Launch an instance (flags verified):

```bash
oci compute instance launch \
  --availability-domain AD_NAME \
  --compartment-id COMPARTMENT_OCID \
  --shape VM.Standard.A1.Flex \
  --shape-config '{"ocpus": 2, "memoryInGBs": 12}' \
  --image-id IMAGE_OCID \
  --subnet-id SUBNET_OCID \
  --ssh-authorized-keys-file ~/.ssh/id_ed25519.pub \
  --assign-public-ip true \
  --display-name NAME \
  --boot-volume-size-in-gbs 50
```

The `--shape-config` JSON form is the usual way to size a flexible shape *(unverified)*.

## Networking and Firewall
Instances sit in a VCN. Two layers filter traffic: security lists or network security groups (NSGs) in OCI, and the guest firewall (for example `iptables` or `firewalld`). Ubuntu images ship with restrictive default `iptables` rules, so opening a port in OCI alone is often not enough.

COMMAND | DESCRIPTION
---|---
`oci network nsg rules add` | Add rules to a network security group *(unverified syntax)*
`oci network security-list update` | Replace a security list's rules (overwrites the full rule set) *(unverified syntax)*

## Object Storage
COMMAND | DESCRIPTION
---|---
`oci os bucket create --name <BUCKET> --compartment-id <COMPARTMENT_OCID>` | Create a bucket *(unverified syntax)*
`oci os object put --bucket-name <BUCKET> --file <FILE>` | Upload an object *(unverified syntax)*

S3-compatible endpoint (path style): `https://<NAMESPACE>.compat.objectstorage.<REGION>.oci.customer-oci.com`. The virtual-hosted style is `https://vhcompat.objectstorage.<REGION>.oci.customer-oci.com`. Authenticate with a Customer Secret Key. Use it as a backup target with [restic](../../backup/restic.md) or [rclone](../../backup/rclone.md).

## See Also
- [Cloud-Provider Comparison](cloud-provider-comparison.md)
- [What is Cloud-Computing?](../what-is-cloud-computing.md)
- [Terraform](../../tools/terraform.md)
- [restic](../../backup/restic.md)

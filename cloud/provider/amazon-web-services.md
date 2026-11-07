# Amazon Web Services
AWS from a self-hoster's point of view: the few services worth using for a VPS, off-site backups, DNS and cost control, and the pitfalls that generate surprise bills. For generic CLI usage see [AWS CLI](../../tools/aws-cli.md); to compare providers see [Cloud-Provider Comparison](cloud-provider-comparison.md).

Documentation: [AWS CLI Command Reference](https://docs.aws.amazon.com/cli/latest/reference/) · [AWS Free Tier](https://aws.amazon.com/free/) · [Terraform AWS provider](https://registry.terraform.io/providers/hashicorp/aws/latest) (see [Terraform](../../tools/terraform.md))

> **Verification:** flag names were checked against the AWS CLI reference pages and prices against the AWS pricing pages (November 2026). No command was run against an account. Prices and free-tier terms change often, so check the pricing pages before relying on a figure. Items marked *(unverified)* were not confirmed.

## Services a Self-Hoster Uses
NEED | SERVICE | NOTES
---|---|---
Virtual machine | EC2 | Billed per second while running
Simple fixed-price VPS | Lightsail | Cheaper and simpler than EC2 for one box
Object storage | S3 | Off-site backups, static files
Cold backups | S3 Glacier classes | Cheap to store, restore delay and fees
DNS | Route 53 | Hosted zones are billed monthly per zone
Firewall | Security groups | Stateful, per instance or network interface
Disk snapshots | EBS snapshots, Data Lifecycle Manager | Scheduled and retained automatically
Access control | IAM | One user or role per purpose, MFA on root
Cost control | Budgets, Cost Explorer | Set a budget on day one

## Free Tier
- New accounts get a **Free plan**: $100 of credits, with up to $100 more for exploring services. It ends after 6 months or when the credits run out. The **Paid plan** gets up to $200 of credits. Source: [AWS Free Tier](https://aws.amazon.com/free/).
- Older accounts may still be on the previous 12-month model. Check the Billing console for which applies.
- Always set a budget (below) even on the Free plan.

## EC2
COMMAND | DESCRIPTION
---|---
`aws ec2 run-instances --image-id <AMI_ID> --instance-type <TYPE> --key-name <KEY_NAME> --security-group-ids <SG_ID> --subnet-id <SUBNET_ID>` | Launch an instance
`--image-id resolve:ssm:/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64` | Use the latest Amazon Linux 2023 AMI (a value for `--image-id`)
`--tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=<NAME>}]'` | Tag the instance at launch
`aws ec2 describe-instances` | List instances (see [AWS CLI](../../tools/aws-cli.md#ec2) for queries)
`aws ec2 stop-instances --instance-ids <ID>` | Stop (compute billing stops, see pitfalls)
`aws ec2 terminate-instances --instance-ids <ID>` | Delete the instance (destroys its data unless volumes are kept)

## Security Groups
COMMAND | DESCRIPTION
---|---
`aws ec2 create-security-group --group-name <NAME> --description <TEXT> --vpc-id <VPC_ID>` | Create a group
`aws ec2 authorize-security-group-ingress --group-id <SG_ID> --protocol tcp --port 22 --cidr 203.0.113.10/32` | Allow SSH from one address only
`aws ec2 describe-security-groups --group-ids <SG_ID>` | Show the rules

Never open SSH or admin ports to `0.0.0.0/0`. Use a VPN such as [WireGuard](../../apps/wireguard.md) or [Tailscale](../../apps/tailscale.md) instead.

## Snapshots and Backups
COMMAND | DESCRIPTION
---|---
`aws ec2 create-snapshot --volume-id <VOLUME_ID> --description <TEXT>` | One-off EBS snapshot
`aws dlm create-lifecycle-policy --execution-role-arn <ROLE_ARN> --description <TEXT> --state ENABLED --policy-details file://policy.json` | Scheduled snapshots with retention (Data Lifecycle Manager)
`aws dlm get-lifecycle-policies` | List policies

## S3
COMMAND | DESCRIPTION
---|---
`aws s3 mb s3://<BUCKET>` | Create a bucket
`aws s3 sync <DIR> s3://<BUCKET>/<PREFIX>` | Upload changes (add `--delete` only if you want removals mirrored)
`aws s3api put-public-access-block --bucket <BUCKET> --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true` | Block all public access
`aws s3api put-bucket-lifecycle-configuration --bucket <BUCKET> --lifecycle-configuration file://lifecycle.json` | Apply lifecycle rules (transition or expire)

STORAGE CLASS | USE | MINIMUM STORAGE
---|---|---
`STANDARD` | Frequent access | none
`STANDARD_IA` | Infrequent access, millisecond reads, retrieval fee | 30 days, 128 KB objects
`GLACIER_IR` | Rarely read (about quarterly), millisecond reads | 90 days
`GLACIER` (Flexible Retrieval) | Archive, restore takes minutes to hours | 90 days
`DEEP_ARCHIVE` | Long-term archive, restore takes hours | 180 days

Lifecycle rule moving backups to Glacier Instant Retrieval after 30 days and deleting after a year (`lifecycle.json`):

```json
{
  "Rules": [
    {
      "ID": "age-out-backups",
      "Status": "Enabled",
      "Filter": { "Prefix": "backups/" },
      "Transitions": [{ "Days": 30, "StorageClass": "GLACIER_IR" }],
      "Expiration": { "Days": 365 }
    }
  ]
}
```

Use S3 as a backup target with [restic](../../backup/restic.md) or [rclone](../../backup/rclone.md).

## IAM for a Backup User
Create one user per purpose with only the access it needs. A policy limited to one bucket (`BUCKET` is a placeholder), adapted from the AWS S3 example policies:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::BUCKET"
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
      "Resource": "arn:aws:s3:::BUCKET/*"
    }
  ]
}
```

COMMAND | DESCRIPTION
---|---
`aws iam create-user --user-name <NAME>` | Create the user
`aws iam put-user-policy --user-name <NAME> --policy-name <POLICY> --policy-document file://policy.json` | Attach an inline policy
`aws iam create-access-key --user-name <NAME>` | Create keys (the secret is shown once, store it in a password manager)
`aws sts get-caller-identity` | Check who the current credentials are

To stop a backup tool deleting its own history, omit `s3:DeleteObject` and rely on lifecycle rules.

## DNS (Route 53)
COMMAND | DESCRIPTION
---|---
`aws route53 list-hosted-zones` | List zones
`aws route53 change-resource-record-sets --hosted-zone-id <ZONE_ID> --change-batch file://change.json` | Create, update or delete records (the JSON holds `Changes` with an `Action` of `UPSERT`, `CREATE` or `DELETE`)

## Cost Control
COMMAND | DESCRIPTION
---|---
`aws budgets create-budget --account-id <ACCOUNT_ID> --budget file://budget.json --notifications-with-subscribers file://notifications.json` | Create a budget with e-mail alerts
`aws ce get-cost-and-usage --time-period Start=2026-11-01,End=2026-12-01 --granularity MONTHLY --metrics UnblendedCost --group-by Type=DIMENSION,Key=SERVICE` | Cost by service for a period

## Pitfalls
PITFALL | DETAIL
---|---
Public IPv4 addresses are billed | $0.005 per hour per address, in use or idle ([VPC pricing](https://aws.amazon.com/vpc/pricing/))
NAT gateway | $0.045 per hour plus $0.045 per GB processed in the example region (us-east-2); other regions *(unverified)*. Use a public subnet or a NAT instance for a homelab
Data transfer out | First 100 GB per month to the internet is free, then charged per GB ([EC2 pricing](https://aws.amazon.com/ec2/pricing/on-demand/))
Stopped instances | Compute billing stops; EBS volume and Elastic IP charges continue *(EBS while stopped unverified on the pricing page; allocated Elastic IPs are charged in use or idle)*
Orphaned snapshots and volumes | Remain billed after the instance is terminated
Access keys | Long-lived keys leak; prefer roles or SSO and never commit `~/.aws/credentials`
Root account | Enable MFA and do not use it day to day

## See Also
- [AWS CLI](../../tools/aws-cli.md)
- [Cloud-Provider Comparison](cloud-provider-comparison.md)
- [What is Cloud-Computing?](../what-is-cloud-computing.md)
- [Terraform](../../tools/terraform.md)
- [restic](../../backup/restic.md)

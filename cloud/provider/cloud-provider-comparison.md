# Cloud-Provider Comparison
Equivalent services across major providers. Background: [What is Cloud-Computing?](../what-is-cloud-computing.md). Provider sheets: [Amazon Web Services](amazon-web-services.md), [Google Cloud](google-cloud.md), [Hetzner Cloud](hetzner-cloud.md), [DigitalOcean](digitalocean.md), [Cloudflare](cloudflare.md), [Oracle Cloud](oracle-cloud.md), [Backblaze B2](backblaze-b2.md) and [Civo](civo.md).

> Product names change. Treat this as a map, then check each provider's current docs and pricing.

## Services Map
CATEGORY | AWS | Azure | Google Cloud | Civo
---|---|---|---|---
Virtual machines | EC2 | Virtual Machines | Compute Engine | Instances
Managed Kubernetes | EKS | AKS | GKE | Civo Kubernetes (K3s)
Serverless functions | Lambda | Functions | Cloud Functions / Cloud Run functions | n/a
Serverless containers | Fargate / App Runner | Container Apps | Cloud Run | n/a
Object storage | S3 | Blob Storage | Cloud Storage | Object Store
Block storage | EBS | Managed Disks | Persistent Disk | Volumes
File storage | EFS | Azure Files | Filestore | n/a
Managed SQL | RDS / Aurora | Azure SQL / Database for PostgreSQL | Cloud SQL / AlloyDB | Databases
NoSQL | DynamoDB | Cosmos DB | Firestore / Bigtable | n/a
Private network | VPC | VNet | VPC | Private networks
Load balancer | ELB / ALB / NLB | Load Balancer / App Gateway | Cloud Load Balancing | Load balancers
DNS | Route 53 | Azure DNS | Cloud DNS | DNS
CDN | CloudFront | Front Door / CDN | Cloud CDN | n/a
Identity | IAM | Entra ID + RBAC | Cloud IAM | Teams / API keys
Secrets | Secrets Manager | Key Vault | Secret Manager | n/a
Monitoring | CloudWatch | Azure Monitor | Cloud Monitoring | Basic metrics
IaC (native) | CloudFormation | Bicep / ARM | Deployment Manager | none (use [Terraform](../../tools/terraform.md))
CLI | `aws` | `az` | `gcloud` | `civo`

## Self-Hosting Providers
PROVIDER | GOOD FOR | SHEET
---|---|---
Hetzner Cloud | Cheap European VPS, Storage Box for backups | [Hetzner Cloud](hetzner-cloud.md)
DigitalOcean | Simple Droplets, Spaces, clear billing | [DigitalOcean](digitalocean.md)
Cloudflare | DNS, Tunnel, R2 with no egress fees | [Cloudflare](cloudflare.md)
Oracle Cloud | Largest free VPS allowance (Always Free) | [Oracle Cloud](oracle-cloud.md)
Backblaze B2 | Cheap off-site backup storage | [Backblaze B2](backblaze-b2.md)
AWS | S3, Route 53, wide catalogue | [Amazon Web Services](amazon-web-services.md)
Google Cloud | Free e2-micro, Cloud Run | [Google Cloud](google-cloud.md)
Civo | Managed K3s, simple pricing | [Civo](civo.md)

## When to Pick What
NEED | LEANING
---|---
Widest service catalogue | AWS
Microsoft shop, hybrid with on-prem AD | Azure
Data, analytics, Kubernetes pedigree | Google Cloud
Simple, predictable pricing, fast K3s clusters, learning | Civo
Small hobby or homelab extension | Civo, Hetzner, DigitalOcean, Linode
Cheap off-site backups | Backblaze B2, Hetzner Storage Box, Cloudflare R2
Free VPS | Oracle Cloud Always Free, Google Cloud e2-micro

## Free Tiers (check current terms)
PROVIDER | TYPICAL OFFER
---|---
AWS | 12 months of small free tier plus always-free services
Azure | Credit plus 12 months of selected services
Google Cloud | Credit plus always-free small usage
Civo | Sign-up credit
Oracle Cloud | Always Free: Arm VM (2 OCPU, 12 GB), 2 AMD micro VMs, 200 GB block storage
Backblaze B2 | First 10 GB of storage free

## CLI Quick Start
PROVIDER | LOGIN | LIST VMS
---|---|---
AWS | `aws configure` | `aws ec2 describe-instances`
Azure | `az login` | `az vm list -o table`
Google Cloud | `gcloud auth login` | `gcloud compute instances list`
Civo | `civo apikey save <NAME> <KEY>` | `civo instance list`

## Cost Tips
- Egress is the common surprise. Keep traffic in one region where possible.
- Use spot or preemptible instances for fault-tolerant work.
- Right-size, and turn off dev environments out of hours.
- Use budgets and alerts on every account.

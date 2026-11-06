# What is Cloud-Computing?
Cloud computing is on-demand access to computing resources (servers, storage, databases, networking, software) over the internet with pay-as-you-go pricing. Provider comparison: [Cloud-Provider Comparison](provider/cloud-provider-comparison.md).

## Service Models
MODEL | YOU MANAGE | PROVIDER MANAGES | EXAMPLES
---|---|---|---
**IaaS** (Infrastructure) | OS, runtime, app, data | Hardware, virtualisation, network | EC2, Azure VMs, Compute Engine, Civo instances
**PaaS** (Platform) | App and data | Everything below | Heroku, App Engine, Azure App Service, Fly.io
**SaaS** (Software) | Your usage and data | Everything | Microsoft 365, Gmail, Salesforce
**FaaS** (Functions) | Function code | Servers, scaling | AWS Lambda, Cloud Functions, Azure Functions
**CaaS** (Containers) | Containers and config | Orchestration, nodes | EKS, GKE, AKS, Civo Kubernetes

## Deployment Models
MODEL | DESCRIPTION
---|---
Public | Shared infrastructure run by a provider
Private | Dedicated to one organisation, on-premises or hosted
Hybrid | Public and private connected together
Multi-cloud | Using more than one public provider

## Shared Responsibility
The provider secures the cloud (hardware, facilities, core services). You secure what you put **in** it: identities, data, configuration, patching of anything you run.

## Key Concepts
TERM | MEANING
---|---
Region | Geographic area containing several data centres
Availability Zone | Isolated data centre (or group) within a region
Elasticity | Scale up and down automatically with demand
Pay-as-you-go | Billed per use, usually per second, hour or GB
Reserved / Savings plan | Discount for committing 1 to 3 years
Spot / Preemptible | Cheap spare capacity that can be reclaimed
Egress | Data leaving the provider, usually the surprise cost
IaC | Infrastructure as Code, see [Terraform](../tools/terraform.md)
Serverless | No servers to manage, billed per invocation
Object storage | Flat, API-accessed storage (S3 style)
Block storage | Disk volumes attached to VMs
CDN | Edge caching close to users
VPC | Your private virtual network inside a provider

## Pros and Cons
PROS | CONS
---|---
No upfront hardware spend | Costs can grow unnoticed
Fast provisioning and global reach | Vendor lock-in
Built-in resilience and managed services | Egress and support fees
Elastic scaling | Shared-responsibility mistakes (open buckets, weak IAM)

## Good Habits
- Tag every resource for cost tracking.
- Set budget alerts on day one.
- Use least-privilege IAM and MFA on the root account.
- Define infrastructure in code ([Terraform](../tools/terraform.md)) and keep it in Git.
- Plan for a second AZ for anything important.
- Delete what you no longer use.

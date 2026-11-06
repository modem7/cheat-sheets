# Terraform
Terraform is an infrastructure as code tool to provision, change, and version resources on any environment. Since 2023 it is source-available (BUSL) rather than open source; **OpenTofu** is the open source fork and a drop-in CLI replacement (`tofu` instead of `terraform`, same commands below). Cloud examples: [Azure CLI (az)](azure-cli.md), [AWS CLI](aws-cli.md), [gcloud (Google Cloud CLI)](gcloud.md), [Civo](../cloud/provider/civo.md).

Project Homepage: [Terraform by HashiCorp](https://www.terraform.io/)
Documentation: [Terraform Docs](https://developer.hashicorp.com/terraform/docs), [OpenTofu](https://opentofu.org)
TF Registry: [Terraform Registry](https://registry.terraform.io/)

## Format and Validate
COMMAND | DESCRIPTION
---|---
`terraform fmt -recursive` | Reformat your configuration in the standard style (add `-check` in CI)
`terraform validate` | Check whether the configuration is valid
## Initialize Working Directory
COMMAND | DESCRIPTION
---|---
`terraform init` | Prepare your working directory for other commands
`terraform init -upgrade` | Upgrade providers within version constraints
`terraform init -migrate-state` | Move state after changing the backend
## Plan, Deploy and Cleanup
COMMAND | DESCRIPTION
---|---
`terraform apply --auto-approve` | Create or update infrastructure without confirmation prompt
`terraform destroy --auto-approve` | Destroy previously-created infrastructure without confirmation prompt
`terraform plan -out plan.out` | Output the deployment plan to plan.out
`terraform apply plan.out` | Use the plan.out to deploy infrastructure
`terraform plan -destroy` | Outputs a destroy plan
`terraform apply -target=aws_instance.myinstance` | Only apply/deploy changes to targeted resource
`terraform apply -var myregion=us-east-1` | Pass a variable via CLI while applying a configuration
`terraform apply -lock-timeout=60s` | Wait for the state lock (locking is on by default for backends that support it)
`terraform apply -refresh=false` | Do not reconcile state file with real-world resources
`terraform apply -replace=aws_instance.myinstance` | Force recreation of one resource (replaces the old `taint`)
`terraform plan -var-file=prod.tfvars` | Use a variables file
`terraform apply --parallelism=5` | Number of simultaneous resource operations
`terraform apply -refresh-only` | Reconcile the state file with real-world resources (the standalone `terraform refresh` is deprecated)
`terraform providers` | Get information about providers used in the current configuration
## Workspaces
COMMAND | DESCRIPTION
---|---
`terraform workspace new myworkspace` | Create a new workspace
`terraform workspace select default` | Change to a workspace
`terraform workspace list` | List all workspaces
## State Manipulation
COMMAND | DESCRIPTION
---|---
`terraform state show aws_instance.myinstance` | Show details stored in the Terraform state file
`terraform state pull > terraform.tfstate` | Output Terraform state to a file
`terraform state mv aws_iam_role.my_ssm_role module.mymodule` | Move a resource tracked via state to different module
`terraform state replace-provider hashicorp/aws registry.custom.com/aws` | Replace an existing provider with another
`terraform state list` | List all resources tracked in the Terraform state file
`terraform state rm aws_instance.myinstance` | Unmanage a resource, delete it from the Terraform state file
## Import and Outputs
COMMAND | DESCRIPTION
---|---
`terraform import resourcetype.myresource <id>` | Import a resource (or use an `import {}` block with `terraform plan -generate-config-out=gen.tf`)
`terraform output` | List all outputs
`terraform output <output>` | List a specific output
`terraform output -json` | List all outputs in JSON format
## Terraform Cloud
COMMAND | DESCRIPTION
---|---
`terraform login` | Login to Terraform Cloud with an API token
`terraform logout` | Logout from Terraform Cloud

## Inspect and Debug
COMMAND | DESCRIPTION
---|---
`terraform show` | Show the current state (`terraform show plan.out` for a saved plan)
`terraform console` | Evaluate expressions interactively
`terraform graph \| dot -Tpng > graph.png` | Dependency graph (needs Graphviz)
`terraform version` | Terraform and provider versions
`TF_LOG=DEBUG terraform plan` | Verbose logging
`terraform force-unlock <LOCK_ID>` | Clear a stuck state lock (only if no run is active)
`terraform providers lock -platform=linux_amd64 -platform=darwin_arm64` | Record provider checksums for several platforms

## Minimal Example
```hcl
terraform {
  required_version = ">= 1.6"
  required_providers {
    civo = {
      source  = "civo/civo"
      version = "~> 1.0"
    }
  }
}

variable "region" {
  type    = string
  default = "LON1"
}

provider "civo" {
  region = var.region   # token from the CIVO_TOKEN environment variable
}

output "region" {
  value = var.region
}
```
Set sensitive values with environment variables such as `TF_VAR_name` or the provider's own variable, never in committed `.tfvars` files.

## Good Practice
- Commit `.terraform.lock.hcl`. Ignore `.terraform/` and `*.tfstate*` in [Git](git.md).
- Use a **remote backend** (S3 with locking, Azure Storage, GCS or Terraform Cloud) for shared state. State can contain secrets.
- Review `terraform plan` output before every apply; in CI run `fmt -check`, `validate`, `plan`.
- Use `terraform apply --auto-approve` only in automation.
- Policy and linting: `tflint`, `trivy config`, `checkov`.

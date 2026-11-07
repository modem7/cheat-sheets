# Terraform State and Modules
State, workspaces, modules, refactoring (`moved`, `removed`, `import` blocks), targeted runs and `terraform test`. Use it after the basics in [Terraform](terraform.md).

Documentation: [Terraform State](https://developer.hashicorp.com/terraform/language/state), [Modules](https://developer.hashicorp.com/terraform/language/modules), [Refactoring](https://developer.hashicorp.com/terraform/language/modules/develop/refactoring), [Tests](https://developer.hashicorp.com/terraform/language/tests)

> **Verification:** commands, flags and HCL blocks were run with Terraform 1.17.1 on small local-only configurations (`terraform_data` resource and a local module, no cloud provider, no remote backend). `terraform -help` output was used for flags. Remote backends, registry and Git module sources, and `-target` against real infrastructure were not run. OpenTofu was not run: its differences are not covered here (unverified).

## State
State maps your configuration to real objects. It can hold secrets in plain text, so keep it out of Git and use a remote backend with locking for shared work.

COMMAND | DESCRIPTION
---|---
`terraform state list` | List every resource instance in state
`terraform state show <ADDRESS>` | Show the attributes of one resource
`terraform state mv <FROM> <TO>` | Rename or move a resource in state (`-dry-run` to preview)
`terraform state rm <ADDRESS>` | Stop managing a resource without destroying it (`-dry-run` to preview)
`terraform state pull > backup.tfstate` | Print the current state, handy as a backup before surgery
`terraform state push <FILE>` | Overwrite remote state from a file. Dangerous: take a backup first
`terraform state replace-provider <FROM> <TO>` | Change the provider recorded in state
`terraform state identities -json` | List resource identities (requires `-json`)
`terraform show` / `terraform show -json` | Human or machine-readable view of state
`terraform apply -refresh-only` | Update state from the real world without changing anything
`terraform force-unlock <LOCK_ID>` | Release a stuck lock. Only when no run is active

Addresses look like `aws_instance.web`, `aws_instance.web[0]`, `aws_instance.web["key"]` and `module.<NAME>.aws_instance.web`. Quote addresses containing `["key"]` in the shell.

### Backend Changes
COMMAND | DESCRIPTION
---|---
`terraform init -migrate-state` | Move existing state to a newly configured backend
`terraform init -reconfigure` | Use the new backend settings and ignore the saved ones, without migrating
`terraform init -backend-config=<FILE>` | Supply backend settings (for example credentials or a bucket name) from a file or `key=value`, kept out of the committed config
`terraform init -backend=false` | Skip backend setup (useful for `validate` in CI)

## Workspaces
Workspaces give one configuration several separate state files within the same backend. They are not a substitute for separate accounts or environments with different access.

COMMAND | DESCRIPTION
---|---
`terraform workspace list` | List workspaces, current one marked `*`
`terraform workspace show` | Name of the current workspace
`terraform workspace new <NAME>` | Create and switch (`-state=<FILE>` copies an existing state in)
`terraform workspace select <NAME>` | Switch
`terraform workspace delete <NAME>` | Delete an empty workspace (`-force` deletes it even if it manages resources, so they are orphaned)

```hcl
resource "terraform_data" "env" {
  input = terraform.workspace == "prod" ? "large" : "small"
}
```
`terraform.workspace` gives the current name. The default workspace is called `default` and cannot be deleted.

## Modules
A module is a directory of `.tf` files. The root module calls child modules.

COMMAND | DESCRIPTION
---|---
`terraform init` | Downloads modules and providers
`terraform get` | Download or refresh modules only (`-update` checks for newer versions)
`terraform init -upgrade` | Upgrade modules and providers within constraints
`terraform modules` | Show the module tree (`-json` for scripts)
`terraform init -from-module=<SOURCE>` | Copy an existing module into an empty directory as a starting point
`terraform plan -target=module.<NAME>` | Plan only that module (see [Targeting](#targeting-and-replacing))

```hcl
module "app" {
  source = "./modules/app"      # local path
  name   = var.name
}

module "net" {
  source  = "terraform-aws-modules/vpc/aws"   # registry: NAMESPACE/NAME/PROVIDER
  version = "~> 5.0"                          # pin registry modules
}

module "git" {
  source = "git::https://example.com/org/repo.git//modules/app?ref=v1.2.0"
}

output "app_id" {
  value = module.app.id
}
```
Inside the module, declare inputs with `variable`, results with `output`, and reference them as `module.<NAME>.<OUTPUT>`. Registry and Git sources above are illustrative and were not downloaded (unverified).

MODULE ARGUMENT | DESCRIPTION
---|---
`source` | Local path, registry address or Git/HTTP URL
`version` | Constraint, registry modules only
`count` / `for_each` | Create several instances of a module
`providers` | Pass non-default provider configurations
`depends_on` | Explicit dependency

## Refactoring Without Destroying
Rename or restructure in code, then record the change so Terraform does not plan a destroy and create. These blocks need a recent Terraform (the `removed` block needs 1.7 or later).

BLOCK | USE
---|---
`moved` | Renamed resource, moved into or out of a module, or changed `count`/`for_each`
`removed` | Drop a resource from state, optionally keeping the real object
`import` | Adopt an existing object into state via `plan` and `apply`

```hcl
moved {
  from = terraform_data.old_name
  to   = terraform_data.new_name
}

moved {
  from = module.old
  to   = module.new
}

removed {
  from = terraform_data.legacy
  lifecycle {
    destroy = false    # forget it, do not destroy the real object
  }
}

import {
  to = terraform_data.imported
  id = "EXISTING_ID"    # the provider's import ID, see the resource docs
}
```
BEHAVIOUR | NOTES
---|---
`terraform plan` shows `has moved to` | The move is applied to state on the next `apply`, nothing is recreated
Keep `moved` blocks | They help anyone who still has older state. Remove only when sure every state has applied them
`removed` with `destroy = false` | Plan reports that Terraform will no longer manage the object
`terraform plan -generate-config-out=gen.tf` | Experimental: writes configuration for `import` blocks that have no resource block yet. Review before use
`terraform import <ADDRESS> <ID>` | Older CLI form. Needs the resource block to exist first and changes state immediately
`import` block `for_each` | Import several objects in one block (checked on 1.17.1)

## Targeting and Replacing
COMMAND | DESCRIPTION
---|---
`terraform plan -target=<ADDRESS>` | Limit the plan to a resource or module and its dependencies
`terraform apply -target=<ADDRESS>` | Apply only that part. Repeat the flag for several addresses
`terraform apply -replace=<ADDRESS>` | Destroy and recreate one resource instance (replaces `terraform taint`)
`terraform plan -replace=<ADDRESS>` | Preview the replacement
`terraform taint <ADDRESS>` / `terraform untaint <ADDRESS>` | Older way to mark a resource for replacement, superseded by `-replace`
`terraform plan -refresh=false` | Skip the refresh step
`terraform plan -detailed-exitcode` | Exit 0 no changes, 1 error, 2 changes pending (CI drift check)

`-target` is for recovery and exceptional cases: Terraform warns that the result may be incomplete and state can drift from code. Run a full plan afterwards.

LIFECYCLE ARGUMENT | EFFECT
---|---
`prevent_destroy = true` | Error on any plan that would destroy the resource
`create_before_destroy = true` | Create the replacement first
`ignore_changes = [<ATTRIBUTE>]` | Ignore drift on listed attributes
`replace_triggered_by = [<RESOURCE>]` | Replace when another resource in the same configuration changes (resource references only, not whole modules)

## Terraform Test
Test files end in `.tftest.hcl` and live next to the configuration or in a `tests/` directory. Each `run` block executes a plan or apply and checks assertions. Resources created by `command = apply` are destroyed when the file finishes.

COMMAND | DESCRIPTION
---|---
`terraform test` | Run all tests
`terraform test -verbose` | Print the plan or state for each run block
`terraform test -filter=<FILE>` | Run only the named test file (repeatable)
`terraform test -var 'name=value'` | Set an input variable
`terraform test -test-directory=<DIR>` | Look for tests somewhere other than `tests`
`terraform test -json` / `-junit-xml=<FILE>` | Machine-readable output and JUnit report for CI

```hcl
variables {
  name = "demo"
}

run "applies" {
  command = apply      # or plan (the default is apply)
  assert {
    condition     = module.app.id != ""
    error_message = "module output is empty"
  }
}

run "rejects_empty_name" {
  command = plan
  variables {
    name = ""
  }
  expect_failures = [var.name]    # passes only if the validation fails
}
```
With `command = plan`, a condition that depends on a value only known after apply fails with "Unknown condition value". Use `command = apply` for those checks.

BLOCK | DESCRIPTION
---|---
`mock_provider "<NAME>" {}` | Replace a provider with a mock so no real infrastructure is touched (Terraform 1.7 or later)
`override_resource { target = <ADDRESS> values = { ... } }` | Fake one resource's attributes (add `override_during = plan` to make them available at plan time)
`override_module`, `override_data` | Same for modules and data sources
`run` `module { source = "<PATH>" }` | Test a different module in that run
`expect_failures = [<ADDRESS>]` | Expect a validation, check or precondition to fail

## Good Practice
- Take `terraform state pull > backup.tfstate` before `state mv`, `state rm` or `state push`.
- Prefer `moved`, `removed` and `import` blocks over CLI state edits: they are reviewable in a pull request.
- Run `terraform plan -detailed-exitcode` in CI to catch drift.
- Pin module versions and commit `.terraform.lock.hcl`.
- Keep `-target` out of routine pipelines.

## OpenTofu
`tofu` accepts the same subcommands used here, but its feature set has diverged from Terraform's since the fork (it adds features such as state encryption, unverified here). Check the [OpenTofu docs](https://opentofu.org/docs/) for each block and flag before relying on it: not verified here.

## See Also
- [Terraform](terraform.md)
- [Ansible Cheat-Sheet](ansible.md)
- [Packer](packer.md)

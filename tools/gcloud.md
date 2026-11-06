# gcloud (Google Cloud CLI)
The `gcloud` CLI manages Google Cloud from the terminal. Compare [AWS CLI](aws-cli.md) and [Azure CLI (az)](azure-cli.md); for infrastructure as code see [Terraform](terraform.md).

Documentation: [gcloud reference](https://cloud.google.com/sdk/gcloud/reference)

---
## Install
PLATFORM | COMMAND
---|---
Debian / Ubuntu | add Google's apt repository and `sudo apt install google-cloud-cli` (see the install docs)
macOS | `brew install --cask google-cloud-sdk` ([Homebrew](../macos/homebrew.md))
Windows | the installer, or `choco install gcloudsdk` ([Chocolatey](../windows/chocolatey.md))

## Sign In and Configuration
COMMAND | DESCRIPTION
---|---
`gcloud init` | Guided login and project selection
`gcloud auth login` | Sign in with your user account
`gcloud auth login --no-browser` | Sign in on a headless machine
`gcloud auth application-default login` | Credentials for client libraries and tools such as [Terraform](terraform.md)
`gcloud auth list` | Accounts
`gcloud config set project PROJECT_ID` | Default project
`gcloud config set compute/region europe-west2` | Default region (also `compute/zone`)
`gcloud config list` | Current settings
`gcloud config configurations create work` | Separate named configuration (`activate` to switch)
`gcloud projects list` | Projects

## Compute
COMMAND | DESCRIPTION
---|---
`gcloud compute instances list` | List VMs
`gcloud compute instances create vm1 --zone=europe-west2-a --machine-type=e2-small --image-family=ubuntu-2204-lts --image-project=ubuntu-os-cloud` | Create a VM
`gcloud compute ssh vm1 --zone=europe-west2-a` | SSH (manages keys for you, see [OpenSSH Cheat-Sheet](openssh.md))
`gcloud compute instances stop\|start\|delete vm1 --zone=...` | Power and delete
`gcloud compute firewall-rules list` | Firewall rules
`gcloud compute images list --filter="family~ubuntu"` | Images

## Kubernetes (GKE)
COMMAND | DESCRIPTION
---|---
`gcloud container clusters list` | List clusters
`gcloud container clusters create-auto mycluster --region=europe-west2` | Autopilot cluster
`gcloud container clusters get-credentials mycluster --region=europe-west2` | Add to kubeconfig ([Kubectl](../kubernetes/kubectl.md))
`gcloud container clusters delete mycluster --region=europe-west2` | Delete

## Storage, IAM and Secrets
COMMAND | DESCRIPTION
---|---
`gcloud storage ls gs://bucket` | List
`gcloud storage cp file gs://bucket/` | Upload (`-r` for directories)
`gcloud storage rsync ./dir gs://bucket/dir` | Sync
`gcloud iam service-accounts list` | Service accounts
`gcloud projects add-iam-policy-binding PROJECT --member=user:me@example.com --role=roles/viewer` | Grant a role
`gcloud secrets versions access latest --secret=NAME` | Read a secret

## Formatting and Components
OPTION | DESCRIPTION
---|---
`--format=json\|yaml\|table\|"value(name)"` | Output format (`value()` is good for scripts)
`--filter="status=RUNNING"` | Server-side filter
`--project=ID` | Override the project for one command
`gcloud components update` | Update (not available when installed by a package manager; use `apt`/`brew`)
`gcloud help <command>` | Help

## Not Verified
Written from knowledge of the CLI and not run against a project. Check `gcloud <command> --help`, as flags and image families change.

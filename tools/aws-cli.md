# AWS CLI
The AWS CLI (v2) manages Amazon Web Services from the terminal. Compare [Azure CLI (az)](azure-cli.md) and [gcloud (Google Cloud CLI)](gcloud.md); for infrastructure as code see [Terraform](terraform.md). Provider-level notes (free tier, pitfalls, backups): [Amazon Web Services](../cloud/provider/amazon-web-services.md).

Documentation: [AWS CLI Command Reference](https://docs.aws.amazon.com/cli/latest/)

---
## Install
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o awscliv2.zip
unzip awscliv2.zip && sudo ./aws/install
aws --version
```
Use `awscli-exe-linux-aarch64.zip` on ARM. macOS: `brew install awscli` ([Homebrew](../macos/homebrew.md)). Windows: `choco install awscli` ([Chocolatey](../windows/chocolatey.md)) or the MSI. Update by re-running the installer with `--update`.

## Credentials and Profiles
COMMAND | DESCRIPTION
---|---
`aws configure` | Set access key, secret, region and output (stored in `~/.aws`)
`aws configure sso` | Set up a profile for IAM Identity Center (SSO)
`aws sso login --profile NAME` | Sign in with SSO
`aws sts get-caller-identity` | Who am I (best first check)
`aws configure list-profiles` | List profiles
`export AWS_PROFILE=NAME` | Use a profile for the shell
`aws s3 ls --profile NAME --region eu-west-2` | Per-command profile and region

Prefer SSO or short-lived roles over long-lived access keys. Never commit `~/.aws/credentials`.

## S3
COMMAND | DESCRIPTION
---|---
`aws s3 ls` | List buckets
`aws s3 ls s3://bucket/prefix/ --recursive --human-readable --summarize` | List with sizes
`aws s3 cp file s3://bucket/` | Upload
`aws s3 cp s3://bucket/file .` | Download
`aws s3 sync ./dir s3://bucket/dir --delete` | Sync a directory (`--delete` removes extra remote files; add `--dryrun` first)
`aws s3 rm s3://bucket/prefix/ --recursive` | Delete
`aws s3 mb s3://new-bucket` | Create a bucket
`aws s3 presign s3://bucket/file --expires-in 3600` | Temporary download URL

## EC2
COMMAND | DESCRIPTION
---|---
`aws ec2 describe-instances --query "Reservations[].Instances[].[InstanceId,State.Name,PrivateIpAddress,Tags[?Key=='Name']\|[0].Value]" --output table` | Instances at a glance
`aws ec2 start-instances --instance-ids i-0123` | Start (also `stop-instances`, `terminate-instances`)
`aws ec2 describe-security-groups --output table` | Security groups
`aws ec2 describe-regions --query "Regions[].RegionName" --output text` | Regions

## IAM, Kubernetes and Containers
COMMAND | DESCRIPTION
---|---
`aws iam list-users --output table` | List users
`aws iam list-attached-user-policies --user-name NAME` | A user's policies
`aws eks list-clusters` | List EKS clusters
`aws eks update-kubeconfig --name CLUSTER --region eu-west-2` | Add the cluster to kubeconfig ([Kubectl](../kubernetes/kubectl.md))
`aws ecr get-login-password --region eu-west-2 \| docker login --username AWS --password-stdin <ACCOUNT>.dkr.ecr.eu-west-2.amazonaws.com` | Log Docker in to ECR ([Docker](../docker/docker.md))
`aws ssm get-parameter --name /path/key --with-decryption --query Parameter.Value --output text` | Read a parameter
`aws secretsmanager get-secret-value --secret-id NAME --query SecretString --output text` | Read a secret

## Output and Querying
OPTION | DESCRIPTION
---|---
`--output table\|json\|text\|yaml` | Output format
`--query 'Items[].Name'` | JMESPath filter (client side)
`--no-cli-pager` | Do not page output (or `export AWS_PAGER=""`)
`--dry-run` | Check permissions for many EC2 actions without doing them
`aws <service> help` | Help for a service
`aws <service> <command> help` | Help and examples for a command

Combine with [jq](jq.md) for anything JMESPath makes awkward.

## Not Verified
Written from knowledge of AWS CLI v2 and not run against an account. Check `aws <service> <command> help` for current flags.

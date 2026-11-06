# Azure CLI (az)
The Azure CLI manages Microsoft Azure resources from the terminal. Compare [[aws-cli]] and [[gcloud]]; for provisioning as code see [[terraform]].

Documentation: [Azure CLI docs](https://learn.microsoft.com/cli/azure/)

---
## Install
PLATFORM | COMMAND
---|---
Debian / Ubuntu | `curl -sL https://aka.ms/InstallAzureCLIDeb \| sudo bash`
macOS | `brew install azure-cli` ([[homebrew]])
Windows | `winget install Microsoft.AzureCLI` or `choco install azure-cli` ([[chocolatey]])
Container | `docker run -it mcr.microsoft.com/azure-cli` ([[docker]])

`az upgrade` updates the CLI. `az version` shows versions.

## Sign In and Subscriptions
COMMAND | DESCRIPTION
---|---
`az login` | Browser sign-in
`az login --use-device-code` | Sign in on a headless machine
`az login --service-principal -u <APP-ID> -p <SECRET> --tenant <TENANT>` | Service principal (automation)
`az account list -o table` | List subscriptions
`az account set --subscription "<NAME-OR-ID>"` | Choose the active subscription
`az account show` | Current subscription
`az logout` | Sign out

## Resource Groups
COMMAND | DESCRIPTION
---|---
`az group create -n myrg -l westeurope` | Create
`az group list -o table` | List
`az group delete -n myrg --yes --no-wait` | Delete a group and everything in it
`az resource list -g myrg -o table` | Resources in a group

## Virtual Machines
COMMAND | DESCRIPTION
---|---
`az vm image list -o table` | Common images
`az vm list-sizes -l westeurope -o table` | Sizes in a region
`az vm create -g myrg -n myvm --image Ubuntu2204 --size Standard_B2s --admin-username azureuser --generate-ssh-keys` | Create a Linux VM
`az vm list -g myrg -d -o table` | List with power state and IPs
`az vm start\|stop\|deallocate\|restart -g myrg -n myvm` | Power actions (use `deallocate` to stop billing for compute)
`az vm open-port -g myrg -n myvm --port 80` | Open a port in the NSG
`az vm delete -g myrg -n myvm --yes` | Delete

## Kubernetes (AKS) and Registry
COMMAND | DESCRIPTION
---|---
`az aks create -g myrg -n myaks --node-count 2 --generate-ssh-keys` | Create a cluster
`az aks get-credentials -g myrg -n myaks` | Add to kubeconfig (see [[kubectl]])
`az aks list -o table` | List clusters
`az aks scale -g myrg -n myaks --node-count 3` | Scale
`az aks delete -g myrg -n myaks --yes --no-wait` | Delete
`az acr create -g myrg -n myregistry --sku Basic` | Create a container registry
`az acr login -n myregistry` | Log Docker in to it

## Storage
COMMAND | DESCRIPTION
---|---
`az storage account create -g myrg -n mystorageacct --sku Standard_LRS` | Create (name is globally unique, lowercase)
`az storage container create --account-name mystorageacct -n data --auth-mode login` | Create a blob container
`az storage blob upload --account-name mystorageacct -c data -f ./file -n file --auth-mode login` | Upload
`az storage blob list --account-name mystorageacct -c data --auth-mode login -o table` | List

## Identity and Access
COMMAND | DESCRIPTION
---|---
`az ad sp create-for-rbac --name myapp --role Contributor --scopes /subscriptions/<SUB>/resourceGroups/myrg` | Service principal limited to one group
`az role assignment create --assignee <ID> --role Reader --scope <SCOPE>` | Grant a role
`az role assignment list --assignee <ID> -o table` | List roles
`az keyvault secret show --vault-name myvault -n mysecret --query value -o tsv` | Read a secret

## Output and Querying
OPTION | DESCRIPTION
---|---
`-o table` / `-o json` / `-o tsv` / `-o yaml` | Output format (`tsv` is good for scripts)
`--query "[].{Name:name, Size:hardwareProfile.vmSize}"` | JMESPath filter
`--query "[?location=='westeurope'].name" -o tsv` | Filter rows
`az config set defaults.group=myrg defaults.location=westeurope` | Default group and location
`az find "az vm create"` | Example commands
`az <group> --help` | Help for any command group

## Not Verified
Written from knowledge of the CLI and not run against a subscription. Check `az <command> --help`, as parameter names and image aliases change.

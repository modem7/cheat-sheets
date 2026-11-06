# Civo

Homepage: [Civo](https://www.civo.com/)
Documentation: [Civo Docs](https://www.civo.com/docs)
Terraform Registry: [Terraform Registry](https://registry.terraform.io/providers/civo/civo/latest) (see [Terraform](../../tools/terraform.md))

> Civo's product line and regions change over time. Check the docs for what is currently offered before relying on any size, image or region below. Commands here were written from knowledge and not run against a live account.

---

## Civo CLI
Civo CLI is a tool to manage your Civo account from the terminal. It is built with Go and distributed as binaries for multiple operating systems, available at https://github.com/civo/cli/releases (or `brew install civo` on macOS, see [Homebrew](../../macos/homebrew.md)).

### Authentication
You authenticate to the Civo API with an API key. Find or regenerate it in the Civo dashboard under your account security settings.

COMMAND | DESCRIPTION
---|---
`civo apikey add <NAME> <KEY>` | Save an API key
`civo apikey list` | List saved keys
`civo apikey current <NAME>` | Choose the active key
`civo region ls` | List regions
`civo region current <REGION>` | Choose the active region

### Kubernetes
Civo's Kubernetes is based on [K3s](../../kubernetes/k3s.md).

COMMAND | DESCRIPTION
---|---
`civo kubernetes size` | List node sizes
`civo kubernetes create <NAME> --size <SIZE> --nodes 3 --wait` | Create a cluster
`civo kubernetes create <NAME> --nodes 3 --wait --save --merge --switch` | Create and add it to `~/.kube/config` and switch context
`civo kubernetes list` | List clusters
`civo kubernetes config <NAME> --save --merge` | Fetch the kubeconfig and merge it (see [Kubectl](../../kubernetes/kubectl.md))
`civo kubernetes scale <NAME> --nodes 5` | Change the node count
`civo kubernetes remove <NAME>` | Delete a cluster

### Instances
Create an instance with `civo instance create` and a hostname, plus any options.

**Example:**
```bash
civo instance create --hostname=<your-hostname> --sshkey=<your-ssh-key-name> --initialuser=<user> --size=<size-from-civo-instance-size> --diskimage=<id-from-civo-diskimage-ls>
```

**Common parameters:**
PARAMETER | DESCRIPTION
---|---
`--diskimage` | Disk image (from `civo diskimage ls`)
`--firewall` | Firewall name or ID
`--hostname` | Hostname
`--initialuser` | Initial user
`--network` | Network name or ID
`--publicip` | `none` or `create` (default `create`)
`--size` | Size (from `civo instance size`)
`--sshkey` | SSH key name or ID
`--tags` | Tags
`--wait` | Wait until the instance is ready

COMMAND | DESCRIPTION
---|---
`civo instance size` | List instance sizes
`civo diskimage ls` | List available disk images (IDs change, never hard-code them)
`civo instance ls` | List instances
`civo instance show <HOSTNAME>` | Show details and IP
`civo instance remove <HOSTNAME>` | Delete an instance
`civo sshkey create <NAME> --key <PATH-TO-PUB-KEY>` | Upload an SSH key
`civo firewall create <NAME>` | Create a firewall (then add rules with `civo firewall rule create`)

### Traefik and DNS
Civo DNS is a supported ACME DNS provider for Traefik (`provider: civo`, see [Traefik](../../apps/traefik.md)) and cert-manager ([Cert-Manager](../../apps/cert-manager.md) via a webhook solver).

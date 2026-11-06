# Helm Cheat-Sheet
Helm is the package manager for [Kubernetes](../kubernetes/kubernetes.md). This sheet uses **Helm 3** syntax: there is no Tiller, release names are positional (no `--name`), and `helm delete` is `helm uninstall`.

Documentation: [Helm Docs](https://helm.sh/docs/)

## Repository Management
COMMAND | DESCRIPTION
---|---
`helm repo add <NAME> <URL>` | Add a chart repository
`helm repo list` | List repositories
`helm repo update` | Refresh chart indexes
`helm repo remove <NAME>` | Remove a repository

## Finding Charts
COMMAND | DESCRIPTION
---|---
`helm search repo <KEYWORD>` | Search added repositories
`helm search repo <REPO>/<CHART> --versions` | List all versions of a chart
`helm search hub <KEYWORD>` | Search Artifact Hub
`helm show values <REPO>/<CHART>` | Show default values
`helm show values <REPO>/<CHART> > values.yaml` | Save defaults as a starting point
`helm show chart <REPO>/<CHART>` | Show chart metadata
`helm show readme <REPO>/<CHART>` | Show the chart README

## Install and Upgrade
COMMAND | DESCRIPTION
---|---
`helm install <RELEASE> <REPO>/<CHART>` | Install a chart
`helm install <RELEASE> <REPO>/<CHART> -n <NS> --create-namespace` | Install into a new namespace
`helm install <RELEASE> <REPO>/<CHART> -f values.yaml` | Install with a values file
`helm install <RELEASE> <REPO>/<CHART> --set key=value` | Override a single value
`helm install <RELEASE> <REPO>/<CHART> --version <VERSION>` | Pin a chart version
`helm upgrade <RELEASE> <REPO>/<CHART> -f values.yaml` | Upgrade a release
`helm upgrade --install <RELEASE> <REPO>/<CHART> -n <NS> --create-namespace -f values.yaml` | Install or upgrade (idempotent, good for CI)
`helm upgrade ... --atomic --timeout 5m` | Roll back automatically if the upgrade fails
`helm upgrade ... --reuse-values` | Keep previous values (prefer explicit `-f`)

## Inspect and Roll Back
COMMAND | DESCRIPTION
---|---
`helm list -A` | List releases in all namespaces
`helm list -n <NS>` | List releases in a namespace
`helm status <RELEASE> -n <NS>` | Release status and notes
`helm get values <RELEASE> -n <NS>` | Values supplied by the user
`helm get values <RELEASE> -n <NS> -a` | All computed values
`helm get manifest <RELEASE> -n <NS>` | Rendered manifests as deployed
`helm history <RELEASE> -n <NS>` | Revision history
`helm rollback <RELEASE> <REVISION> -n <NS>` | Roll back to a revision
`helm uninstall <RELEASE> -n <NS>` | Remove a release
`helm uninstall <RELEASE> -n <NS> --keep-history` | Remove but keep history

## Testing and Debugging
COMMAND | DESCRIPTION
---|---
`helm template <RELEASE> <REPO>/<CHART> -f values.yaml` | Render manifests locally
`helm install <RELEASE> <REPO>/<CHART> --dry-run --debug` | Simulate an install against the cluster
`helm lint <DIR>` | Lint a chart
`helm diff upgrade <RELEASE> <REPO>/<CHART> -f values.yaml` | Preview changes (needs the `helm-diff` plugin)
`helm test <RELEASE>` | Run chart tests

## Creating Charts
COMMAND | DESCRIPTION
---|---
`helm create <NAME>` | Scaffold a chart
`helm dependency update <DIR>` | Fetch dependencies listed in `Chart.yaml`
`helm package <DIR>` | Package into a `.tgz`
`helm push <CHART>.tgz oci://<REGISTRY>/<PATH>` | Push to an OCI registry
`helm install <RELEASE> oci://<REGISTRY>/<PATH>/<CHART> --version <VERSION>` | Install from OCI

## Chart Folder Structure
```
wordpress/
  Chart.yaml          # Chart metadata, and dependencies (Helm 3)
  Chart.lock          # Locked dependency versions
  LICENSE             # OPTIONAL: license for the chart
  README.md           # OPTIONAL: human-readable README
  values.yaml         # Default configuration values
  values.schema.json  # OPTIONAL: JSON schema to validate values
  charts/             # Chart dependencies
  templates/          # Templates combined with values to render manifests
  templates/NOTES.txt # OPTIONAL: usage notes shown after install
```

## Handy Plugins
```bash
helm plugin install https://github.com/databus23/helm-diff
helm plugin list
```

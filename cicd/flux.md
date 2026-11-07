# Flux CD
Flux is a GitOps toolkit for [Kubernetes](../kubernetes/kubernetes.md): controllers in the cluster pull manifests, Helm charts or OCI artifacts from a source and keep the cluster in step with it. Use it for continuous delivery after CI has built and pushed an image. Compare with [Argo CD](../apps/argocd.md) and see [Kubernetes Automation](../kubernetes/kubernetes-automation.md) for the wider picture. Command output below was checked against `flux` v2.10.0.

Documentation: [Flux docs](https://fluxcd.io/flux/)
Project: [fluxcd/flux2](https://github.com/fluxcd/flux2)

---
## Concepts
OBJECT | PURPOSE
---|---
`GitRepository`, `OCIRepository`, `HelmRepository`, `Bucket` | Sources: where manifests or charts come from
`Kustomization` | Applies a path from a source (plain YAML or Kustomize), optionally pruning and health checking
`HelmRelease` | Installs and upgrades a Helm chart from a source
`Provider`, `Alert`, `Receiver` | Notifications out, webhooks in
Image automation objects | Scan registries and commit new tags back to Git (`flux create image`)

Everything lives in the `flux-system` namespace by default (`-n` changes it).

## Install and Bootstrap
COMMAND | DESCRIPTION
---|---
`flux check --pre` | Check the cluster meets the prerequisites
`flux check` | Check the installed components are healthy
`flux install` | Install or upgrade the controllers directly (no Git involved)
`flux install --export > flux.yaml` | Write the install manifests to stdout instead of applying them
`flux bootstrap github --owner=<OWNER> --repository=<REPO> --branch=main --path=clusters/prod --personal` | Create the repo if needed, commit Flux manifests and sync the cluster to that path (`--personal` means the owner is a user, not an organisation)
`flux bootstrap github ... --read-write-key` | Give the deploy key write access (needed for image automation)
`flux bootstrap github ... --private=false` | Make the repository public (the default is private)
`flux bootstrap git --url=ssh://git@HOST/ORG/REPO --private-key-file=<KEY> --path=<PATH>` | Bootstrap against any Git server (`flux bootstrap gitlab`, `gitea` and others exist)
`flux uninstall --dry-run` | Preview what would be removed
`flux uninstall --silent` | Remove Flux and its CRDs without asking (deletes the toolkit resources; `--keep-namespace` keeps the namespace)
`flux version` | Client and server component versions

Set `GITHUB_TOKEN` in the environment before `bootstrap github` (shown in its `--help` examples); `--token-auth` uses the token instead of an SSH deploy key.

## Inspect
COMMAND | DESCRIPTION
---|---
`flux get all` | Every Flux resource and its status
`flux get sources git` | GitRepository status (also `helm`, `oci`, `bucket`, or `flux get sources all`)
`flux get kustomizations` | Kustomization status
`flux get helmreleases -A` | HelmReleases in all namespaces
`flux get kustomizations --status-selector ready=false` | Only the ones that are not ready
`flux get kustomizations -w` | Watch for changes
`flux tree kustomization <NAME>` | Resources reconciled by a Kustomization (preview command)
`flux trace <KIND>/<NAME> -n <NAMESPACE>` | Show which source and revision manages an object (preview command)
`flux events --for Kustomization/<NAME>` | Events for one object (`--types Warning`, `-w`)
`flux logs --level=error --all-namespaces` | Controller logs (preview command; `--kind`, `--name`, `--since`, `-f`, `--tail`)
`flux stats` | Report of resources and source storage used (preview command)

## Create and Reconcile
COMMAND | DESCRIPTION
---|---
`flux create source git <NAME> --url=<URL> --branch=main --interval=5m` | Define a Git source (`--tag`, `--tag-semver`, `--secret-ref`, `--username`, `--password`)
`flux create source helm <NAME> --url=<URL> --interval=1h` | Define a Helm repository
`flux create kustomization <NAME> --source=GitRepository/<SRC> --path=./deploy --prune=true --interval=10m` | Apply a path from a source
`flux create kustomization ... --wait=true --health-check-timeout=3m` | Wait for workloads to become ready
`flux create kustomization ... --depends-on=<OTHER>` | Apply only after another Kustomization is ready
`flux create helmrelease <NAME> --source=HelmRepository/<REPO> --chart=<CHART> --chart-version=">=6.0.0" --interval=10m` | Install a chart
`flux create secret git <NAME> --url=ssh://git@HOST/ORG/REPO` | Generate a Git credentials secret (SSH key or `--username`/`--password`)
`flux create ... --export` | Print the YAML instead of applying it (the usual way to produce files for Git)
`flux export source git --all > sources.yaml` | Export existing objects as YAML
`flux reconcile source git <NAME>` | Fetch the source now
`flux reconcile kustomization <NAME> --with-source` | Re-sync the source then apply
`flux reconcile helmrelease <NAME>` | Reconcile a HelmRelease
`flux suspend kustomization <NAME>` / `flux resume kustomization <NAME>` | Pause and restart reconciliation (`--all` for every resource of that kind in the namespace)
`flux delete kustomization <NAME>` | Delete the object (with pruning on, its resources go too)
`flux diff kustomization <NAME> --path=./deploy` | Server-side dry run of local files against the cluster (exit 1 if there are differences)
`flux build kustomization <NAME> --path=./deploy` | Render the manifests locally

## Example Objects
Produced by `flux create ... --export` on v2.10.0:

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: app
  namespace: flux-system
spec:
  interval: 5m0s
  ref:
    branch: main
  url: https://git.example.com/org/app
---
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: app
  namespace: flux-system
spec:
  interval: 10m0s
  path: ./deploy
  prune: true
  sourceRef:
    kind: GitRepository
    name: app
  timeout: 2m0s
  wait: true
```

```yaml
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata:
  name: podinfo
  namespace: flux-system
spec:
  chart:
    spec:
      chart: podinfo
      reconcileStrategy: ChartVersion
      sourceRef:
        kind: HelmRepository
        name: podinfo
      version: '>=6.0.0'
  interval: 10m0s
```

## OCI Artifacts
COMMAND | DESCRIPTION
---|---
`flux push artifact oci://REGISTRY/NAME:TAG --path=./deploy --source=<GIT_URL> --revision=<REV>` | Package a directory as an OCI artifact (`--revision` format is `<branch\|tag>@sha1:<commit>`)
`flux pull artifact oci://REGISTRY/NAME:TAG --output=./out` | Download one
`flux tag artifact oci://REGISTRY/NAME:TAG --tag=latest` | Add a tag
`flux list artifacts oci://REGISTRY/NAME` | List tags

Create the source with `flux create source oci <NAME> --url=oci://REGISTRY/NAME --tag=<TAG>` (or `--tag-semver`), then point a Kustomization at it with `--source=OCIRepository/<NAME>`.

## Troubleshooting
SYMPTOM | FIX
---|---
Kustomization not ready | `flux get kustomizations`, then `kubectl describe kustomization <NAME> -n flux-system` and `flux logs --kind=Kustomization --name=<NAME>`
Change in Git not applied yet | `flux reconcile kustomization <NAME> --with-source`
Resources deleted unexpectedly | `prune: true` removes anything no longer in Git; suspend first when restructuring
Source cannot authenticate | Recreate the secret (`flux create secret git`) and check `spec.secretRef` on the source
Dependency never becomes ready | Check `dependsOn` chains and `wait`/health check timeouts
Need to stop Flux touching something | `flux suspend kustomization <NAME>`; remember to resume

## See Also
- [Argo CD](../apps/argocd.md)
- [Kubernetes Automation](../kubernetes/kubernetes-automation.md)
- [kubectl](../kubernetes/kubectl.md)
- [Helm](../tools/helm.md)
- [CI/CD Overview](cicd.md)

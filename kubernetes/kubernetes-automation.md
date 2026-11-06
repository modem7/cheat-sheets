# Kubernetes Automation
Tools and patterns for managing Kubernetes ([[kubernetes]]) declaratively instead of by hand.

## GitOps
Keep manifests in Git and let a controller in the cluster apply them. Drift is corrected automatically.

TOOL | DESCRIPTION
---|---
Argo CD | See [[argocd]]. UI plus CRDs, syncs apps from Git or Helm
Flux | Controller toolkit. CLI-first, integrates with Helm and Kustomize

```bash
flux bootstrap github --owner=<USER> --repository=<REPO> --path=clusters/prod --personal
flux get all
flux reconcile source git flux-system
```

## Kustomize (built into kubectl)
COMMAND | DESCRIPTION
---|---
`kubectl kustomize <DIR>` | Render a kustomization
`kubectl apply -k <DIR>` | Apply a kustomization
`kubectl diff -k <DIR>` | Preview changes

`kustomization.yaml`
```yaml
resources:
  - deployment.yaml
  - service.yaml
namespace: prod
images:
  - name: nginx
    newTag: "1.27"
patches:
  - path: replicas-patch.yaml
```

## Helm
See [[helm]]. Use `helm upgrade --install --atomic` in pipelines.

## Validating Manifests Before Applying
COMMAND | DESCRIPTION
---|---
`kubectl apply --dry-run=client -f <FILE>` | Local validation
`kubectl apply --dry-run=server -f <FILE>` | Validation by the API server
`kubectl diff -f <FILE>` | Show what would change
`kubeconform -strict -summary <DIR>` | Validate against the Kubernetes schemas
`kube-linter lint <DIR>` | Best-practice lint
`datree test <FILE>` | Policy check, see [[datree]]

## Autoscaling
COMMAND | DESCRIPTION
---|---
`kubectl autoscale deployment <NAME> --min=2 --max=10 --cpu-percent=70` | Create a Horizontal Pod Autoscaler
`kubectl get hpa` | List autoscalers
`kubectl top pods` / `kubectl top nodes` | Live usage (needs metrics-server)

## Scheduled and Batch Work
COMMAND | DESCRIPTION
---|---
`kubectl create cronjob <NAME> --image=<IMAGE> --schedule="0 3 * * *" -- <CMD>` | Create a CronJob
`kubectl create job <NAME> --from=cronjob/<CRON>` | Run a CronJob now
`kubectl get jobs,cronjobs` | List them

## Rollouts
COMMAND | DESCRIPTION
---|---
`kubectl rollout status deployment/<NAME>` | Wait for a rollout (good CI gate)
`kubectl rollout restart deployment/<NAME>` | Rolling restart
`kubectl rollout history deployment/<NAME>` | Revision history
`kubectl rollout undo deployment/<NAME> --to-revision=<N>` | Roll back

## Dependency Updates
Renovate can open PRs to bump image tags, Helm charts and Argo CD/Flux manifests automatically. Enable the `kubernetes`, `helm-values`, `argocd` and `flux` managers in `renovate.json`.

# Argo CD
**Argo CD** is a declarative, GitOps continuous delivery tool for **[Kubernetes](../kubernetes/kubernetes.md)**. Application definitions, configuration and environments are declarative and version controlled, and deployment and lifecycle management are automated, auditable and easy to understand.

Documentation & Project Homepage: [Argo CD Docs](https://argo-cd.readthedocs.io/en/stable/)

---
## Installation

1. Install Argo CD on a **[Kubernetes](../kubernetes/kubernetes.md)** cluster, using **[kubectl](../kubernetes/kubectl.md)**.

```bash
kubectl create namespace argocd
kubectl apply -n argocd --server-side --force-conflicts -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```
`--server-side` avoids the "annotation too long" error that large CRDs cause with a client-side apply. Pin a release (replace `stable` with a tag such as `v2.14.0`) for repeatable installs. A Helm chart is also available (see [Helm Cheat-Sheet](../tools/helm.md)).

2. Install the CLI (macOS: `brew install argocd`, Linux: download from the [releases page](https://github.com/argoproj/argo-cd/releases)).

3. Expose the UI. For a quick look use a port-forward:

```bash
kubectl -n argocd port-forward svc/argocd-server 8080:443
```

4. Or add a **Traefik IngressRoute ([Traefik](traefik.md))**.

```yaml
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: argocd-server
  namespace: argocd
spec:
  entryPoints:
    - websecure
  routes:
    - kind: Rule
      match: Host(`argocd.example.com`)
      priority: 10
      services:
        - name: argocd-server
          port: 80
    - kind: Rule
      match: Host(`argocd.example.com`) && Header(`Content-Type`, `application/grpc`)
      priority: 11
      services:
        - name: argocd-server
          port: 80
          scheme: h2c
  tls:
    certResolver: default
```
`traefik.io/v1alpha1` is the current API group; older Traefik v2 clusters use `traefik.containo.us/v1alpha1`.

5. Disable internal TLS when TLS ends at the proxy: set `server.insecure: "true"` in the `argocd-cmd-params-cm` ConfigMap and restart `argocd-server`.

```bash
kubectl -n argocd patch configmap argocd-cmd-params-cm --type merge -p '{"data":{"server.insecure":"true"}}'
kubectl -n argocd rollout restart deployment argocd-server
```

---
## Get the admin password
The initial password is in a secret named `argocd-initial-admin-secret` (Argo CD v1.9 and later).

```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo
argocd admin initial-password -n argocd
```
Change it after the first login, then delete the secret:
```bash
argocd login argocd.example.com --grpc-web
argocd account update-password
kubectl -n argocd delete secret argocd-initial-admin-secret
```

---
## CLI Commands
COMMAND | DESCRIPTION
---|---
`argocd login <HOST> --grpc-web` | Log in (use `--insecure` for self-signed certificates)
`argocd app list` | List applications
`argocd app get <APP>` | Show status, sync state and resources
`argocd app sync <APP>` | Sync to the Git state
`argocd app diff <APP>` | Show drift between live and Git
`argocd app history <APP>` | Show deployment history
`argocd app rollback <APP> <ID>` | Roll back (auto-sync must be off)
`argocd app set <APP> --sync-policy automated --auto-prune --self-heal` | Enable automated sync
`argocd app delete <APP>` | Delete an app (add `--cascade=false` to keep the resources)
`argocd repo add <URL> --username <USER> --password <TOKEN>` | Add a private repository
`argocd repo list` | List repositories
`argocd cluster add <KUBE-CONTEXT>` | Register an external cluster
`argocd cluster list` | List clusters
`argocd proj list` | List projects

---
## Configuration

### Add private GitHub Repositories

1. Create a GitHub token: https://github.com/settings/tokens

2. Add the repository in Argo CD via **[kubectl](../kubernetes/kubectl.md)**, the CLI or the GUI

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: repo-private-1
  namespace: argocd
  labels:
    argocd.argoproj.io/secret-type: repository
stringData:
  type: git
  url: https://github.com/your-user/private-repo
  username: not-used
  password: <github-token>
```

3. Verify the repository is connected (Settings > Repositories shows *Successful*, or `argocd repo list`).

For SSH access use `sshPrivateKey` in place of `username`/`password`.

---

### Declarative Application and ApplicationSet

Apart from using the web UI to add managed apps to Argo CD, you can configure `Application` and `ApplicationSet` resources. This enables you to define not only Argo CD and your apps as code, but also which applications you want to manage. With apps defined as YAML via an `Application`, you can e.g. deploy the app within a CI/CD pipeline that deploys your Argo instance.

There are two resource types. `Application` is a single deployment. An `ApplicationSet` uses generators (clusters, Git directories, lists and more) to template many `Application` resources. If you manage multiple clusters and want an `Application` deployed with cluster specific parameters, use an `ApplicationSet`.

**Application:**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: guestbook
  namespace: argocd
spec:
  destination:
    namespace: default
    server: 'https://kubernetes.default.svc'
  source:
    path: kustomize-guestbook
    repoURL: 'https://github.com/argoproj/argocd-example-apps'
    targetRevision: HEAD
  project: default
  syncPolicy:
    automated:
      prune: false
      selfHeal: false
    syncOptions:
      - CreateNamespace=true
```

**ApplicationSet:**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: guestbook
  namespace: argocd
spec:
  generators:
  - clusters: {} # a cluster generator: one Application per registered cluster
  template:
    # A template Argo CD Application with parameter substitution.
    metadata:
      name: '{{name}}-guestbook'
    spec:
      project: "default"
      source:
        repoURL: https://github.com/argoproj/argocd-example-apps/
        targetRevision: HEAD
        path: kustomize-guestbook
      destination:
        server: '{{server}}'
        namespace: default
```

### Sync Policy Options
OPTION | DESCRIPTION
---|---
`automated` | Sync automatically when Git changes
`prune: true` | Delete resources that were removed from Git
`selfHeal: true` | Revert manual changes made in the cluster
`CreateNamespace=true` | Create the destination namespace if missing
`ServerSideApply=true` | Use server-side apply (helps with large CRDs)

---
## Troubleshooting
- **OutOfSync but nothing changed**: a controller or mutating webhook edits the resource. Add `ignoreDifferences` to the Application.
- **`ComparisonError` or repo errors**: check `argocd repo list` and the `argocd-repo-server` logs (`kubectl -n argocd logs deploy/argocd-repo-server`).
- **Redirect loop behind a proxy**: enable `server.insecure` (see step 5).

## Further information

- Basic tutorial for installation and configuration: [Let loose the squid - Deploy ArgoCD the declarative way](https://thedatabaseme.de/2022/06/05/let-loose-the-squid-deploy-argocd-the-declarative-way/)
- Writing ArgoCD Plugins: [ArgoCD Custom Plugins](https://dev.to/tylerauerbeck/argocd-custom-plugins-creating-a-custom-plugin-to-process-openshift-templates-4p5m)
- See also [Kubernetes Automation](../kubernetes/kubernetes-automation.md) for GitOps in general.

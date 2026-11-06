# Datree
> [!warning] Discontinued
> Datree is no longer maintained: the company wound down its service in 2023 and the open source repositories are archived (not re-verified here). The commands below only work against old releases and the hosted dashboard no longer exists. Prefer the maintained alternatives in the next section for new work.

## Alternatives
TOOL | USE
---|---
`kubeconform` | Fast schema validation of manifests (replaces kubeval)
`kube-linter` | Best-practice checks for manifests and Helm charts
`kubescape` | Security and compliance scanning (NSA, CIS frameworks)
`conftest` | Write your own policies in Rego (OPA)
`trivy config .` | Misconfiguration scan for Kubernetes, Terraform and Dockerfiles
`kubectl apply --dry-run=server -f file.yaml` | Let the API server validate ([Kubectl](../kubernetes/kubectl.md))
Kyverno / OPA Gatekeeper | Admission-time policy in the cluster

```bash
kubeconform -strict -summary manifests/
kube-linter lint manifests/
helm template ./chart | kubeconform -strict -summary
```
See [Helm Cheat-Sheet](helm.md) and [Kubernetes](../kubernetes/kubernetes.md).

---
## Datree (Legacy)
Datree can be used on the command line to run policies against Kubernetes manifests YAML files or Helm charts. It prevents Kubernetes misconfigurations from reaching production.

## Installation

**Windows** (PowerShell)
```powershell
iwr -useb https://get.datree.io/windows_install.ps1 | iex

setx PATH "$env:path;C:\Users\$env:UserName\AppData\Local\datree" -m
```

**Linux** (Bash)
```bash
sudo apt -y install unzip

curl https://get.datree.io | /bin/bash
```

**Usage**
```bash
datree test ~/.datree/k8s-demo.yaml
```

## Policies
"Centralized policy" is the concept of controlling distributed policy execution from a centralized location. This concept enables the policy owner to easily control the rules that are evaluated in each run of Datree without creating operation overhead. The centralized policy can be managed by logging into the dashboard.

To run the Datree CLI against the new policy (instead of the default one), you will need to add the `-p POLICYNAME` to your policy check execution:

```
datree test ~/.datree/k8s-demo.yaml -p POLICYNAME
```


### Helm
A Helm plugin to validate charts against the Datree policy.
> [!attention]
> Only works on Linux


**Installation Linux** (Bash)
```bash
helm plugin install https://github.com/datreeio/helm-datree
```

### Usage
Trigger datree policy check via the helm CLI
```bash
helm datree test [CHART_DIRECTORY]
```


**Usage**

If you need to pass helm arguments to your template, you will need to add -- before them:

```bash
helm datree test [CHART_DIRECTORY] -- --values values.yaml --set name=prod
```

## Webhooks

### Installation

Install with providing Datree token. The Datree token is optional, and can be entered during the installation procedure as well.

```bash
DATREE_TOKEN=[your-token] bash <(curl https://get.datree.io/admission-webhook)
```

### Ignore a namespace

Add the label "admission.datree/validate=skip" to the configuration of the namespace you would like to ignore:

```bash
kubectl label namespaces default "admission.datree/validate=skip"
```

To delete the label and resume running the datree webhook on the namespace again:

```bash
kubectl label namespaces default "admission.datree/validate-"
```

### Uninstallation

To uninstall the webhook, copy the following command and run it in your terminal:

```bash
bash <(curl https://get.datree.io/admission-webhook-uninstall)
```

To uninstall the helm release, copy the following command and run it in your terminal:

```bash
helm uninstall datree-webhook -n datree
kubectl delete ns datree
```
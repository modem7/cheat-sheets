# Tekton
Tekton is a Kubernetes-native CI/CD framework: tasks and pipelines are custom resources and every step runs in a container in a pod. Use it when you want pipelines that run inside an existing [Kubernetes](../kubernetes/kubernetes.md) cluster. The `tkn` commands below were checked against `tkn` v0.46.2; the YAML and install URL come from the Tekton docs and were not run against a cluster (unverified).

Documentation: [Tekton docs](https://tekton.dev/docs/)
Project: [tektoncd/pipeline](https://github.com/tektoncd/pipeline), [tektoncd/cli](https://github.com/tektoncd/cli)

---
## Concepts
OBJECT | PURPOSE
---|---
`Task` | A list of steps (containers) that run in order in one pod
`Pipeline` | Tasks wired together with `runAfter`, parameters and workspaces
`TaskRun`, `PipelineRun` | One execution of a Task or Pipeline
`Workspace` | Shared storage (PVC, emptyDir, ConfigMap, Secret) mounted into tasks
`Result` | Small values a task passes on to later tasks
`finally` | Tasks that run at the end whatever the outcome
Triggers | `EventListener`, `TriggerBinding`, `TriggerTemplate` start runs from webhooks

## Install
Install the controller, then the CLI (a binary from the releases page, or the `.deb`/`.rpm` packages).

```bash
kubectl apply -f https://infra.tekton.dev/tekton-releases/pipeline/latest/release.yaml   # URL unverified: check the install page
kubectl get pods -n tekton-pipelines --watch
```

## Run and Inspect (tkn)
All commands accept `-n <NAMESPACE>`, `-c <CONTEXT>`, `-k <KUBECONFIG>` and `-C` (no colour).

COMMAND | DESCRIPTION
---|---
`tkn task list` / `tkn pipeline list` | List Tasks or Pipelines
`tkn task describe <NAME>` / `tkn pipeline describe <NAME>` | Show parameters, workspaces and recent runs
`tkn task start <NAME> -p KEY=VALUE -w name=<WS>,emptyDir= --showlog` | Create a TaskRun and stream its logs
`tkn task start --use-param-defaults <NAME>` | Skip the prompts, use default parameter values
`tkn task start -f task.yaml` | Start from a local or remote Task definition
`tkn pipeline start <NAME> -p KEY=VALUE -s <SERVICE_ACCOUNT> --showlog` | Create a PipelineRun and follow it
`tkn pipeline start <NAME> --last` | Re-run with the values of the last PipelineRun
`tkn pipeline start <NAME> --dry-run -o yaml` | Preview the PipelineRun without creating it
`tkn pipeline start <NAME> -w name=<WS>,claimName=<PVC>` | Bind a PVC workspace (also `emptyDir=`, `secret=`, `config=`, `volumeClaimTemplateFile=`)
`tkn pipelinerun list` / `tkn taskrun list` | Recent runs (aliases `tkn pr`, `tkn tr`)
`tkn pipelinerun describe <NAME>` | Status of each task in a run
`tkn pipelinerun logs <NAME> -f` | Stream logs (`-t <TASK>` one task, `-a` include init steps, `--log-failed`, `-L` last run)
`tkn pipelinerun cancel <NAME>` / `tkn taskrun cancel <NAME>` | Cancel a running run
`tkn pipelinerun delete <NAME>` / `tkn pipelinerun delete --all` | Delete runs (`--all` removes every run in the namespace; `--keep <N>` keeps the newest N, `-p <PIPELINE>` limits to one Pipeline)
`tkn pipelinerun export <NAME>` | Export a run as YAML
`tkn hub search <TERM>` | Search the Tekton catalogue (hub subcommands: `get`, `info`, `install`, `upgrade`, `reinstall`, `downgrade`, `check-upgrade`)
`tkn version` | Client version

`-E` (`--exit-with-pipelinerun-error`) on `tkn pipeline start --showlog` and `tkn pipelinerun logs` returns the run's result as the exit code, which makes it usable from another CI job.

## Task and Pipeline YAML
```yaml
apiVersion: tekton.dev/v1
kind: Task
metadata:
  name: build
spec:
  params:
    - name: image
      type: string
      default: alpine:3.22
  workspaces:
    - name: source
  results:
    - name: digest
  steps:
    - name: compile
      image: $(params.image)
      workingDir: $(workspaces.source.path)
      script: |
        #!/bin/sh
        set -eu
        echo "building"
        echo -n "abc123" > $(results.digest.path)
---
apiVersion: tekton.dev/v1
kind: Pipeline
metadata:
  name: ci
spec:
  workspaces:
    - name: shared
  tasks:
    - name: build
      taskRef:
        name: build
      workspaces:
        - name: source
          workspace: shared
    - name: report
      runAfter: [build]
      taskSpec:
        steps:
          - name: show
            image: alpine:3.22
            script: echo done
  finally:
    - name: notify
      taskSpec:
        steps:
          - name: send
            image: alpine:3.22
            script: echo "pipeline finished"
```

A PipelineRun binds the pipeline's workspaces to real storage:

```yaml
apiVersion: tekton.dev/v1
kind: PipelineRun
metadata:
  generateName: ci-run-
spec:
  pipelineRef:
    name: ci
  workspaces:
    - name: shared
      volumeClaimTemplate:
        spec:
          accessModes: [ReadWriteOnce]
          resources:
            requests:
              storage: 1Gi
```

Create it with `kubectl create -f run.yaml` (`generateName` needs `create`, not `apply`).

## Variable Substitution
EXPRESSION | MEANING
---|---
`$(params.NAME)` | Parameter value
`$(workspaces.NAME.path)` | Mount path of a workspace
`$(results.NAME.path)` | File a step writes a result to
`$(tasks.TASK.results.NAME)` | In a pipeline, another task's result
`$(context.pipelineRun.name)` | Name of the current PipelineRun

## Troubleshooting
SYMPTOM | FIX
---|---
Run stuck in Pending | The PVC cannot bind (storage class, access mode) or the pod cannot be scheduled: `kubectl describe pod`
`tkn` shows no runs | Wrong namespace: add `-n <NAMESPACE>`
Task cannot pull images or push | Attach credentials to the service account the run uses (`-s`)
Result not visible to the next task | The step must write to `$(results.NAME.path)`; results are meant for small values only
Workspace empty in the next task | Both tasks must bind the same pipeline workspace, and `runAfter` must order them

## See Also
- [Flux CD](flux.md)
- [Argo CD](../apps/argocd.md)
- [kubectl](../kubernetes/kubectl.md)
- [CI/CD Overview](cicd.md)

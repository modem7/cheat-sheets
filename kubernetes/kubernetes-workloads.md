# Kubernetes Workloads
Deployments, StatefulSets, DaemonSets, Jobs and CronJobs, plus the probe and resource settings every workload needs. Use it for rollout, rollback and scheduling behaviour; see [Kubernetes](kubernetes.md) for the concepts and [Kubectl](kubectl.md) for general commands.

Documentation: [Kubernetes Workloads](https://kubernetes.io/docs/concepts/workloads/), [Configure Liveness, Readiness and Startup Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/), [Resource Management for Pods and Containers](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)

> **Verification:** `kubectl` subcommands and flags were checked against `kubectl --help` from v1.37.2 (no cluster available, so nothing was applied). Manifest field names and enum values were checked against the OpenAPI schema of Kubernetes v1.37.2 (`api/openapi-spec/swagger.json`); `kubectl explain` needs a live API server and was not run. Rollout, probe and scheduling behaviour follows the official docs and was not observed on a cluster. Some features are version-dependent (noted below).

## Choosing a Workload
KIND | USE FOR | NOTES
---|---|---
Deployment | Stateless apps | Rolling updates, rollback, scaling
StatefulSet | Databases, clustered apps | Stable names (`NAME-0`, `NAME-1`), one PVC per Pod, ordered start and update
DaemonSet | Node agents (logs, monitoring, CNI) | One Pod per matching node
Job | Run-to-completion task | Retries until the completion count is met
CronJob | Scheduled task | Creates a Job on a cron schedule

## Deployments
COMMAND | DESCRIPTION
---|---
`kubectl create deployment <NAME> --image=<IMAGE> --replicas=2 --dry-run=client -o yaml` | Generate a starter manifest without creating anything
`kubectl apply -f <FILE>` | Create or update
`kubectl set image deployment/<NAME> <CONTAINER>=<IMAGE>:<TAG>` | Change an image, which triggers a rollout
`kubectl scale deployment/<NAME> --replicas=5` | Change the replica count
`kubectl scale deployment/<NAME> --current-replicas=2 --replicas=5` | Scale only if the current count matches
`kubectl autoscale deployment <NAME> --min=2 --max=10 --cpu=80%` | Create a HorizontalPodAutoscaler (needs metrics-server)
`kubectl rollout status deployment/<NAME> --timeout=120s` | Wait for a rollout, non-zero exit on failure (good for CI)
`kubectl rollout history deployment/<NAME>` | List revisions
`kubectl rollout history deployment/<NAME> --revision=2` | Show one revision's Pod template
`kubectl rollout undo deployment/<NAME>` | Roll back to the previous revision
`kubectl rollout undo deployment/<NAME> --to-revision=2` | Roll back to a given revision
`kubectl rollout restart deployment/<NAME>` | Rolling restart with the same template
`kubectl rollout pause deployment/<NAME>` / `kubectl rollout resume deployment/<NAME>` | Batch several changes into one rollout
`kubectl annotate deployment/<NAME> kubernetes.io/change-cause="<REASON>"` | Record why, shown in the `CHANGE-CAUSE` column of `rollout history`

### Strategy
FIELD | DESCRIPTION
---|---
`spec.strategy.type: RollingUpdate` | Default. Replace Pods gradually
`spec.strategy.type: Recreate` | Stop all old Pods, then start new ones (downtime; use when two versions must never overlap)
`rollingUpdate.maxSurge` | Extra Pods allowed above `replicas` during an update (number or %, default 25%)
`rollingUpdate.maxUnavailable` | Pods allowed to be unavailable during an update (number or %, default 25%)
`spec.minReadySeconds` | How long a new Pod must be ready before it counts as available
`spec.progressDeadlineSeconds` | Time before the rollout is reported as failed (default 600). Kubernetes does not roll back automatically
`spec.revisionHistoryLimit` | Old ReplicaSets kept for rollback (default 10)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3
  revisionHistoryLimit: 5
  minReadySeconds: 5
  progressDeadlineSeconds: 300
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: web
          image: nginx:1.27
          ports:
            - containerPort: 80
```
`maxUnavailable: 0` with `maxSurge: 1` keeps full capacity during updates but needs room for one extra Pod. `spec.selector` is immutable after creation.

## StatefulSets
Needs a headless Service (`clusterIP: None`) whose name matches `spec.serviceName`. Pods get stable DNS names `<POD>.<SERVICE>.<NAMESPACE>.svc`.

COMMAND | DESCRIPTION
---|---
`kubectl get statefulset,pods,pvc -l app=<LABEL>` | Show the set, its Pods and its claims
`kubectl scale statefulset/<NAME> --replicas=3` | Scale (ordered by default)
`kubectl rollout status statefulset/<NAME>` | Watch an update
`kubectl rollout undo statefulset/<NAME>` | Roll back the Pod template
`kubectl delete statefulset/<NAME> --cascade=orphan` | Delete the set but leave the Pods running
`kubectl delete pvc <PVC>` | Claims are kept by default when the set is deleted or scaled down. This deletes the data

FIELD | DESCRIPTION
---|---
`spec.serviceName` | Headless Service that governs the Pods
`spec.podManagementPolicy` | `OrderedReady` (default, one at a time) or `Parallel`
`spec.updateStrategy.type` | `RollingUpdate` (default, highest ordinal first) or `OnDelete` (update only when you delete a Pod)
`spec.updateStrategy.rollingUpdate.partition` | Only Pods with ordinal >= partition are updated. Use for canaries
`spec.volumeClaimTemplates` | One PVC per Pod, named `<TEMPLATE>-<POD>`
`spec.persistentVolumeClaimRetentionPolicy` | `whenDeleted` / `whenScaled`: `Retain` (default) or `Delete`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: db
spec:
  clusterIP: None
  selector:
    app: db
  ports:
    - port: 5432
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: db
spec:
  serviceName: db
  replicas: 3
  selector:
    matchLabels:
      app: db
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      partition: 0
  template:
    metadata:
      labels:
        app: db
    spec:
      containers:
        - name: db
          image: postgres:17
          ports:
            - containerPort: 5432
          volumeMounts:
            - name: data
              mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 1Gi
```
Image and credentials above are illustrative: a real Postgres Pod also needs `POSTGRES_PASSWORD` from a Secret.

## DaemonSets
COMMAND | DESCRIPTION
---|---
`kubectl get daemonset -n <NAMESPACE>` | `DESIRED`, `CURRENT` and `READY` per node count
`kubectl rollout status daemonset/<NAME>` | Watch an update
`kubectl rollout undo daemonset/<NAME>` | Roll back
`kubectl get pods -o wide -l <LABEL>` | See which node each Pod landed on

FIELD | DESCRIPTION
---|---
`spec.updateStrategy.type` | `RollingUpdate` (default) or `OnDelete`
`spec.updateStrategy.rollingUpdate.maxUnavailable` | Nodes updated at once (default 1)
`spec.updateStrategy.rollingUpdate.maxSurge` | Nodes that may run an extra updated Pod before the old one is removed (default 0; cannot be 0 if `maxUnavailable` is 0)
`spec.template.spec.nodeSelector` | Restrict to labelled nodes
`spec.template.spec.tolerations` | Run on tainted nodes, e.g. control plane

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-agent
spec:
  selector:
    matchLabels:
      app: node-agent
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
  template:
    metadata:
      labels:
        app: node-agent
    spec:
      tolerations:
        - key: node-role.kubernetes.io/control-plane
          operator: Exists
          effect: NoSchedule
      containers:
        - name: agent
          image: busybox:1.37
          command: ["sh", "-c", "while true; do sleep 3600; done"]
```

## Jobs
COMMAND | DESCRIPTION
---|---
`kubectl create job <NAME> --image=busybox -- date` | Create a one-off Job
`kubectl create job <NAME> --from=cronjob/<CRONJOB>` | Run a CronJob now
`kubectl get jobs` | `COMPLETIONS` shows succeeded/required
`kubectl wait --for=condition=complete job/<NAME> --timeout=300s` | Block until done
`kubectl logs job/<NAME>` | Logs from one of the Job's Pods
`kubectl delete job <NAME>` | Remove the Job and its Pods

FIELD | DESCRIPTION
---|---
`spec.completions` | Successful Pods needed (default 1)
`spec.parallelism` | Pods running at once (default 1)
`spec.backoffLimit` | Retries before the Job is marked failed (default 6)
`spec.activeDeadlineSeconds` | Hard time limit for the whole Job
`spec.ttlSecondsAfterFinished` | Auto-delete the Job after it finishes
`spec.completionMode` | `NonIndexed` (default) or `Indexed` (each Pod gets an index)
`spec.suspend` | Pause creation of Pods
`spec.template.spec.restartPolicy` | Must be `Never` or `OnFailure`, not `Always`

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: migrate
spec:
  backoffLimit: 3
  activeDeadlineSeconds: 600
  ttlSecondsAfterFinished: 3600
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: migrate
          image: busybox:1.37
          command: ["sh", "-c", "echo migrating"]
```

## CronJobs
COMMAND | DESCRIPTION
---|---
`kubectl create cronjob <NAME> --image=busybox --schedule="*/5 * * * *" -- date` | Create a CronJob
`kubectl get cronjob` | Shows schedule, `SUSPEND`, `ACTIVE` and `LAST SCHEDULE`
`kubectl patch cronjob <NAME> -p '{"spec":{"suspend":true}}'` | Pause scheduling (`false` to resume)
`kubectl create job <NAME> --from=cronjob/<CRONJOB>` | Trigger a manual run

FIELD | DESCRIPTION
---|---
`spec.schedule` | Standard five-field cron expression
`spec.timeZone` | IANA zone such as `Europe/London`. Without it the schedule uses the time zone of the controller manager
`spec.concurrencyPolicy` | `Allow` (default), `Forbid` (skip if still running) or `Replace`
`spec.startingDeadlineSeconds` | How late a run may start before it counts as missed
`spec.successfulJobsHistoryLimit` | Finished Jobs kept (default 3)
`spec.failedJobsHistoryLimit` | Failed Jobs kept (default 1)
`spec.suspend` | Stop creating Jobs
`spec.jobTemplate` | A Job spec, as above

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: nightly-backup
spec:
  schedule: "0 2 * * *"
  timeZone: Europe/London
  concurrencyPolicy: Forbid
  startingDeadlineSeconds: 300
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  jobTemplate:
    spec:
      backoffLimit: 2
      ttlSecondsAfterFinished: 86400
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: backup
              image: busybox:1.37
              command: ["sh", "-c", "echo backup"]
```

## Probes
PROBE | PURPOSE | ON FAILURE
---|---|---
`startupProbe` | App has finished starting. Other probes are disabled until it succeeds | Container restarted
`livenessProbe` | App is still working | Container restarted
`readinessProbe` | App can take traffic | Pod removed from Service endpoints (no restart)

HANDLER | DESCRIPTION
---|---
`httpGet` | Success on HTTP status 200 to 399
`tcpSocket` | Success if the port accepts a connection
`exec` | Success if the command exits 0
`grpc` | Success if the gRPC health check returns `SERVING`

TIMING FIELD | DEFAULT | DESCRIPTION
---|---|---
`initialDelaySeconds` | 0 | Wait before the first probe
`periodSeconds` | 10 | Interval between probes
`timeoutSeconds` | 1 | Time allowed per probe
`successThreshold` | 1 | Passes needed to recover (must be 1 for liveness and startup)
`failureThreshold` | 3 | Failures before the probe is considered failed
`terminationGracePeriodSeconds` | Pod value | Overrides the Pod's grace period when this probe fails (feature-gated in some versions)

```yaml
containers:
  - name: web
    image: nginx:1.27
    ports:
      - containerPort: 80
    startupProbe:
      httpGet: { path: /, port: 80 }
      periodSeconds: 5
      failureThreshold: 30    # up to 150s to start
    livenessProbe:
      httpGet: { path: /, port: 80 }
      periodSeconds: 10
    readinessProbe:
      httpGet: { path: /, port: 80 }
      periodSeconds: 5
```
Keep liveness probes cheap and independent of dependencies such as the database, otherwise an outage restarts every Pod. Probe failures appear as events in `kubectl describe pod <POD>`.

## Resource Requests and Limits
FIELD | DESCRIPTION
---|---
`resources.requests` | Used by the scheduler to place the Pod, and the guaranteed share
`resources.limits` | Hard ceiling. CPU over the limit is throttled; memory over the limit gets the container `OOMKilled`
`cpu: 500m` | 500 millicores (half a core)
`memory: 256Mi` | Binary units (`Mi`, `Gi`). `M` and `G` are decimal

QOS CLASS | WHEN
---|---
`Guaranteed` | Every container has requests equal to limits for both CPU and memory
`Burstable` | At least one request or limit is set, but not Guaranteed
`BestEffort` | No requests or limits. First to be evicted under node pressure

COMMAND | DESCRIPTION
---|---
`kubectl set resources deployment/<NAME> -c=<CONTAINER> --requests=cpu=100m,memory=128Mi --limits=memory=256Mi` | Change resources on a live Deployment (triggers a rollout)
`kubectl top pod --containers` | Live usage per container (needs metrics-server)
`kubectl top pod --sort-by=memory` | Heaviest Pods first
`kubectl top node` | Node usage
`kubectl describe node <NODE>` | Allocatable capacity and what is already requested
`kubectl get pod <POD> -o jsonpath='{.status.qosClass}'` | Show the QoS class
`kubectl get pod <POD> -o jsonpath='{.status.containerStatuses[*].lastState.terminated.reason}'` | `OOMKilled` after a memory kill

```yaml
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    memory: 256Mi    # no CPU limit: avoids throttling, still requests CPU
```
Omitting a CPU limit is a common choice, not a rule: set one if you need a hard cap. Set a namespace default with a `LimitRange` and a cap with a `ResourceQuota`.

## Troubleshooting
SYMPTOM | CHECK
---|---
Rollout stuck, new Pods `0/1` | `kubectl describe pod <POD>`: failing readiness probe, image pull or no resources. `kubectl rollout undo` to revert
`ProgressDeadlineExceeded` | `progressDeadlineSeconds` passed. The old Pods keep serving. Fix and re-apply, or undo
Pod restarts repeatedly | Liveness probe too strict or `initialDelaySeconds` too short: add a `startupProbe`
Pod `Pending` | Requests exceed free node capacity (`kubectl describe node`), or taints and selectors do not match
StatefulSet Pod stuck | Ordered start waits for the previous Pod to be ready. Check its PVC is `Bound`
CronJob never runs | `SUSPEND` is true, bad cron expression or too many missed runs (check `kubectl describe cronjob`)
Job Pods keep failing | `kubectl logs job/<NAME>`; remember `backoffLimit` retries before the Job fails
Old Jobs pile up | Set `ttlSecondsAfterFinished` or the CronJob history limits

## See Also
- [Kubernetes](kubernetes.md)
- [Kubectl](kubectl.md)
- [Kubernetes DNS](kubernetes-dns.md)
- [Helm Cheat-Sheet](../tools/helm.md)
- [K9s](k9s.md)

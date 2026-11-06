# Woodpecker CI
Woodpecker is a lightweight, self-hosted, container-native CI system (a community fork of Drone). Every step runs in a container, workflows live in `.woodpecker/*.yaml` (or a single `.woodpecker.yaml`) in the repo, and it connects to Gitea/Forgejo, GitHub, GitLab or Bitbucket. This sheet targets Woodpecker **v3** (latest release seen: v3.20.1); v2 differences are in the last table. For overall concepts see [[cicd]], for the forge see [[gitea]], and for image builds see [[ci-docker-builds]].

Documentation: [Woodpecker docs](https://woodpecker-ci.org/docs/intro), [Workflow syntax](https://woodpecker-ci.org/docs/usage/workflow-syntax), [CLI](https://woodpecker-ci.org/docs/cli)

---
## Minimal Workflow
```yaml
# .woodpecker/test.yaml
when:
  - event: [push, pull_request]
    branch: main            # for pull_request this matches the target branch

steps:
  - name: test
    image: node:22
    commands:
      - npm ci
      - npm test
```

Several files in `.woodpecker/` are separate **workflows** that run in parallel unless linked with `depends_on`. A pipeline is one run containing all of its workflows.

## Step Keywords
KEYWORD | DESCRIPTION
---|---
`name` | Step name (optional, otherwise numbered); must be unique once `depends_on` is used
`image` | Container image, pin a tag or digest
`commands` | Shell commands, run as one script; the step fails on the first non-zero exit
`environment` | Environment variables (map only in v3)
`settings` | Plugin parameters; they become `PLUGIN_<NAME>` variables
`when` | Conditions deciding if the step runs
`depends_on` | Make a DAG; steps run in parallel except where dependencies exist
`failure` | `fail` (default), `ignore` or `cancel`
`detach` | Run in the background until the workflow ends
`volumes` | Extra volume mounts (trusted repos only)
`privileged` | Privileged container (trusted repos only)
`pull` | Always pull the image
`backend_options` | Backend specific options (Docker user, Kubernetes service account)
`directory` | Working directory for the step

Steps can be a list (shown above, the v3 form) or a map keyed by name; both are accepted.

## Workflow Level Keywords
KEYWORD | DESCRIPTION
---|---
`steps` | The ordered list of steps (required)
`services` | Sidecar containers such as databases; the `name` becomes the hostname
`when` | Skip the whole workflow unless the conditions hold
`depends_on` | Run after other workflows (file name without path, dot and extension)
`matrix` | Run the workflow once per combination (max 64 combinations, 10 values per axis)
`labels` | Pick an agent, e.g. `platform: linux/arm64`
`clone` | Customise the clone step (`git: image: woodpeckerci/plugin-git`)
`skip_clone` | Do not clone, for notification-only workflows
`workspace` | Change the workspace path
`concurrency` | `concurrency: 1` limits parallel runs of this workflow; extra runs queue instead of cancelling
`variables` | Home for YAML anchors that you reuse in the file

## when Conditions
A `when` list is OR-ed; the keys inside one list item are AND-ed.
```yaml
steps:
  - name: deploy
    image: alpine
    commands: [./deploy.sh]
    when:
      - event: push
        branch: main
      - event: tag
        ref: refs/tags/v*
      - event: manual
      - evaluate: 'CI_COMMIT_MESSAGE not contains "[skip deploy]"'
        event: push
  - name: notify-failure
    image: alpine
    commands: [./notify.sh]
    when:
      - status: [failure]
        event: [push, tag]
```

FILTER | DESCRIPTION
---|---
`event` | `push`, `pull_request`, `pull_request_closed`, `pull_request_metadata`, `tag`, `release`, `deployment`, `cron`, `manual`
`branch` | Branch (glob). For pull requests it is the **target** branch
`ref` | Full ref, e.g. `refs/tags/v*`
`repo` | `owner/name`
`cron` | Name of the cron job (also needs `event: cron`)
`path` | `include`/`exclude` globs on changed files (push and pull_request only)
`status` | `success` (default) or `failure`
`platform` | Agent platform, e.g. `linux/arm64`
`matrix` | Only for one matrix permutation
`instance` | Only on this Woodpecker server host
`evaluate` | Expression on `CI_*` variables and custom variables

Always give every `when` item an `event` filter; the built-in linter warns otherwise, because new event types would trigger the step.

## Services, Dependencies and Matrix
```yaml
matrix:
  GO_VERSION: ["1.23", "1.24"]
  DB: [postgres, mariadb]

services:
  - name: database
    image: postgres:17
    environment:
      POSTGRES_PASSWORD: example     # throw-away CI value

steps:
  - name: build
    image: golang:${GO_VERSION}
    commands: [go build ./...]
  - name: test
    image: golang:${GO_VERSION}
    depends_on: [build]
    environment:
      DATABASE_URL: postgres://postgres:example@database:5432/postgres
    commands: [go test ./...]
```
Matrix variables are substituted with `${VAR}` before the YAML is parsed. Use `include:` to list explicit combinations instead of a full product.

Workflow dependencies across files:
```yaml
# .woodpecker/deploy.yaml
depends_on: [lint, test]          # files .woodpecker/lint.yaml and test.yaml
when:
  - event: push
    branch: main
```
In a monorepo with `when.path`, mark dependencies `optional: true` (`depends_on: [{name: lint, optional: true}]`) so a skipped workflow does not block the deploy.

## Secrets
Add secrets under repo Settings > Secrets, or with the CLI. By default a secret is **not** available to `pull_request` events (enable that event explicitly and only for safe secrets). You can also restrict a secret to named plugin images.
```yaml
steps:
  - name: publish
    image: woodpeckerci/plugin-docker-buildx
    settings:
      repo: ghcr.io/<OWNER>/<IMAGE>
      registry: ghcr.io
      username: <USER>
      password:
        from_secret: ghcr_token
      tags: latest
    when:
      - event: push
        branch: main

  - name: call-api
    image: curlimages/curl
    environment:
      API_TOKEN:
        from_secret: api_token
    commands:
      - 'curl -fsS -H "Authorization: Bearer $API_TOKEN" https://api.example.com/ping'
```
Write `$VAR` (not `${VAR}`) for runtime shell variables in `commands`; `${...}` expressions are pre-processed before the pipeline starts. Escape them as `$${VAR}` if you need a literal.

## Built-in Variables
VARIABLE | MEANING
---|---
`CI_REPO` | `owner/name`
`CI_COMMIT_SHA` | Commit SHA
`CI_COMMIT_BRANCH` | Branch (target branch for pull requests)
`CI_COMMIT_TAG` | Tag name, empty unless the event is `tag`
`CI_COMMIT_PULL_REQUEST` | PR number
`CI_PIPELINE_EVENT` | The event that triggered the pipeline
`CI_PIPELINE_NUMBER` | Pipeline number
`CI_REPO_DEFAULT_BRANCH` | Default branch of the repo
`CI_WORKSPACE` | Workspace path
`CI_PIPELINE_DEPLOY_TARGET` | Target of a `deployment` event

## Cron and Manual Runs
- Cron: in the repo settings add a cron job (name + schedule), then give the steps `event: cron` (and optionally `cron: <NAME>`).
- Manual: use the "Run pipeline" button or `woodpecker-cli pipeline create`; steps need `event: manual` to run. Variables passed with `--var` are available as environment variables.
- Deployments: `woodpecker-cli pipeline deploy <REPO> <PIPELINE> <TARGET>` creates a `deployment` event with `CI_PIPELINE_DEPLOY_TARGET`.

## woodpecker-cli
Point the CLI at the server and authenticate with your personal token (User settings > Personal access token):
```bash
export WOODPECKER_SERVER=https://woodpecker.modem7.com
export WOODPECKER_TOKEN=<TOKEN>
```

COMMAND | DESCRIPTION
---|---
`woodpecker-cli repo list` | Repos you can see
`woodpecker-cli repo add <FORGE-REMOTE-ID>` | Activate a repo
`woodpecker-cli repo show <REPO>` | Repo settings
`woodpecker-cli repo sync` | Resync the repo list from the forge
`woodpecker-cli repo repair` | Re-create webhooks
`woodpecker-cli pipeline list <REPO>` | Recent pipelines
`woodpecker-cli pipeline last <REPO>` | Most recent pipeline
`woodpecker-cli pipeline show <REPO> <NUMBER>` | Details of one pipeline
`woodpecker-cli pipeline ps <REPO> <NUMBER>` | Steps of a pipeline
`woodpecker-cli pipeline log show <REPO> <NUMBER> <STEP>` | Step log
`woodpecker-cli pipeline create --branch <BRANCH> <REPO>` | Trigger a manual run (`--var KEY=VALUE`, `--workflow <NAME>`)
`woodpecker-cli pipeline start <REPO> <NUMBER>` | Restart a pipeline
`woodpecker-cli pipeline stop <REPO> <NUMBER>` | Stop a running pipeline
`woodpecker-cli pipeline kill <REPO> <NUMBER>` | Force kill
`woodpecker-cli pipeline approve <REPO> <NUMBER>` | Approve a pipeline held for approval
`woodpecker-cli pipeline decline <REPO> <NUMBER>` | Decline it
`woodpecker-cli pipeline queue` | Pending and running pipelines
`woodpecker-cli repo secret add --repository <REPO> --name <NAME> --value <VALUE>` | Add a secret (`--event push --event tag` limits events)
`woodpecker-cli repo secret list <REPO>` | List secrets (values hidden)
`woodpecker-cli lint .woodpecker/` | Lint workflow files offline
`woodpecker-cli exec .woodpecker/test.yaml` | Run a workflow locally (needs Docker)
`woodpecker-cli exec --backend-engine docker --pipeline-event push --commit-branch main <FILE>` | Local run with metadata overrides
`woodpecker-cli setup` | Interactive login/config

Flag names for the secret commands moved between releases; run `woodpecker-cli repo secret add --help` to confirm on your version.

## Server and Agent (Docker Compose)
The server serves the UI/API and talks to the forge; one or more agents execute the workflows. See [[docker-compose]].
```yaml
services:
  woodpecker-server:
    image: woodpeckerci/woodpecker-server:v3
    restart: unless-stopped
    ports: ["8000:8000"]
    volumes:
      - woodpecker-data:/var/lib/woodpecker
    environment:
      WOODPECKER_HOST: https://woodpecker.example.com
      WOODPECKER_AGENT_SECRET: ${WOODPECKER_AGENT_SECRET}
      WOODPECKER_GITEA: "true"                      # or WOODPECKER_GITHUB / WOODPECKER_FORGEJO
      WOODPECKER_GITEA_URL: https://git.example.com
      WOODPECKER_GITEA_CLIENT: ${GITEA_OAUTH_CLIENT}
      WOODPECKER_GITEA_SECRET: ${GITEA_OAUTH_SECRET}
      WOODPECKER_ADMIN: <USER>

  woodpecker-agent:
    image: woodpeckerci/woodpecker-agent:v3
    restart: unless-stopped
    depends_on: [woodpecker-server]
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      WOODPECKER_SERVER: woodpecker-server:9000
      WOODPECKER_AGENT_SECRET: ${WOODPECKER_AGENT_SECRET}
      WOODPECKER_MAX_WORKFLOWS: 2

volumes:
  woodpecker-data:
```
Generate the shared secret with `openssl rand -hex 32` ([[openssl]]) and keep it in an `.env` file out of Git. The server needs a working webhook path from the forge and an OAuth app on the forge.

## Docker Backend Notes
- Each step is a container on a per-workflow Docker network; services are reachable by their `name`.
- The agent needs the Docker socket, which is root-equivalent on the host. Treat anyone who can edit a pipeline as able to run code on the agent host.
- `privileged`, `volumes` and custom networks only work for repositories an admin marks **Trusted** (repo Settings). Docker-in-Docker (`docker:dind` service) needs `privileged: true`.
- Extra agent settings: `WOODPECKER_BACKEND_DOCKER_NETWORK`, `WOODPECKER_BACKEND_DOCKER_VOLUMES`, `WOODPECKER_MAX_WORKFLOWS`, `WOODPECKER_AGENT_LABELS`.
- Agent images accumulate; prune on a schedule (`docker image prune -af --filter until=168h`).
- For image builds use `woodpeckerci/plugin-docker-buildx` (see [[ci-docker-builds]]) or a dind service.

## v2 to v3 Differences
TOPIC | v2 | v3
---|---|---
Secrets in steps | `secrets: [name]` list | Removed; use `environment: NAME: from_secret: name` or `settings: key: from_secret: name`
Environment | Map or list | Map only; list form is rejected
Parallel steps | `group:` | Removed; use `depends_on:`
Agent platform filter | `platform:` | Removed; use `labels: platform: linux/arm64`
Event filters | `includes` / `excludes`, `environment` filter | Removed; use `when.evaluate`
Failure steps | `runs_on: [failure]` | `runs_on` is deprecated; use `when: status: [failure]`
Cron schedule | Cron with seconds | Standard five-field cron, no seconds
Image tags | `latest` | `latest` dropped; pin `v3` or a full version
PR approval | "gated" option | Replaced by "require approval" setting
CLI binary in DEB/RPM | `woodpecker` | `woodpecker-cli`

Source: [migration notes](https://woodpecker-ci.org/migrations). Run `woodpecker-cli lint` after migrating.

## Troubleshooting
SYMPTOM | CAUSE AND FIX
---|---
Pipeline never starts | Webhook missing or failing: `woodpecker-cli repo repair`, check forge webhook delivery log and `WOODPECKER_HOST`
No workflow file found | File must be `.woodpecker/*.yaml` or `.woodpecker.yaml` on the commit being built
Step skipped unexpectedly | `when` item without matching `event`; for pull requests `branch` matches the target branch; check `woodpecker-cli lint`
Secret is empty | Secret not enabled for that `event` (pull requests are off by default) or restricted to other plugin images
`${VAR}` is empty in `commands` | Pre-processing consumed it; use `$VAR`, or `$${VAR}`
`privileged` ignored or rejected | Repo is not marked Trusted
Pipeline waiting forever | No agent matches the workflow `labels`, or all agents are at `WOODPECKER_MAX_WORKFLOWS`
Agent cannot reach server | `WOODPECKER_SERVER` must be the gRPC address (port 9000), and `WOODPECKER_AGENT_SECRET` must match
Pull request from a fork needs approval | Project setting "Require approval for": approve with the UI or `pipeline approve`
Cannot pull private image | Add registry credentials in repo Settings > Registries, or `WOODPECKER_DOCKER_CONFIG` on the agent

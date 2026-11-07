# Drone CI
Drone is a self-hosted, container-native CI system: every step runs in a container and pipelines live in `.drone.yml` in the repository. [Woodpecker CI](woodpecker-ci.md) is a community fork of Drone, so the two share ideas but differ in syntax (file names, `when` versus `trigger`, `kind: pipeline` headers); use this sheet for Drone itself. The `drone` CLI section was checked against `drone` v1.9.0 (`--help` output); the pipeline syntax, server and runner settings come from the Drone docs and were not run here (unverified).

Documentation: [Drone docs](https://docs.drone.io/)
Project: [harness/drone](https://github.com/harness/drone), [harness/drone-cli](https://github.com/harness/drone-cli)

---
## Minimal Pipeline
```yaml
# .drone.yml
kind: pipeline
type: docker
name: default

trigger:
  branch: [main]
  event: [push, pull_request]

steps:
  - name: test
    image: node:22
    commands:
      - npm ci
      - npm test

  - name: publish
    image: plugins/docker
    settings:
      repo: registry.example.com/org/app
      tags: latest
      username:
        from_secret: registry_user
      password:
        from_secret: registry_password
    when:
      event: [push]
      branch: [main]
```

Steps run in order in one shared workspace. `commands` run as one shell script inside the image and the step fails on the first non-zero exit.

## Pipeline Keys
KEY | DESCRIPTION
---|---
`kind: pipeline` | Document type (others: `secret`, `signature`)
`type` | Runner type: `docker`, `exec`, `kubernetes`, `ssh`
`name` | Pipeline name (must be unique in the repo when there are several)
`platform` | `os` and `arch` the pipeline needs, to pick a matching runner
`clone` | Clone options, such as `depth` or `disable: true`
`trigger` | Conditions for the whole pipeline (`branch`, `event`, `ref`, `status`, `target`, `cron`, `repo`)
`depends_on` | Names of other pipelines in the file that must finish first
`concurrency` | Limit simultaneous runs of this pipeline
`node` | Runner labels the pipeline must match
`services` | Containers kept running for the steps (databases and similar)
`volumes` | Volumes: `temp` for sharing between steps, `host` for a path on the runner (trusted repositories only)
`image_pull_secrets` | Names of registry credentials for pulling private images
`steps[].name` / `image` / `commands` | Step name, container image, commands
`steps[].environment` | Environment variables, plain or `from_secret`
`steps[].settings` | Plugin parameters
`steps[].when` | Step level conditions (same fields as `trigger`)
`steps[].depends_on` | Make steps a graph so independent ones run in parallel
`steps[].failure: ignore` | Do not fail the pipeline if the step fails
`steps[].detach: true` | Run in the background
`steps[].privileged: true` | Privileged container (trusted repositories only)

## Services, Volumes and Dependencies
```yaml
kind: pipeline
type: docker
name: integration

services:
  - name: db
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: example

steps:
  - name: test
    image: golang:1.24
    commands:
      - go test ./...

---
kind: pipeline
type: docker
name: deploy
depends_on: [integration]

trigger:
  event: [promote]
  target: [production]

steps:
  - name: ship
    image: alpine:3.22
    commands:
      - echo deploying
```

Separate pipelines in one file are divided by `---`. A `promote` pipeline runs only when a build is promoted (CLI below).

## Secrets
SECRET TYPE | HOW
---|---
Repository secret | `drone secret add` or the web UI; use as `from_secret: NAME`
Organisation secret | `drone orgsecret add`; shared by the organisation's repositories
Secret from an external store | A `kind: secret` document with a `get:` block (`path` and `name`) for a configured secret extension (unverified: see the docs)
Pull request exposure | Secrets are not shared with pull requests unless `--allow-pull-request` is set, so do not enable it for untrusted forks

```yaml
steps:
  - name: deploy
    image: alpine:3.22
    environment:
      API_TOKEN:
        from_secret: api_token
    commands:
      - ./deploy.sh
```

## The drone CLI
Set `DRONE_SERVER` (for example `https://drone.example.com`) and `DRONE_TOKEN` (your personal token from the web UI), or pass `-s/--server` and `-t/--token`.

COMMAND | DESCRIPTION
---|---
`drone info` | Show the current user (confirms server and token work)
`drone repo ls` | List repositories
`drone repo enable ORG/REPO` / `repo disable` | Activate or deactivate a repository
`drone repo update ORG/REPO --trusted` | Update repository settings (also `--protected`, `--timeout`, `--visibility`, `--ignore-forks`, `--ignore-pull-requests`, `--auto-cancel-*`, `--config`)
`drone repo sync` | Re-sync the repository list from the forge
`drone repo repair ORG/REPO` | Repair webhooks
`drone repo chown ORG/REPO` | Take ownership of a repository
`drone build ls ORG/REPO` | Build history (`--branch`, `--event`, `--status`, `--limit`, `--page`, `--format`)
`drone build last ORG/REPO` / `build info ORG/REPO BUILD` | Latest build, or one build
`drone build create ORG/REPO --branch main -p KEY=VALUE` | Start a build (`--commit`, `-p` parameters)
`drone build restart ORG/REPO BUILD` / `build stop` | Restart or stop a build
`drone build approve` / `build decline` | Answer an approval gate on a stage
`drone build promote ORG/REPO BUILD ENVIRONMENT -p KEY=VALUE` | Promote a build to an environment (triggers `event: promote`)
`drone build rollback ORG/REPO BUILD ENVIRONMENT` | Roll back a build to an environment
`drone build queue` | Show the build queue
`drone log view ORG/REPO BUILD STAGE STEP` | Show a step's logs
`drone log purge ORG/REPO BUILD STAGE STEP` | Delete a step's log (destructive)
`drone secret add --repository ORG/REPO --name NAME --data VALUE` | Add a repository secret (`--allow-pull-request`, `--allow-push-on-pull-request`)
`drone secret ls ORG/REPO` / `secret info` / `secret update` / `secret rm` | Manage repository secrets
`drone orgsecret add ORG NAME VALUE` | Add an organisation secret (`--allow-pull-request`, `--allow-push-on-pull-request`)
`drone cron add ORG/REPO NAME EXPR` | Add a cron job (`--branch`, default `master`; also `cron ls`, `info`, `enable`, `disable`, `exec ORG/REPO NAME`, `rm`)
`drone template add` / `template ls` / `template info` / `template update` / `template rm` | Manage pipeline templates
`drone encrypt ORG/REPO VALUE` | Encrypt a secret for the repository (legacy)
`drone queue ls` / `queue pause` / `queue resume` | Queue operations

Local files (no server needed):

COMMAND | DESCRIPTION
---|---
`drone lint .drone.yml` | Check the YAML (`--trusted` for a trusted repository)
`drone exec .drone.yml` | Run a pipeline locally in Docker (needs Docker)
`drone exec --pipeline NAME` | Run one named pipeline
`drone exec --include STEP --exclude STEP` | Run only some steps
`drone exec --secret-file FILE --env-file FILE` | Provide `from_secret` values and extra environment (the secret file format is in the docs)
`drone exec --event push --branch main --repo ORG/REPO` | Pretend the build came from a given event, branch or repo
`drone exec --trusted --privileged IMAGE` | Allow trusted features, or privileged images (default privileged plugins: `plugins/docker`, `plugins/acr`, `plugins/ecr`, `plugins/gcr`, `plugins/heroku`)
`drone sign ORG/REPO --save` | Sign the repository's pipeline file and save the signature into it (needed for protected repositories; the argument is the repository per the Drone docs, unverified)
`drone jsonnet --source .drone.jsonnet --target .drone.yml --stdout` | Generate YAML from Jsonnet (`--format`, `--stream`, `-V`, `-J`); `drone starlark` does the same for Starlark (`--source`, default `.drone.star`)

## Running the Server and a Runner
Unverified: the variable names below come from the Drone install guides. Check them for your forge (Gitea shown) before use.

```yaml
services:
  drone:
    image: drone/drone:2
    ports:
      - "8080:80"
    volumes:
      - drone-data:/data
    environment:
      DRONE_GITEA_SERVER: https://git.example.com
      DRONE_GITEA_CLIENT_ID: OAUTH_CLIENT_ID
      DRONE_GITEA_CLIENT_SECRET: OAUTH_CLIENT_SECRET
      DRONE_RPC_SECRET: SHARED_SECRET
      DRONE_SERVER_HOST: drone.example.com
      DRONE_SERVER_PROTO: https
  runner:
    image: drone/drone-runner-docker:1
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      DRONE_RPC_PROTO: https
      DRONE_RPC_HOST: drone.example.com
      DRONE_RPC_SECRET: SHARED_SECRET
      DRONE_RUNNER_CAPACITY: "2"
      DRONE_RUNNER_NAME: runner-1
volumes:
  drone-data:
```

Generate the shared secret with `openssl rand -hex 16`. The runner mounts the Docker socket, which gives its pipelines control of the host's Docker, so only run trusted repositories on it.

## Built-in Variables
VARIABLE | MEANING
---|---
`DRONE_COMMIT_SHA` | Commit being built
`DRONE_BRANCH` | Branch name
`DRONE_TAG` | Tag name for tag builds
`DRONE_BUILD_NUMBER` | Build number
`DRONE_BUILD_EVENT` | `push`, `pull_request`, `tag`, `promote`, `rollback`, `cron`
`DRONE_REPO` | `ORG/REPO`
`DRONE_COMMIT_AUTHOR` | Commit author

## Troubleshooting
SYMPTOM | FIX
---|---
Pipeline never starts | The repository is not activated, the webhook failed (`drone repo repair`), or `trigger` excludes the event
`from_secret` is empty in a pull request | Secrets are withheld from pull requests unless the secret allows it
Step fails with a permission error on `privileged` or volumes | The repository must be marked trusted by an admin
Pipeline YAML rejected | `drone lint .drone.yml` locally
Runner never picks up a build | `DRONE_RPC_SECRET`/host mismatch, or `platform`/`node` labels do not match the runner
Want to debug locally | `drone exec` with the same image set

## See Also
- [Woodpecker CI](woodpecker-ci.md)
- [CI/CD Overview](cicd.md)
- [CI Docker Builds](ci-docker-builds.md)
- [Gitea (and Forgejo)](../tools/gitea.md)
- [Jenkins](jenkins.md)

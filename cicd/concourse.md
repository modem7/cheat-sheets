# Concourse CI
Concourse is a container-based CI system where a pipeline is one YAML file of resources (things to watch) and jobs (things to run), driven entirely from the `fly` CLI. Use it for self-hosted pipelines whose every build runs in a fresh container. The `fly` commands and flags below were checked against `fly` v8.3.3; the pipeline YAML and the Compose quick start come from the Concourse docs and were not run here (unverified).

Documentation: [Concourse docs](https://concourse-ci.org/docs/)
Project: [concourse/concourse](https://github.com/concourse/concourse)

---
## Quick Start (Docker Compose)
Unverified: the environment variable names come from the Concourse install docs, so compare with the current docs before use. Replace the placeholder credentials.

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: concourse
      POSTGRES_USER: concourse_user
      POSTGRES_PASSWORD: DB_PASSWORD
  concourse:
    image: concourse/concourse
    command: quickstart
    privileged: true
    depends_on: [db]
    ports:
      - "8080:8080"
    environment:
      CONCOURSE_POSTGRES_HOST: db
      CONCOURSE_POSTGRES_USER: concourse_user
      CONCOURSE_POSTGRES_PASSWORD: DB_PASSWORD
      CONCOURSE_POSTGRES_DATABASE: concourse
      CONCOURSE_EXTERNAL_URL: http://localhost:8080
      CONCOURSE_ADD_LOCAL_USER: ADMIN_USER:ADMIN_PASSWORD
      CONCOURSE_MAIN_TEAM_LOCAL_USER: ADMIN_USER
```

Download `fly` from the web UI (it matches the server version), or run `fly -t <TARGET> sync` to replace it with the server's version.

## fly Basics
Every command takes `-t <TARGET>` (the saved target name). Most pipeline commands take `-p <PIPELINE>` and `--team <TEAM>` when the pipeline is not in the target's default team.

COMMAND | DESCRIPTION
---|---
`fly -t <TARGET> login -c http://HOST:8080 -u <USER> -p <PASSWORD>` | Log in and save the target (`-n <TEAM>` team, `-k` skip TLS verification, `-b` browser login)
`fly targets` | List saved targets
`fly -t <TARGET> status` | Login status
`fly -t <TARGET> sync` | Download and replace `fly` from the server
`fly -t <TARGET> userinfo` | Show the logged-in user
`fly -t <TARGET> teams` / `workers` | List teams, or registered workers (`-d` for details, `--json`)
`fly -v` | Print the fly version

## Pipelines
COMMAND | DESCRIPTION
---|---
`fly -t <TARGET> validate-pipeline -c pipeline.yml` | Check the YAML (`-s` fails on warnings, `-o` prints the templated result)
`fly -t <TARGET> set-pipeline -p <PIPELINE> -c pipeline.yml` | Create or update a pipeline (shows a diff and asks to confirm; `-n` skips the prompt, `-d` dry run)
`fly -t <TARGET> set-pipeline -p <PIPELINE> -c pipeline.yml -v KEY=VALUE -l vars.yml` | Fill `((KEY))` variables (`-v` string, `-y` YAML value, `-l` vars from a file)
`fly -t <TARGET> unpause-pipeline -p <PIPELINE>` | New pipelines start paused
`fly -t <TARGET> pause-pipeline -p <PIPELINE>` | Pause (`-a` for all)
`fly -t <TARGET> pipelines` | List pipelines
`fly -t <TARGET> get-pipeline -p <PIPELINE>` | Print the live config (`-j` for JSON)
`fly -t <TARGET> rename-pipeline -o <OLD> -n <NEW>` | Rename
`fly -t <TARGET> destroy-pipeline -p <PIPELINE>` | Delete a pipeline and its history (`-n` skips confirmation)
`fly -t <TARGET> archive-pipeline -p <PIPELINE>` | Archive instead of deleting

## Jobs, Builds and Resources
COMMAND | DESCRIPTION
---|---
`fly -t <TARGET> trigger-job -j <PIPELINE>/<JOB> -w` | Start a job and watch it
`fly -t <TARGET> watch -j <PIPELINE>/<JOB>` | Stream a job's output (`-b <BUILD>` a specific build)
`fly -t <TARGET> builds -j <PIPELINE>/<JOB> -c 10` | Recent builds (`--json`, `--since`, `--until`)
`fly -t <TARGET> abort-build -j <PIPELINE>/<JOB> -b <BUILD>` | Abort a build (`--force` is a last resort)
`fly -t <TARGET> rerun-build -j <PIPELINE>/<JOB> -b <BUILD> -w` | Re-run a build and watch it
`fly -t <TARGET> jobs -p <PIPELINE>` | List jobs
`fly -t <TARGET> pause-job -j <PIPELINE>/<JOB>` / `unpause-job` | Pause or resume one job
`fly -t <TARGET> resources -p <PIPELINE>` | List resources
`fly -t <TARGET> check-resource -r <PIPELINE>/<RESOURCE>` | Force a resource check now (`-f <VERSION>` checks from a version, `-a` does not wait)
`fly -t <TARGET> resource-versions -r <PIPELINE>/<RESOURCE>` | Versions a resource has found (`-c <N>` limits, `--json`)
`fly -t <TARGET> pin-resource -r <PIPELINE>/<RESOURCE> -v <VERSION>` / `unpin-resource` | Pin a resource to one version (`-c` stores a comment)
`fly -t <TARGET> hijack -j <PIPELINE>/<JOB> -s <STEP>` | Shell into a build container (default command is `bash`; `--step-type`, `-b <BUILD>`)
`fly -t <TARGET> containers` / `volumes` | Active containers and volumes

## One-off Tasks
`fly execute` runs a task file against local files without a pipeline, which is the fastest way to test a task.

COMMAND | DESCRIPTION
---|---
`fly -t <TARGET> execute -c task.yml -i <NAME>=<PATH>` | Upload a local directory as the task input `<NAME>` and run (`-i` repeats)
`fly -t <TARGET> execute -c task.yml -i src=. -o out=./out` | Fetch the task output `out` into `./out`
`fly -t <TARGET> execute -c task.yml -i src=. -p` | Run privileged
`fly -t <TARGET> execute -c task.yml -j <PIPELINE>/<JOB> -i src=.` | Take the other inputs from a job (`-j` is `--inputs-from`)

## Pipeline YAML
Unverified against a running server: the structure follows the Concourse docs.

```yaml
resources:
  - name: repo
    type: git
    source:
      uri: https://git.example.com/org/app.git
      branch: main

jobs:
  - name: test
    plan:
      - get: repo
        trigger: true
      - task: unit
        config:
          platform: linux
          image_resource:
            type: registry-image
            source:
              repository: alpine
              tag: "3.22"
          inputs:
            - name: repo
          run:
            path: sh
            args: [-c, "cd repo && ./run-tests.sh"]
  - name: publish
    plan:
      - get: repo
        passed: [test]
        trigger: true
      - task: build
        file: repo/ci/build.yml
        params:
          REGISTRY_TOKEN: ((registry_token))
```

KEYWORD | MEANING
---|---
`resources` | External things the pipeline watches or writes (git repos, images, time)
`resource_types` | Custom resource implementations
`jobs[].plan` | Steps: `get`, `put`, `task`, `in_parallel`, `do`, `try`, `set_pipeline`, `across`
`get: X` with `trigger: true` | Start the job when a new version of `X` appears
`passed: [JOB]` | Only use versions that have gone through those jobs
`task` with `file:` | Load a task definition from an input (keeps YAML out of the pipeline)
`((NAME))` | Variable filled by `fly set-pipeline -v/-l` or by a credential manager
`params` | Environment variables for a task

Common built-in resource types (named in the Concourse docs): `git`, `registry-image`, `time`, `s3`, `docker-image`.

## Troubleshooting
SYMPTOM | FIX
---|---
Nothing runs after `set-pipeline` | Pipelines start paused: `fly unpause-pipeline -p <PIPELINE>`
`fly` says it is out of date | `fly -t <TARGET> sync`
Job does not start on a new commit | Check the resource: `fly check-resource`, and that the `get` step has `trigger: true`
Need to debug a failing step | `fly hijack -j <PIPELINE>/<JOB>` while the container still exists
Variable `((X))` unresolved | Pass `-v X=...` or `-l file.yml` to `set-pipeline`, or configure a credential manager
No workers | `fly workers`; the worker process must be able to reach the web node's TSA port

## See Also
- [CI/CD Overview](cicd.md)
- [Jenkins](jenkins.md)
- [Drone CI](drone-ci.md)
- [Docker Compose](../docker/docker-compose.md)

# GitLab CI/CD
GitLab CI/CD is configured by a `.gitlab-ci.yml` file at the repo root. Jobs run on runners (shared, group or self-hosted) and are grouped into stages. For the GitLab host itself and the `glab` CLI see [GitLab and the glab CLI](../tools/gitlab.md); for the shared concepts see [CI/CD Overview](cicd.md); for building images see [CI Docker Builds](ci-docker-builds.md).

Documentation: [CI/CD YAML reference](https://docs.gitlab.com/ci/yaml/), [Predefined variables](https://docs.gitlab.com/ci/variables/predefined_variables/), [glab ci](https://gitlab.com/gitlab-org/cli/-/tree/main/docs/source/ci)

---
## Minimal Pipeline
```yaml
stages: [lint, test, build, deploy]

default:
  image: node:22
  interruptible: true

variables:
  npm_config_cache: "$CI_PROJECT_DIR/.npm"

lint:
  stage: lint
  script:
    - npm ci
    - npm run lint
  cache:
    key:
      files: [package-lock.json]
    paths: [.npm/]

test:
  stage: test
  script:
    - npm ci
    - npm test -- --ci
  coverage: '/All files[^|]*\|[^|]*\s+([\d\.]+)/'
  artifacts:
    when: always
    reports:
      junit: junit.xml
    expire_in: 1 week

build:
  stage: build
  script:
    - npm run build
  artifacts:
    paths: [dist/]
    expire_in: 1 day

deploy:
  stage: deploy
  script:
    - ./scripts/deploy.sh
  environment:
    name: production
    url: https://example.com
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: manual
```

## Job Keywords
KEYWORD | DESCRIPTION
---|---
`stage` | Stage the job belongs to (default `test`)
`image` | Container image the job runs in (Docker/Kubernetes executors)
`script` | Commands to run (required)
`before_script` / `after_script` | Commands before/after `script` (`after_script` runs even on failure)
`variables` | Job-level variables
`rules` | Conditions deciding whether the job is added to the pipeline
`needs` | Start as soon as the listed jobs finish, ignoring stage order (DAG)
`dependencies` | Which earlier jobs' artifacts to download
`artifacts` | Files kept after the job (`paths`, `expire_in`, `reports`, `when`)
`cache` | Files reused between pipelines (`key`, `paths`, `policy`)
`environment` | Deployment target (`name`, `url`, `action`, `on_stop`)
`services` | Sidecar containers (databases, `docker:dind`)
`tags` | Select runners by tag
`timeout` | Job timeout, e.g. `30 minutes`
`retry` | Retry count, optionally limited with `when: runner_system_failure`
`allow_failure` | Job may fail without failing the pipeline
`interruptible` | Auto-cancel when a newer pipeline starts on the ref
`parallel` | Run N copies, or `parallel: matrix:` for a matrix
`resource_group` | Serialise jobs, e.g. one deploy at a time
`extends` | Inherit from a hidden job (name starting with `.`)
`trigger` | Start a downstream or child pipeline
`coverage` | Regex to scrape the coverage figure from the log

## Rules
`only`/`except` are legacy; use `rules`. The first matching rule wins.
```yaml
workflow:                 # controls whether the whole pipeline is created
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH && $CI_OPEN_MERGE_REQUESTS
      when: never         # avoid duplicate branch + MR pipelines
    - if: $CI_COMMIT_BRANCH
    - if: $CI_COMMIT_TAG

job:
  script: echo hi
  rules:
    - if: $CI_COMMIT_TAG =~ /^v\d+\.\d+\.\d+$/
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      changes: [src/**/*, package-lock.json]
    - when: never
```

CLAUSE | DESCRIPTION
---|---
`if:` | Expression on variables (`==`, `!=`, `=~`, `&&`, `\|\|`)
`changes:` | Run only if matching files changed
`exists:` | Run only if the files exist in the repo
`when:` | `on_success` (default), `manual`, `delayed`, `always`, `never`
`allow_failure:` | Per-rule override
`variables:` | Per-rule variables

## Useful Predefined Variables
VARIABLE | MEANING
---|---
`CI_COMMIT_SHA` / `CI_COMMIT_SHORT_SHA` | Commit hash
`CI_COMMIT_BRANCH` / `CI_COMMIT_TAG` | Ref name (branch is unset in tag pipelines)
`CI_DEFAULT_BRANCH` | The project's default branch
`CI_PIPELINE_SOURCE` | `push`, `merge_request_event`, `schedule`, `web`, `api`, `trigger`
`CI_MERGE_REQUEST_IID` | MR number (MR pipelines only)
`CI_PROJECT_DIR` | Checkout directory
`CI_REGISTRY` / `CI_REGISTRY_IMAGE` | GitLab container registry host and this project's image path
`CI_REGISTRY_USER` / `CI_REGISTRY_PASSWORD` | Short-lived registry credentials for the job
`CI_JOB_TOKEN` | Token for API and registry calls from the job
`CI_ENVIRONMENT_NAME` | Environment of the current job

## needs, Parallel and Matrix
```yaml
build:
  stage: build
  script: make

unit:
  stage: test
  needs: [build]         # starts as soon as build is done
  script: make test

test-matrix:
  stage: test
  parallel:
    matrix:
      - PYTHON: ["3.12", "3.13"]
        OS: [alpine, bookworm]
  image: python:${PYTHON}-${OS}
  script: pytest
```

## Include and Reuse
```yaml
include:
  - local: /ci/lint.yml                           # file in this repo
  - project: group/ci-templates                   # file in another project
    ref: v1.2.0
    file: /templates/docker.yml
  - remote: https://example.com/ci/common.yml     # public URL
  - template: Security/SAST.gitlab-ci.yml         # GitLab-provided template
  - component: $CI_SERVER_FQDN/group/components/build@1.0.0   # CI/CD component

.node-base:               # hidden job, only used via extends
  image: node:22
  before_script: [npm ci]

test:
  extends: .node-base
  script: npm test
```
Pin `ref:` and component versions to a tag or SHA, not a moving branch.

## Cache vs Artifacts
| | CACHE | ARTIFACTS |
|---|---|---|
| Purpose | Speed up repeated work (dependencies) | Pass results between jobs, keep outputs |
| Reliability | Best effort, may be missing | Guaranteed for later stages and download |
| Scope | Per runner/key, across pipelines | Per pipeline, with expiry |
| Key | `key:` (`files:` for lock-file hash) | Job and `expire_in` |

## Docker Builds
```yaml
build-image:
  stage: build
  image: docker:27
  services: [docker:27-dind]
  variables:
    DOCKER_TLS_CERTDIR: "/certs"
  before_script:
    - echo "$CI_REGISTRY_PASSWORD" | docker login -u "$CI_REGISTRY_USER" --password-stdin "$CI_REGISTRY"
  script:
    - docker build -t "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA" .
    - docker push "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA"
```
Docker-in-Docker needs a runner with `privileged = true`. Daemonless alternatives are Kaniko-style tools or `buildah`. See [CI Docker Builds](ci-docker-builds.md) for buildx, caching and scanning.

## Variables and Secrets
- Set them under Settings > CI/CD > Variables. Mark them **Masked** (hidden in logs) and **Protected** (only on protected branches/tags).
- Use **File** type for certificates and kubeconfigs.
- Use `id_tokens:` to get an OIDC JWT for keyless cloud auth instead of storing cloud keys.
```yaml
deploy:
  id_tokens:
    CLOUD_ID_TOKEN:
      aud: https://cloud.example.com
  script: ./login-with-oidc.sh "$CLOUD_ID_TOKEN"
```

## Runners
COMMAND | DESCRIPTION
---|---
`gitlab-runner register` | Register a runner (prompts for URL, token, executor)
`gitlab-runner list` | List configured runners
`gitlab-runner verify` | Check runners can still reach GitLab
`gitlab-runner run` | Run in the foreground
`gitlab-runner --version` | Version

Run a runner in Docker ([Docker-Compose](../docker/docker-compose.md)):
```yaml
services:
  gitlab-runner:
    image: gitlab/gitlab-runner:latest
    restart: unless-stopped
    volumes:
      - ./config:/etc/gitlab-runner
      - /var/run/docker.sock:/var/run/docker.sock
```
Mounting the Docker socket gives jobs root-equivalent access to the host; only do it for trusted projects.

## glab ci
COMMAND | DESCRIPTION
---|---
`glab ci status` | Status of the current branch's pipeline
`glab ci view` | Interactive pipeline view
`glab ci list` | List recent pipelines
`glab ci run` | Start a pipeline for the current branch (`--variables KEY:VALUE`)
`glab ci trace [<JOB>]` | Stream a job's log
`glab ci retry <JOB>` | Retry a job
`glab ci lint` | Validate `.gitlab-ci.yml`
`glab ci config compile` | Show the fully resolved config after `include`
`glab ci delete <ID>` | Delete a pipeline
`glab ci artifact <REF> <JOB>` | Download a job's artifacts

## Troubleshooting
SYMPTOM | CAUSE AND FIX
---|---
Pipeline not created / "No stages/jobs" | Every job's `rules` evaluated false, or `workflow:rules` blocked it; check with `glab ci lint`
Duplicate pipelines (branch and MR) | Add the `workflow:rules` block shown above
Job stuck "pending" | No runner matches the `tags`, or runners are offline/paused
`Cannot connect to the Docker daemon` | Missing `docker:dind` service, wrong `DOCKER_HOST`, or runner not privileged
Variable empty on a branch | Variable is **Protected** and the branch is not
Cache not restored | Different `key` or runner; caches are per runner unless distributed cache is configured
`needs` job fails on missing artifact | The needed job produced no `artifacts:` or they expired
YAML invalid | Run `glab ci lint`; the CI Lint tool in the UI shows the merged config

# GitLab and the glab CLI
GitLab is a Git host with built-in CI/CD, container registry and issue tracking, available as a SaaS (gitlab.com) or self-hosted. `glab` is its official CLI. For plain Git see [[git]], for GitHub see [[github-cli]], and for a lighter self-hosted option see [[gitea]].

Documentation: [GitLab Docs](https://docs.gitlab.com), [glab](https://gitlab.com/gitlab-org/cli)

---
## glab CLI
Install: `brew install glab` ([[homebrew]]), `choco install glab` ([[chocolatey]]) or a release package.

COMMAND | DESCRIPTION
---|---
`glab auth login` | Log in (use `--hostname` for self-hosted)
`glab repo clone GROUP/PROJECT` | Clone
`glab repo create NAME --private` | Create a project
`glab mr create --fill` | Open a merge request
`glab mr list` | List merge requests
`glab mr checkout 12` | Check out an MR
`glab mr merge 12 --squash --remove-source-branch` | Merge
`glab issue create --title "T"` | Create an issue
`glab ci status` | Pipeline status for the branch
`glab ci view` | Interactive pipeline view
`glab ci run` | Trigger a pipeline
`glab ci lint` | Validate `.gitlab-ci.yml`
`glab api projects/:id` | Call the REST API
`glab variable set NAME value` | Set a CI/CD variable

## .gitlab-ci.yml Basics
```yaml
stages: [test, build, deploy]

default:
  image: alpine:3

test:
  stage: test
  script:
    - echo "run tests"
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

build:
  stage: build
  image: docker:27
  services: [docker:27-dind]
  script:
    - docker login -u "$CI_REGISTRY_USER" -p "$CI_REGISTRY_PASSWORD" "$CI_REGISTRY"
    - docker build -t "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA" .
    - docker push "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA"
```
Common predefined variables: `CI_COMMIT_SHA`, `CI_COMMIT_REF_NAME`, `CI_PROJECT_DIR`, `CI_REGISTRY_IMAGE`, `CI_DEFAULT_BRANCH`. Mask secrets in Settings > CI/CD > Variables. Image tags above are examples; pin the versions you use. See [[docker]].

## Self-Host with Docker
```yaml
services:
  gitlab:
    image: gitlab/gitlab-ce:latest
    container_name: gitlab
    restart: unless-stopped
    hostname: gitlab.example.com
    shm_size: 256m
    ports:
      - "80:80"
      - "443:443"
      - "2222:22"
    volumes:
      - ./config:/etc/gitlab
      - ./logs:/var/log/gitlab
      - ./data:/var/opt/gitlab
    environment:
      GITLAB_OMNIBUS_CONFIG: |
        external_url 'https://gitlab.example.com'
        gitlab_rails['gitlab_shell_ssh_port'] = 2222
```
GitLab needs several GB of RAM and a few minutes to start. Get the first root password with `docker exec gitlab cat /etc/gitlab/initial_root_password` (the file is removed after about 24 hours). See [[docker-compose]].

## Runner
```bash
docker run -d --name gitlab-runner --restart unless-stopped \
  -v /srv/gitlab-runner/config:/etc/gitlab-runner \
  -v /var/run/docker.sock:/var/run/docker.sock \
  gitlab/gitlab-runner:latest
docker exec -it gitlab-runner gitlab-runner register
```
Registration asks for the instance URL, a token created in the UI, and an executor (usually `docker`). Mounting `docker.sock` gives jobs control of the host.

## Backup (Omnibus)
```bash
docker exec gitlab gitlab-backup create
```
Also back up `/etc/gitlab` (it holds `gitlab-secrets.json`, which is not in the backup archive).

## Not Verified
Written from knowledge and not run here. Check the GitLab docs for the current version, runner token flow and Docker image tags.

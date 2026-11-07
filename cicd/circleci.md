# CircleCI
CircleCI is a hosted CI/CD service (with a self-hosted runner option) configured by `.circleci/config.yml`. This sheet covers the version 2.1 config syntax and the `circleci` CLI. The CLI section was checked against `circleci` 1.14.0, a rewrite of the older CLI; the config YAML comes from the CircleCI docs and was not validated here because `circleci config validate` needs to reach the CircleCI API (unverified). For concepts shared with other systems see [CI/CD Overview](cicd.md).

Documentation: [CircleCI docs](https://circleci.com/docs/), [CLI reference](https://cli.circleci.com/reference/)
Project: [CircleCI-Public/circleci-cli](https://github.com/CircleCI-Public/circleci-cli)

---
## Minimal Config
```yaml
version: 2.1

executors:
  node:
    docker:
      - image: cimg/node:22.11
    resource_class: medium

commands:
  install-deps:
    steps:
      - restore_cache:
          keys:
            - deps-v1-{{ checksum "package-lock.json" }}
      - run: npm ci
      - save_cache:
          key: deps-v1-{{ checksum "package-lock.json" }}
          paths:
            - ~/.npm

jobs:
  test:
    executor: node
    steps:
      - checkout
      - install-deps
      - run:
          name: Run tests
          command: npm test
      - store_test_results:
          path: test-results
      - persist_to_workspace:
          root: .
          paths: [dist]
  deploy:
    executor: node
    steps:
      - attach_workspace:
          at: .
      - run: ./deploy.sh

workflows:
  main:
    jobs:
      - test
      - hold:
          type: approval
          requires: [test]
          filters:
            branches:
              only: main
      - deploy:
          requires: [hold]
          context: production
          filters:
            branches:
              only: main
  nightly:
    triggers:
      - schedule:
          cron: "0 3 * * *"
          filters:
            branches:
              only: main
    jobs:
      - test
```

## Config Keys
KEY | PURPOSE
---|---
`version: 2.1` | Required for orbs, commands, executors and parameters
`orbs` | Import shared packages of jobs, commands and executors
`executors` | Reusable environments: `docker`, `machine` (a VM) or `macos`, plus `resource_class`
`commands` | Reusable step lists with parameters
`jobs` | Named collections of steps run in one executor
`workflows` | Order and filter jobs: `requires`, `filters`, `context`, `matrix`, `triggers`
`parameters` | Pipeline parameters, set at trigger time
`parallelism` (job) | Run N copies of a job, usually to split tests
`working_directory`, `environment`, `shell` (job) | Job level defaults

## Steps
STEP | DESCRIPTION
---|---
`checkout` | Clone the repository at the pipeline's commit
`run` | Run a command (`name`, `command`, `environment`, `when: always\|on_fail`, `no_output_timeout`)
`save_cache` / `restore_cache` | Cache paths between runs, keyed on `{{ checksum "FILE" }}`
`persist_to_workspace` / `attach_workspace` | Pass files between jobs in one workflow
`store_artifacts` | Keep files for download
`store_test_results` | Upload JUnit style results for the test insights UI
`when` / `unless` | Conditional steps using a parameter or pipeline value
`setup_remote_docker` | Remote Docker engine for building images (see [CI Docker Builds](ci-docker-builds.md))

## Environment Variables
VARIABLE | MEANING
---|---
`CIRCLE_SHA1` | Commit being built
`CIRCLE_BRANCH` | Branch name
`CIRCLE_TAG` | Tag name when built from a tag
`CIRCLE_BUILD_NUM` | Job build number
`CIRCLE_PROJECT_REPONAME` | Repository name
`CIRCLE_WORKING_DIRECTORY` | Job working directory

Project variables and contexts are set in the web app or with `circleci envvar` and `circleci context` (below). Contexts hold secrets shared across projects and are referenced from a workflow job with `context:`.

## circleci CLI
Install by downloading the release archive (it contains a single `circleci` binary) or the `.deb` or `.rpm`. Global flags: `-c/--config`, `--debug`, `--no-color`, `-q/--quiet`. Help for any command: `circleci help <COMMAND>`.

COMMAND | DESCRIPTION
---|---
`circleci auth login` | Log in through the browser (`auth me` shows the account, `auth logout` clears credentials)
`circleci config validate [PATH]` | Validate a config (default `.circleci/config.yml`; `-` reads stdin; `--org gh/ORG` for private orbs; `--json`)
`circleci config process PATH` | Print the fully expanded config (orbs inlined, matrices and parameters resolved; `--pipeline-parameters 'key: value'`)
`circleci config pack DIR` | Merge a split config directory into one YAML document on stdout
`circleci config generate [PATH]` | Write a starter `.circleci/config.yml` from a scan of the repo (will not overwrite an existing file)
`circleci run list` | Recent runs for the project (`run get`, `run watch`, `run trigger`, `run cancel`, `run approve`)
`circleci workflow list` / `workflow rerun` / `workflow cancel` | Inspect and control workflows (IDs appear in `circleci run get`)
`circleci job get` / `job output` / `job artifact` | Job details, step output and artifacts
`circleci preflight run` | Push the working tree (including uncommitted changes) to a temporary `cci/preflight/` branch and watch the run; `circleci preflight cleanup` deletes those branches
`circleci envvar list` / `set NAME VALUE` / `delete NAME` | Project environment variables (`--project gh/ORG/REPO`; listed values are masked)
`circleci context list` / `create` / `get` / `delete` | Contexts (`context secret` manages the variables in one)
`circleci orb list` / `validate FILE` / `process FILE` / `publish` | Work with orbs
`circleci runner resource-class` / `token` / `instance` / `config` | Self-hosted runner management
`circleci project follow` / `project link` | Follow a project, or bind this checkout to one
`circleci completion` | Install or print shell completions

Version 1.14.0 has no `circleci local execute`; the older CLI used it to run a job locally. Use `circleci preflight run` (which runs in CircleCI itself) or run the job's image locally instead.

## Troubleshooting
SYMPTOM | FIX
---|---
`config validate` cannot reach the API | It compiles the config on CircleCI's servers, so it needs network access
Private orb not found | Add `--org gh/ORG` and log in (`circleci auth login`)
Workflow does not start | Config error, or branch and tag `filters` exclude it; tag filters need the job and every job it `requires` to allow the tag
Cache never restores | The key changes every run, or the checksum file differs on the branch
Deploy runs on every branch | Add `filters: branches: only: main` to the workflow job
Secret empty in a fork PR | Secrets are withheld from forks by default

## See Also
- [CI/CD Overview](cicd.md)
- [GitHub Actions](github-actions.md)
- [GitLab CI/CD](gitlab-ci.md)
- [CI Docker Builds](ci-docker-builds.md)

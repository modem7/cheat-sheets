# GitHub Actions
GitHub Actions runs workflows defined in `.github/workflows/*.yml` on GitHub-hosted or self-hosted runners. A workflow has triggers (`on`), jobs, and steps that run shell commands or reusable actions. Manage runs from the terminal with `gh run` (see also [[github-cli]]). General CI concepts are in [[cicd]], image builds in [[ci-docker-builds]], ready-made pipelines in [[ci-recipes]], and automated version bumps in [[renovate]].

Documentation: [Workflow syntax](https://docs.github.com/actions/reference/workflow-syntax-for-github-actions), [Events](https://docs.github.com/actions/reference/events-that-trigger-workflows), [Security hardening](https://docs.github.com/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions)

---
## Minimal Workflow
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v7.0.1
      - uses: actions/setup-node@v7.1.0
        with:
          node-version: 22
          cache: npm
      - run: npm ci
      - run: npm test
```

## Triggers
TRIGGER | DESCRIPTION
---|---
`push` | Branch or tag push (`branches`, `tags`, `paths`, `paths-ignore`)
`pull_request` | PR opened/updated (default types: `opened`, `synchronize`, `reopened`); runs the merge commit with a read-only token for forks
`pull_request_target` | Like `pull_request` but runs the **base** branch workflow with secrets, see pitfalls below
`workflow_dispatch` | Manual run from the UI, `gh workflow run`, or the API; supports `inputs`
`schedule` | Cron in UTC, minimum every 5 minutes; only runs on the default branch
`workflow_call` | Makes the workflow reusable by other workflows
`release` | `types: [published]` etc.
`issues`, `issue_comment` | Issue events
`workflow_run` | After another workflow finishes (runs with default-branch code and secrets)
`repository_dispatch` | External webhook trigger
`merge_group` | Merge queue checks

```yaml
on:
  push:
    tags: ["v*.*.*"]
    paths: ["src/**", "package-lock.json"]
  schedule:
    - cron: "0 3 * * 1"          # Mondays 03:00 UTC
  workflow_dispatch:
    inputs:
      environment:
        description: Target environment
        type: choice
        options: [staging, production]
        default: staging
      dry_run:
        type: boolean
        default: true
```
Read inputs with `${{ inputs.environment }}`. Scheduled workflows are disabled after 60 days of repo inactivity on public repos.

## Contexts and Expressions
EXPRESSION | MEANING
---|---
`${{ github.sha }}` / `github.ref_name` | Commit SHA / branch or tag name
`${{ github.event_name }}` | Trigger name
`${{ github.actor }}` | User that triggered the run
`${{ github.repository }}` | `owner/repo`
`${{ secrets.NAME }}` | A secret
`${{ vars.NAME }}` | A configuration variable (not secret)
`${{ env.NAME }}` | Environment variable
`${{ runner.os }}` | `Linux`, `Windows`, `macOS`
`${{ steps.<ID>.outputs.<NAME> }}` | Step output
`${{ needs.<JOB>.outputs.<NAME> }}` | Output from an earlier job
`${{ hashFiles('**/package-lock.json') }}` | Hash of matching files, for cache keys
`if: always()` / `failure()` / `success()` / `cancelled()` | Status checks for `if:`
`contains()`, `startsWith()`, `format()`, `fromJSON()`, `toJSON()` | Helper functions

Pass data between steps with files in `$GITHUB_OUTPUT`, `$GITHUB_ENV`, `$GITHUB_STEP_SUMMARY`:
```yaml
      - id: ver
        run: echo "version=$(cat VERSION)" >> "$GITHUB_OUTPUT"
      - run: echo "Building ${{ steps.ver.outputs.version }}"
      - run: echo "### Done :rocket:" >> "$GITHUB_STEP_SUMMARY"
```

## Matrix
```yaml
jobs:
  test:
    strategy:
      fail-fast: false
      max-parallel: 4
      matrix:
        os: [ubuntu-latest, windows-latest]
        python: ["3.12", "3.13"]
        include:
          - os: ubuntu-latest
            python: "3.14"
            experimental: true
        exclude:
          - os: windows-latest
            python: "3.12"
    runs-on: ${{ matrix.os }}
    continue-on-error: ${{ matrix.experimental == true }}
    steps:
      - uses: actions/checkout@v7.0.1
      - uses: actions/setup-python@v7.1.0
        with:
          python-version: ${{ matrix.python }}
          cache: pip
      - run: pytest
```

## Caching and Artifacts
```yaml
      - uses: actions/cache@v6.1.0
        with:
          path: ~/.cache/go-build
          key: go-${{ runner.os }}-${{ hashFiles('**/go.sum') }}
          restore-keys: |
            go-${{ runner.os }}-

      - uses: actions/upload-artifact@v7.0.2
        with:
          name: dist
          path: dist/
          retention-days: 7
          if-no-files-found: error

  # in a later job
      - uses: actions/download-artifact@v8.0.2
        with:
          name: dist
          path: dist/
```
Many `setup-*` actions have a built-in `cache:` input; prefer it. Caches are for speed (may be evicted); artifacts are for passing files between jobs and keeping outputs. Caches written on a PR are only readable by that PR and its base branch.

## Permissions
Set the default token to read-only and grant per job only what is needed.
```yaml
permissions:
  contents: read          # workflow default

jobs:
  release:
    permissions:
      contents: write       # create releases and tags
      pull-requests: write
      packages: write       # push to GHCR
      id-token: write       # OIDC token request
      attestations: write   # artifact attestations
```
`permissions: {}` removes all. Org/repo setting "Workflow permissions" should be read-only by default.

## Secrets, Variables and Environments
```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://example.com
    steps:
      - run: ./deploy.sh
        env:
          API_TOKEN: ${{ secrets.API_TOKEN }}
```
- Environments add required reviewers, wait timers, branch restrictions and environment-scoped secrets; a job targeting one pauses until approved.
- Set secrets with `gh secret set <NAME> --env production` or `--repo <OWNER>/<REPO>`.
- Secrets are masked in logs but can be exfiltrated by any code that runs in the job: only give them to jobs that need them.

## Reusable Workflows and Composite Actions
```yaml
# .github/workflows/build.yml (callee)
on:
  workflow_call:
    inputs:
      image:
        required: true
        type: string
    secrets:
      registry_token:
        required: false
    outputs:
      digest:
        value: ${{ jobs.build.outputs.digest }}
jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      digest: ${{ steps.push.outputs.digest }}
    steps:
      - id: push
        run: echo "digest=sha256:example" >> "$GITHUB_OUTPUT"
```
```yaml
# caller
jobs:
  build:
    uses: <OWNER>/<REPO>/.github/workflows/build.yml@v1
    with:
      image: ghcr.io/<OWNER>/app
    secrets: inherit        # or pass named secrets explicitly
```
```yaml
# .github/actions/setup/action.yml (composite action, used as ./.github/actions/setup)
name: Setup
runs:
  using: composite
  steps:
    - uses: actions/setup-node@v7.1.0
      with: { node-version: 22, cache: npm }
    - run: npm ci
      shell: bash
```
Use a reusable workflow for whole jobs, a composite action for a few steps. Reusable workflows can call other reusable workflows, but nesting depth is limited (check the current limit in the docs).

## OIDC to Clouds (No Stored Keys)
The job requests a short-lived OIDC token and exchanges it for cloud credentials; trust is configured on the cloud side (restrict by repo, branch and environment).
```yaml
permissions:
  id-token: write
  contents: read

steps:
  - uses: aws-actions/configure-aws-credentials@v6.3.0
    with:
      role-to-assume: arn:aws:iam::<ACCOUNT_ID>:role/<ROLE>
      aws-region: eu-west-2

  - uses: azure/login@v3.1.0
    with:
      client-id: ${{ vars.AZURE_CLIENT_ID }}
      tenant-id: ${{ vars.AZURE_TENANT_ID }}
      subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}

  - uses: google-github-actions/auth@v3
    with:
      workload_identity_provider: projects/<NUM>/locations/global/workloadIdentityPools/<POOL>/providers/<PROVIDER>
      service_account: <SA>@<PROJECT>.iam.gserviceaccount.com
```
See [[aws-cli]], [[azure-cli]], [[gcloud]] and [[terraform]] for what to run once authenticated.

## Concurrency
```yaml
concurrency:
  group: deploy-${{ github.ref }}
  cancel-in-progress: false      # queue deploys instead of killing a running one
```
Use `cancel-in-progress: true` for CI on PRs (a newer push makes the old run pointless) and `false` for deployments. With `cancel-in-progress: false` a newer pending run replaces an older pending one, so only the latest queued run survives.

## Pinning Actions
FORM | EXAMPLE | TRADE-OFF
---|---|---
Major tag | `actions/checkout@v7` | Easy, but the tag can move
Exact tag | `actions/checkout@v7.0.1` | Readable; tags can still be re-pointed
Commit SHA | `actions/checkout@<FULL_SHA> # v7.0.1` | Immutable; recommended for third-party actions

Let [[renovate]] keep pins current: the preset `helpers:pinGitHubActionDigests` rewrites tags to digests and keeps the `# vX.Y.Z` comment updated. Pin every third-party action, and treat first-party `actions/*` and `github/*` as lower risk.

## Service Containers and Conditions
```yaml
jobs:
  integration:
    runs-on: ubuntu-latest
    services:
      db:
        image: postgres:17
        env:
          POSTGRES_PASSWORD: example     # throw-away CI value
        ports: ["5432:5432"]
        options: >-
          --health-cmd pg_isready --health-interval 10s --health-retries 5
    steps:
      - uses: actions/checkout@v7.0.1
      - run: ./scripts/integration-tests.sh
        env:
          DATABASE_URL: postgres://postgres:example@localhost:5432/postgres

      - name: Deploy only from main
        if: github.ref == 'refs/heads/main'
        run: ./deploy.sh

      - name: Annotate
        run: echo "::notice title=Done::finished"      # also ::warning and ::error
```

## gh run and gh workflow
COMMAND | DESCRIPTION
---|---
`gh run list` | Recent runs (`--workflow <FILE>`, `--branch <B>`, `--status failure`, `--limit 5`)
`gh run view <ID>` | Run summary (`--log` all logs, `--log-failed` only failed steps, `--job <ID>`)
`gh run watch <ID>` | Stream progress until done (`--exit-status` to fail on failure)
`gh run rerun <ID>` | Re-run all jobs (`--failed` only failed jobs, `--debug` with debug logging)
`gh run cancel <ID>` | Cancel a run
`gh run download <ID>` | Download artifacts (`-n <NAME>`)
`gh run delete <ID>` | Delete a run
`gh workflow list` | Workflows in the repo
`gh workflow run <FILE> -f key=value` | Trigger `workflow_dispatch` with inputs (`--ref <BRANCH>`)
`gh workflow view <FILE>` | Show a workflow (`--yaml`)
`gh workflow enable <FILE>` / `disable <FILE>` | Toggle a workflow
`gh secret set <NAME>` | Add a secret (reads stdin or prompts)
`gh variable set <NAME> --body <VALUE>` | Add a configuration variable
`gh cache list` / `gh cache delete <KEY>` | Manage Actions caches

Wait for the latest run on the current branch and fail on error:
```bash
gh run watch "$(gh run list --branch "$(git branch --show-current)" --limit 1 --json databaseId --jq '.[0].databaseId')" --exit-status
```

## Debugging
- Re-run with debug logging: `gh run rerun <ID> --debug`, or set the secrets/variables `ACTIONS_STEP_DEBUG=true` and `ACTIONS_RUNNER_DEBUG=true`.
- Dump contexts: `- run: echo '${{ toJSON(github) }}'` (never dump `secrets`).
- Validate locally: [`actionlint`](https://github.com/rhysd/actionlint) catches syntax and expression errors; [`act`](https://github.com/nektos/act) runs workflows in Docker (approximate, not identical).
- Add `timeout-minutes` to every job so a hang does not burn 6 hours (the default limit).
- Reproduce on the runner with `tmate` only on private repos and only temporarily; it exposes the job.

## Security Pitfalls
PITFALL | FIX
---|---
`pull_request_target` plus checking out the PR head and running it | Never run untrusted PR code with secrets or a write token; use `pull_request`, or split into an unprivileged build and a privileged `workflow_run` that only consumes inert artifacts
Script injection: `run: echo "${{ github.event.pull_request.title }}"` | Pass untrusted values through `env:` and use `"$VAR"` in the script
Over-broad `GITHUB_TOKEN` | Declare `permissions:` explicitly
Unpinned third-party actions | Pin to a full SHA, let [[renovate]] update them
`secrets: inherit` into untrusted callee | Pass only the secrets needed
Long-lived cloud keys in secrets | Use OIDC
`workflow_run` triggered by a fork | It runs with default-branch secrets; treat the triggering artifacts as untrusted
Self-hosted runners on public repos | Anyone can open a PR that runs on your hardware; use ephemeral runners or avoid
`actions/checkout` leaving credentials on disk | Set `persist-credentials: false` when later steps run untrusted code

Safe pattern for untrusted input:
```yaml
      - name: Print PR title
        env:
          TITLE: ${{ github.event.pull_request.title }}
        run: echo "$TITLE"
```

## Troubleshooting
SYMPTOM | CAUSE AND FIX
---|---
Workflow does not appear / run | YAML invalid (check the Actions tab banner), file not in `.github/workflows/`, trigger filter excludes it, or it is on a non-default branch (for `schedule` and `workflow_dispatch` it must be on the default branch)
`Resource not accessible by integration` | Missing `permissions:`; add the scope the step needs
Secrets empty on a PR | PR from a fork; secrets are not passed. Use a trusted workflow or an approval flow
`workflow_dispatch` button missing | The trigger is absent on the default branch
Cache never hits | Key includes something that changes each run; check `restore-keys` and branch scoping
`Error: Process completed with exit code 1` with no detail | Run `gh run view <ID> --log-failed`, then re-run with `--debug`
Actions pushed by `GITHUB_TOKEN` do not trigger workflows | By design; use a GitHub App token or PAT if a follow-up workflow must run
Scheduled run delayed or skipped | High load at the top of the hour (use an off-peak minute), or the repo was inactive
Reusable workflow cannot see caller's secrets | Declare them under `workflow_call.secrets` or use `secrets: inherit`

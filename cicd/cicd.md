# CI/CD Overview
Continuous integration (CI) builds and tests every change automatically; continuous delivery/deployment (CD) ships what passed. This sheet covers the concepts shared by every tool (stages, branch flow, secrets, caching) and links to the per-tool sheets: [[github-actions]], [[woodpecker-ci]], [[gitlab-ci]], [[renovate]], [[ci-docker-builds]] and [[ci-recipes]].

Documentation: [GitHub Actions](https://docs.github.com/actions), [Woodpecker](https://woodpecker-ci.org/docs/intro), [GitLab CI/CD](https://docs.gitlab.com/ci/)

---
## Choosing a Tool
TOOL | GOOD FOR | NOTES
---|---|---
GitHub Actions | Repos hosted on GitHub | Hosted runners, huge action marketplace, see [[github-actions]]
Woodpecker CI | Self-hosted, container-native pipelines | Runs on Gitea/Forgejo/GitHub/GitLab, see [[woodpecker-ci]]
GitLab CI | Repos hosted on GitLab | Built in, see [[gitlab-ci]] and [[gitlab]]
Gitea/Forgejo Actions | Self-hosted Gitea | GitHub-compatible syntax, see [[gitea]]
Renovate | Dependency update PRs | Not a CI system, but triggers CI on every PR, see [[renovate]]

## Pipeline Stages
STAGE | PURPOSE | TYPICAL JOBS
---|---|---
Lint | Fast feedback on style and syntax | `markdownlint`, `yamllint`, `shellcheck`, `hadolint`, `eslint`
Test | Prove behaviour | unit tests, integration tests with service containers
Build | Produce the artifact | compile, `docker buildx build`, package
Scan | Catch known problems | Trivy image scan, dependency audit, secret scan
Publish | Make the artifact available | push image to a registry, upload release assets
Deploy | Run it somewhere | `docker compose pull && up -d`, `helm upgrade`, [[ansible-playbook]], [[terraform]] apply
Verify | Check it works | smoke test, health check, notify on failure

Rules of thumb:
- Put the cheapest, fastest jobs first so a typo fails in seconds, not after a 10 minute build.
- Run independent jobs in parallel (`needs:` / `depends_on:` only where there is a real dependency).
- Build once, promote the same artifact (image digest) through environments; do not rebuild per environment.
- Deploy only from the default branch or from tags, never from a pull request from a fork.

## Branch and PR Flow
STEP | WHAT HAPPENS
---|---
1. Branch | `git switch -c feat/<NAME>` off an up to date default branch ([[git]])
2. Push and open PR | `gh pr create` ([[github-cli]]), CI runs the lint, test and build stages
3. Review | Required checks must be green, at least one review
4. Merge | Squash or rebase merge into the default branch
5. Default branch pipeline | Builds again, publishes `latest` or a version, deploys to staging
6. Tag / release | A `v1.2.3` tag (or release-please PR merge) publishes versioned artifacts and deploys to production

Protect the default branch: require status checks, require PRs, block force pushes, and (where possible) require signed commits.

## Triggers Compared
EVENT | GITHUB ACTIONS | WOODPECKER | GITLAB CI
---|---|---|---
Push to branch | `push` | `event: push` | `$CI_PIPELINE_SOURCE == "push"`
Pull / merge request | `pull_request` | `event: pull_request` | `$CI_PIPELINE_SOURCE == "merge_request_event"`
Tag | `push` with `tags:` | `event: tag` | `$CI_COMMIT_TAG`
Manual | `workflow_dispatch` | `event: manual` | `when: manual` or "Run pipeline" in the UI
Schedule | `schedule` (cron) | `event: cron` (set up in the UI) | Pipeline schedules in the UI
Deploy | `environment:` / `deployment` | `event: deployment` | `environment:`

## Secrets Handling
RULE | WHY
---|---
Store secrets in the CI system's secret store, never in the repo | Git history is forever
Scope secrets to the narrowest level (environment, repo) | A leak affects less
Prefer short-lived credentials (OIDC to the cloud) over long-lived keys | Nothing to rotate or steal, see [[github-actions]]
Never `echo` a secret, never pass it as a command-line argument | Logs and `ps` expose it
Do not expose secrets to pull requests from forks | An attacker's PR could print them
Use a dedicated bot account or deploy key with minimum scopes | Limits blast radius
Rotate after any suspected leak, then clean up history | Removing a commit does not un-leak a key

Scan for leaked secrets before they land:
```bash
gitleaks detect --source . --verbose        # scan the repo history
gitleaks protect --staged                   # scan only what is staged (pre-commit hook)
```

## Caching and Speed
TECHNIQUE | HOW
---|---
Dependency cache | Key on the lock file hash (`hashFiles('**/package-lock.json')`)
Docker layer cache | `cache-from` / `cache-to` with the `gha` or `registry` backend, see [[ci-docker-builds]]
Shallow clone | `fetch-depth: 1` (the default in most tools); use full history only for changelogs and version tools
Path filters | Skip jobs when only docs changed (`paths:` / `when.path`)
Cancel superseded runs | `concurrency` with `cancel-in-progress` on PRs
Pre-built tool images | Run steps in an image that already contains the tools instead of installing them each time

## Dependency Updates
Automated update PRs ([[renovate]]) are only as safe as the CI behind them. Keep tests meaningful, pin versions, auto-merge only patch and digest updates that pass CI, and keep majors for human review.

## Troubleshooting
SYMPTOM | CAUSE AND FIX
---|---
Works locally, fails in CI | Different tool versions or missing env vars; pin versions and run the same container locally
Pipeline does not trigger | Event filter, path filter or branch filter excludes it; the YAML failed to parse; the app/webhook is not installed
Secret is empty in a PR | Secrets are withheld from fork PRs by design
Flaky test | Retry masks it; quarantine and fix, do not just add `retry:`
Slow pipeline | Add caches, parallelise, drop unused jobs, use path filters
Cache never hits | Cache key changes every run (timestamps, `github.run_id`) or branch scoping prevents sharing
Deploy ran twice | No `concurrency` group on the deploy job

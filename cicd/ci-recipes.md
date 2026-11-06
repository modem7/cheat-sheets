# CI Recipes
Copy-and-adapt pipelines for the jobs most repos need: lint, test, build, release, housekeeping and documentation checks. Examples are GitHub Actions ([[github-actions]]); the ideas port directly to [[woodpecker-ci]] and [[gitlab-ci]]. Image publishing is in [[ci-docker-builds]], dependency PRs in [[renovate]], and concepts in [[cicd]].

Documentation: [release-please](https://github.com/googleapis/release-please-action), [semantic-release](https://semantic-release.gitbook.io), [markdownlint-cli2](https://github.com/DavidAnson/markdownlint-cli2), [lychee](https://lychee.cli.rs)

---
## Lint, Test, Build Skeleton
```yaml
name: CI
on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

concurrency:
  group: ci-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7.0.1
      - uses: actions/setup-node@v7.1.0
        with: { node-version: 22, cache: npm }
      - run: npm ci
      - run: npm run lint

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7.0.1
      - uses: actions/setup-node@v7.1.0
        with: { node-version: 22, cache: npm }
      - run: npm ci
      - run: npm test -- --ci

  build:
    needs: [lint, test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7.0.1
      - uses: actions/setup-node@v7.1.0
        with: { node-version: 22, cache: npm }
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-artifact@v7.0.2
        with: { name: dist, path: dist/, retention-days: 7 }
```
Make one summary job (for example `ci-ok` with `needs: [lint, test, build]` and `if: always()`) the single required status check, so renaming a job never breaks branch protection.

## Lint Everything Else
LINTER | WHAT FOR | COMMAND
---|---|---
`actionlint` | GitHub workflow files | `actionlint`
`yamllint` | YAML syntax and style | `yamllint .`
`shellcheck` | Shell scripts | `shellcheck scripts/*.sh`
`hadolint` | Dockerfiles | `hadolint Dockerfile`
`markdownlint-cli2` | Markdown | `markdownlint-cli2 "**/*.md"`
`docker compose config -q` | Compose files ([[docker-compose]]) | `docker compose -f compose.yaml config -q`
`terraform fmt -check` / `terraform validate` | Terraform ([[terraform]]) | in the module directory
`ansible-lint` | Playbooks ([[ansible]]) | `ansible-lint`
`gitleaks` | Committed secrets | `gitleaks detect --source .`
`renovate-config-validator` | Renovate config | `npx --yes --package renovate -- renovate-config-validator --strict`

## Markdown Lint and Link Check
A good fit for a documentation or cheat-sheet repo.
```yaml
# .github/workflows/docs.yml
name: Docs
on:
  pull_request:
    paths: ["**/*.md", ".markdownlint*", ".lychee.toml"]
  schedule:
    - cron: "0 5 * * 1"      # weekly, catches rotted external links
  workflow_dispatch:

permissions:
  contents: read

jobs:
  markdownlint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7.0.1
      - uses: DavidAnson/markdownlint-cli2-action@v25.0.0
        with:
          globs: "**/*.md"

  links:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7.0.1
      - uses: lycheeverse/lychee-action@v2.9.0
        with:
          args: --no-progress --max-concurrency 8 --accept 200,429 './**/*.md'
          fail: true
```
Config files:
```json
{
  "default": true,
  "MD013": false,
  "MD033": false,
  "MD041": false
}
```
(`.markdownlint-cli2.jsonc` or `.markdownlint.json`; line length and inline HTML rules are usually turned off for cheat sheets.) Wiki-style `[[links]]` are not Markdown links; check them separately:
```bash
# print every [[name]] that has no matching file basename
comm -23 \
  <(grep -rhoE '\[\[[^]|#]+' --include='*.md' . | sed 's/^\[\[//' | sort -u) \
  <(find . -name '*.md' -not -path './.git/*' -exec basename {} .md \; | sort -u)
```
Anything printed is a broken wikilink (or a literal syntax example to ignore). Run the lychee link check on a schedule rather than every PR so a third-party outage does not block merges.

## Release with release-please
release-please reads Conventional Commits on `main`, keeps a "release PR" open with the next version and changelog, and when you merge it creates the tag and GitHub release.
```yaml
# .github/workflows/release-please.yml
name: Release Please
on:
  push:
    branches: [main]

permissions:
  contents: write
  pull-requests: write
  issues: write

jobs:
  release-please:
    runs-on: ubuntu-latest
    outputs:
      release_created: ${{ steps.rp.outputs.release_created }}
      tag_name: ${{ steps.rp.outputs.tag_name }}
    steps:
      - id: rp
        uses: googleapis/release-please-action@v5.0.0
        with:
          config-file: release-please-config.json
          manifest-file: .release-please-manifest.json

  publish:
    needs: release-please
    if: ${{ needs.release-please.outputs.release_created }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7.0.1
      - run: echo "Publishing ${{ needs.release-please.outputs.tag_name }}"
```
```json
{
  "release-type": "simple",
  "packages": { ".": {} }
}
```
```json
{ ".": "0.0.0" }
```
(first is `release-please-config.json`, second is `.release-please-manifest.json`.) Release types include `simple`, `node`, `python`, `go`, `rust`, `helm`. Releases and tags created with the default `GITHUB_TOKEN` do not trigger other workflows, so either run the publish job in the same workflow (as above) or give the action a PAT or GitHub App token via `token:`. The repo setting "Allow GitHub Actions to create and approve pull requests" must be on. v5 only changed the runtime to Node 24; the inputs are the same as v4.

Commit prefixes drive the version: `fix:` patch, `feat:` minor, `feat!:` or a `BREAKING CHANGE:` footer major; `chore:`, `docs:` do not release.

## Release with semantic-release
Fully automatic: every merge to `main` that contains releasable commits publishes a release, no release PR.
```yaml
jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      issues: write
      pull-requests: write
      id-token: write         # npm provenance
    steps:
      - uses: actions/checkout@v7.0.1
        with:
          fetch-depth: 0
          persist-credentials: false
      - uses: actions/setup-node@v7.1.0
        with: { node-version: 22 }
      - run: npx semantic-release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
```json
{
  "branches": ["main"],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    "@semantic-release/changelog",
    "@semantic-release/github"
  ]
}
```
(`.releaserc.json`). Choose release-please when you want a human to approve each release and a reviewable changelog; choose semantic-release for fully hands-off publishing, especially for packages.

## Tag-Triggered Release with Assets
```yaml
on:
  push:
    tags: ["v*.*.*"]

permissions:
  contents: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7.0.1
      - run: make dist
      - uses: softprops/action-gh-release@v3.0.4
        with:
          files: dist/*
          generate_release_notes: true
```
Or without a third-party action: `gh release create "$GITHUB_REF_NAME" dist/* --generate-notes` with `GH_TOKEN: ${{ github.token }}` ([[github-cli]]).

## Auto-Assign PRs and Issues
This is the pattern used in this repo: assign new issues and PRs to the maintainer, and sweep Renovate PRs that did not automerge.
```yaml
name: Issue and PR assignment
on:
  issues:
    types: [opened]
  pull_request:
    types: [opened]
  schedule:
    - cron: "0 */6 * * *"
  workflow_dispatch: {}

jobs:
  auto-assign-pr:
    if: github.event_name == 'pull_request' && github.actor != 'renovate[bot]'
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
      issues: write
    steps:
      - uses: pozil/auto-assign-issue@v4.1.0
        with:
          assignees: <USER>

  assign-stale-renovate-prs:
    if: github.event_name == 'schedule' || github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
    steps:
      - env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh pr list --repo "$GITHUB_REPOSITORY" --author "renovate[bot]" --state open \
            --json number,assignees --jq '.[] | select(.assignees | length == 0) | .number' |
          while read -r pr; do
            gh pr edit "$pr" --repo "$GITHUB_REPOSITORY" --add-assignee <USER>
          done
```
Renovate PRs that automerge never need a human; the ones still open after the schedule are the ones that do. Renovate can also assign directly with `"assignees": ["<USER>"]` in its config.

## Validate Renovate Config on PRs
```yaml
name: Renovate config
on:
  pull_request:
    paths: ["renovate.json", ".github/renovate.json", "renovate.json5"]
permissions:
  contents: read
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7.0.1
      - run: npx --yes --package renovate -- renovate-config-validator --strict
```

## Run actionlint on Workflow Changes
```yaml
jobs:
  actionlint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7.0.1
      - name: actionlint
        run: |
          bash <(curl -fsSL https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash)
          ./actionlint -color
```
Prefer pinning the download script to a release tag or using a container image so the lint step is itself reproducible.

## Required Checks and Merge Policy
SETTING | RECOMMENDATION
---|---
Branch protection / ruleset on the default branch | Require PRs, require the `ci-ok` summary check, block force pushes
"Require branches to be up to date" | On for busy repos, off for small ones (it forces rebases)
Merge method | Squash, so the PR title becomes the Conventional Commit that release-please reads
Automerge | Renovate patch/digest PRs only, see [[renovate]]
CODEOWNERS | Require review for `.github/workflows/` and deploy configuration

## Troubleshooting
SYMPTOM | CAUSE AND FIX
---|---
Required check stays "Expected" forever | The workflow is skipped by `paths:` filters; use a summary job that always runs, or drop path filters on required workflows
release-please opens no PR | No releasable commits since the last release, or commits are not Conventional (`fix:`/`feat:`); check the manifest version
release-please PR has no CI | PR created by `GITHUB_TOKEN` does not trigger workflows; use a PAT/App token in `token:`
Tag created but publish workflow did not run | Same cause; trigger from the same workflow with `needs`, or use a PAT
semantic-release "no release published" | Shallow clone (needs `fetch-depth: 0`) or no commits with release types
markdownlint fails on tables or long lines | Disable `MD013` (line length) in the config, or fix once and enforce
lychee fails on rate limits (429) | Accept 429, add `--max-concurrency`, cache results with `--cache`, or exclude the host
Link check passes locally, fails in CI | Relative links resolved from a different root; set `--root-dir`

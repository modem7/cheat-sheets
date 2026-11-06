# Renovate
Renovate opens pull requests that update dependencies (Docker images, GitHub Actions, npm, Go, Compose files, Helm charts, Terraform providers and more) and can automerge the safe ones. It is configured with a JSON config file in each repo, usually extending a shared preset. Updated Actions versions are covered in [[github-actions]], Woodpecker steps in [[woodpecker-ci]], image tags in [[ci-docker-builds]] and [[docker-compose]].

Documentation: [Renovate docs](https://docs.renovatebot.com), [Configuration options](https://docs.renovatebot.com/configuration-options/), [Preset reference](https://docs.renovatebot.com/presets-default/), [Config validation](https://docs.renovatebot.com/config-validation/)

---
## Minimal renovate.json
Renovate looks for `renovate.json`, `renovate.json5`, `.github/renovate.json`, `.gitlab/renovate.json`, `.renovaterc` and a `renovate` key in `package.json`.
```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": ["config:recommended"]
}
```
`config:recommended` enables the Dependency Dashboard, groups common monorepo and workspace packages, and enables sensible defaults.

## Shared Preset Pattern
Keep one preset repo and extend it everywhere. This repo's `renovate.json` is only:
```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": ["github>modem7/renovate-config"]
}
```
The preset repo (`modem7/renovate-config`) holds `default.json` (extends `shared`), `shared.json`, `automergePatch.json`, `automergeDigest.json` and `docker.json`. A repo can opt in to extras:
```json
{
  "extends": [
    "github>modem7/renovate-config",
    "github>modem7/renovate-config:automergePatch",
    "github>modem7/renovate-config:docker"
  ]
}
```
PRESET SYNTAX | MEANING
---|---
`config:recommended` | Built-in preset
`:automergeMinor` | Built-in "default" preset (leading colon); also `:automergePatch`, `:automergeDigest`, `:automergeAll`, `:maintainLockFilesWeekly`
`schedule:weekly` | Built-in schedule preset; others include `schedule:nonOfficeHours`, `schedule:earlyMondays`, `schedule:monthly`
`helpers:pinGitHubActionDigests` | Pin Actions to commit SHAs and keep the version comment updated
`docker:pinDigests` | Pin Docker images to digests
`github>OWNER/REPO` | `default.json` of a GitHub repo
`github>OWNER/REPO:NAME` | `NAME.json` in that repo
`github>OWNER/REPO:NAME#v1.0.0` | Pinned to a tag
`gitlab>GROUP/PROJECT`, `local>OWNER/REPO` | Same idea for GitLab, or the platform you are on

## Common Top-Level Options
OPTION | DESCRIPTION
---|---
`extends` | List of presets, applied in order (later wins)
`schedule` | When Renovate may create branches/PRs, e.g. `["before 6am on monday"]`
`timezone` | IANA zone used by `schedule`, e.g. `Europe/London`
`labels` / `addLabels` | Labels on PRs
`assignees` / `reviewers` | Who gets assigned or asked to review
`prConcurrentLimit` | Max open PRs (0 = unlimited); `prHourlyLimit` for rate
`automerge` | Merge when checks pass
`automergeType` | `pr` (default) or `branch`
`platformAutomerge` | Use GitHub/GitLab native auto-merge when allowed
`ignoreTests` | Automerge even with no CI configured
`minimumReleaseAge` | Wait N days after release before proposing (e.g. `3 days`), a defence against bad or malicious releases
`dependencyDashboard` | Maintain an issue listing all updates
`separateMajorMinor` | Separate PRs for major and minor (default true)
`enabledManagers` | Restrict to listed managers
`ignorePaths` | Paths to skip
`rebaseWhen` | `auto`, `behind-base-branch`, `conflicted`, `never`
`semanticCommits` | `enabled` / `disabled` / `auto`
`lockFileMaintenance` | Periodically refresh lock files
`pinDigests` | Pin Docker/Actions digests
`commitMessagePrefix`, `commitMessageTopic` | PR/commit title formatting

## packageRules
Rules are evaluated top to bottom; later matching rules override earlier ones. All `match*` conditions in a rule must hold.
```json
{
  "packageRules": [
    {
      "description": "Automerge minor and patch for dev dependencies",
      "matchDepTypes": ["devDependencies"],
      "matchUpdateTypes": ["minor", "patch"],
      "automerge": true
    },
    {
      "description": "Group all GitHub Actions updates",
      "matchManagers": ["github-actions"],
      "groupName": "github actions"
    },
    {
      "description": "Majors need a human and a wait",
      "matchUpdateTypes": ["major"],
      "automerge": false,
      "minimumReleaseAge": "7 days",
      "addLabels": ["major"]
    },
    {
      "description": "Hold back one image",
      "matchPackageNames": ["postgres"],
      "allowedVersions": "<18"
    },
    {
      "description": "Never touch these",
      "matchPackageNames": ["/^internal\\//"],
      "enabled": false
    }
  ]
}
```
MATCHER | MATCHES
---|---
`matchManagers` | Manager name: `github-actions`, `dockerfile`, `docker-compose`, `npm`, `gomod`, `woodpecker`, `helm-values`, `terraform` ...
`matchUpdateTypes` | `major`, `minor`, `patch`, `pin`, `digest`, `pinDigest`, `lockFileMaintenance`, `rollback`, `bump`
`matchPackageNames` | Package names, with globs or `/regex/`
`matchDepNames` | Dependency names as shown in the PR
`matchDepTypes` | e.g. `dependencies`, `devDependencies`, `action`
`matchFileNames` | Files the dependency was found in (globs)
`matchCurrentVersion` | Current version range
`matchBaseBranches` | Target branches
Actions on a match: `automerge`, `enabled`, `groupName`, `schedule`, `labels`, `addLabels`, `assignees`, `allowedVersions`, `versioning`, `pinDigests`, `minimumReleaseAge`, `extends` (apply a preset)

## Automerge
```json
{
  "extends": [":automergeDigest", ":automergePatch"],
  "platformAutomerge": false,
  "packageRules": [
    {
      "matchManagers": ["github-actions", "woodpecker"],
      "matchUpdateTypes": ["minor", "patch", "digest"],
      "automerge": true
    }
  ]
}
```
- Automerge needs required status checks to pass, so give the repo CI (see [[ci-recipes]]) or set `ignoreTests`.
- `platformAutomerge: true` uses GitHub's own auto-merge and requires branch protection with required checks; `false` makes Renovate merge on its next run.
- Run Renovate often enough (hourly) for automerge to complete; each run only merges a PR that is up to date and green.
- Keep majors manual. Digest and patch updates of CI plumbing are good automerge candidates.

## Schedules
```json
{
  "timezone": "Europe/London",
  "schedule": ["before 6am on monday"],
  "packageRules": [
    {
      "matchUpdateTypes": ["digest"],
      "extends": ["schedule:nonOfficeHours"]
    }
  ],
  "lockFileMaintenance": { "enabled": true, "schedule": ["before 4am on the first day of the month"] }
}
```
Schedules use "later" syntax (`after 10pm every weekday`, `every weekend`). Renovate still has to run during that window. Items outside the schedule appear in the Dependency Dashboard and can be forced with its checkbox.

## Custom (Regex) Managers
Use these for versions in arbitrary files. A comment above the value tells Renovate where to look it up.
```yaml
# compose.yaml / workflow / Dockerfile
env:
  NODE_VERSION: 22.12.0 # renovate: datasource=node-version depName=node
  # or
ARG S6_OVERLAY_VERSION=3.2.0.2
```
```json
{
  "customManagers": [
    {
      "customType": "regex",
      "description": "Versions annotated with a renovate comment",
      "managerFilePatterns": ["/(^|/)Dockerfile$/", "/^\\.github/workflows/.+\\.ya?ml$/"],
      "matchStrings": [
        "[A-Z_]+_VERSION[=:] ?(?<currentValue>\\S+) # renovate: datasource=(?<datasource>\\S+) depName=(?<depName>\\S+)"
      ]
    },
    {
      "customType": "regex",
      "description": "Fixed upstream project via templates",
      "managerFilePatterns": ["/^Dockerfile$/"],
      "matchStrings": ["ARG S6_OVERLAY_VERSION=(?<currentValue>[0-9.]+)"],
      "datasourceTemplate": "github-releases",
      "packageNameTemplate": "just-containers/s6-overlay",
      "extractVersionTemplate": "^v(?<version>.*)$"
    }
  ]
}
```
FIELD | DESCRIPTION
---|---
`customType` | `regex` (or `jsonata`)
`managerFilePatterns` | Files to scan; regex between `/ /` or globs (formerly `fileMatch`, which is auto-migrated)
`matchStrings` | Regexes with named groups `currentValue`, `datasource`, `depName` / `packageName`
`datasourceTemplate`, `depNameTemplate`, `packageNameTemplate` | Fixed values instead of capture groups; use `{{{ }}}` to avoid escaping
`versioningTemplate` | `semver`, `loose`, `docker`, `regex:...`
`extractVersionTemplate` | Strip a prefix like `v` from tags
Common datasources: `github-releases`, `github-tags`, `docker`, `npm`, `pypi`, `go`, `helm`, `node-version`.

The `modem7/renovate-config:shared` preset already ships two regex managers for `version:` and `*_VERSION:` values annotated with `# renovate: datasource=... depName=...` in `.github/workflows/` and `.woodpecker/` files.

## Dependency Dashboard
A GitHub/GitLab issue titled "Dependency Dashboard" lists every pending, open, rate-limited and errored update.
- Tick a box to force a PR now (bypasses schedule and rate limits) or to retry a failed one.
- Tick "Check this box to trigger a request for Renovate to run again" to rerun without waiting for the schedule.
- Detected dependencies are listed for debugging "why isn't it updating X?".
- Require approval for risky updates with `"dependencyDashboardApproval": true` in a `packageRules` entry (e.g. majors).

## Validating Config
```bash
npx --yes --package renovate -- renovate-config-validator            # checks the default config files
npx --yes --package renovate -- renovate-config-validator --strict   # also fails if the config needs migration
npx --yes --package renovate -- renovate-config-validator renovate.json
```
Passing a filename makes the validator treat it as global self-hosted config, so for a normal repo `renovate.json` run it with no filename. Run it in CI on PRs that touch the config, and as a pre-commit hook.

## Self-Hosted vs the Mend Renovate App
| | MEND RENOVATE APP (GitHub) | SELF-HOSTED |
|---|---|---|
| Setup | Install the GitHub app on repos | Run the `renovate/renovate` container or `npx renovate` on a schedule |
| Runs | Hosted by Mend | Your cron, GitHub Action, Woodpecker cron or K8s CronJob |
| Platforms | GitHub | GitHub, GitLab, Gitea/Forgejo ([[gitea]]), Bitbucket, Azure DevOps |
| Control | Per-repo config only | Global config, private registries, any schedule |
| Maintenance | None | You upgrade it and manage the token |

Self-hosted run with Docker ([[docker]]):
```bash
docker run --rm \
  -e RENOVATE_TOKEN="$RENOVATE_TOKEN" \
  -e RENOVATE_PLATFORM=gitea \
  -e RENOVATE_ENDPOINT=https://git.example.com/api/v1 \
  -e RENOVATE_AUTODISCOVER=true \
  -e LOG_LEVEL=debug \
  renovate/renovate:<VERSION>
```
VARIABLE | DESCRIPTION
---|---
`RENOVATE_TOKEN` | Bot account token (repo, PR and issue scopes)
`RENOVATE_PLATFORM` | `github`, `gitlab`, `gitea`, `bitbucket`, `azure` ...
`RENOVATE_ENDPOINT` | API URL for self-hosted forges
`RENOVATE_AUTODISCOVER` | Process every repo the token can access
`RENOVATE_REPOSITORIES` | Explicit list instead of autodiscover
`RENOVATE_GIT_AUTHOR` | Commit author, e.g. `Renovate Bot <bot@example.com>`
`RENOVATE_ONBOARDING_CONFIG` | Config PR content for new repos
`RENOVATE_GITHUB_COM_TOKEN` | A github.com token so changelogs and release lookups are not rate limited
`LOG_LEVEL` | `info`, `debug` (use `debug` when diagnosing)

Run it on a schedule from GitHub Actions with the official action (see [[github-actions]]) or from a Woodpecker cron job ([[woodpecker-ci]]) using the same container.

## Troubleshooting
SYMPTOM | CAUSE AND FIX
---|---
No onboarding PR | Repo not enabled for the app, or token lacks access; check the app's repo selection
Nothing updates | Outside `schedule`; rate limited (`prConcurrentLimit`); `enabledManagers` too narrow; look at the Dependency Dashboard and the debug log
Dependency not detected | No manager matches the file; add a custom manager or widen `managerFilePatterns`
Automerge never happens | Required checks not passing or not configured, branch protection blocks it, or `platformAutomerge` mismatch
PR created but CI does not run | Bot PRs from a GitHub Actions run with `GITHUB_TOKEN` do not trigger workflows; use a PAT/app token
Config error issue | Run the validator; a `packageRules` entry mixing conflicting options is a common cause
Version is not parsed (v-prefix, unusual tags) | Set `versioning` or `extractVersion` on a rule (see `modem7/renovate-config:shared` for the GitHub Actions v-prefix case)
Too many PRs at once | Set `prConcurrentLimit`, group with `groupName`, or schedule weekly
Wrong release proposed (unstable tag) | Set `allowedVersions` or `ignoreUnstable`, use `minimumReleaseAge`

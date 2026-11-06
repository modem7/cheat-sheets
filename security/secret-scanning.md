# Secret Scanning
Secret scanners find API keys, passwords and private keys in source code and Git history before an attacker does. This sheet covers gitleaks and TruffleHog (local and CI), pre-commit hooks, and GitHub's built-in secret scanning with push protection. Related: [Git](../tools/git.md), [GitHub and the gh CLI](../tools/github-cli.md), [SOPS and age](sops-age.md) for storing secrets safely, [Container Scanning](container-scanning.md) for images.

Documentation: [gitleaks](https://github.com/gitleaks/gitleaks) · [TruffleHog](https://github.com/trufflesecurity/trufflehog) · [GitHub secret scanning](https://docs.github.com/en/code-security/secret-scanning)

> If a secret was ever committed, treat it as compromised: **rotate it first**, then clean history. Deleting it in a later commit does not help.

## gitleaks
COMMAND | DESCRIPTION
---|---
`gitleaks git -v` | Scan the full Git history of the current repo
`gitleaks git --staged -v` | Scan only staged changes (pre-commit)
`gitleaks git --log-opts="--since=2025-01-01"` | Limit history with `git log` options
`gitleaks dir .` | Scan files on disk, ignoring Git
`gitleaks dir <PATH> --no-banner` | Scan a directory
`cat file \| gitleaks stdin` | Scan piped input
`gitleaks git --redact` | Hide secret values in the output
`gitleaks git -r report.json -f json` | Write a report (`json`, `csv`, `sarif`, `junit`)
`gitleaks git --baseline-path report.json` | Ignore findings already in an earlier report
`gitleaks git -c .gitleaks.toml` | Use a specific config
`gitleaks git --exit-code 0` | Don't fail the build (default is exit 1 on leaks)

Older versions (before 8.19) use `gitleaks detect` and `gitleaks protect --staged`; both still work as deprecated aliases.

### .gitleaks.toml
```toml
[extend]
useDefault = true            # keep built-in rules and add yours

[[rules]]
id = "internal-api-token"
description = "Internal API token"
regex = '''myco_[A-Za-z0-9]{32}'''
keywords = ["myco_"]

[allowlist]
description = "Global allowlist"
paths = [
  '''(^|/)tests?/fixtures/''',
  '''\.lock$''',
]
regexes = ['''EXAMPLE_KEY_[A-Z0-9]+''']
```
Ignore one specific finding by adding its fingerprint (printed in the report) to `.gitleaksignore`, or add `gitleaks:allow` as a comment on the offending line.

## TruffleHog
COMMAND | DESCRIPTION
---|---
`trufflehog git file://. --only-verified` | Scan local repo history, report only secrets confirmed live
`trufflehog git https://github.com/<ORG>/<REPO>.git` | Scan a remote repo
`trufflehog git file://. --since-commit <SHA> --branch HEAD` | Scan new commits only
`trufflehog github --org=<ORG>` | Scan every repo in a GitHub org
`trufflehog github --repo=https://github.com/<ORG>/<REPO>` | Scan one GitHub repo
`trufflehog filesystem <PATH>` | Scan files on disk
`trufflehog docker --image <IMAGE>` | Scan a container image
`trufflehog git file://. --fail` | Exit non-zero (183) if results found
`trufflehog git file://. --json` | JSON lines output
`trufflehog git file://. --no-update` | Skip the self-update check (CI)

`--only-verified` calls the provider API to check whether the credential is still valid, which means the key is sent to that provider. Drop it for an offline scan, at the cost of more false positives.

## pre-commit Hooks
Add to `.pre-commit-config.yaml` (install with `pip install pre-commit && pre-commit install`):
```yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: <TAG>                 # pin to a release tag, e.g. v8.x.y
    hooks:
      - id: gitleaks
  - repo: https://github.com/trufflesecurity/trufflehog
    rev: <TAG>
    hooks:
      - id: trufflehog
        args: ["--only-verified"]
```
COMMAND | DESCRIPTION
---|---
`pre-commit run --all-files` | Run every hook on the whole repo
`pre-commit run gitleaks --all-files` | Run one hook
`pre-commit autoupdate` | Bump `rev:` pins
`git commit --no-verify` | Bypass hooks (don't, unless it is a verified false positive)

Hooks are local and optional, so always back them with a CI check.

## CI (GitHub Actions)
```yaml
name: secrets
on: [push, pull_request]
jobs:
  gitleaks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@<SHA_OR_TAG>
        with:
          fetch-depth: 0              # full history, otherwise old leaks are missed
      - uses: gitleaks/gitleaks-action@<SHA_OR_TAG>
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
The gitleaks action requires a licence key for organisation-owned repos; for those, run the binary directly instead. Pin actions to a tag or commit SHA.

## GitHub Secret Scanning and Push Protection
Free for public repos; private repos need GitHub Secret Protection (GitHub Advanced Security). Push protection blocks a push containing a recognised secret.

Enable on a repository via the API:
```bash
gh api -X PATCH repos/<OWNER>/<REPO> --input - <<'EOF'
{"security_and_analysis":{
  "secret_scanning":{"status":"enabled"},
  "secret_scanning_push_protection":{"status":"enabled"}}}
EOF
```
COMMAND | DESCRIPTION
---|---
`gh api repos/<OWNER>/<REPO>/secret-scanning/alerts` | List alerts
`gh api repos/<OWNER>/<REPO>/secret-scanning/alerts --jq '.[] \| {number, secret_type, state}'` | Summarise alerts
`gh api -X PATCH repos/<OWNER>/<REPO>/secret-scanning/alerts/<N> -f state=resolved -f resolution=revoked` | Close an alert after rotating

When a push is blocked, GitHub prints the file and line. Remove the secret (`git commit --amend`, or `git rebase -i` for older commits) and push again. A bypass option exists ("it's used in tests", "false positive", "I'll fix it later") and is logged.

## Removing a Leaked Secret from History
```bash
pip install git-filter-repo
git filter-repo --replace-text expressions.txt     # lines like: literal:<LEAKED_VALUE>==>REDACTED
git push --force --all && git push --force --tags
```
Everyone with a clone must re-clone, and forks and caches (and GitHub pull-request refs) may still hold the old objects. Rotation is the only real fix.

## Troubleshooting
SYMPTOM | FIX
---|---
Too many false positives | Add paths or regexes to the `[allowlist]`; use `--baseline-path` to adopt the tool on an existing repo
Scan misses old leaks in CI | `fetch-depth: 0` on checkout
`gitleaks: unknown command "git"` | Old binary; upgrade, or use `gitleaks detect`
Findings print the secret in CI logs | Use `--redact`
TruffleHog is slow on big orgs | Narrow with `--repo`, `--since-commit`, or `--results=verified`

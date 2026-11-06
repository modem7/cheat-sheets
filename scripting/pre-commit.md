# pre-commit
`pre-commit` is a framework that runs linters and formatters on staged files before each `git commit`, using hooks pinned in a `.pre-commit-config.yaml` at the repo root. It catches problems locally, and the same config can run in CI. Hooks here cover shell ([ShellCheck and shfmt](shellcheck-shfmt.md)), Markdown, YAML and secrets. Git basics are in [Git](../tools/git.md).

Documentation: [pre-commit.com](https://pre-commit.com/), [supported hooks list](https://pre-commit.com/hooks.html)

## Install and Use
COMMAND | DESCRIPTION
---|---
`uv tool install pre-commit` | Install (or `pipx install pre-commit`, `pip install pre-commit`, `brew install pre-commit`)
`pre-commit --version` | Verify
`pre-commit install` | Install the git hook into `.git/hooks/pre-commit`
`pre-commit install --hook-type commit-msg` | Also install a hook for commit messages
`pre-commit run` | Run hooks on staged files
`pre-commit run --all-files` | Run on every file (do this first after adding hooks)
`pre-commit run <HOOK_ID>` | Run one hook
`pre-commit run <HOOK_ID> --all-files` | Run one hook everywhere
`pre-commit run --files <FILE>...` | Run on specific files
`pre-commit run --from-ref origin/master --to-ref HEAD` | Run on files changed in a branch (CI)
`pre-commit autoupdate` | Bump every `rev` to the latest tag
`pre-commit autoupdate --repo <REPO_URL>` | Bump one repo
`pre-commit autoupdate --freeze` | Pin to commit SHAs instead of tags
`pre-commit clean` | Delete cached hook environments
`pre-commit gc` | Remove unused cached repos
`pre-commit uninstall` | Remove the git hook
`git commit --no-verify` | Skip hooks for one commit (emergencies only)
`SKIP=<HOOK_ID> git commit -m "msg"` | Skip specific hooks, comma-separated

When a hook modifies files, the commit is aborted. Review the changes, `git add` them and commit again.

## Config Reference
```yaml
# .pre-commit-config.yaml
default_install_hook_types: [pre-commit, commit-msg]
default_stages: [pre-commit]
fail_fast: false
exclude: ^(vendor/|\.venv/)

repos:
  - repo: <REPO_URL>
    rev: <TAG_OR_SHA>
    hooks:
      - id: <HOOK_ID>
        args: [--option]
        files: \.sh$
        exclude: ^legacy/
        types: [shell]
        additional_dependencies: []
```
KEY | DESCRIPTION
---|---
`repo` | Git repository containing the hook (or `local` / `meta`)
`rev` | Tag or commit SHA to use; pin it, never use a branch name
`id` | Which hook from the repository
`args` | Extra command-line arguments
`files` / `exclude` | Regex filters on file paths
`types` / `types_or` | Filter by file type (`python`, `shell`, `yaml`, `markdown`)
`stages` | `pre-commit`, `pre-push`, `commit-msg`, `manual`
`pass_filenames` | Set `false` for hooks that scan the whole repo
`always_run` | Run even when no matching file changed
`verbose` | Print hook output even on success

## Example Config
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
        args: [--allow-multiple-documents]
      - id: check-merge-conflict
      - id: check-added-large-files
      - id: detect-private-key
      - id: check-executables-have-shebangs
      - id: check-shebang-scripts-are-executable

  - repo: https://github.com/shellcheck-py/shellcheck-py
    rev: v0.11.0.1
    hooks:
      - id: shellcheck
        args: [-x]

  - repo: https://github.com/scop/pre-commit-shfmt
    rev: v3.14.1-1
    hooks:
      - id: shfmt
        args: [-i, "2", -ci]

  - repo: https://github.com/igorshubovych/markdownlint-cli
    rev: v0.50.0
    hooks:
      - id: markdownlint
        args: [--fix]

  - repo: https://github.com/adrienverge/yamllint
    rev: v1.38.0
    hooks:
      - id: yamllint
        args: [-c, .yamllint.yml]

  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.30.1
    hooks:
      - id: gitleaks
```
The `rev` values above are examples from the time of writing. Run `pre-commit autoupdate` to move them to current releases and let Renovate keep them fresh (it supports pre-commit configs).

HOOK | PURPOSE
---|---
`pre-commit-hooks` | Whitespace, EOF newline, YAML/JSON syntax, merge-conflict markers, large files, private keys
`shellcheck-py` | ShellCheck without a system install
`pre-commit-shfmt` | shfmt without a system install
`markdownlint-cli` | Markdown style (config in `.markdownlint.yaml`)
`yamllint` | YAML style (config in `.yamllint.yml`)
`gitleaks` | Secret scanning of staged changes

Related config files:
```yaml
# .yamllint.yml
extends: default
rules:
  line-length: disable
  truthy: { check-keys: false }
  document-start: disable
```
```yaml
# .markdownlint.yaml
default: true
MD013: false     # line length
MD033: false     # inline HTML
MD041: false     # first line heading
```

## Local Hooks
Run any command already in your repo as a hook:
```yaml
  - repo: local
    hooks:
      - id: compose-config
        name: docker compose config
        entry: docker compose -f compose.yml config -q
        language: system
        files: ^compose\.ya?ml$
        pass_filenames: false
```
`language: system` uses whatever is on `PATH`; other languages (`python`, `node`, `docker`, `script`) build their own environment.

## CI
```yaml
# GitHub Actions
name: pre-commit
on: [push, pull_request]
jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - uses: pre-commit/action@v3.0.1
```
```yaml
# Woodpecker CI
steps:
  - name: pre-commit
    image: python:3.12
    commands:
      - pip install pre-commit
      - pre-commit run --all-files --show-diff-on-failure
```
`--show-diff-on-failure` prints what a fixing hook changed. Cache `~/.cache/pre-commit` between runs to save time.

## Tips
- Run `pre-commit run --all-files` once when adding a new hook, and commit the resulting fixes on their own.
- Use `stages: [manual]` for slow hooks and run them with `pre-commit run --hook-stage manual`.
- `gitleaks` only finds secrets in what you commit; rotate any secret that has ever been pushed.
- A hook failing in CI but not locally usually means different hook versions or a missing `pre-commit install`.
- See also [Bash Recipes](bash-recipes.md) for the scripts that local hooks often call.

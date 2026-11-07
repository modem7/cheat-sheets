# Cloudsmith CLI
The Cloudsmith CLI manages packages and repositories on Cloudsmith, a hosted package and container registry. Use it to push and promote packages, manage entitlement tokens and script CI uploads.

Documentation: [Cloudsmith CLI](https://docs.cloudsmith.com/developer-tools/cli) · [Package upload](https://docs.cloudsmith.com/artifact-management/package-upload) · [Entitlement tokens via the CLI](https://docs.cloudsmith.com/software-distribution/entitlement-tokens-via-the-cloudsmith-cli)
Project: [cloudsmith-io/cloudsmith-cli](https://github.com/cloudsmith-io/cloudsmith-cli)

> **Verification:** install, authentication, push and entitlement commands were checked against the Cloudsmith docs and the CLI source (November 2026). The CLI was not installed or run. Flags marked *(source only)* appear in the source but not the docs. Items marked *(unverified)* were not confirmed. Related: [Docker Registry](../docker/docker-registry.md), [AWS CLI](aws-cli.md), [GitHub and the gh CLI](github-cli.md).

## Install
COMMAND | DESCRIPTION
---|---
`python3 -m pip install --upgrade cloudsmith-cli` | Install with pip (extras `[aws]` and `[gcp]` exist for OIDC)
`curl -fsSL https://install.cloudsmith.com/raw/versions/latest/cli.sh \| sh` | Install script for Linux and macOS (read it before piping to a shell)
`brew install cloudsmith-io/cloudsmith-cli/cloudsmith-cli` | Homebrew (see [Homebrew](../macos/homebrew.md))
`docker run --rm -e CLOUDSMITH_API_KEY=<API_KEY> cloudsmith/cloudsmith-cli:<VERSION> whoami` | Run from the container image
`cloudsmith --version` | Check the version *(unverified)*

Binaries are also on the GitHub releases page. `pipx` and `uv` installs are not documented by Cloudsmith.

## Authentication
COMMAND | DESCRIPTION
---|---
`export CLOUDSMITH_API_KEY=<API_KEY>` | Authenticate with an API key (or `-k` / `--api-key`)
`cloudsmith auth --workspace <SLUG>` | Browser-based SSO login (`--no-browser` to print the URL)
`cloudsmith whoami` | Show who you are (exit code 0 if authenticated, 1 if anonymous)
`cloudsmith logout` | Remove stored credentials
`cloudsmith login` | Deprecated alias of `tokens`; stops working on 2026-11-20

The API key can also be stored as `api_key` in `credentials.ini`.

CI with OIDC: set `CLOUDSMITH_WORKSPACE` and `CLOUDSMITH_SERVICE_SLUG`, then run `cloudsmith whoami`. Supported providers: GitHub, GitLab, CircleCI, Azure DevOps, Bitbucket, Buildkite, AWS, GCP and generic. Prefer this over long-lived keys.

## Configuration and Global Flags
The CLI reads `config.ini` and `credentials.ini` from the working directory, then `~/.config/cloudsmith` or `~/.cloudsmith` on Linux. Files use INI sections `[default]` or `[profile:NAME]`.

FLAG | DESCRIPTION
---|---
`-P` / `--profile <NAME>` | Use a profile (`CLOUDSMITH_PROFILE`)
`-F` / `--output-format <FORMAT>` | `pretty`, `json` or `pretty_json`
`-v` | Verbose output
`-C` / `--config-file <FILE>` | Alternative config file
`--credentials-file <FILE>` | Alternative credentials file
`-w` / `--workspace <SLUG>` | Workspace
`--proxy <URL>` | Use a proxy
`-R` / `--without-rate-limit` | Skip rate-limit handling
`-l`, `-p`, `--page-all` | Paging on `list` commands

Repositories are identified as `OWNER/REPO`, and packages as `OWNER/REPO/ID`.

## Push
COMMAND | DESCRIPTION
---|---
`cloudsmith push <FORMAT> <OWNER>/<REPO> <FILE>` | Upload a package
`cloudsmith push deb <OWNER>/<REPO>/<DISTRO>/<VERSION> <FILE>.deb --tags <TAG1>,<TAG2>` | Upload a Debian package for a distribution and version
`cloudsmith push python <OWNER>/<REPO> <FILE>` | Upload a Python package
`cloudsmith push docker ...` | Docker push exists in the CLI; exact usage *(unverified)*
`--republish` | Overwrite an existing package version (documented)
`--dry-run` | Check without uploading *(source only)*
`-s` / `--skip-errors`, `-W` / `--no-wait-for-sync`, `-I` / `--wait-interval`, `--sync-attempts` | Control error handling and waiting *(source only)*

## List, Inspect and Manage
COMMAND | DESCRIPTION
---|---
`cloudsmith list repos` | List repositories (`repositories` is the full name)
`cloudsmith list packages <OWNER>/<REPO> --query <QUERY> --sort <FIELD>` | List and search packages
`cloudsmith list entitlements <OWNER>/<REPO>` | List entitlement tokens
`cloudsmith list distros` / `cloudsmith list dependencies` | Other listings
`cloudsmith status <OWNER>/<REPO>/<ID>` | Show sync status of a package
`cloudsmith copy <OWNER>/<REPO>/<ID> <DEST_REPO>` | Copy a package to another repository (alias `cp`)
`cloudsmith move <OWNER>/<REPO>/<ID> <DEST_REPO>` | Move or promote a package (aliases `mv`, `promote`)
`cloudsmith delete <OWNER>/<REPO>/<ID>` | Delete a package (destructive, alias `rm`)
`cloudsmith tags list\|add\|clear` | Manage package tags
`cloudsmith quarantine add\|remove` | Quarantine or release a package
`cloudsmith resync <OWNER>/<REPO>/<ID>` | Resync a package
`cloudsmith download` | Download packages *(arguments unverified)*
`cloudsmith check rates` / `cloudsmith check service` | Check API rate limits or service status
`cloudsmith metrics` / `cloudsmith quota` | Usage metrics and quota
`cloudsmith tokens list\|create` | List or create API tokens

Other top-level commands present in the CLI: `dependencies`, `docs`, `domains`, `mcp`, `metadata`, `policy`, `update`, `upstream`, `vulnerabilities`, `credential-helper`, `help`.

Use `-F json` with [jq](jq.md) for scripting, for example `cloudsmith list packages -F json <OWNER>/<REPO> | jq '.data[].name'` *(output shape unverified)*.

## Entitlement Tokens
Entitlement tokens give read-only access to a repository for installing packages without full credentials.

COMMAND | DESCRIPTION
---|---
`cloudsmith ents list <OWNER>/<REPO>` | List tokens (`ents` is short for `entitlements`)
`cloudsmith ents create <OWNER>/<REPO> --name <NAME>` | Create a token
`cloudsmith ents refresh <OWNER>/<REPO>/<ID>` | Regenerate a token
`cloudsmith ents sync <OWNER>/<TARGET> <SOURCE>` | Sync tokens from a source repository
`cloudsmith ents delete <OWNER>/<REPO>/<ID>` | Delete a token (destructive)

## Docker Registry Login
The registry host is `docker.cloudsmith.io`. With an entitlement token the username is `<OWNER>/<REGISTRY>` and the password is the token; with a service account the username is its name and the password its token. Source: [Docker registry format](https://docs.cloudsmith.com/formats/docker-registry). The exact command below is inferred from that page *(unverified)*:

```bash
echo "$CLOUDSMITH_TOKEN" | docker login docker.cloudsmith.io -u USERNAME --password-stdin
```

See [Docker Registry](../docker/docker-registry.md) for general registry usage. pip, npm and apt client setup and plan limits were not checked.

## Troubleshooting
SYMPTOM | FIX
---|---
`cloudsmith whoami` shows anonymous | Set `CLOUDSMITH_API_KEY` or run `cloudsmith auth`
`login` command warns or fails | Use `auth` or API keys; `login` is deprecated
Push fails with a version conflict | Use `--republish` or bump the version
Rate limited | Check `cloudsmith check rates`

## See Also
- [Docker Registry](../docker/docker-registry.md)
- [AWS CLI](aws-cli.md)
- [GitHub and the gh CLI](github-cli.md)
- [jq](jq.md)
- [Homebrew](../macos/homebrew.md)

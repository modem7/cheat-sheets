# Contributing
How to add or change a cheat sheet. Start from [`_template.md`](_template.md) and look at existing sheets such as `tools/jq.md`, `docker/docker-compose.md` and `tools/helm.md` for the house style. AI coding agents should also read `AGENTS.md` in the repo root.

## House Style
- **One topic per file.** A sheet covers one tool or subject. Split it if it grows into two.
- **Title.** The first line is a single `# Title`. Keep it short, e.g. `# jq`.
- **Intro.** One or two sentences straight after the title: what it is and when to use it.
- **Links.** Optional `Documentation:` and `Project:` lines with links to the official docs or site, placed right after the intro.
- **Sections.** Use `##` headings, one per task or area, e.g. `## Options`, `## Install and Upgrade`.
- **Tables.** Commands go in `COMMAND | DESCRIPTION` tables (or `OPTION`, `FILTER`, `FIELD` as the first header where it fits). Put the command or option in backticks. Escape a literal pipe inside a cell as `\|`.
- **Code blocks.** Multi-line commands and config go in fenced blocks with a language tag (`bash`, `yaml`, `json`, `ini`, `powershell`, `text`).
- **Placeholders.** Write anything the reader must replace in ALL CAPS or `<ANGLE_BRACKETS>`, e.g. `<HOST>`, `CONTAINER`, `API_TOKEN`.
- **Links between sheets.** Use standard relative Markdown links with the `.md` extension, e.g. `[Docker Compose](docker-compose.md)` in the same folder or `[Docker](../docker/docker.md)` from another folder. Use the target's H1 as the link text. Link to a heading with a GitHub-style anchor, e.g. `[Compose files](docker-compose.md#compose-files)`. Do not use `[[wikilinks]]`: the checker rejects them outside code spans and fences, and they do not work on GitHub or the Hugo site.
- **Links must resolve.** Relative paths must exist, and `#anchor` fragments on `.md` links must match a heading in the target.
- **No empty stubs.** Do not commit a file that is empty or only a title. Add the sheet when it has content.
- **File names.** Lower-case kebab-case, ending in `.md`, e.g. `docker-compose.md`. The only exceptions are `README.md`, `CONTRIBUTING.md` and `AGENTS.md`.
- **Language.** British English, plain and terse. Prefer a table row over a paragraph.

## Which Folder
FOLDER | WHAT GOES THERE
---|---
`apps/` | Self-hosted applications and services (Traefik, Grafana, Tailscale)
`backup/` | Backup tools and strategies
`cicd/` | CI/CD systems and pipelines
`cloud/` | Cloud concepts and provider comparisons
`databases/` | Database engines and their CLIs
`docker/` | Docker, Dockerfile, Compose, container networking
`homelab/` | Homelab design, services and operations
`infra/` | Infrastructure platforms and appliances
`kubernetes/` | Kubernetes, K3s, kubectl and cluster tooling
`linux/` | Linux commands, shell utilities, firewall, storage
`macos/` | macOS-specific tools and shortcuts
`misc/` | Reference material that fits nowhere else (status codes, colour codes, Markdown)
`networking/` | Protocols, DNS, TLS, VPN, mail records
`proxmox/` | Proxmox VE
`recipes/` | End-to-end task pages that combine several sheets
`scripting/` | Shell, Python and other scripting references
`security/` | Hardening, scanning, secrets and identity tooling
`tools/` | General command-line tools, Git hosts, IaC, editors and desktop apps
`windows/` | Windows and PowerShell

### Where New Sections Go
Add a new top-level folder only when you have several sheets for a theme that none of the folders above fits, for example `security/`, `backup/`, `scripting/`, `homelab/`, `cicd/` or `recipes/`. Use a short lower-case name, add the folder and its sheets in the same PR, and add the section to the README index. A single sheet goes into the closest existing folder instead.

## Content Rules
- **Verify facts.** Check every command, flag and default against the official documentation or by running it. Do not invent commands or flags. If something cannot be verified, say so in the sheet (for example `(unverified)`) rather than guessing.
- **Pin the version** when behaviour differs between major versions (for example Helm 3, Compose v2).
- **No secrets.** Never commit passwords, tokens, keys, private hostnames, real public IP addresses or personal domains. Use placeholders and documentation ranges such as `192.0.2.0/24`, `198.51.100.0/24` and `example.com`.
- **Mark destructive commands.** Say in the description when a command deletes data.

## Adding a Sheet
1. Create a branch off an up-to-date `master`.
2. Copy `docs/_template.md` to the right folder with a kebab-case name and fill it in.
3. Regenerate the `README.md` index: `python3 scripts/gen-index.py`.
4. Add relative links to and from related sheets.
5. Run the checks below.
6. Open a pull request. Do not push to `master`.

## Checks
CI runs these checks on every pull request and on pushes to `master` (`.github/workflows/lint.yml`). Run them locally first.

```bash
# Relative links and anchors, leftover wikilinks and empty files (Python 3, no dependencies)
python3 scripts/check-links.py

# README index is up to date (use without --check to regenerate it)
python3 scripts/gen-index.py --check

# Markdown style (needs Node.js)
npx markdownlint-cli2 "**/*.md"

# No real-looking public IPv4 addresses (Python 3, no dependencies)
python3 scripts/check-ips.py
```

A separate workflow (`.github/workflows/secret-scan.yml`) also runs gitleaks over the full history and the IP check. The IP check allows the documentation ranges, loopback, private and CGNAT ranges, netmasks and a few well-known public DNS resolvers. For anything else, use a placeholder. If a match is genuinely not an address (a version string, say), add it to `.ip-allowlist` with a comment, or put `ip-scan: ignore` on that line.

Configuration lives in `.markdownlint-cli2.yaml`. Fix the content rather than loosening a rule; if a rule is genuinely wrong for this repo, change the config in its own PR and explain why.

## Issue Forms
Not ready to write a sheet? Open an issue with one of the forms in `.github/ISSUE_TEMPLATE/`: **Request a sheet** to suggest a tool or topic, or **Report an error** for a wrong command, flag, default or link. Blank issues are disabled.

## External Link Check
A weekly workflow (`.github/workflows/external-links.yml`, config in `.lychee.toml`) checks every `http(s)` link with [lychee](https://github.com/lycheeverse/lychee). It does not run on pull requests. When it finds broken links it opens or updates one issue titled "Broken external links"; fix the links in a PR. Run it locally with `lychee --config .lychee.toml "**/*.md"` (or the `lycheeverse/lychee` Docker image).

## Freshness Check
A monthly workflow (`.github/workflows/freshness.yml`) runs `scripts/check-freshness.py` and, when sheets have not been touched for over 12 months, opens or updates one issue titled "Stale sheets to re-verify". Re-check the listed sheets against the official docs and commit any fix; a commit resets a sheet's age. Mechanical mass edits (link conversions, reformatting) should be listed in `.freshness-ignore-revs` so they do not make every sheet look freshly reviewed. The same dates drive the website's "Updated" date and "May be out of date" chip (see `site/SITE.md`). Run it locally with `python3 scripts/check-freshness.py --months 12 --format text` (needs full git history).

## PR Templates
Opening a pull request fills in `.github/PULL_REQUEST_TEMPLATE.md`. For sheet changes, add a query parameter to the PR URL to use a dedicated template (`https://github.com/modem7/cheat-sheets/compare/master...BRANCH?template=new-sheet.md`):

TEMPLATE | USE FOR
---|---
`new-sheet.md` | Adding a new sheet
`update-sheet.md` | Changing an existing sheet
default | Everything else (fixes, repo and CI changes)

## PR Checklist
- [ ] One topic per file, kebab-case file name, correct folder
- [ ] Title, intro, and a documentation link where one exists
- [ ] Commands in `COMMAND | DESCRIPTION` tables, code blocks have a language
- [ ] Placeholders in ALL CAPS, no secrets, real IPs or personal domains
- [ ] Commands and flags verified against official docs; unverified items marked
- [ ] Relative links resolve and related sheets link back; no `[[wikilinks]]`
- [ ] `README.md` index regenerated for new sheets
- [ ] `python3 scripts/check-links.py`, `python3 scripts/gen-index.py --check` and `npx markdownlint-cli2 "**/*.md"` pass

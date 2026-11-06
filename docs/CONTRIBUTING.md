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
- **Wikilinks.** Cross-link sheets with `[[basename]]`, where the basename is the file name without `.md` (e.g. `[[docker-compose]]`). `[[name|alias]]` and `[[name#heading]]` are fine. Wikilinks resolve by basename anywhere in the repo, so basenames must be unique. Inside code spans and fences they are ignored.
- **Plain Markdown links** (`[text](path.md)`) must use relative paths that exist.
- **No empty stubs.** Do not commit a file that is empty or only a title. Add the sheet when it has content.
- **File names.** Lower-case kebab-case, ending in `.md`, e.g. `docker-compose.md`. The only exceptions are `README.md`, `CONTRIBUTING.md` and `AGENTS.md`.
- **Language.** British English, plain and terse. Prefer a table row over a paragraph.

## Which Folder
FOLDER | WHAT GOES THERE
---|---
`apps/` | Self-hosted applications and services (Traefik, Grafana, Tailscale)
`cloud/` | Cloud concepts and provider comparisons
`databases/` | Database engines and their CLIs
`docker/` | Docker, Dockerfile, Compose, container networking
`infra/` | Infrastructure platforms and appliances
`kubernetes/` | Kubernetes, K3s, kubectl and cluster tooling
`linux/` | Linux commands, shell utilities, firewall, storage
`macos/` | macOS-specific tools and shortcuts
`misc/` | Reference material that fits nowhere else (status codes, colour codes, Markdown)
`networking/` | Protocols, DNS, TLS, VPN, mail records
`proxmox/` | Proxmox VE
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
3. Add the sheet to the index in `README.md`.
4. Add wikilinks to and from related sheets.
5. Run the checks below.
6. Open a pull request. Do not push to `master`.

## Checks
CI runs the same two checks on every pull request and on pushes to `master` (`.github/workflows/lint.yml`). Run them locally first.

```bash
# Wikilinks, relative links, empty files and duplicate basenames (Python 3, no dependencies)
python3 scripts/check-links.py

# Markdown style (needs Node.js)
npx markdownlint-cli2 "**/*.md"
```

Configuration lives in `.markdownlint-cli2.yaml`. Fix the content rather than loosening a rule; if a rule is genuinely wrong for this repo, change the config in its own PR and explain why.

## PR Checklist
- [ ] One topic per file, kebab-case file name, correct folder
- [ ] Title, intro, and a documentation link where one exists
- [ ] Commands in `COMMAND | DESCRIPTION` tables, code blocks have a language
- [ ] Placeholders in ALL CAPS, no secrets, real IPs or personal domains
- [ ] Commands and flags verified against official docs; unverified items marked
- [ ] Wikilinks resolve and related sheets link back
- [ ] `README.md` index updated for new sheets
- [ ] `python3 scripts/check-links.py` and `npx markdownlint-cli2 "**/*.md"` pass

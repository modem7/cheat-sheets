# AGENTS.md
Guidance for AI coding agents working in this repository. Human contributors should read `docs/CONTRIBUTING.md`; this file is the single source of truth for agents.

## Purpose
A personal homelab and DevOps knowledge base: Markdown cheat sheets with quick-scan command tables for tools, platforms and concepts. There is no build step and no application code, only Markdown plus a small link checker and CI config.

## Layout
- One folder per theme (`linux/`, `docker/`, `kubernetes/`, `networking/`, `tools/`, `apps/`, and others; new themed folders such as `security/` or `backup/` appear over time). One sheet per file.
- `README.md`: intro and the generated sheet index, grouped by folder.
- `docs/CONTRIBUTING.md` and `docs/_template.md`: house style and a starting template. Folder choice guide is in CONTRIBUTING.
- `scripts/check-links.py`: link, anchor and file checker.
- `scripts/gen-index.py`: generates the `README.md` index (`--check` in CI).
- `.markdownlint-cli2.yaml`, `.github/workflows/lint.yml`: CI checks.

## House Style
- First line `# Title`, then a one or two sentence intro, then optional `Documentation:` and `Project:` link lines.
- `##` sections. Commands in `COMMAND | DESCRIPTION` tables with the command in backticks (escape literal pipes as `\|`).
- Multi-line commands and config in fenced blocks with a language tag.
- Placeholders in ALL CAPS or `<ANGLE_BRACKETS>`.
- Cross-link with relative Markdown links including `.md` (e.g. `[Docker](../docker/docker.md)`), link text is the target's H1. Never use `[[wikilinks]]`.
- Kebab-case file names. No empty or title-only files.
- British English, terse.

## Rules
1. Never invent commands, flags, options or defaults. Verify against the official documentation (or by running the command) before writing it.
2. Mark anything you could not verify as unverified in the sheet, and say so in the PR description.
3. No secrets, tokens, real IP addresses, internal hostnames or personal domains. Use placeholders, `example.com` and documentation ranges (`192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`).
4. Keep every relative link and `#anchor` valid. When you rename or delete a sheet, fix the links that point to it.
5. When you add a sheet, regenerate the `README.md` index (`python3 scripts/gen-index.py`), and update any site or content list the repository keeps, in the same PR.
6. Edit only what the task requires. Do not reformat unrelated sheets.
7. Run all three checks before opening a PR and fix what they report in the content, not by loosening the config:
   - `python3 scripts/check-links.py`
   - `python3 scripts/gen-index.py --check`
   - `npx markdownlint-cli2 "**/*.md"`
8. Work on a branch and open a pull request. Never push to `master`. Do not change repository settings or branch protection.
9. Do not edit `renovate.json` or the shared preset it extends.
10. Keep temporary files outside the repository.

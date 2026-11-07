## Update to an existing sheet
<!-- House style is in docs/CONTRIBUTING.md. Edit only what this change needs. -->

**Sheet(s):** <!-- e.g. docker/docker-compose.md -->
**Official docs checked:**

## What changed and why
<!-- Added commands, corrected flags, new version behaviour, removed content. -->

## Checklist
- [ ] Only the lines this change needs are touched; no unrelated reformatting
- [ ] Every new or changed command, flag and default checked against the official docs or by running it
- [ ] Anything unverified is marked `(unverified)`
- [ ] New commands follow the `COMMAND | DESCRIPTION` table style; fenced blocks have a language tag
- [ ] Version noted where behaviour differs between major versions
- [ ] No secrets, real IP addresses or personal domains
- [ ] If a sheet was renamed, retitled or removed: links to it are fixed and the `README.md` index regenerated with `python3 scripts/gen-index.py`
- [ ] `python3 scripts/check-links.py`, `python3 scripts/gen-index.py --check` and `npx markdownlint-cli2 "**/*.md"` pass

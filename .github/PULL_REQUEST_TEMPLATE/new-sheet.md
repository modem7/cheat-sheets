## New sheet
<!-- Start from docs/_template.md. House style is in docs/CONTRIBUTING.md. -->

**Tool or topic:**
**File:** <!-- e.g. tools/jq.md (lower-case kebab-case, correct folder) -->
**Version covered:** <!-- Only if behaviour differs between major versions -->
**Official docs:**

## Summary
<!-- What the tool is and why it belongs here. -->

## Sheet checklist
- [ ] One topic per file, kebab-case name, in the right folder (see "Which Folder" in `docs/CONTRIBUTING.md`)
- [ ] `# Title`, one or two sentence intro, then `Documentation:` and `Project:` links where they exist
- [ ] Commands in `COMMAND | DESCRIPTION` tables; fenced blocks have a language tag
- [ ] Placeholders in ALL CAPS or `<ANGLE_BRACKETS>`
- [ ] Relative links to related sheets, and related sheets link back; no `[[wikilinks]]`
- [ ] Not empty or title-only
- [ ] British English, plain and terse

## Accuracy
- [ ] Every command, flag and default checked against the official docs or by running it
- [ ] Anything I could not verify is marked `(unverified)` in the sheet
- [ ] Destructive commands say so in their description

## Safety
- [ ] No passwords, tokens, keys, private hostnames, real public IPs or personal domains (use `example.com` and `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`)

## Checks
- [ ] `python3 scripts/gen-index.py` run, and the updated `README.md` index is included
- [ ] `python3 scripts/check-links.py` passes
- [ ] `python3 scripts/gen-index.py --check` passes
- [ ] `npx markdownlint-cli2 "**/*.md"` passes

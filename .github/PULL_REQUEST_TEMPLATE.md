## What does this change?
<!-- One or two sentences. -->

## Type of change
<!-- Tick one. For a new or updated sheet, use the dedicated template instead:
     add ?template=new-sheet.md or ?template=update-sheet.md to the PR URL. -->
- [ ] New sheet
- [ ] Update to an existing sheet
- [ ] Fix (typo, broken link, wrong command)
- [ ] Repo, CI or tooling change

## Checklist
- [ ] `python3 scripts/check-links.py` passes
- [ ] `python3 scripts/gen-index.py --check` passes (regenerate with `python3 scripts/gen-index.py` if a sheet was added, renamed or retitled)
- [ ] `npx markdownlint-cli2 "**/*.md"` passes
- [ ] No secrets, real IP addresses or personal domains
- [ ] Commands and flags verified against official docs; anything unverified is marked in the sheet

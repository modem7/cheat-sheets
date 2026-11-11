@AGENTS.md

## Design tooling

- The `impeccable` design plugin is enabled in this repository only (`.claude/settings.json`). It is off in the global settings.
- It applies to the **site theme only**: `site/assets/css/` (`main.css`, `syntax.css`), `site/assets/js/main.js`, `site/layouts/` and `site/static/`. Not the cheat-sheet Markdown or the checker scripts.
- Its edit hook scans `.html`, `.css` and `.js` after an edit. The only such files in the repo are under `site/`; Hugo output (`site/public/`, `site/.build/`) is git-ignored and is never edited by hand.
- Colour tokens must keep 4.5:1 contrast in both themes (see `site/SITE.md`).
- Adoption only: no design command has been run. Its files (`PRODUCT.md`, `DESIGN.md`, `.impeccable/`) do not exist until `/impeccable init`. Runtime files in `.impeccable/` are in `.gitignore`; shared ones stay tracked.
- To turn it off: remove `impeccable@impeccable` from `enabledPlugins`, or set `hook.enabled` to `false` in `.impeccable/config.json`.

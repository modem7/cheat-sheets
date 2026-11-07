# Cheat Sheets website

A [Hugo](https://gohugo.io/) site that publishes the Markdown sheets in this repository to
<https://modem7.github.io/cheat-sheets/>. Authoring stays exactly as before: plain Markdown
files in topic folders at the repo root. Nothing under `site/` needs touching to add or edit a sheet.

## Local preview

You need Hugo **extended** (CI pins `0.169.0`) and Python 3. Run from the repo root:

```bash
./site/scripts/dev.sh
```

That builds the content once, watches the sheets for changes and starts `hugo server` on
<http://localhost:1313/>. Equivalent by hand:

```bash
python3 site/scripts/prepare-content.py --watch &
hugo server --source site
```

Search uses [Pagefind](https://pagefind.app/), which indexes the built HTML, so it is not available
under `hugo server`. To try it locally:

```bash
python3 site/scripts/prepare-content.py
hugo --source site --minify --baseURL http://localhost:8000/
npx --yes pagefind@1.6.0 --site site/public
python3 -m http.server --directory site/public 8000
```

## How content is mounted

Sheets have no front matter (and Hugo needs a content directory of its own), so a small script
sits in front of Hugo:

1. `site/scripts/prepare-content.py` walks the repo, discovers **every folder containing `.md` files**
   (no folder list anywhere), and writes transformed copies to `site/.build/content/` (git-ignored).
   Skipped: dot-folders, `site/`, `node_modules/` and `.md` files in the repo root (the generated home
   page replaces the root `README.md`).
2. `site/hugo.toml` mounts `site/.build/content` as Hugo's `content` directory, and mounts the repo
   root as `static` for linked assets (PDFs, images, anything under an `assets/` folder), so
   `linux/assets/awk.cheat.sheet.pdf` is served at the same path.

The script adds front matter to each copy: `title` from the first `# H1`, `description` from the first
paragraph, and `weight: 1` for the lead sheet of a folder (the one named after the folder, e.g.
`docker/docker.md`) so it sorts first. A sheet that already has front matter keeps it. Your source files are
never modified.

Each top-level folder becomes a **section**: it gets a sidebar group, a page count on the home page, a
section page and prev/next navigation. Subfolders (e.g. `cloud/provider/`) are shown under their top-level
section.

## Links

Sheets link to each other with ordinary relative Markdown links, e.g. `[Sed](sed.md)` or
`[Docker](../docker/docker.md#build-images)`. `layouts/_default/_markup/render-link.html` resolves them
to the published page URL (correct for the Pages sub-path), keeps `#anchors`, and serves non-Markdown
files such as PDFs from their repo path. A link to a missing sheet renders as dotted red text with a
warning mark and prints `WARN broken link "x" in <file>` in the Hugo build log. `scripts/check-links.py`
checks the same links in CI.

GitHub-style callouts (`> [!NOTE]`, `> [!attention]`, `> [!INFO] Custom title`) are rendered as coloured
callout boxes by `render-blockquote.html`. Unknown types fall back to the "note" style.

## Search and navigation

All vanilla JS in `assets/js/main.js`; the pages work without it. Search, its chips and highlighting need the
Pagefind build (see Local preview), and the table marker comes from `layouts/_default/_markup/render-table.html`.

- **Search** (Pagefind in a dialog): open with `/` or `Ctrl`/`Cmd`+`K`. Each sheet is indexed with a `section`
  filter (`data-pagefind-filter` in `single.html`); the dialog shows one chip per section (taken from the
  sidebar) and the built-in Pagefind filter panel is hidden. Selected chips are OR-ed. The last five searches
  are kept in `localStorage` (`recent-searches`) and shown as chips while the box is empty, with a Clear button.
  Result links carry `?highlight=term`; on the destination page the script loads `pagefind/pagefind-highlight.js`
  and marks the terms, with a "Clear highlights" link.
- **Sidebar**: a filter box over sheet titles (matching sections open, others hide, the previous open/closed
  state returns when cleared; Enter follows the first match, Esc clears) and a Collapse all / Expand all button. Open sections are remembered in
  `localStorage` (`nav-sections`); the current sheet's section always opens.
- **Click-to-copy**: in a table whose first header is `Command`, clicking the first-column cell copies the
  command (the single `code` element if there is one, otherwise the cell text). Links are left alone, a double
  or triple click or an existing text selection selects instead of copying, and the result is announced through
  the `#live` polite live region. Mouse and touch only: keyboard users have the Copy button on code blocks.

Storage access is always wrapped in `try`/`catch`, so blocked storage only means nothing is remembered.

## Accessibility and mobile

- Checked with axe-core (WCAG 2.2 A/AA plus best practices) in dark and light, at 1440px and 390px, on the
  home page, a section page and several sheets: 0 violations at the time of writing. To repeat it, install
  `axe-core` somewhere outside the repo, open a built page in Playwright, inject `axe.min.js` and call `axe.run()`.
  Colour tokens (`--accent-text` in `main.css`, `--t-comment` in `syntax.css`) are chosen to keep 4.5:1 in both themes; keep
  that in mind when changing the palette. Skip link, `:focus-visible` rings, `scroll-padding-top` for
  in-page anchors, `forced-colors`, reduced-motion and print rules are unchanged.
- Each table is a labelled scroll region (`Table N`, N = its position on the page), so landmarks stay unique.
- Up to 1180px wide, with JS, "On this page" is a floating button (bottom left) that opens a sheet with the
  contents; it closes on a link click, an outside click or Esc, and is hidden while the navigation drawer is
  open. The `js` class on `<html>` (set in `head.html`) gates this, so without JS the collapsed in-flow box
  remains.
- Tables that scroll sideways show an edge shadow on the side with more content
  (`.table-scroll` + `more-left`/`more-right`, toggled from `main.js`).

## Adding a new section

Create a folder at the repo root and put sheets in it. That is all: it appears on the next build.

Optional: to control its display name (the default is the folder name with a capital letter, so
`my-folder` becomes "My folder"), add an entry to `[params.sectionTitles]` in `site/hugo.toml`, for
example `cicd = "CI/CD"`.

## Layout of `site/`

| Path | Purpose |
| --- | --- |
| `hugo.toml` | Config: base URL, markup, mounts, section display names |
| `scripts/prepare-content.py` | Front-matter preprocessing (stdlib only) |
| `scripts/dev.sh` | Local preview helper |
| `layouts/` | Templates: base, home, section, sheet, 404, render hooks (links, code blocks, tables, callouts, headings) |
| `assets/css`, `assets/js` | Hand-written CSS and vanilla JS, minified and fingerprinted by Hugo |
| `static/` | Favicon |

## Deployment

`.github/workflows/pages.yml` runs on every pull request (build only) and on pushes to `master`
(build and deploy). Steps: prepare content, `hugo --minify` with the right `baseURL` for the project
page, Pagefind index, upload and deploy with the official Pages actions.

One-time repository setting: **Settings > Pages > Build and deployment > Source: GitHub Actions**.

To bump Hugo or Pagefind, change `HUGO_VERSION` / `PAGEFIND_VERSION` in the workflow.

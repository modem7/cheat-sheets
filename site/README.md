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

Hugo cannot parse Obsidian `[[wikilinks]]` and sheets have no front matter, so a small script
sits in front of it:

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

## Wikilinks

Supported forms: `[[name]]`, `[[name|alias]]`, `[[name#heading]]`, `[[name#heading|alias]]`, `[[#heading]]`.
The escaped pipe `[[name\|alias]]` used in table cells works too.

- Resolution is by **file name** (case-insensitive, without `.md`), across the whole repo, exactly like
  Obsidian. `[[docker]]` finds `docker/docker.md`. If two sheets share a file name the one in the same folder
  wins, then the first by path, and a warning is printed.
- They are rewritten to ordinary relative Markdown links, which `layouts/_default/_markup/render-link.html`
  then turns into correct page URLs for the Pages sub-path.
- Wikilinks inside fenced code blocks, inline code and HTML comments are left untouched.
- An **unresolved** link renders as dotted red text with a warning mark, and the build log gets a
  `WARN <file>:<line>: unresolved wikilink [[x]]` line (plus a GitHub Actions annotation in CI). Add
  `--strict` to `prepare-content.py` to make that fail the build.
- Plain relative links (`[Sed](sed.md)`) are resolved the same way; broken ones produce a Hugo warning.

GitHub-style callouts (`> [!NOTE]`, `> [!attention]`, `> [!INFO] Custom title`) are rendered as coloured
callout boxes by `render-blockquote.html`. Unknown types fall back to the "note" style.

## Adding a new section

Create a folder at the repo root and put sheets in it. That is all: it appears on the next build.

Optional: to control its display name (the default is the folder name with a capital letter, so
`my-folder` becomes "My folder"), add an entry to `[params.sectionTitles]` in `site/hugo.toml`, for
example `cicd = "CI/CD"`.

## Layout of `site/`

| Path | Purpose |
| --- | --- |
| `hugo.toml` | Config: base URL, markup, mounts, section display names |
| `scripts/prepare-content.py` | Wikilink and front-matter preprocessing (stdlib only) |
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

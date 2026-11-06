# Logseq
Logseq is an open-source, local-first **outliner** for notes and knowledge management. Everything is a block in a bulleted outline, pages link to each other with `[[wikilinks]]`, and every day gets a journal page. Data is stored as Markdown (or Org-mode) files in a folder. Similar to [Obsidian](obsidian.md) but block-first; for a notebook style app see [Joplin](joplin.md).

Homepage: [Logseq](https://logseq.com)
Docs: [Logseq Docs](https://docs.logseq.com)
Source: [logseq/logseq](https://github.com/logseq/logseq)

---
## Graph Folder Layout
FOLDER | CONTENT
---|---
`pages/` | One file per page
`journals/` | One file per day (`2026_11_06.md`)
`assets/` | Attached images and files
`logseq/` | Config, custom CSS and plugins (`config.edn`, `custom.css`)

Because it is plain Markdown, the folder works with [Git](git.md) and any file sync tool.

## Syntax
SYNTAX | DESCRIPTION
---|---
`[[Page]]` | Link to a page
`#tag` or `#[[multi word tag]]` | Tag (a tag is a page)
`((` then search | Reference another block
`{{embed [[Page]]}}` | Embed a page
`{{embed ((block-uuid))}}` | Embed a block
`TODO` / `DOING` / `DONE` / `LATER` / `NOW` | Task markers at the start of a block
`SCHEDULED: <2026-11-06 Fri>` | Scheduled date
`key:: value` | Block or page property
`/` | Slash command menu (templates, queries, dates, and more)

## Queries
Simple queries go in a block:
```
{{query (and [[project]] (task TODO DOING))}}
{{query (between [[today]] [[today+7d]])}}
```
Advanced queries use Datalog in a `#+BEGIN_QUERY` block. See the docs for the query syntax.

## Keyboard Shortcuts
On macOS use `Cmd` for `Ctrl`. Rebind under Settings > Keymap.

SHORTCUT | DESCRIPTION
---|---
`Ctrl`+`K` | Search
`Tab` / `Shift`+`Tab` | Indent or outdent a block
`Alt`+`Shift`+`Up` / `Down` | Move a block
`Esc` | Leave editing, select the block
`Ctrl`+`Enter` | Cycle TODO / DOING / DONE
`Ctrl`+`Shift`+`A` | Select all blocks
`t r` | Toggle the right sidebar
`t l` | Toggle the left sidebar
`t t` | Toggle light and dark theme
`t w` | Toggle wide mode
`g j` | Go to journals
`g a` | Go to all pages
`g g` | Go to the graph view
`g h` | Go home

Single-letter `t` and `g` shortcuts work when you are not editing a block.

## Sync and Backup
- Folder-based, so use [Git](git.md), Syncthing, Nextcloud or iCloud on the graph folder.
- **Logseq Sync** is a paid encrypted service.
- Keep one sync method per graph to avoid conflicts, and commit before big changes.

## Logseq vs Obsidian
- Logseq is outline-first (each line is a block you can reference and query); [Obsidian](obsidian.md) is document-first.
- Logseq is open source; Obsidian is closed source but free for personal use.
- Logseq is moving to a database-backed version. The file-based version described here is the long-standing one; check the project for the state of the newer release.

## Not Verified
Shortcuts and syntax were written from knowledge of the file-based version and not checked against a current install, so confirm in Settings > Keymap.

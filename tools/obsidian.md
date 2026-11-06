# Obsidian
Obsidian is a local-first note-taking and knowledge-base app. Notes are plain Markdown files in a folder (a **vault**), linked together with `[[wikilinks]]`. This repository uses standard relative Markdown links instead, so it also works on GitHub and outside Obsidian (Obsidian can be set to use Markdown links under Settings, Files and links).

Homepage: [Obsidian](https://obsidian.md)
Help: [Obsidian Help](https://help.obsidian.md)

---
## Using This Repo as a Vault
1. Open Obsidian, choose **Open folder as vault** and pick the cloned repository.
2. Wikilinks between sheets resolve by file name, so `[[docker]]` opens `docker/docker.md`.
3. The vault settings live in `.obsidian/` inside the folder and are git-ignored here.

See [Git](git.md) for the version control side.

## Vault and Files
- A vault is just a folder. Everything is plain `.md`, so any editor, `grep` or [Git](git.md) works on it.
- `.obsidian/` holds settings, themes and plugins for that vault. Commit it only if you want to share your setup.
- Attachments (images, PDFs) sit in the vault; the default folder is set under Settings > Files and links.

## Markdown and Links
SYNTAX | DESCRIPTION
---|---
`[[Note]]` | Link to a note
`[[Note\|alias]]` | Link with different display text
`[[Note#Heading]]` | Link to a heading
`[[Note#^block-id]]` | Link to a block (add `^block-id` at the end of the block)
`![[Note]]` | Embed a note
`![[image.png\|300]]` | Embed an image at 300 px wide
`#tag` / `#parent/child` | Tag and nested tag
`- [ ] task` | Task checkbox
`> [!note] Title` | Callout (also `tip`, `warning`, `danger`, `info`, and more)
`==highlight==` | Highlight
`%%comment%%` | Hidden comment
`$E=mc^2$` | Inline math (LaTeX)
` ```mermaid ` | Diagram block

Properties (front matter) go at the top of a note:
```yaml
---
tags: [cheat-sheet, linux]
aliases: [Linux Basics]
created: 2026-11-06
---
```
For standard Markdown see [Markdown](../misc/markdown.md).

## Shortcuts
The shortcuts below use Windows/Linux keys; on macOS use `Cmd` for `Ctrl` (see [MacOS keyboard shortcuts](../macos/macos-shortcuts.md)). They can be rebound under Settings > Hotkeys.

SHORTCUT | DESCRIPTION
---|---
`Ctrl`+`P` | Command palette
`Ctrl`+`O` | Quick switcher (open or create a note)
`Ctrl`+`N` | New note
`Ctrl`+`E` | Toggle edit and reading view
`Ctrl`+`Shift`+`F` | Search across the vault
`Ctrl`+`F` | Search in the current note
`Ctrl`+`G` | Graph view
`Ctrl`+`Click` | Open link in a new tab
`Ctrl`+`K` | Insert a link to a note on the selected text
`Ctrl`+`,` | Settings

## Search Operators
OPERATOR | DESCRIPTION
---|---
`"exact phrase"` | Exact match
`-word` | Exclude a word
`tag:#linux` | Notes with a tag
`path:kubernetes` | Notes whose path contains this
`file:readme` | Match on file name
`line:(a b)` | Both words on one line
`task-todo:` | Open tasks

## Plugins
Turn on **Community plugins** under Settings. Popular ones:

PLUGIN | USE
---|---
Dataview | Query notes like a database
Templater | Advanced templates and scripting
Obsidian Git | Auto commit, pull and push the vault
Calendar | Calendar and daily notes view
Tasks | Task queries and due dates
Excalidraw | Hand-drawn diagrams inside notes

Core plugins (built in) include Daily notes, Templates, Backlinks, Outgoing links, Canvas, Bases and Properties view.

## Sync and Backup
- **Obsidian Sync** (paid) is the official end-to-end encrypted sync.
- **Git**: the Obsidian Git plugin, or a normal [Git](git.md) repository with a scheduled commit.
- **File sync tools**: Syncthing, Nextcloud, iCloud or Dropbox on the vault folder. Do not run two sync tools on the same folder.
- Back up the whole vault folder, including `.obsidian/` if you want your setup kept.

## Obsidian vs Similar Tools
| | Obsidian | [Logseq](logseq.md) | [Joplin](joplin.md) |
|---|---|---|---|
| Style | Documents with links | Outliner (every line is a block) | Notebooks and notes |
| Storage | Markdown files in a folder | Markdown or Org files in a folder | Database, exportable to Markdown |
| Licence | Closed source, free for personal use | Open source (AGPL) | Open source (AGPL) |
| Sync | Obsidian Sync (paid) or your own | Your own (Git, file sync); paid Logseq Sync | E2EE to Nextcloud, WebDAV, S3, Dropbox, Joplin Server and others |
| Plugins | Very large community | Large | Moderate |
| Best for | Linked knowledge base, docs | Daily journaling, outlines | Plain notes, web clipper, self-hosted sync |

Other tools in the same space: Foam and Dendron (VS Code, see [VSCode (Visual Studio Code)](vscode.md)), Notable, Standard Notes, Trilium, SiYuan and AFFiNE.

## Not Verified
Commands, shortcuts and plugin names were written from knowledge of the current app and not checked against a fresh install. Licensing terms and pricing change, so check the Obsidian site.

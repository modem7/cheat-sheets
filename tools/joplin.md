# Joplin
Joplin is an open-source note-taking and to-do app with desktop, mobile and terminal clients. Notes are written in Markdown, organised in notebooks and tagged, and can be synced with end-to-end encryption. Compare with [Obsidian](obsidian.md) (linked notes in plain files) and [Logseq](logseq.md) (outliner).

Homepage: [Joplin](https://joplinapp.org)
Docs: [Joplin Documentation](https://joplinapp.org/help/)
Source: [laurent22/joplin](https://github.com/laurent22/joplin)

---
## Install
PLATFORM | COMMAND
---|---
Windows | `choco install joplin` ([Chocolatey](../windows/chocolatey.md)) or the installer
macOS | `brew install --cask joplin` ([Homebrew](../macos/homebrew.md))
Linux | the official install script from the Joplin site, or AppImage
Terminal app | `npm install -g joplin` (needs Node.js)

## Sync
Set the target under Tools > Options > Synchronisation. Supported targets include Joplin Cloud, Joplin Server, Nextcloud, WebDAV, Dropbox, OneDrive, AWS S3 and a plain folder (use with Syncthing).

- Enable **end-to-end encryption** under Options > Encryption, and do it on every device. **Keep the master key and password safe**: lost keys mean unreadable notes.
- Do not sync one profile with two different targets.

## Self-Host Joplin Server
```yaml
services:
  db:
    image: postgres:16
    restart: unless-stopped
    environment:
      POSTGRES_USER: joplin
      POSTGRES_PASSWORD: change-me
      POSTGRES_DB: joplin
    volumes:
      - joplin_db:/var/lib/postgresql/data
  app:
    image: joplin/server:latest
    restart: unless-stopped
    depends_on:
      - db
    ports:
      - "22300:22300"
    environment:
      APP_PORT: 22300
      APP_BASE_URL: https://joplin.example.com
      DB_CLIENT: pg
      POSTGRES_HOST: db
      POSTGRES_PORT: 5432
      POSTGRES_USER: joplin
      POSTGRES_PASSWORD: change-me
      POSTGRES_DATABASE: joplin
volumes:
  joplin_db:
```
See [Docker-Compose](../docker/docker-compose.md) and [PostgreSQL Cheat-Sheet](../databases/postgres.md). Put it behind a reverse proxy with TLS ([Traefik](../apps/traefik.md), [Nginx](../apps/nginx.md)). Joplin Server's first admin account is documented upstream with a default login; **change that default password immediately**.

## Terminal Client
Start with `joplin`. Commands start with `:` in the app, or run from the shell as `joplin <command>`.

COMMAND | DESCRIPTION
---|---
`mkbook <NAME>` | Create a notebook
`use <NOTEBOOK>` | Switch notebook
`mknote <TITLE>` | Create a note
`ls` | List notes
`cat <NOTE>` | Show a note
`edit <NOTE>` | Edit in `$EDITOR`
`set <NOTE> todo 1` | Make the note a to-do
`sync` | Sync now
`config <KEY> <VALUE>` | Set an option (for example the sync target)
`help` | List commands

## Markdown Tips
- Full Markdown plus checklists (`- [ ]`), tables, math (`$...$`), Mermaid and footnotes. See [Markdown](../misc/markdown.md) and [Mermaid](mermaid.md).
- Internal links use note IDs (`[Title](:/noteid)`); right-click a note > Copy Markdown link.
- The **Web Clipper** browser extension saves pages as Markdown notes.
- Export and import as Markdown, JEX or raw files (File > Export all).

## Backup
Sync is not a backup. Export regularly (File > Export all as JEX) or copy the profile folder (`~/.config/joplin-desktop` on Linux).

## Not Verified
Written from knowledge and not checked against a current install. Check the Joplin docs for Joplin Server environment variables and the default admin login.

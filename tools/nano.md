# nano
GNU nano is a small terminal text editor with its key bindings listed on screen. Use it for quick edits when you do not want to learn modes; see [Vim](vim.md) for the alternative.

Documentation: [nano manual](https://www.nano-editor.org/dist/latest/nano.html), [nanorc(5)](https://www.nano-editor.org/dist/latest/nanorc.5.html), [Key cheatsheet](https://www.nano-editor.org/dist/latest/cheatsheet.html)

Checked against the nano 9.3 manual. In key lists `^` means Ctrl and `M-` means Alt (Cmd on macOS terminals that map it).

## Start Options
COMMAND | DESCRIPTION
---|---
`nano FILE` | Edit a file
`nano +LINE,COLUMN FILE` | Open with the cursor at a line and column
`nano -l FILE` | Show line numbers
`nano -m FILE` | Enable the mouse
`nano -c FILE` | Always show the cursor position
`nano -i FILE` | Auto-indent new lines
`nano -E FILE` | Convert typed tabs to spaces
`nano -T N FILE` | Set the tab size to `N` (default 8)
`nano -S FILE` | Soft-wrap long lines
`nano -w FILE` | Do not hard-wrap long lines (the default)
`nano -B FILE` | Back up the existing file to `FILE~` when saving
`nano -v FILE` | View mode (read-only)
`nano -R FILE` | Restricted mode

## File and Buffers
KEYS | DESCRIPTION
---|---
`^O` | Write out (save)
`^X` | Close the buffer, and exit if it is the last one; asks to save changes
`^R` | Read a file into the buffer
`^G` | Open the help
`^C` | Show the cursor position
`M-X` | Hide or show the help lines at the bottom
`M-N` | Turn line numbers on or off
`M-P` | Show or hide whitespace

## Move and Edit
KEYS | DESCRIPTION
---|---
`^A` / `^E` | Start / end of the line
`^Y` / `^V` | Page up / down
`M-G` | Go to a line
`M-]` | Jump to the matching bracket
`^K` | Cut the line (or the marked region)
`M-6` | Copy the line (or the marked region)
`^U` | Paste
`^6` or `M-A` | Set or unset the mark to select text
`Tab` / `Shift-Tab` | Indent / unindent the marked region
`M-3` | Comment or uncomment the line or region
`^J` | Justify the paragraph or region
`M-U` / `M-E` | Undo / redo

## Search and Replace
KEYS | DESCRIPTION
---|---
`^F` or `^W` | Search forward (`^F` and `^B` forward and backward since nano 8.0)
`^B` | Search backward
`M-F` / `M-B` | Next / previous match (per the official key cheatsheet)
`M-R` or `^\` | Replace
`M-B` / `M-C` / `M-R` | While searching: toggle backwards, case-sensitive, regular expression
`^T` `^T` | Spell check

## Configuration
Settings go in `~/.nanorc` (also read from `$XDG_CONFIG_HOME/nano/nanorc` or `~/.config/nano/nanorc`), or system-wide in `/etc/nanorc` (the path may differ by distribution).

OPTION | DESCRIPTION
---|---
`set linenumbers` | Show line numbers
`set tabsize N` | Tab width, greater than 0 (default 8)
`set tabstospaces` | Convert typed tabs to spaces
`set autoindent` | Indent new lines like the previous one
`set mouse` | Enable the mouse
`set softwrap` | Soft-wrap long lines
`include "FILE"` | Read syntax definitions from a file

```text
set linenumbers
set tabsize 4
set tabstospaces
set autoindent
set mouse
```

## Version Notes
VERSION | CHANGE
---|---
4.0 | No hard-wrapping by default
8.0 | `^F` and `^B` became the search keys
9.0 | `M-<` and `M->` became scroll left and scroll right

## See Also
- [Vim](vim.md)
- [tmux](tmux.md)
- [VSCode (Visual Studio Code)](vscode.md)

# Vim
Vim is a modal terminal text editor, installed almost everywhere. Use it for quick edits over SSH or inside [tmux](tmux.md), and see [nano](nano.md) for a simpler editor.

Documentation: [Vim help (vimhelp.org)](https://vimhelp.org/)
Project: [vim.org](https://www.vim.org/)

Commands below are checked against the Vim 9.2 help. Neovim was not checked, so defaults and config paths may differ there. The `Ctrl-x` keys mean hold Ctrl.

## Start and Exit
COMMAND | DESCRIPTION
---|---
`vim FILE` | Edit a file
`vim +LINE FILE` | Open with the cursor on line `LINE`
`vim -R FILE` | Open read-only
`vim -O FILE1 FILE2` / `vim -o FILE1 FILE2` | Open files in vertical / horizontal split windows
`vim -d FILE1 FILE2` / `vimdiff FILE1 FILE2` | Diff mode
`vim -r` | List swap files; `vim -r FILE` recovers that file
`:w` | Write (save)
`:q` | Quit (fails if there are unsaved changes)
`:wq` / `:x` | Write and quit; `:x` writes only if changed
`:q!` | Quit without writing, discarding changes
`ZZ` / `ZQ` | Write if changed and close / close without writing
`:wa` / `:qa` | Write all buffers / quit Vim

## Modes
KEY | DESCRIPTION
---|---
`Esc` | Back to Normal mode
`i` / `a` | Insert before / after the cursor
`I` / `A` | Insert at the first non-blank / at the end of the line
`o` / `O` | Open a new line below / above
`R` | Replace mode (overtype)
`v` / `V` / `Ctrl-v` | Visual mode: characters, lines, block

## Movement
KEY | DESCRIPTION
---|---
`h` `j` `k` `l` | Left, down, up, right
`w` / `b` / `e` | Word forward / word back / end of word
`0` / `^` / `$` | Start of line / first non-blank / end of line
`gg` / `G` | First / last line (`NG` or `:N` goes to line `N`)
`%` | Jump to the matching bracket
`{` / `}` | Paragraph back / forward
`Ctrl-d` / `Ctrl-u` | Scroll half a screen down / up
`Ctrl-f` / `Ctrl-b` | Scroll a screen forward / back
`zz` | Centre the cursor line in the window
`ma` / `'a` | Set mark `a` / jump to mark `a`

## Edit
KEY | DESCRIPTION
---|---
`x` | Delete the character under the cursor
`dd` / `D` | Delete the line / delete to the end of the line
`d` + motion | Delete what the motion covers, e.g. `dw`, `d$`
`cw` | Change a word (does not include the trailing space)
`c` + motion | Change what the motion covers, e.g. `ciw` (inner word), `ci"` (inside quotes)
`yy` | Yank (copy) the line
`p` / `P` | Put after / before the cursor
`"ayy` / `"ap` | Yank into register `a` / put from register `a`
`u` / `Ctrl-r` | Undo / redo
`.` | Repeat the last change
`>>` / `<<` | Shift the line right / left by `shiftwidth`
`J` | Join lines
`~` | Switch case and move right
`rX` | Replace the character with `X`

## Search and Replace
COMMAND | DESCRIPTION
---|---
`/PATTERN` / `?PATTERN` | Search forward / backward
`n` / `N` | Repeat the search in the same / opposite direction
`*` / `#` | Search forward / backward for the word under the cursor
`:noh` | Stop highlighting matches (comes back on the next search)
`:s/OLD/NEW/` | Replace the first match on the current line
`:s/OLD/NEW/g` | Replace all matches on the line
`:%s/OLD/NEW/g` | Replace all matches in the file (`%` means every line)
`:%s/OLD/NEW/gc` | Same, asking for each one: `y` yes, `n` no, `a` all remaining, `q` quit

## Buffers, Windows and Tabs
COMMAND | DESCRIPTION
---|---
`:ls` | List buffers
`:bn` / `:bp` | Next / previous buffer
`:bd` | Remove the buffer from the list
`:sp` / `:vs` | Split horizontally / vertically (optionally `:sp FILE`)
`Ctrl-w h` / `j` / `k` / `l` | Move to the window left / down / up / right
`:tabnew` | New tab page
`gt` / `gT` | Next / previous tab page (wraps around)

## Shell and Files
COMMAND | DESCRIPTION
---|---
`:!COMMAND` | Run a shell command
`:r !COMMAND` | Insert the command's output below the cursor
`:r FILE` | Insert a file below the cursor
`:w !COMMAND` | Send the lines to a command (note the space before `!`); does not write the file
`:recover` | Recover from the swap file; the current buffer contents are lost
`:recover!` | Discard changes and recover
`:help TOPIC` / `:h TOPIC` | Open help on a topic

## Settings
Put settings in `~/.vimrc` (Unix also reads `~/.vim/vimrc` and `$XDG_CONFIG_HOME/vim/vimrc`). Use `:set OPTION` to try one in the current session.

OPTION | DESCRIPTION
---|---
`set number` / `set relativenumber` | Absolute / relative line numbers (off by default)
`set ignorecase` | Ignore case when searching (off by default)
`set smartcase` | With `ignorecase`, match case if the pattern has capitals (off by default)
`set hlsearch` | Highlight all matches (off by default)
`set incsearch` | Show matches as you type (off by default; `defaults.vim` turns it on when available)
`set expandtab` | Insert spaces instead of tabs (off by default)
`set tabstop=4` | Width of a tab character (default 8)
`set shiftwidth=4` | Indent width for `>>`, `<<` and autoindent
`set autoindent` | Copy the indent of the previous line (off by default)

```vim
set number
set ignorecase smartcase
set hlsearch incsearch
set expandtab tabstop=4 shiftwidth=4
set autoindent
```

## See Also
- [nano](nano.md)
- [tmux](tmux.md)
- [VSCode (Visual Studio Code)](vscode.md)

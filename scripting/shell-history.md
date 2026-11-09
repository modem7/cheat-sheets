# Shell History
How Bash and Zsh record, search, share and clean up command history. Settings belong in [bashrc](bashrc.md) or [zshrc](zshrc.md); the OMZ `history` plugin gives a few aliases ([Oh My Zsh](oh-my-zsh.md)).

Documentation: [Bash History Facilities](https://www.gnu.org/software/bash/manual/html_node/Bash-History-Facilities.html), [Zsh Options: History](https://zsh.sourceforge.io/Doc/Release/Options.html#History)

Checked against Bash 5.3 and Zsh 5.9.

## Search and Reuse
COMMAND | DESCRIPTION
---|---
`Ctrl+R` / `Ctrl+S` | Incremental search backwards / forwards (`Ctrl+S` may need `stty -ixon`)
`Up` / `Down` | Step through history
`!!` | Previous command
`sudo !!` | Run the previous command with `sudo`
`!$` | Last argument of the previous command
`!^` | First argument of the previous command
`!*` | All arguments of the previous command
`!N` / `!-N` | Entry number N / N entries back
`!STRING` | Most recent command starting with `STRING`
`!?STRING` | Most recent command containing `STRING`
`^OLD^NEW` | Rerun the previous command, replacing `OLD` with `NEW`
`!!:s/OLD/NEW/` | Same, in full modifier form
`Alt+.` | Insert the last argument of the previous command (repeat to go back)
`history \| grep TEXT` | Search the list

Add `:p` to print instead of running, e.g. `!!:p`.

## Viewing and Editing
COMMAND | SHELL | DESCRIPTION
---|---|---
`history` | Bash | Whole history, numbered
`history N` | Bash | Last N entries
`history 1` | Zsh | Whole history (Zsh shows only recent entries without an argument)
`history -i 1` | Zsh | With ISO timestamps
`fc -l -20` | Both | Last 20 entries
`fc -ln -1` | Both | Previous command without its number
`fc` | Both | Open the previous command in `$EDITOR`, then run it
`history -d N` | Bash | Delete entry N from memory
`history -c` | Bash | Clear this shell's history
`history -c && history -w` | Bash | Clear memory and empty the file
`fc -W` | Zsh | Write this session's history to `$HISTFILE`
`fc -R` | Zsh | Read the history file into this session

Edit the history file directly (with no shells writing to it) to remove a line you recorded by mistake.

## Bash Settings
Put in `~/.bashrc`.

SETTING | EFFECT
---|---
`HISTSIZE=100000` | Entries kept in memory
`HISTFILESIZE=200000` | Lines kept in `~/.bash_history`
`HISTCONTROL=ignoreboth:erasedups` | `ignorespace` + `ignoredups`, and delete older duplicates
`HISTIGNORE='ls:cd:pwd:exit'` | Colon-separated patterns never recorded
`HISTTIMEFORMAT='%F %T '` | Store and show timestamps
`shopt -s histappend` | Append on exit instead of overwriting
`shopt -s cmdhist` | Save a multi-line command as one entry (on by default)
`PROMPT_COMMAND='history -a'` | Write each command to the file as it runs
`PROMPT_COMMAND='history -a; history -c; history -r'` | Also re-read the file, to share history live across terminals

`HISTCONTROL=ignorespace` means a command typed with a leading space is not recorded, handy for secrets on the command line (still avoid typing secrets).

## Zsh Settings
Put in `~/.zshrc`. Zsh starts with `SAVEHIST=0` and no `HISTFILE`, so set both or nothing is saved.

SETTING | EFFECT
---|---
`HISTFILE=~/.zsh_history` | Where history is saved
`HISTSIZE=100000` | Entries kept in memory
`SAVEHIST=100000` | Entries saved to the file
`setopt EXTENDED_HISTORY` | Save `:START:ELAPSED;command` with timestamps
`setopt SHARE_HISTORY` | Share across running shells (implies incremental append)
`setopt INC_APPEND_HISTORY` | Append as commands run, without sharing
`setopt HIST_IGNORE_ALL_DUPS` | Remove older duplicates
`setopt HIST_IGNORE_DUPS` | Do not record a command identical to the previous one
`setopt HIST_IGNORE_SPACE` | Do not record commands starting with a space
`setopt HIST_REDUCE_BLANKS` | Trim superfluous blanks
`setopt HIST_SAVE_NO_DUPS` | Do not write duplicates to the file
`setopt HIST_FIND_NO_DUPS` | Skip duplicates while searching
`setopt HIST_EXPIRE_DUPS_FIRST` | Drop duplicates first when the file exceeds `HISTSIZE`
`setopt HIST_VERIFY` | Show `!!` expansions for editing before running
`setopt HIST_FCNTL_LOCK` | Use `fcntl` locking on the history file

## Better Search Tools
TOOL | WHAT IT ADDS
---|---
fzf | `Ctrl+R` fuzzy search; its shell integration is loaded with `source <(fzf --zsh)` or `eval "$(fzf --bash)"` on recent versions (`(unverified)` for your version; `fzf --help` lists it)
`zsh-history-substring-search` | Up / down arrows match what you have already typed
`per-directory-history` (OMZ plugin) | Separate history per directory
[Atuin](https://atuin.sh/) | SQLite history with sync across machines (`(unverified)`)

## Migrate Bash History to Zsh
Zsh reads plain lines, so append the Bash file to the Zsh file once. With `EXTENDED_HISTORY`, plain lines are accepted, but they carry no timestamps.

```bash
cat ~/.bash_history >> ~/.zsh_history
```

## Troubleshooting
SYMPTOM | FIX
---|---
History empty after a crash or closing the terminal | Bash: add `PROMPT_COMMAND='history -a'`; Zsh: use `INC_APPEND_HISTORY` or `SHARE_HISTORY`
History lost when two terminals close | Bash: set `shopt -s histappend`
Nothing saved in Zsh | `SAVEHIST` is 0 or `HISTFILE` is unset
`zsh: corrupt history file` | Back up the file, then try `strings ~/.zsh_history > fixed` and move `fixed` into place (`(unverified)`)
`!` in a double-quoted string expands | Use single quotes, or `set +H` (Bash) / `setopt NO_BANG_HIST` (Zsh)
Secrets in history | Edit the file, then `history -c` (Bash) or `fc -R` (Zsh) to reload

## See Also
- [Bash](bash.md)
- [bashrc](bashrc.md)
- [Zsh](zsh.md)
- [zshrc](zshrc.md)
- [Oh My Zsh](oh-my-zsh.md)
- [Modern CLI Tools](../tools/modern-cli-tools.md)

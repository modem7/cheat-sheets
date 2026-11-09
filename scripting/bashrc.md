# bashrc
A commented layout for `~/.bashrc`, the file Bash reads for interactive non-login shells, plus how it relates to the other startup files. Language features are in [Bash](bash.md); history settings in [Shell History](shell-history.md).

Documentation: [Bash Startup Files](https://www.gnu.org/software/bash/manual/html_node/Bash-Startup-Files.html)

Checked against Bash 5.3 and the Ubuntu default `~/.bashrc`.

## Startup Files
FILE | READ BY
---|---
`/etc/profile`, then the first of `~/.bash_profile`, `~/.bash_login`, `~/.profile` | Login shells
`~/.bashrc` | Interactive non-login shells (a new terminal tab, `bash`)
`~/.bash_logout` | Login shells on exit
`~/.bash_aliases` | Sourced by the Debian and Ubuntu `~/.bashrc` if it exists
`~/.inputrc` | Readline settings

SSH logins and many terminals start login shells, which skip `~/.bashrc`. Make sure `~/.profile` (or `~/.bash_profile`) sources it:

```bash
if [ -n "$BASH_VERSION" ] && [ -f "$HOME/.bashrc" ]; then
  . "$HOME/.bashrc"
fi
```

## Skeleton
```bash
# Stop here for non-interactive shells
case $- in
  *i*) ;;
  *) return ;;
esac

# History
HISTCONTROL=ignoreboth:erasedups
HISTSIZE=100000
HISTFILESIZE=200000
HISTTIMEFORMAT='%F %T '
shopt -s histappend
PROMPT_COMMAND='history -a'

# Window size and globbing
shopt -s checkwinsize globstar

# Colour for ls and grep
if [ -x /usr/bin/dircolors ]; then
  eval "$(dircolors -b)"
  alias ls='ls --color=auto'
  alias grep='grep --color=auto'
fi

# Aliases
alias ll='ls -alF'
alias la='ls -A'
[ -f ~/.bash_aliases ] && . ~/.bash_aliases

# Completion
if ! shopt -oq posix; then
  if [ -f /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
  elif [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
  fi
fi

# Environment
export EDITOR=nano
export LANG=en_GB.UTF-8
```

Keep `export` lines that other programs need (not only your shell) in `~/.profile`, because `~/.bashrc` is not read by login shells or by scripts.

## Useful shopt Options
Set with `shopt -s NAME`, unset with `shopt -u NAME`; `shopt` alone lists them.

OPTION | EFFECT
---|---
`histappend` | Append to the history file instead of overwriting
`checkwinsize` | Update `LINES` and `COLUMNS` after each command
`globstar` | `**` matches recursively
`autocd` | Type a directory name to `cd` into it
`cdspell` | Fix small typos in `cd` arguments
`dotglob` | `*` matches dotfiles
`nocaseglob` | Case-insensitive globbing
`extglob` | Extended patterns such as `!(*.md)` (on by default in interactive shells)
`cmdhist` | Keep a multi-line command as one history entry

## Prompt
VARIABLE | MEANING
---|---
`PS1` | Main prompt
`PS2` | Continuation prompt
`PROMPT_COMMAND` | Command run before each prompt

Escapes: `\u` user, `\h` host, `\w` working directory, `\$` `$` or `#`, `\t` time, `\j` jobs. Wrap colour codes in `\[` and `\]` so line editing counts widths correctly:

```bash
PS1='\[\e[32m\]\u@\h\[\e[0m\]:\[\e[34m\]\w\[\e[0m\]\$ '
```

For a prompt that works in any shell see [Starship Prompt](../tools/starship.md).

## Readline (`~/.inputrc`)
```text
set completion-ignore-case on
set show-all-if-ambiguous on
"\e[A": history-search-backward
"\e[B": history-search-forward
```

The two bindings make Up and Down search history for what you have typed. Reload with `Ctrl+X Ctrl+R` or `bind -f ~/.inputrc`.

## Reload and Debug
COMMAND | DESCRIPTION
---|---
`source ~/.bashrc` | Reload the file in this shell
`exec bash` | Replace this shell with a fresh one
`bash --norc` | Start without `~/.bashrc`, to test
`bash -x -i -c exit` | Trace an interactive start
`time bash -i -c exit` | Time an interactive start

## Troubleshooting
SYMPTOM | FIX
---|---
Settings missing over SSH | Login shell: source `~/.bashrc` from `~/.profile`
Aliases not working in scripts | Aliases are off in non-interactive shells; use functions or full commands
`scp` or `rsync` breaks with "protocol error" | `~/.bashrc` prints output for non-interactive shells: put the `case $- in` guard at the top
Prompt wraps strangely | Colour codes are missing `\[ \]`
`command not found` after editing `PATH` | `hash -r`, or start a new shell

## See Also
- [Bash](bash.md)
- [Bash Recipes](bash-recipes.md)
- [Shell History](shell-history.md)
- [zshrc](zshrc.md)
- [Shell Comparison](shell-comparison.md)
- [Starship Prompt](../tools/starship.md)

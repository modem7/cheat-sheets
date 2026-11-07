# Zsh
Zsh is a Bourne-style shell with powerful globbing, parameter expansion and completion, and is the default login shell on macOS. This sheet covers what differs from [Bash](bash.md); most Bash syntax (`if`, `for`, `$(...)`, redirection, here-docs) works unchanged. Pick between shells with [Shell Comparison](shell-comparison.md).

Documentation: [Zsh Manual](https://zsh.sourceforge.io/Doc/Release/)
Project: [Zsh](https://www.zsh.org/)

Checked against Zsh 5.9. Examples were run unless marked `(unverified)`.

## Startup Files
FILE | READ BY
---|---
`~/.zshenv` | Every zsh, including scripts (keep it tiny: environment only)
`~/.zprofile` | Login shells, before `.zshrc`
`~/.zshrc` | Interactive shells (aliases, prompt, completion, key bindings)
`~/.zlogin` | Login shells, after `.zshrc`
`~/.zlogout` | Login shells on exit
`ZDOTDIR` | Directory zsh looks in for these files instead of `$HOME` (set it in `/etc/zshenv` or `~/.zshenv`)

`zsh -f` starts without any startup files, which is handy for testing. `#!/usr/bin/env zsh` is the shebang for scripts.

## Arrays and Associative Arrays
Zsh arrays start at 1 and `$a` expands to all elements without needing `[@]`.

COMMAND | DESCRIPTION
---|---
`a=(x y z)` | Create an array
`$a[1]`, `$a[-1]` | First and last element (1-based)
`$a[2,3]` | Slice, inclusive of both ends
`${#a}` | Number of elements
`${a[(i)y]}` | Index of the first element equal to `y`
`${a[(r)y]}` | The first element matching `y`
`a+=(w)` | Append
`${a:#y}` | Remove elements matching pattern `y`
`${(o)a}`, `${(O)a}` | Sorted ascending, descending
`${(u)a}` | Unique elements
`typeset -U path` | Keep `path` free of duplicates (`path` is the array form of `PATH`)
`typeset -A m; m=(k v k2 v2)` | Associative array from key/value pairs
`${(k)m}`, `${(v)m}`, `${(kv)m}` | Keys, values, both
`${m[k]}` | Look up a key

## Parameter Expansion Flags
Flags go in parentheses straight after `${`.

FLAG | DESCRIPTION
---|---
`${(U)s}`, `${(L)s}` | Upper / lower case
`${s:u}`, `${s:l}` | Same, modifier form
`${(j:,:)a}` | Join array with `,`
`${(s:,:)s}` | Split string on `,` into an array
`${(f)"$(cmd)"}` | Split command output into lines (an array)
`${(q)s}` | Quote for reuse in the shell
`${(l:8::0:)n}`, `${(r:8::.:)n}` | Left / right pad to width 8 with `0` / `.`
`${(t)v}` | Type of a variable (`scalar`, `array`, `association`)
`${s:0:2}` | Substring (offset, length)
`${s[1,3]}`, `${s[-2,-1]}` | Substring by position, negative counts from the end
`${s/l/L}`, `${s//l/L}` | Replace first / all (same as Bash)

History-style modifiers work on variables too, which replaces `dirname`, `basename` and `realpath` for most uses:

COMMAND | DESCRIPTION
---|---
`${x:h}` | Head (dirname)
`${x:t}` | Tail (basename)
`${x:r}` | Remove the last extension
`${x:e}` | Only the extension
`${x:A}` | Absolute path with symlinks resolved

## Globbing
Needs `setopt extended_glob` for the `^`, `~` and `(#i)` forms. Unlike Bash, a pattern that matches nothing is an error (`no matches found`), not the literal text; add `(N)` to get an empty result instead.

PATTERN | MATCHES
---|---
`**/*.md` | Recursive, no `globstar` option needed
`*(.)`, `*(/)` | Regular files only, directories only
`*(@)`, `*(x)` | Symlinks, executables
`*(.om[1])` | Newest regular file (`om` = sort by modification time, `[1]` = first)
`*(.on[1])` | First regular file by name
`*(.L0)` | Empty files (`L` is size; `L+1` is larger than 1 byte)
`*(N)` | Null glob: no error when nothing matches
`^*.txt` | Everything except `*.txt`
`*~*.log` | `*` except names matching `*.log`
`(#i)readme*` | Case-insensitive match

## zmv
`zmv` renames with patterns. Load it first with `autoload -Uz zmv`.

COMMAND | DESCRIPTION
---|---
`zmv -n '(*).md' '$1.txt'` | Dry run: print the `mv` commands only
`zmv '(*).md' '$1.txt'` | Rename every `.md` to `.txt` (renames files in place)
`zmv -W '*.md' '*.txt'` | Same with wildcards on both sides

## Options
Set with `setopt NAME`, unset with `unsetopt NAME` (case and underscores are ignored). `setopt` alone lists the options that are on.

OPTION | EFFECT
---|---
`autocd` | Type a directory name to `cd` into it
`auto_pushd`, `pushd_ignore_dups` | Make `cd` push onto the directory stack, without duplicates
`cdable_vars` | `cd NAME` treats `NAME` as a variable holding a path
`extended_glob` | Enable the extra glob operators above
`glob_dots` | Globs match dotfiles
`nullglob` | Unmatched globs expand to nothing (global version of `(N)`)
`noclobber` | Refuse `>` over existing files
`correct` | Offer spelling corrections for commands
`interactive_comments` | Allow `#` comments at the prompt
`prompt_subst` | Expand `$vars` and `$(...)` in the prompt string
`hist_ignore_all_dups` | Drop older duplicates from history
`hist_ignore_space` | Do not record commands that start with a space
`share_history` | Share history between running shells
`inc_append_history` | Write each command to the history file as it runs
`hist_verify` | Show a history expansion (`!!`) for editing instead of running it

## History
```zsh
HISTFILE=~/.zsh_history
HISTSIZE=50000      # lines kept in memory
SAVEHIST=50000      # lines saved to HISTFILE
setopt share_history hist_ignore_all_dups hist_ignore_space
```
Both `HISTSIZE` and `SAVEHIST` matter: zsh starts with `SAVEHIST=0`, so history is not written to disk until you set it (the file is also only written if `HISTFILE` is set).

COMMAND | DESCRIPTION
---|---
`!!` | Previous command
`!$` | Last argument of the previous command
`fc -l 1` | List history from entry 1
`history 1` | List the full history (the number is the first entry shown)
`Ctrl+R` | Incremental search backwards

## Completion
```zsh
autoload -Uz compinit && compinit
zstyle ':completion:*' menu select
```
`compinit` is required for completion to work. Tools usually print their own completions, e.g. `source <(kubectl completion zsh)`; see [Kubectl](../kubernetes/kubectl.md).

COMMAND | DESCRIPTION
---|---
`zstyle ':completion:*' menu select` | Arrow-key selectable completion menu
`zstyle -L` | List the zstyles set in this shell
`compinit -u` | Skip the insecure-directory check (use only when you know why it complains)
`fpath` | Array of directories searched for completion functions and autoloaded functions

## Prompt
`print -P` expands prompt escapes, which is the quickest way to try a prompt.

ESCAPE | EXPANDS TO
---|---
`%n`, `%m` | User name, host name
`%~` | Current directory, `~` for home
`%#` | `%` for a normal user, `#` for root
`%T` | Time, 24-hour `HH:MM`
`%F{red}`...`%f` | Start / end of foreground colour
`%?` | Exit code of the last command

```zsh
setopt prompt_subst
PROMPT='%F{green}%n@%m%f %F{blue}%~%f %# '
```
For a ready-made cross-shell prompt see [Starship Prompt](../tools/starship.md).

## Key Bindings
COMMAND | DESCRIPTION
---|---
`bindkey -e` | Emacs key bindings (the default for most setups)
`bindkey -v` | Vi key bindings
`bindkey '^R' history-incremental-search-backward` | Bind a key to a widget
`bindkey` | List all bindings
`autoload -Uz add-zsh-hook` | Load the hook helper
`add-zsh-hook precmd FUNCTION` | Run `FUNCTION` before each prompt (also `preexec`, `chpwd`)

## Aliases
COMMAND | DESCRIPTION
---|---
`alias ll='ls -l'` | Normal alias (command position only)
`alias -g L='\| less'` | Global alias, expands anywhere on the line
`alias -s md=cat` | Suffix alias: typing `file.md` runs `cat file.md`
`whence -w NAME` | What `NAME` is (alias, builtin, command, function)

## Differences from Bash
ZSH | BASH
---|---
Arrays are 1-based | Arrays are 0-based
`$a` is the whole array | `$a` is only the first element; use `"${a[@]}"`
Unquoted `$var` is not word-split | Unquoted `$var` is split and globbed
A non-matching glob is an error | A non-matching glob stays literal
`print` is the preferred builtin | `echo` and `printf`
`setopt` / `unsetopt` | `shopt` and `set -o`
`$path` and `$fpath` arrays tied to `PATH` and `FPATH` | Colon-separated strings only
`$pipestatus` | `$PIPESTATUS`
`zsh -f` | `bash --noprofile --norc`

Because of the splitting difference, a script written for Bash does not behave the same under Zsh without care. Use `#!/usr/bin/env bash` for portable scripts and lint them with [ShellCheck and shfmt](shellcheck-shfmt.md).

## See Also
- [Bash](bash.md)
- [Bash Recipes](bash-recipes.md)
- [Shell Comparison](shell-comparison.md)
- [Starship Prompt](../tools/starship.md)
- [Modern CLI Tools](../tools/modern-cli-tools.md)

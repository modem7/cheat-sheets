# Fish
Fish is an interactive shell with autosuggestions, syntax highlighting and sensible defaults out of the box, but its scripting syntax is not POSIX-compatible. Use it as a friendly login shell and keep portable scripts in [Bash](bash.md). Pick between shells with [Shell Comparison](shell-comparison.md).

Documentation: [Fish Documentation](https://fishshell.com/docs/current/)
Project: [Fish shell](https://fishshell.com/)

Checked against fish 4.2.1. Examples were run unless marked `(unverified)`.

## Not Bash
BASH | FISH
---|---
`NAME=value` | `set NAME value`
`export NAME=value` | `set -x NAME value`
`unset NAME` | `set -e NAME`
`$(cmd)` | `(cmd)` or `$(cmd)`
`cmd1 && cmd2` | `cmd1; and cmd2` (`&&` also works in current fish)
`cmd1 \|\| cmd2` | `cmd1; or cmd2` (`\|\|` also works in current fish)
`if [[ -f f ]]; then ... fi` | `if test -f f; ...; end`
`for i in 1 2; do ... done` | `for i in 1 2; ...; end`
`$?` | `$status`
`${PIPESTATUS[@]}` | `$pipestatus`
`"$@"` | `$argv`
`{ cmd; }` | `begin; cmd; end`
`alias ll='ls -l'` | `alias ll 'ls -l'` (creates a function)
Unquoted `$var` is split on whitespace | Variables are never word-split; every variable is a list
`~/.bashrc` | `~/.config/fish/config.fish`

Fish has no `$((...))` arithmetic and no `<<EOF` here-docs; use `math` and `string` (below) for arithmetic and string handling.

## Variables
Every fish variable is a list, indexed from 1.

COMMAND | DESCRIPTION
---|---
`set a x y z` | Set a list
`set -l NAME value` | Local to the current block or function
`set -g NAME value` | Global to this session
`set -U NAME value` | Universal: shared by all sessions and kept across restarts
`set -x NAME value` | Exported to child processes (`set -gx` for global and exported)
`set -e NAME` | Erase
`set -q NAME` | Test whether set (exit status only)
`set -S NAME` | Show scope, export state and elements
`$a[1]`, `$a[-1]` | First and last element
`$a[2..3]` | Range
`count $a` | Number of elements
`set a $a w` | Append
`contains y $a` | Exit status 0 if `y` is in the list; add `-i` to print its index
`echo {a,b}c` | Brace expansion: `ac bc`

## PATH
COMMAND | DESCRIPTION
---|---
`fish_add_path /usr/local/bin` | Add to `PATH` persistently (stored in `fish_user_paths`, a universal variable); ignores directories that do not exist
`echo $PATH` | Prints one element per entry, not colon-separated

## Functions
```fish
function hi --description "say hi"
    echo hi $argv
end

hi there          # hi there
functions hi      # show the definition
funcsave hi       # save it to ~/.config/fish/functions/hi.fish
```
COMMAND | DESCRIPTION
---|---
`functions` | List functions
`functions -e NAME` | Erase a function
`funcsave NAME` | Write a function to its own autoloaded file
`funced NAME` | Edit a function in `$EDITOR`
`type NAME` | What `NAME` is (also shows alias definitions)
`command -q NAME` | Exit status 0 if the command exists (use with `and`)

Functions in `~/.config/fish/functions/NAME.fish` are autoloaded on first use, so there is no need to source them from `config.fish`.

## Abbreviations
An abbreviation expands in place as you type, so history shows the full command.

COMMAND | DESCRIPTION
---|---
`abbr -a gco "git checkout"` | Add an abbreviation
`abbr --show` | List them as `abbr` commands
`abbr -e gco` | Erase one

## Control Flow
```fish
if test -f /etc/passwd
    echo file
else if test -d /etc/passwd
    echo directory
end

for i in (seq 3)
    echo $i
end

while true
    break
end

switch $argv[1]
    case "f*"
        echo starts with f
    case "*"
        echo other
end
```
`test` supports the same operators as POSIX `test` (`-f`, `-d`, `-z`, `-n`, `-eq`, `=`). `not`, `and` and `or` are commands that combine exit statuses.

## string and math
`string` replaces most uses of `sed`, `cut` and `tr` on single values.

COMMAND | DESCRIPTION
---|---
`string upper hello`, `string lower ABC` | Change case
`string replace -a l L hello` | Replace all matches (`heLLo`)
`string match "*.txt" a.txt` | Glob match (prints the match)
`string match -r "h(.)l" hello` | Regex match, prints the match then each capture group
`string split , a,b,c` | Split into a list, one item per line
`string join - a b c` | Join arguments with a separator (`a-b-c`)
`string length hello` | Length in characters
`string sub -s 2 -l 2 hello` | Substring from position 2, length 2 (`el`)
`string trim "  x "` | Strip surrounding whitespace
`string pad -w 6 ab` | Pad to width 6 (right-aligned by default)
`string repeat -n 2 ab` | Repeat (`abab`)
`math 2 + 3 \* 4` | Arithmetic (escape `*` or quote the expression)
`math -s0 7 / 2` | Integer result (`3`); `-s` sets the number of decimal places
`math "sqrt 16"` | Functions available, e.g. `sqrt`
`read -l x` | Read a line into a local variable (`echo a \| read -l x`)

## Redirection and Pipes
COMMAND | DESCRIPTION
---|---
`cmd > file`, `cmd >> file` | Stdout to file, append
`cmd 2> file` | Stderr to file
`cmd &> file` | Stdout and stderr to a file
`cmd 2>&1 \| other` | Pipe both streams
`cmd \| tee file` | Show and save output
`diff (sort a \| psub) (sort b \| psub)` | Process substitution equivalent (`psub`)

## Interactive Features
KEY / COMMAND | DESCRIPTION
---|---
`→` or `Ctrl+F` | Accept the autosuggestion
`Alt+→` | Accept one word of the suggestion `(unverified)`
`Ctrl+R` | History search
`Alt+S` | Prepend `sudo` to the current command (or the previous one if the line is empty) `(unverified)`
`fish_config` | Browser-based theme and prompt picker
`history` | Show history
`history search TEXT` | Search history
`history delete --contains TEXT` | Delete matching entries
`fish_key_reader` | Show the key sequence a key press sends
`set -U fish_greeting` | Empty the welcome message (set it to nothing)
`status is-interactive` | Exit status 0 in an interactive session (guard `config.fish` with it)
`fish_vi_key_bindings`, `fish_default_key_bindings` | Switch to vi or back to the default bindings

## Configuration
```fish
# ~/.config/fish/config.fish
if status is-interactive
    abbr -a gco "git checkout"
    fish_add_path ~/.local/bin
end
```
Cross-shell tools such as [Starship Prompt](../tools/starship.md) support Fish: `starship init fish | source`. Other initialisers follow the same pattern, e.g. `zoxide init fish | source` (see [Modern CLI Tools](../tools/modern-cli-tools.md)). Both `init fish` forms are from the tools' documentation and were not run here `(unverified)`.

## See Also
- [Bash](bash.md)
- [Zsh](zsh.md)
- [Shell Comparison](shell-comparison.md)
- [Starship Prompt](../tools/starship.md)
- [Modern CLI Tools](../tools/modern-cli-tools.md)

# Shell Comparison
Side-by-side syntax and guidance for choosing between Bash, Zsh, Fish, Nushell and PowerShell. Read it to translate a command from one shell to another or to decide which shell suits a job; full details are in each shell's own sheet.

Documentation: [Bash Reference Manual](https://www.gnu.org/software/bash/manual/bash.html), [Zsh Manual](https://zsh.sourceforge.io/Doc/Release/), [Fish Documentation](https://fishshell.com/docs/current/), [The Nushell Book](https://www.nushell.sh/book/), [PowerShell Documentation](https://learn.microsoft.com/en-us/powershell/)

Bash, Zsh, Fish and PowerShell columns were run on Bash 5.3, Zsh 5.9, fish 4.2.1 and PowerShell 7.6. The Nushell column comes from its documentation and was not run; rows marked `(unverified)` were not confirmed.

## Which Shell
SHELL | BEST FOR | SCRIPTS PORTABLE?
---|---
[Bash](bash.md) | Servers, scripts, CI, anything others will run | Yes: the de facto standard on Linux
[Zsh](zsh.md) | Interactive use with powerful globbing and completion; macOS default | Mostly Bash-like, with different array and splitting rules
[Fish](fish.md) | Friendly interactive use with no configuration | No: its own syntax
[Nushell](nushell.md) | Working with structured data (tables, JSON, CSV) in a pipeline | No: its own syntax and still changing between releases
[PowerShell Cheat-Sheet](../windows/powershell.md) | Windows administration and anything that returns objects | Cross-platform, but not POSIX-like
POSIX `sh` (`dash`, BusyBox `ash`) | Minimal images and scripts that must run anywhere | Yes, with the fewest features; lint with `shellcheck -s sh` ([ShellCheck and shfmt](shellcheck-shfmt.md))

A common setup is an interactive shell of your choice with `#!/usr/bin/env bash` at the top of every script, so scripts behave the same everywhere.

## Syntax Side by Side
TASK | BASH AND ZSH | FISH | NUSHELL | POWERSHELL
---|---|---|---|---
Set a variable | `NAME=value` | `set NAME value` | `let name = "value"` | `$name = "value"`
Export / environment | `export NAME=value` | `set -gx NAME value` | `$env.NAME = "value"` | `$env:NAME = "value"`
Command substitution | `$(cmd)` | `(cmd)` | `(cmd)` | `$(cmd)`
List | `a=(x y z)` | `set a x y z` | `let a = [x y z]` | `$a = "x","y","z"`
First element | Bash `${a[0]}`, Zsh `$a[1]` | `$a[1]` | `$a.0` `(unverified)` | `$a[0]`
Last exit status | `$?` | `$status` | `$env.LAST_EXIT_CODE` (external commands) | `$LASTEXITCODE`
All script arguments | `"$@"` | `$argv` | `def main [...rest] { }` | `$args`
If statement | `if [[ -f f ]]; then ...; fi` | `if test -f f; ...; end` | `if ("f" \| path exists) { ... }` `(unverified)` | `if (Test-Path f) { ... }`
Loop | `for i in 1 2 3; do ...; done` | `for i in 1 2 3; ...; end` | `for i in 1..3 { ... }` | `foreach ($i in 1..3) { ... }`
Function | `f() { ...; }` | `function f; ...; end` | `def f [] { ... }` | `function f { ... }`
Run on error | `cmd \|\| other` | `cmd; or other` | `try { cmd } catch { other }` | `try { cmd } catch { other }`
Start-up file | `~/.bashrc`, `~/.zshrc` | `~/.config/fish/config.fish` | `config nu` opens it | `$PROFILE`

## Pipelines
SHELL | WHAT FLOWS BETWEEN COMMANDS
---|---
Bash, Zsh, Fish | Plain text (bytes); filter with [Grep](../linux/grep.md), [AWK](../linux/awk.md), [jq](../tools/jq.md)
Nushell | Structured data (tables, records, lists)
PowerShell | .NET objects

Mixing models is fine: Nushell and PowerShell both run external programs and capture their text output, and `jq` still works in Bash, Zsh and Fish for JSON.

## Switching Your Login Shell
COMMAND | DESCRIPTION
---|---
`echo "$SHELL"` | Login shell of the current user
`cat /etc/shells` | Shells the system allows as login shells
`chsh -s "$(command -v zsh)"` | Change your login shell (replace `zsh` with `fish` etc.); log out and in again
`command -v bash zsh fish nu pwsh` | Which of these shells are installed

The shell must be listed in `/etc/shells` before `chsh` accepts it. On Debian and Ubuntu these are in the `bash`, `zsh` and `fish` packages; Nushell and PowerShell come from their own project repositories or release downloads (see each project's install page). Changing the login shell of a service or automation account is rarely a good idea: leave it as `bash` or `sh`.

## Cross-Shell Tools
TOOL | USE
---|---
[Starship Prompt](../tools/starship.md) | One prompt for every shell
[Modern CLI Tools](../tools/modern-cli-tools.md) | `fzf`, `zoxide`, `eza` and friends, each with integrations for several shells
[tmux](../tools/tmux.md) | Terminal multiplexer, works with any shell
[ShellCheck and shfmt](shellcheck-shfmt.md) | Lint and format Bash and POSIX `sh` (it does not support Fish, Nushell or PowerShell)

## See Also
- [Scripting](scripting.md)
- [Bash](bash.md)
- [Bash Recipes](bash-recipes.md)
- [Zsh](zsh.md)
- [Fish](fish.md)
- [Nushell](nushell.md)
- [PowerShell Cheat-Sheet](../windows/powershell.md)

# Nushell
Nushell (`nu`) is a cross-platform shell where commands pass structured data (tables, records, lists) instead of text, so `ls` output can be filtered like a database. Use it for interactive data wrangling or readable scripts; it is not POSIX-compatible, so keep portable scripts in [Bash](bash.md). Pick between shells with [Shell Comparison](shell-comparison.md).

Documentation: [The Nushell Book](https://www.nushell.sh/book/), [Command reference](https://www.nushell.sh/commands/)
Project: [Nushell](https://www.nushell.sh/)

Checked against the official documentation for Nushell 0.116.1. Nushell was **not installed or run** when writing this sheet, and the project is pre-1.0, so commands change between releases: check `help COMMAND` on your version. Rows marked `(unverified)` were not found in the pages that were checked.

## Variables and Environment
COMMAND | DESCRIPTION
---|---
`let x = 1` | Immutable variable
`mut x = 1; $x += 1` | Mutable variable (`mut`, not `let mut`)
`const X = 1` | Constant, evaluated at parse time
`$env.NAME = "value"` | Set an environment variable (current scope)
`$env.NAME` | Read an environment variable
`load-env {A: "1", B: "2"}` | Set several at once from a record
`$env.PATH = ($env.PATH \| prepend '/opt/tool/bin')` | Prepend to `PATH` (a list, not a colon-separated string)
`use std/util "path add"; path add '/opt/tool/bin'` | Add to `PATH` with the standard library helper
`def --env cdd [] { cd /tmp }` | Command whose environment changes (such as `cd`) persist after it returns

## Strings
COMMAND | DESCRIPTION
---|---
`$"hello ($name)"` | Interpolation; escapes like `\n` work
`$'hello ($name)'` | Interpolation, no escape processing
`"a,b" \| split row ","` | Split into a list
`["a" "b"] \| str join "-"` | Join a list
`$s \| str replace "old" "new"` | Replace (first match; `--all` for all)
`$s \| str contains "x"` | Substring test
`"a b" \| parse "{first} {second}"` | Extract fields into a table

## Pipelines and Data
Everything below works on tables and lists. Row marked `(unverified)` means the command or flag was not read in the docs checked, although it is listed in the command reference.

COMMAND | DESCRIPTION
---|---
`ls \| where size > 1mb \| sort-by modified` | Files over 1 MB, oldest first `(unverified)`
`ls \| get name` | One column as a list `(unverified)`
`ls \| select name size` | Keep chosen columns `(unverified)`
`$t \| where col == "x"` | Filter rows `(unverified)`
`$t \| sort-by col` | Sort `(unverified)`
`$t \| group-by col` | Group `(unverified)`
`$list \| each {\|x\| $x * 2}` | Map with a closure `(unverified)`
`$list \| par-each {\|x\| $x * 2}` | Map in parallel (`--keep-order` keeps input order)
`$list \| reduce {\|it, acc\| $acc + $it}` | Fold `(unverified)`
`$t \| transpose` | Swap rows and columns
`1..5` | Range, end inclusive
`$in` | The pipeline input inside a block or command
`{\|x\| $x * 2}` | Closure syntax
`ps`, `sys host`, `du`, `which NAME` | Process table, host information, disk usage, locate a command

## Files and Formats
COMMAND | DESCRIPTION
---|---
`open file.json` | Read and parse by extension into structured data
`open --raw file.txt` | Read as plain text
`$data \| save out.json` | Write (format chosen by extension)
`$data \| save --append out.txt` | Append (`-a`)
`$data \| save --force out.json` | Overwrite an existing file (`-f`)
`$data \| to yaml` | Convert to YAML
`$data \| to nuon` | Convert to Nushell's own data notation
`http get https://example.com/api` | HTTP GET, parsed if the response is JSON
`from json`, `to json`, `from csv`, `to csv` | Convert between text and data (`(unverified)`: not read in the docs checked)

## External Commands and Errors
COMMAND | DESCRIPTION
---|---
`^ls -l` | Run the external command, bypassing a Nushell command of the same name
`^cmd \| complete` | Capture `stdout`, `stderr` and `exit_code` as a record
`$env.LAST_EXIT_CODE` | Exit code of the last external command
`do -i { ^cmd }` | Run a block and ignore errors (`--ignore-errors`)
`try { ... } catch {\|err\| ... }` | Handle errors
`timeit { ^cmd }` | Time a block
`print "text"` | Print to stdout
`input "Name: "` | Prompt for a line

## Control Flow
```nu
if $x > 1 { "big" } else { "small" }

match $x {
    1 => "one"
    _ => "other"
}

for i in 1..3 { print $i }

mut n = 0
while $n < 3 { $n += 1 }

loop { break }
```

## Custom Commands and Scripts
```nu
#!/usr/bin/env nu

# Greet someone
def greet [
    name: string          # required, typed
    count?: int           # optional
    --shout (-s)          # flag
    ...rest: string       # remaining arguments
] {
    let msg = $"hello ($name)"
    if $shout { $msg | str upcase } else { $msg }
}

def main [name: string] {
    greet $name
}
```
Run a script with `nu script.nu` or a one-liner with `nu -c 'ls'`. In a script, `def main` is the entry point and its parameters become the command-line arguments.

COMMAND | DESCRIPTION
---|---
`source file.nu` | Run a file in the current scope (parse-time path)
`use module.nu` | Load a module's commands
`overlay use module.nu` | Activate a module as a removable overlay (`overlay hide` removes it)
`alias ll = ls -l` | Alias (note the `=`)

## Configuration
COMMAND | DESCRIPTION
---|---
`config nu` | Open `config.nu` for editing
`config env` | Edit `env.nu`
`$nu.config-path` | Path to the active `config.nu` `(unverified)`
`$env.config.show_banner = false` | Hide the start-up banner
`$env.config.edit_mode = 'vi'` | Vi key bindings (`emacs` is the other common option)
`help commands` | List every command
`help COMMAND` | Help for one command
`history`, `history --long` | Show history (`--long` adds timestamps and more detail)
`Ctrl+R` | Open the history menu

For external completions, Nushell's docs show [carapace](https://carapace.sh/) wired up as `$env.config.completions.external.completer` (see the [custom completions](https://www.nushell.sh/book/custom_completions.html) page).

## See Also
- [Bash](bash.md)
- [Zsh](zsh.md)
- [Fish](fish.md)
- [Shell Comparison](shell-comparison.md)
- [jq](../tools/jq.md)
- [Starship Prompt](../tools/starship.md)

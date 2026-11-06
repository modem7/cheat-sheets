# ShellCheck and shfmt
`shellcheck` is a static analyser that finds quoting bugs, portability problems and common mistakes in shell scripts; `shfmt` is a formatter for the same scripts. Run both locally, in [[pre-commit]] and in CI. Language reference: [[bash]]; patterns that already pass: [[bash-recipes]].

Documentation: [ShellCheck wiki](https://www.shellcheck.net/wiki/) (each code has a page at `https://www.shellcheck.net/wiki/SC2086`), [shfmt](https://github.com/mvdan/sh#shfmt)

## Install
COMMAND | DESCRIPTION
---|---
`sudo apt install shellcheck shfmt` | Debian / Ubuntu (shfmt is in Ubuntu 22.04+ and Debian 12+)
`brew install shellcheck shfmt` | macOS / Linuxbrew
`go install mvdan.cc/sh/v3/cmd/shfmt@latest` | shfmt from source
`docker run --rm -v "$PWD:/mnt" koalaman/shellcheck:stable script.sh` | ShellCheck via Docker
`docker run --rm -v "$PWD:/mnt" -w /mnt mvdan/shfmt -d .` | shfmt via Docker
`pipx install shellcheck-py` | ShellCheck binary from PyPI (no system package needed)
`shellcheck --version`, `shfmt --version` | Verify

## ShellCheck Usage
COMMAND | DESCRIPTION
---|---
`shellcheck script.sh` | Lint one file
`shellcheck *.sh` | Lint several
`shellcheck -x script.sh` | Follow `source`d files
`shellcheck -s bash script.sh` | Force the dialect (`sh`, `bash`, `dash`, `ksh`)
`shellcheck -S warning script.sh` | Minimum severity: `error`, `warning`, `info`, `style`
`shellcheck -e SC2034,SC2154 script.sh` | Exclude codes
`shellcheck -o all script.sh` | Enable all optional checks
`shellcheck -o require-variable-braces script.sh` | Enable one optional check
`shellcheck --list-optional` | Show the optional checks
`shellcheck -f gcc script.sh` | Output format: `tty`, `gcc`, `json`, `json1`, `checkstyle`, `diff`, `quiet`
`shellcheck -f diff script.sh \| git apply` | Apply the auto-fixes it can offer
`git ls-files -z '*.sh' \| xargs -0 -r shellcheck` | Lint every tracked script
`shellcheck -P SCRIPTDIR -x script.sh` | Look for sourced files relative to the script

Exit code is 0 when clean and non-zero when anything at or above the severity is found, so it works directly as a CI gate.

## Common Codes and Fixes
CODE | PROBLEM | FIX
---|---|---
SC2086 | Unquoted variable: word splitting and globbing | `"$var"`
SC2046 | Unquoted command substitution | `"$(cmd)"`
SC2068 | Unquoted `$@` or `${arr[@]}` | `"$@"`, `"${arr[@]}"`
SC2164 | `cd` can fail and the script continues | `cd dir \|\| exit 1`
SC2155 | `local x=$(cmd)` hides the exit status | `local x; x="$(cmd)"`
SC2162 | `read` without `-r` mangles backslashes | `read -r line`
SC2006 | Backtick command substitution | `$(cmd)`
SC2181 | Checking `$?` indirectly | `if cmd; then` instead of `cmd; if [ $? -eq 0 ]`
SC2002 | Useless `cat` | `grep foo file` or `< file cmd`
SC2012 | Parsing `ls` output | Use a glob or `find -print0`
SC2015 | `A && B \|\| C` is not if/else (C runs if B fails) | Use `if A; then B; else C; fi`
SC2016 | Expression in single quotes will not expand | Use double quotes if you meant expansion; ignore for `awk`/`sed` programs
SC2034 | Variable appears unused | Remove, `export` it, or add a disable directive
SC2154 | Variable referenced but never assigned | Assign it or declare where it comes from
SC2148 | No shebang | Add `#!/usr/bin/env bash` or `# shellcheck shell=bash`
SC2115 | `rm -rf "$dir/"` can become `rm -rf /` when empty | `rm -rf "${dir:?}/"`
SC2207 | `arr=($(cmd))` splits badly | `mapfile -t arr < <(cmd)`
SC2129 | Several redirects to one file | `{ cmd1; cmd2; } >> file`
SC2001 | `sed` for a simple substitution | `${var//old/new}`
SC2064 | `trap "..."` expands variables now | Use single quotes: `trap 'rm "$f"' EXIT`
SC2145 | Mixing string and array in one argument | `"$@"` on its own
SC2317 | Command appears unreachable (often a function only called by `trap`) | Add a disable directive for that function
SC1090 / SC1091 | Cannot follow a `source`d file | `# shellcheck source=path`, or run with `-x`
SC3010 / SC3037 | Bashism in a `#!/bin/sh` script (`[[`, `echo -e`) | Use POSIX syntax or switch the shebang to bash

## Directives
Placed on the line above the command (or at the top of the file for the whole file).
```bash
#!/usr/bin/env bash
# shellcheck shell=bash
# shellcheck disable=SC2034          # whole file when placed before the first command

# shellcheck disable=SC2086
cmd $unquoted_on_purpose             # next command only

# shellcheck source=lib/common.sh
source "$DIR/lib/common.sh"          # tell it where the file is

# shellcheck source=/dev/null
source "$HOME/.profile"              # do not try to follow

# shellcheck disable=SC2317
cleanup() { rm -f "$tmp"; }          # only used via trap
trap cleanup EXIT
```
Always add a reason in a comment next to a `disable`.

## .shellcheckrc
Put it in the repo root (or `~/.config/shellcheckrc`) so every run, including the editor and CI, uses the same settings.
```ini
shell=bash
external-sources=true
source-path=SCRIPTDIR
enable=require-variable-braces
disable=SC2317
```

## shfmt Usage
FLAG | DESCRIPTION
---|---
`shfmt script.sh` | Print the formatted file
`-w` | Write the result back to the file
`-d` | Show a diff and exit non-zero if anything differs (CI check)
`-l` | List files whose formatting differs
`-i <N>` | Indent with N spaces (`0` = tabs, the default)
`-ci` | Indent `case` branches
`-bn` | Binary operators (`&&`, `\|`) may start a line
`-sr` | Add a space after redirect operators (`> file`)
`-kp` | Keep column alignment padding
`-fn` | Put the function opening brace on the next line
`-s` | Simplify code where safe
`-mn` | Minify
`-ln <DIALECT>` | Language: `auto` (default), `bash`, `posix`, `mksh`, `bats`
`-f` | Find shell scripts in the given directories
`shfmt -i 2 -ci -w .` | Format every shell file under the current directory with 2-space indents

Files are detected by extension (`.sh`, `.bash`) or shebang. With no flags shfmt reads `.editorconfig`, which is the easiest way to keep editor and CI in agreement:
```ini
# .editorconfig
[*.sh]
indent_style = space
indent_size = 2
switch_case_indent = true
binary_next_line = true
```
Explicit command-line flags override `.editorconfig`.

## CI
```yaml
# GitHub Actions
name: lint-shell
on: [push, pull_request]
jobs:
  shell:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: ShellCheck
        run: git ls-files -z '*.sh' | xargs -0 -r shellcheck -x
      - name: shfmt
        run: |
          sudo apt-get install -y shfmt
          git ls-files -z '*.sh' | xargs -0 -r shfmt -d
```
Pin action versions with a digest or let Renovate manage them. ShellCheck is already installed on GitHub-hosted Ubuntu runners; `shfmt` is not.

```yaml
# Woodpecker CI
steps:
  - name: shell-lint
    image: koalaman/shellcheck-alpine:stable
    commands:
      - find . -name '*.sh' -not -path './.git/*' -print0 | xargs -0 -r shellcheck -x
```
Local gate before every commit: [[pre-commit]] with the `shellcheck-py` and `shfmt` hooks.

# Bash
Bash is the default shell on most Linux servers and the language most homelab glue is written in. This sheet covers the syntax you reach for daily; ready-made patterns are in [Bash Recipes](bash-recipes.md), linting in [ShellCheck and shfmt](shellcheck-shfmt.md). For text tools see [Grep](../linux/grep.md), [SED Cheat-Sheet](../linux/sed.md), [AWK](../linux/awk.md) and [jq](../tools/jq.md).

Documentation: [Bash Reference Manual](https://www.gnu.org/software/bash/manual/bash.html)

## Script Skeleton
```bash
#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

main() {
  echo "hello ${1:-world}"
}

main "$@"
```

## Strict Mode
OPTION | DESCRIPTION
---|---
`set -e` | Exit when a command fails (not inside `if`, `&&`, `\|\|` or `while` conditions)
`set -u` | Error on unset variables
`set -o pipefail` | A pipeline fails if any stage fails, not just the last
`set -E` | ERR trap is inherited by functions and subshells
`set -x` | Trace every command (debugging)
`set +e` | Turn an option off again
`shopt -s nullglob` | Unmatched globs expand to nothing instead of themselves
`shopt -s globstar` | `**` matches recursively
`command \|\| true` | Allow one command to fail under `set -e`

`set -e` has many exceptions and is not a substitute for checking the commands that matter. `bash -n script.sh` checks syntax without running it.

## Variables
SYNTAX | DESCRIPTION
---|---
`NAME=value` | Assign (no spaces around `=`)
`"$NAME"` / `"${NAME}"` | Expand (always quote)
`export NAME=value` | Pass to child processes
`readonly NAME=value` | Constant
`local NAME=value` | Function-scoped variable
`declare -i N=5` | Integer
`declare -r`, `declare -x` | Read-only, export
`$(command)` | Command substitution
`$((A + B))` | Arithmetic
`$0`, `$1`...`$9`, `${10}` | Script name and positional arguments
`$#` | Number of arguments
`"$@"` | All arguments, each one preserved (use this)
`"$*"` | All arguments as one string
`$?` | Exit code of the last command
`$$` | PID of the shell
`$!` | PID of the last background job
`$RANDOM` | Random integer 0-32767
`$SECONDS` | Seconds since the shell started
`$LINENO`, `$FUNCNAME`, `$BASH_SOURCE` | Debug helpers
`read -r -p "Name: " NAME` | Prompt for input
`read -r -s -p "Password: " PW` | Silent input

## Quoting
SYNTAX | DESCRIPTION
---|---
`"$var"` | Expands variables and commands, no word splitting
`'$var'` | Literal text, nothing expands
`$'a\tb\n'` | ANSI-C quoting with escapes
`\$` | Escape a single character
`"$(cmd "$arg")"` | Quotes nest inside `$()`

Unquoted `$var` is split on whitespace and glob-expanded. Quote every expansion unless you specifically want splitting.

## Arrays
```bash
files=(a.txt "b c.txt" c.txt)
files+=(d.txt)
echo "${files[0]}"        # first element
echo "${files[@]}"        # all elements (quote it)
echo "${#files[@]}"       # length
echo "${files[@]:1:2}"    # slice: offset 1, length 2
for f in "${files[@]}"; do echo "$f"; done

mapfile -t lines < <(grep -v '^#' list.txt)   # file/command to array

declare -A ports=([web]=80 [ssh]=22)          # associative (Bash 4+)
ports[db]=5432
echo "${ports[web]}"
echo "${!ports[@]}"       # keys
echo "${ports[@]}"        # values
[[ -v ports[ssh] ]] && echo "key exists"
unset 'ports[web]'
for k in "${!ports[@]}"; do echo "$k=${ports[$k]}"; done
```

## Parameter Expansion
SYNTAX | DESCRIPTION
---|---
`${VAR:-default}` | Use default if unset or empty
`${VAR:=default}` | Assign default if unset or empty
`${VAR:?message}` | Exit with message if unset or empty
`${VAR:+value}` | `value` if VAR is set, else empty
`${#VAR}` | Length
`${VAR:2:5}` | Substring (offset, length)
`${VAR#pattern}` | Strip shortest prefix match
`${VAR##pattern}` | Strip longest prefix match (`${path##*/}` = basename)
`${VAR%pattern}` | Strip shortest suffix match
`${VAR%%pattern}` | Strip longest suffix match (`${file%.*}` = no extension)
`${VAR/old/new}` | Replace first match
`${VAR//old/new}` | Replace all matches
`${VAR/#old/new}`, `${VAR/%old/new}` | Replace at start / end
`${VAR^^}`, `${VAR,,}` | Upper / lower case (Bash 4+)
`${!PREFIX@}` | Names of variables starting with PREFIX
`${!REF}` | Indirect expansion (value of the variable named by REF)

## Conditionals
```bash
if [[ -f "$file" && -r "$file" ]]; then
  echo "readable file"
elif [[ -d "$file" ]]; then
  echo "directory"
else
  echo "missing"
fi

case "$1" in
  start|up)  echo "starting" ;;
  stop)      echo "stopping" ;;
  *)         echo "usage: $0 {start|stop}" >&2; exit 2 ;;
esac

[[ "$a" == prefix* ]]        # glob match (unquoted right side)
[[ "$a" =~ ^[0-9]+$ ]]       # regex match, groups in BASH_REMATCH
(( count > 3 )) && echo big  # arithmetic test
```

Prefer `[[ ]]` over `[ ]` in Bash: no word splitting, supports `&&`, `\|\|`, `==` patterns and `=~`.

### Test Operators
OPERATOR | TRUE WHEN
---|---
`-e <PATH>` | Exists
`-f <PATH>` | Regular file
`-d <PATH>` | Directory
`-L <PATH>` | Symlink
`-r`, `-w`, `-x <PATH>` | Readable, writable, executable
`-s <PATH>` | Exists and is not empty
`<A> -nt <B>`, `<A> -ot <B>` | A newer / older than B
`-z "$s"` | String is empty
`-n "$s"` | String is not empty
`"$a" == "$b"`, `!=` | String equal / not equal
`"$a" < "$b"` | String sorts before (inside `[[ ]]`)
`-eq -ne -lt -le -gt -ge` | Integer comparisons
`-v NAME` | Variable is set
`! <EXPR>` | Negate

## Loops
```bash
for i in 1 2 3; do echo "$i"; done
for i in {1..10..2}; do echo "$i"; done          # 1 3 5 7 9
for ((i = 0; i < 5; i++)); do echo "$i"; done
for f in *.log; do gzip "$f"; done

while [[ $n -lt 5 ]]; do ((n++)); done
until ping -c1 -W1 host >/dev/null; do sleep 2; done

while IFS= read -r line; do echo "$line"; done < file.txt
break; continue          # leave the loop / skip to the next iteration
```
`((n++))` returns exit code 1 when `n` was 0, which kills a `set -e` script. Use `n=$((n + 1))` instead.

## Functions
```bash
greet() {
  local name="${1:?name required}"
  echo "Hello, $name"
  return 0                 # return codes only; output goes to stdout
}

greeting="$(greet Bob)"    # capture stdout
greet Bob || echo "failed"
```
Variables are global unless declared `local`. Functions share the script's `$@` only if you pass it (`main "$@"`).

## trap
```bash
cleanup() { rm -rf -- "$tmpdir"; }
trap cleanup EXIT                         # runs on any exit
trap 'echo "line $LINENO failed" >&2' ERR # with set -E
trap 'echo interrupted; exit 130' INT TERM
trap - EXIT                               # remove a trap
trap -l                                   # list signals
```
SIGNAL | MEANING
---|---
`EXIT` | Shell exit (pseudo-signal, always runs)
`ERR` | A command failed
`INT` | Ctrl+C
`TERM` | Default `kill`
`HUP` | Terminal closed
`DEBUG` | Before every command

`SIGKILL` (`kill -9`) cannot be trapped, so cleanup does not run.

## getopts
```bash
usage() { echo "Usage: $0 [-v] [-n NAME] FILE..." >&2; exit 2; }

verbose=0 name=""
while getopts ":vn:h" opt; do
  case "$opt" in
    v) verbose=1 ;;
    n) name="$OPTARG" ;;
    h) usage ;;
    :) echo "-$OPTARG needs an argument" >&2; usage ;;
    \?) echo "unknown option -$OPTARG" >&2; usage ;;
  esac
done
shift $((OPTIND - 1))     # remaining args are the positional ones
```
`getopts` handles short options only. For `--long` options see the template in [Bash Recipes](bash-recipes.md).

## Here-docs and Here-strings
```bash
cat <<EOF                 # variables expand
Hello $USER
EOF

cat <<'EOF'               # quoted delimiter: no expansion
Literal $USER
EOF

cat <<-EOF                # <<- strips leading TABs (not spaces)
	indented
	EOF

grep -c foo <<< "$text"   # here-string
ssh host bash -s <<'EOF'  # run a script remotely
uptime
EOF
```

## Redirection
SYNTAX | DESCRIPTION
---|---
`cmd > file` | Stdout to file (overwrite)
`cmd >> file` | Append stdout
`cmd 2> file` | Stderr to file
`cmd > file 2>&1` | Both to file (order matters)
`cmd &> file` | Both to file (Bash shorthand)
`cmd 2>&1 \| other` | Pipe stdout and stderr
`cmd \|& other` | Same, shorter
`cmd < file` | Read stdin from file
`cmd > /dev/null 2>&1` | Discard all output
`cmd >&2` | Send stdout to stderr (error messages)
`cmd \| tee file` | Show and save output
`cmd \| tee -a file` | Show and append
`exec > >(tee -a log.txt) 2>&1` | Log everything the rest of the script prints
`set -o noclobber` | Refuse `>` over existing files (override with `>\|`)

## Process Substitution
SYNTAX | DESCRIPTION
---|---
`diff <(sort a) <(sort b)` | Treat command output as a file
`while read -r l; do ...; done < <(cmd)` | Loop over output without a subshell (variables survive)
`tee >(grep ERR > errors.log) > all.log` | Feed output to a command as a file

`cmd \| while read ...` runs the loop in a subshell, so variables set inside are lost. Use `< <(cmd)` instead.

## Exit Codes
CODE | MEANING
---|---
`0` | Success
`1` | General error
`2` | Misuse of shell builtin or bad usage (conventional for usage errors)
`126` | Found but not executable
`127` | Command not found
`128+N` | Killed by signal N (`130` = Ctrl+C, `137` = SIGKILL, `143` = SIGTERM)

```bash
if ! grep -q foo file; then echo "no match"; fi
cmd; rc=$?                       # capture the code
echo "${PIPESTATUS[@]}"          # exit code of each pipeline stage
exit 3                           # your own code
```

## Misc
COMMAND | DESCRIPTION
---|---
`source file.sh` / `. file.sh` | Run a file in the current shell
`"$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"` | Directory of the running script
`command -v <CMD> >/dev/null` | Test whether a command exists (portable)
`printf '%s\n' "$var"` | Safe printing (`echo` mangles `-n`, `-e` and backslashes)
`printf '%05d %-10s\n' 7 name` | Formatted output
`$(< file)` | Read a whole file without `cat`
`wait` | Wait for background jobs
`cmd &` | Run in the background
`nohup cmd &` | Keep running after logout
`timeout 30 cmd` | Kill after 30 seconds
`env -i bash --noprofile --norc` | Clean shell for testing
`type -a <CMD>` | Show every definition of a name

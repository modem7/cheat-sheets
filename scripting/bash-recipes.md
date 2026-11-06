# Bash Recipes
Copy-paste patterns for scripts that run unattended: argument parsing, logging, locking, retries, safe temp files and parallelism. Syntax is explained in [Bash](bash.md); run [ShellCheck and shfmt](shellcheck-shfmt.md) over anything you paste in. Text processing lives in [Grep](../linux/grep.md), [SED Cheat-Sheet](../linux/sed.md), [AWK](../linux/awk.md) and [jq](../tools/jq.md); HTTP calls in [curl](../tools/curl.md).

## Argument Parsing Template (long and short options)
```bash
#!/usr/bin/env bash
set -Eeuo pipefail

usage() {
  cat <<EOF
Usage: ${0##*/} [-v|--verbose] [-n|--name NAME] [--dry-run] FILE...

  -n, --name NAME   Name to use (default: world)
  -v, --verbose     Verbose output
      --dry-run     Print actions instead of doing them
  -h, --help        Show this help
EOF
}

verbose=0 dry_run=0 name="world"
args=()
while (($#)); do
  case "$1" in
    -v|--verbose) verbose=1 ;;
    -n|--name)    name="${2:?--name needs a value}"; shift ;;
    --name=*)     name="${1#*=}" ;;
    --dry-run)    dry_run=1 ;;
    -h|--help)    usage; exit 0 ;;
    --)           shift; args+=("$@"); break ;;
    -*)           echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
    *)            args+=("$1") ;;
  esac
  shift
done
set -- "${args[@]}"
(($#)) || { echo "FILE required" >&2; usage >&2; exit 2; }
```

## Logging Functions
```bash
log()  { printf '%s [%s] %s\n' "$(date '+%F %T')" "$1" "${*:2}" >&2; }
info() { log INFO "$@"; }
warn() { log WARN "$@"; }
err()  { log ERROR "$@"; }
die()  { err "$@"; exit 1; }

# Colour only when stderr is a terminal
if [[ -t 2 ]]; then RED=$'\e[31m' RESET=$'\e[0m'; else RED='' RESET=''; fi
echo "${RED}failed${RESET}" >&2

# Also write everything to a log file
exec > >(tee -a "/var/log/${0##*/}.log") 2>&1
```
Send logs to stderr so stdout stays clean for data. To log to the system journal use `logger -t <TAG> "message"`.

## Lockfile with flock
Stops two copies of a script (for example two cron runs) overlapping. The lock is released automatically when the script exits, even on a crash.
```bash
exec 9>/var/lock/myscript.lock
flock -n 9 || { echo "already running" >&2; exit 1; }
# ... critical section ...
```

COMMAND | DESCRIPTION
---|---
`flock -n <LOCKFILE> <CMD>` | Run a command only if the lock is free (wrapper form, handy in crontab)
`flock -w 30 9` | Wait up to 30 seconds for the lock
`flock -x 9` / `flock -s 9` | Exclusive (default) / shared lock
`flock -u 9` | Release early

```text
# Crontab form
*/5 * * * * flock -n /var/lock/backup.lock /usr/local/bin/backup.sh
```

## Retry with Backoff
```bash
retry() {
  local max="$1" delay="$2" n=1
  shift 2
  until "$@"; do
    if ((n >= max)); then
      echo "failed after $n attempts: $*" >&2
      return 1
    fi
    echo "attempt $n failed, retrying in ${delay}s" >&2
    sleep "$delay"
    delay=$((delay * 2))
    n=$((n + 1))
  done
}

retry 5 2 curl -fsS https://example.com/health
```
`curl` has its own retry flags (`--retry 5 --retry-delay 2 --retry-connrefused`), see [curl](../tools/curl.md).

## Temp Files and Directories Safely
```bash
tmpdir="$(mktemp -d)"
trap 'rm -rf -- "$tmpdir"' EXIT
tmpfile="$(mktemp "$tmpdir/out.XXXXXX")"

# Atomic file replacement: write beside the target, then rename
tmp="$(mktemp "${target}.XXXXXX")"
generate_config > "$tmp"
chmod 644 "$tmp"
mv -- "$tmp" "$target"
```
Never use predictable names like `/tmp/out.$$`. `mktemp` creates the file with mode 600 and a random name.

## Idempotent Checks
Safe to run twice: check state first, then change it.
```bash
mkdir -p /opt/app                                 # no error if it exists
ln -sfn /opt/app/v2 /opt/app/current              # replace a symlink
id deploy &>/dev/null || useradd -m deploy        # create user once
command -v docker >/dev/null || install_docker    # install once
grep -qxF 'net.ipv4.ip_forward=1' /etc/sysctl.conf || echo 'net.ipv4.ip_forward=1' >> /etc/sysctl.conf
[[ -f "$dest" ]] && cmp -s "$src" "$dest" || install -m 644 "$src" "$dest"
systemctl is-active --quiet nginx || systemctl start nginx
```
`grep -qxF` matches the whole line as a fixed string, so you can append a line only when it is missing.

## Require Root (or a Tool)
```bash
if ((EUID != 0)); then
  echo "Run as root (try: sudo $0 $*)" >&2
  exit 1
fi

# Re-run with sudo automatically
((EUID == 0)) || exec sudo -- "$0" "$@"

# Required commands
for cmd in curl jq docker; do
  command -v "$cmd" >/dev/null || { echo "missing: $cmd" >&2; exit 1; }
done
```

## Parallelism with xargs -P
OPTION | DESCRIPTION
---|---
`-P <N>` | Run N processes in parallel (`-P 0` = as many as possible)
`-n <N>` | Arguments per command invocation
`-I {}` | Replace `{}` with each input item (implies one item per run)
`-0` | NUL-separated input (pair with `find -print0`)
`-r` | Do nothing on empty input (GNU)
`-t` | Print each command before running it

```bash
# Compress every log, 4 at a time, safe for odd filenames
find /var/log/app -name '*.log' -print0 | xargs -0 -r -P 4 -n 1 gzip

# Ping many hosts in parallel
xargs -a hosts.txt -P 10 -I {} sh -c 'ping -c1 -W1 {} >/dev/null && echo "{} up" || echo "{} down"'

# Run a shell function in parallel (export it first)
work() { echo "processing $1"; sleep 1; }
export -f work
printf '%s\n' item{1..8} | xargs -P 4 -I {} bash -c 'work "$1"' _ {}

# Plain Bash alternative: background jobs plus wait
for h in web1 web2 web3; do ssh "$h" uptime & done
wait
```
Output from parallel jobs interleaves. Have each job write its own file if order matters.

## Read Files Line by Line
```bash
while IFS= read -r line; do
  [[ -z "$line" || "$line" == \#* ]] && continue   # skip blanks and comments
  echo "line: $line"
done < input.txt

# Split into fields
while IFS=, read -r name ip port; do
  echo "$name -> $ip:$port"
done < hosts.csv

# Last line without a trailing newline is still processed
while IFS= read -r line || [[ -n "$line" ]]; do echo "$line"; done < input.txt

# Into an array
mapfile -t lines < input.txt

# Output of a command, keeping variables in the current shell
while IFS= read -r line; do count=$((count + 1)); done < <(some_command)
```
`IFS=` keeps leading and trailing whitespace and `-r` keeps backslashes. Loops that read stdin (for example `ssh`) swallow the rest of the file; add `< /dev/null` to those commands inside the loop.

## Confirm Prompt
```bash
confirm() {
  read -r -p "${1:-Continue?} [y/N] " reply
  [[ "$reply" =~ ^[Yy]$ ]]
}
confirm "Delete everything?" || exit 1
```

## Run a Command and Capture Both Output and Status
```bash
if output="$(some_command 2>&1)"; then
  echo "ok"
else
  rc=$?
  echo "failed ($rc): $output" >&2
fi
```
Assigning with `local out="$(cmd)"` hides the exit code of `cmd`. Declare first (`local out`), assign on the next line.

## Script Directory and Config Loading
```bash
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
[[ -f "$SCRIPT_DIR/.env" ]] && source "$SCRIPT_DIR/.env"

# Load KEY=VALUE pairs into the environment
set -a; source .env; set +a
```

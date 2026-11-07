#!/usr/bin/env python3
"""Flag real-looking public IPv4 addresses in tracked text files.

Usage: python3 scripts/check-ips.py [ROOT]

ROOT defaults to the repository root (the parent of scripts/).

Repo rule: no real IP addresses. Use placeholders or the documentation
ranges 192.0.2.0/24, 198.51.100.0/24 and 203.0.113.0/24.

Scans files from `git ls-files`. Skips binary files, site/static/,
this script and the allowlist file.

Never flagged:
  - documentation, loopback, 0.0.0.0/8, RFC 1918, 100.64.0.0/10,
    link-local, multicast, 240.0.0.0/4, 198.18.0.0/15;
  - contiguous netmasks (255.255.255.0) and wildcard masks (0.0.0.255);
  - a few well-known public DNS resolvers (see PUBLIC_RESOLVERS);
  - entries in .ip-allowlist at ROOT: one per line, `IP`, `CIDR`, or
    `IP-or-CIDR path-glob`. `#` comments and blank lines are ignored;
  - any line containing the marker `ip-scan: ignore`.

Prints `path:line: IP` and the trimmed line for each finding, then a
summary line. Exits 1 if anything was found, 0 if not, 2 on a usage
or setup error.
"""

import argparse
import fnmatch
import ipaddress
import os
import re
import subprocess
import sys

ALLOWLIST_NAME = ".ip-allowlist"
SELF_PATH = "scripts/check-ips.py"
SKIP_PREFIXES = ("site/static/",)
IGNORE_MARKER = "ip-scan: ignore"
CONTEXT_MAX = 120

ALLOWED_NETS = [
    ipaddress.ip_network(n)
    for n in (
        "192.0.2.0/24",
        "198.51.100.0/24",
        "203.0.113.0/24",
        "127.0.0.0/8",
        "0.0.0.0/8",
        "10.0.0.0/8",
        "172.16.0.0/12",
        "192.168.0.0/16",
        "100.64.0.0/10",
        "169.254.0.0/16",
        "224.0.0.0/4",
        "240.0.0.0/4",
        "198.18.0.0/15",
    )
]

PUBLIC_RESOLVERS = {
    ipaddress.ip_address(a)
    for a in (
        "1.1.1.1",
        "1.0.0.1",
        "9.9.9.9",
        "149.112.112.112",
        "8.8.8.8",
        "8.8.4.4",
        "208.67.222.222",
        "208.67.220.220",
    )
}

# Dotted quad not inside a longer dotted number or word, so
# 1.2.3.4.5 and v3.2.0.2 do not match. A trailing full stop is fine.
IP_RE = re.compile(
    r"(?<![\w.])"
    r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    r"(?!\w|\.\d)"
)

MASK32 = 0xFFFFFFFF


def is_mask(addr):
    """True for a contiguous netmask or wildcard mask."""
    v = int(addr)
    inv = ~v & MASK32
    return (inv & (inv + 1)) == 0 or (v & (v + 1)) == 0


def load_allowlist(path):
    """Return a list of (network, glob-or-None). Raises ValueError."""
    entries = []
    if not os.path.isfile(path):
        return entries
    with open(path, encoding="utf-8", errors="replace") as fh:
        for num, raw in enumerate(fh, 1):
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) > 2:
                raise ValueError(
                    "{}:{}: expected `IP [GLOB]`".format(ALLOWLIST_NAME, num)
                )
            try:
                net = ipaddress.IPv4Network(parts[0], strict=False)
            except ValueError:
                raise ValueError(
                    "{}:{}: bad IP or CIDR: {}".format(
                        ALLOWLIST_NAME, num, parts[0]
                    )
                )
            glob = parts[1] if len(parts) == 2 else None
            entries.append((net, glob))
    return entries


def is_allowed(addr, path, allowlist):
    if addr in PUBLIC_RESOLVERS or is_mask(addr):
        return True
    if any(addr in net for net in ALLOWED_NETS):
        return True
    for net, glob in allowlist:
        if addr in net and (glob is None or fnmatch.fnmatchcase(path, glob)):
            return True
    return False


def tracked_files(root):
    """Return sorted tracked paths (relative, forward slashes)."""
    out = subprocess.run(
        ["git", "-C", root, "ls-files", "-z"],
        check=True,
        stdout=subprocess.PIPE,
    ).stdout
    names = [n.decode("utf-8", "replace") for n in out.split(b"\0") if n]
    return sorted(set(names))


def read_text(full):
    """Return file text, or None if missing or binary."""
    try:
        with open(full, "rb") as fh:
            data = fh.read()
    except OSError:
        return None
    if b"\0" in data[:8192]:
        return None
    return data.decode("utf-8", errors="replace")


def context(line):
    text = line.strip()
    if len(text) > CONTEXT_MAX:
        text = text[: CONTEXT_MAX - 3] + "..."
    return text


def scan(text, path, allowlist):
    """Yield (line_number, ip, context) for each finding."""
    for num, line in enumerate(text.splitlines(), 1):
        if IGNORE_MARKER in line:
            continue
        for m in IP_RE.finditer(line):
            try:
                addr = ipaddress.IPv4Address(m.group(1))
            except ValueError:
                continue
            if not is_allowed(addr, path, allowlist):
                yield num, m.group(1), context(line)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Flag real-looking public IPv4 addresses in tracked "
        "files. Use 192.0.2.0/24, 198.51.100.0/24 or 203.0.113.0/24 "
        "instead. Allow exceptions in .ip-allowlist or with an "
        "`ip-scan: ignore` marker on the line."
    )
    parser.add_argument(
        "root",
        nargs="?",
        help="repository root (default: parent of scripts/)",
    )
    args = parser.parse_args(argv)

    default_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    root = os.path.abspath(args.root or default_root)
    if not os.path.isdir(root):
        print("error: not a directory: {}".format(root), file=sys.stderr)
        return 2

    try:
        allowlist = load_allowlist(os.path.join(root, ALLOWLIST_NAME))
    except ValueError as exc:
        print("error: {}".format(exc), file=sys.stderr)
        return 2

    try:
        names = tracked_files(root)
    except (OSError, subprocess.CalledProcessError) as exc:
        print("error: git ls-files failed: {}".format(exc), file=sys.stderr)
        return 2

    skip = {SELF_PATH, ALLOWLIST_NAME}
    findings = []
    checked = 0
    for name in names:
        if name in skip or name.startswith(SKIP_PREFIXES):
            continue
        text = read_text(os.path.join(root, name))
        if text is None:
            continue
        checked += 1
        for num, ip, ctx in scan(text, name, allowlist):
            findings.append((name, num, ip, ctx))

    for name, num, ip, ctx in findings:
        print("{}:{}: {}  {}".format(name, num, ip, ctx))

    if findings:
        bad = len({f[0] for f in findings})
        print(
            "FAIL: {} real-looking IP address(es) in {} of {} file(s)".format(
                len(findings), bad, checked
            )
        )
        return 1
    print(
        "OK: {} file(s) checked, no real-looking IP addresses".format(checked)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

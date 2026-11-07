#!/usr/bin/env python3
"""List cheat sheets that have not been touched for over N months.

Usage: python3 scripts/check-freshness.py [--months N] [--today YYYY-MM-DD]
           [--ignore-revs-file PATH] [--format {markdown,text}]
           [--fail-on-stale] [ROOT]

ROOT defaults to the repository root (the parent of scripts/).

Sheets are the tracked *.md files inside theme folders. Top-level files
(README.md, AGENTS.md, CLAUDE.md and so on), files named _template.md
and anything under docs/, site/, node_modules/ or a dot-directory
(.github/, .claude/, ...) are skipped.

A sheet's last-touched date is the author date of the most recent commit
that touched it, as `git log -1 --format=%aI -- FILE` would report,
found in a single pass over history. Paths are taken as they are now;
history from before a rename is not followed. Commits listed in the
ignore-revs file (default .freshness-ignore-revs at ROOT, if present)
are skipped, so bulk edits do not reset every sheet's date (a sheet
touched only by ignored commits keeps the latest of those). Dates are
compared as UTC calendar dates. Age in months is days / 30.4375, floored.

Output is Markdown (for an issue body) or plain text on stdout. Warnings
go to stderr.

The functions last_touched, load_ignored and is_stale are also imported by
site/scripts/prepare-content.py to date the website's sheets.

Exits 0 when the scan worked, whether or not sheets are stale. With
--fail-on-stale, exits 1 if any sheet is stale. Exits 2 on a usage
error or a git failure, including a shallow clone (CI needs
fetch-depth: 0).
"""

import argparse
import datetime
import math
import os
import subprocess
import sys

DEFAULT_IGNORE_REVS = ".freshness-ignore-revs"
SKIP_DIRS = {"docs", "site", "node_modules"}
SKIP_NAMES = {"_template.md"}
DAYS_PER_MONTH = 30.4375
# Marks the start of each commit record in git log output.
SENTINEL = "\x01"


class GitError(Exception):
    pass


def git(root, *args):
    """Run git in root and return stdout, raising GitError on failure."""
    cmd = [
        "git",
        "-C", root,
        "-c", "core.quotePath=false",
        "-c", "log.showSignature=false",
        *args,
    ]
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", check=False
        )
    except OSError as exc:
        raise GitError(f"cannot run git: {exc}") from exc
    if proc.returncode != 0:
        msg = proc.stderr.strip() or f"exit status {proc.returncode}"
        raise GitError(f"git {' '.join(args)}: {msg}")
    return proc.stdout


def is_sheet(path):
    """True if a repo-relative path is a cheat sheet."""
    parts = path.split("/")
    if len(parts) < 2 or not path.endswith(".md"):
        return False
    if parts[-1] in SKIP_NAMES:
        return False
    for part in parts[:-1]:
        if part.startswith(".") or part in SKIP_DIRS:
            return False
    return True


def list_sheets(root):
    out = git(root, "ls-files", "-z", "--", "*.md")
    return sorted(p for p in out.split("\0") if p and is_sheet(p))


def read_ignore_revs(path):
    """Return the SHA prefixes listed in an ignore-revs file."""
    revs = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.split("#", 1)[0].strip()
            if line:
                revs.append(line.lower())
    return revs


def resolve_revs(root, revs, source):
    """Resolve SHA prefixes to full commit SHAs. Warn about bad ones."""
    full = set()
    for rev in revs:
        try:
            sha = git(root, "rev-parse", "--verify", "--quiet",
                      f"{rev}^{{commit}}").strip()
        except GitError:
            sha = ""
        if sha:
            full.add(sha)
        else:
            print(f"warning: {source}: {rev}: not a commit in this "
                  "repository, ignored", file=sys.stderr)
    return full


def load_ignored(root, revs_path=None):
    """Return the full SHAs of the commits to skip.

    revs_path defaults to DEFAULT_IGNORE_REVS at root, if it exists.
    Unknown SHAs are warned about on stderr and dropped. Raises OSError
    if the file cannot be read.
    """
    if revs_path is None:
        default = os.path.join(root, DEFAULT_IGNORE_REVS)
        if not os.path.isfile(default):
            return set()
        revs_path = default
    revs = read_ignore_revs(revs_path)
    return resolve_revs(root, revs, revs_path)


def last_touched(root, sheets, ignored):
    """Map each sheet to the UTC date of its latest non-ignored commit.

    A sheet touched only by ignored commits falls back to the latest of
    those, so it is still reported rather than dropped.
    """
    wanted = set(sheets)
    found = {}
    fallback = {}
    out = git(
        root, "log", "--no-color", "--name-only",
        f"--format={SENTINEL}%H %aI", "HEAD",
    )
    sha, when = None, None
    for line in out.splitlines():
        if line.startswith(SENTINEL):
            sha, stamp = line[1:].split(" ", 1)
            when = (datetime.datetime.fromisoformat(stamp)
                    .astimezone(datetime.timezone.utc).date())
            continue
        if not line or line not in wanted or line in found:
            continue
        if sha in ignored:
            fallback.setdefault(line, when)
            continue
        found[line] = when
        if len(found) == len(wanted):
            break
    for path, when in fallback.items():
        found.setdefault(path, when)
    return found


def is_stale(when, today, months=12):
    """True if when is more than months (of DAYS_PER_MONTH) before today."""
    return (today - when).days > months * DAYS_PER_MONTH


def months_between(earlier, later):
    return math.floor((later - earlier).days / DAYS_PER_MONTH)


def render_markdown(stale, total, months):
    if not stale:
        return (f"All {total} sheets were touched in the last "
                f"{months} months.\n")
    lines = [
        "## Stale cheat sheets",
        "",
        f"{len(stale)} of {total} sheets not touched in over "
        f"{months} months.",
        "",
        "SHEET | LAST TOUCHED | AGE (MONTHS)",
        "--- | --- | ---",
    ]
    for path, when, age in stale:
        lines.append(f"`{path}` | {when} | {age}")
    return "\n".join(lines) + "\n"


def render_text(stale, total, months):
    if not stale:
        return (f"All {total} sheets were touched in the last "
                f"{months} months.\n")
    lines = [
        "Stale cheat sheets",
        f"{len(stale)} of {total} sheets not touched in over "
        f"{months} months.",
        "",
    ]
    width = max(len("SHEET"), *(len(p) for p, _, _ in stale))
    lines.append(f"{'SHEET':<{width}}  LAST TOUCHED  AGE (MONTHS)")
    for path, when, age in stale:
        lines.append(f"{path:<{width}}  {str(when):<12}  {age}")
    return "\n".join(lines) + "\n"


def parse_date(value):
    try:
        return datetime.date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"invalid date {value!r}, expected YYYY-MM-DD") from exc


def non_negative(value):
    try:
        n = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid number {value!r}") from exc
    if n < 0:
        raise argparse.ArgumentTypeError("must be 0 or more")
    return n


def build_parser():
    parser = argparse.ArgumentParser(
        description="List cheat sheets not touched for over N months, "
        "using git history.",
    )
    parser.add_argument(
        "root", nargs="?", metavar="ROOT",
        help="repository root (default: the parent of scripts/)",
    )
    parser.add_argument(
        "--months", type=non_negative, default=12, metavar="N",
        help="flag sheets older than N months (default: 12)",
    )
    parser.add_argument(
        "--today", type=parse_date, metavar="YYYY-MM-DD",
        help="date to measure age from (default: today, UTC)",
    )
    parser.add_argument(
        "--ignore-revs-file", metavar="PATH",
        help="file of commit SHAs to skip, one per line, # comments "
        f"(default: {DEFAULT_IGNORE_REVS} at ROOT, if it exists)",
    )
    parser.add_argument(
        "--format", choices=("markdown", "text"), default="markdown",
        help="output format (default: markdown)",
    )
    parser.add_argument(
        "--fail-on-stale", action="store_true",
        help="exit 1 if any sheet is stale",
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    root = args.root or os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))
    today = args.today or datetime.datetime.now(datetime.timezone.utc).date()

    try:
        shallow = git(root, "rev-parse", "--is-shallow-repository").strip()
        if shallow == "true":
            print("error: this is a shallow clone, so last-touched dates "
                  "would be wrong. Fetch full history (in GitHub Actions, "
                  "set fetch-depth: 0 on actions/checkout).",
                  file=sys.stderr)
            return 2

        try:
            ignored = load_ignored(root, args.ignore_revs_file)
        except OSError as exc:
            print(f"error: cannot read ignore-revs file: {exc}",
                  file=sys.stderr)
            return 2

        sheets = list_sheets(root)
        dates = last_touched(root, sheets, ignored)
    except GitError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    stale = []
    for path in sheets:
        when = dates.get(path)
        if when is None:
            print(f"warning: {path}: no commit found (not committed yet), "
                  "skipped", file=sys.stderr)
            continue
        if is_stale(when, today, args.months):
            stale.append((path, when, months_between(when, today)))
    stale.sort(key=lambda item: (item[1], item[0]))

    render = render_markdown if args.format == "markdown" else render_text
    sys.stdout.write(render(stale, len(sheets), args.months))

    if args.fail_on_stale and stale:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

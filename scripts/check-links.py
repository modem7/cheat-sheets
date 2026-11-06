#!/usr/bin/env python3
"""Check links and basic structure in a Markdown cheat-sheet repo.

Usage: python3 scripts/check-links.py [ROOT]

ROOT defaults to the repository root (the parent of scripts/).

Checks every *.md file under ROOT (dot-directories and node_modules
are skipped) for:
  - wikilinks ([[name]], [[name|alias]], [[name#heading]],
    [[name#heading|alias]]) whose name matches no Markdown basename;
  - relative Markdown links and images whose target does not exist;
  - files that are empty or contain only a single heading;
  - duplicate basenames, since wikilinks resolve by basename.

Links inside fenced code blocks and inline code spans are ignored.
Fragments (#anchor) are stripped but not checked.

Prints one `path:line: message` per problem, then a summary line.
Exits 1 if any problem was found, 0 if none, 2 on a usage error.
"""

import os
import re
import sys
from urllib.parse import unquote

SKIP_DIRS = {"node_modules"}

FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}(\s|$)")
WIKILINK_RE = re.compile(r"\[\[([^\[\]|#]*)(?:#[^\[\]|]*)?(?:\|[^\[\]]*)?\]\]")
# Link text allows one level of nested brackets, e.g. [![img](a)](b).
LINK_RE = re.compile(
    r"!?\[(?:[^\[\]]|\[[^\[\]]*\])*\]"
    r"\(\s*(<[^>\n]*>|[^)\s]+)(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\s*\)"
)
SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
BACKTICKS_RE = re.compile(r"`+")


def find_markdown(root):
    """Return sorted paths of all .md files under root."""
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(
            d for d in dirnames if not d.startswith(".") and d not in SKIP_DIRS
        )
        for name in filenames:
            if name.endswith(".md"):
                found.append(os.path.join(dirpath, name))
    return sorted(found)


def strip_inline_code(line):
    """Blank out inline code spans (matching backtick runs) in a line."""
    out = []
    pos = 0
    while True:
        m = BACKTICKS_RE.search(line, pos)
        if not m:
            out.append(line[pos:])
            break
        run = m.group(0)
        close = re.compile(r"(?<!`)" + re.escape(run) + r"(?!`)")
        end = close.search(line, m.end())
        if not end:
            # Unmatched run is literal text; keep scanning after it.
            out.append(line[pos:m.end()])
            pos = m.end()
            continue
        out.append(line[pos:m.start()])
        out.append(" " * (end.end() - m.start()))
        pos = end.end()
    return "".join(out)


def prose_lines(lines):
    """Yield (line_number, text) for lines outside fences, code spans removed."""
    fence = None
    for num, line in enumerate(lines, 1):
        m = FENCE_RE.match(line)
        if fence is None:
            if m:
                marker, info = m.group(1), m.group(2)
                if not (marker[0] == "`" and "`" in info):
                    fence = marker
                    continue
            yield num, strip_inline_code(line)
        else:
            if (
                m
                and m.group(1)[0] == fence[0]
                and len(m.group(1)) >= len(fence)
                and not m.group(2).strip()
            ):
                fence = None


def link_target(raw):
    """Return the local path for a link target, or None if it is not checked."""
    if raw.startswith("<") and raw.endswith(">"):
        raw = raw[1:-1]
    raw = raw.strip()
    if not raw or raw.startswith(("#", "/")) or SCHEME_RE.match(raw):
        return None
    for sep in ("#", "?"):
        raw = raw.split(sep, 1)[0]
    path = unquote(raw)
    return path or None


def check_structure(text):
    """Return a message if the file is empty or title-only, else None."""
    content = [ln for ln in text.splitlines() if ln.strip()]
    if not content:
        return "file is empty"
    if len(content) == 1 and HEADING_RE.match(content[0]):
        return "file has only a title and no content"
    return None


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) > 1:
        print("usage: check-links.py [ROOT]", file=sys.stderr)
        return 2
    default_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    root = os.path.abspath(args[0] if args else default_root)
    if not os.path.isdir(root):
        print("error: not a directory: {}".format(root), file=sys.stderr)
        return 2

    files = find_markdown(root)

    def rel(path):
        return os.path.relpath(path, root).replace(os.sep, "/")

    stems = {}
    for path in files:
        stems.setdefault(os.path.basename(path)[:-3], []).append(path)

    problems = []
    for stem, paths in stems.items():
        if len(paths) > 1:
            names = [rel(p) for p in paths]
            for name in names:
                others = ", ".join(n for n in names if n != name)
                problems.append(
                    (name, 1, "duplicate basename '{}' (also: {})".format(stem, others))
                )

    for path in files:
        name = rel(path)
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()

        msg = check_structure(text)
        if msg:
            problems.append((name, 1, msg))

        base = os.path.dirname(path)
        for num, line in prose_lines(text.splitlines()):
            for m in WIKILINK_RE.finditer(line):
                target = m.group(1).strip()
                if target and target not in stems:
                    problems.append(
                        (name, num, "broken wikilink [[{}]]".format(target))
                    )
            for m in LINK_RE.finditer(line):
                target = link_target(m.group(1))
                if target is None:
                    continue
                if not os.path.exists(os.path.join(base, target)):
                    problems.append(
                        (name, num, "broken link: {}".format(m.group(1)))
                    )

    problems.sort()
    for name, num, msg in problems:
        print("{}:{}: {}".format(name, num, msg))

    if problems:
        bad = len({p[0] for p in problems})
        print(
            "FAIL: {} problem(s) in {} of {} file(s)".format(
                len(problems), bad, len(files)
            )
        )
        return 1
    print("OK: {} file(s) checked, no problems".format(len(files)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

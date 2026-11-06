#!/usr/bin/env python3
"""Check links and basic structure in a Markdown cheat-sheet repo.

Usage: python3 scripts/check-links.py [ROOT]

ROOT defaults to the repository root (the parent of scripts/).

Checks every *.md file under ROOT (dot-directories and node_modules
are skipped) for:
  - wikilinks ([[name]] and variants), which are not allowed; use
    relative Markdown links instead. POSIX classes such as [[:alpha:]]
    are not flagged;
  - relative Markdown links and images whose target does not exist;
  - fragments (#anchor) on links to .md files, including same-file
    links, that match no heading in the target (GitHub-style slugs);
  - files that are empty or contain only a single heading.

Links inside fenced code blocks and inline code spans are ignored.
Fragments on non-.md targets and external URLs are not checked.

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
ATX_RE = re.compile(r"^ {0,3}#{1,6}(?:[ \t]+(.*?))?[ \t]*$")
CLOSING_HASHES_RE = re.compile(r"(?:^|[ \t]+)#+$")
# A [[ not followed by ':' so POSIX classes like [[:alpha:]] pass.
WIKILINK_RE = re.compile(r"\[\[(?!:)([^\[\]\n]*)\]\]")
# Link text allows one level of nested brackets, e.g. [![img](a)](b).
LINK_RE = re.compile(
    r"!?\[(?:[^\[\]]|\[[^\[\]]*\])*\]"
    r"\(\s*(<[^>\n]*>|[^)\s]+)(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\s*\)"
)
SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
BACKTICKS_RE = re.compile(r"`+")
CODE_SPAN_RE = re.compile(r"(`+)(.+?)(?<!`)\1(?!`)")
INLINE_LINK_RE = re.compile(r"!?\[([^\[\]]*)\]\([^)]*\)")
HTML_TAG_RE = re.compile(r"<[^>]+>")
# Underscores only count as emphasis at a word boundary.
EMPH_UNDERSCORE_RE = re.compile(r"(?<![^\W_])_+|_+(?![^\W_])")
SLUG_STRIP_RE = re.compile(r"[^\w\- ]")


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


def unfenced_lines(lines):
    """Yield (line_number, text) for raw lines outside fenced code blocks."""
    fence = None
    for num, line in enumerate(lines, 1):
        m = FENCE_RE.match(line)
        if fence is None:
            if m:
                marker, info = m.group(1), m.group(2)
                if not (marker[0] == "`" and "`" in info):
                    fence = marker
                    continue
            yield num, line
        else:
            if (
                m
                and m.group(1)[0] == fence[0]
                and len(m.group(1)) >= len(fence)
                and not m.group(2).strip()
            ):
                fence = None


def prose_lines(lines):
    """Yield (line_number, text) for lines outside fences, code spans removed."""
    for num, line in unfenced_lines(lines):
        yield num, strip_inline_code(line)


def heading_text(text):
    """Return heading text with inline markup removed, code content kept."""
    parts = []
    pos = 0
    for m in CODE_SPAN_RE.finditer(text):
        parts.append(_strip_markup(text[pos:m.start()]))
        parts.append(m.group(2).strip())
        pos = m.end()
    parts.append(_strip_markup(text[pos:]))
    return "".join(parts)


def _strip_markup(text):
    """Remove links, HTML tags and emphasis markers from non-code text."""
    prev = None
    while prev != text:
        prev = text
        text = INLINE_LINK_RE.sub(r"\1", text)
    text = HTML_TAG_RE.sub("", text)
    text = text.replace("*", "")
    return EMPH_UNDERSCORE_RE.sub("", text)


def slugify(text):
    """Return a GitHub-style anchor slug for heading text."""
    slug = SLUG_STRIP_RE.sub("", heading_text(text).strip().lower())
    return slug.replace(" ", "-")


def heading_anchors(text):
    """Return the set of anchors for ATX headings outside fences."""
    anchors = set()
    counts = {}
    for _, line in unfenced_lines(text.splitlines()):
        m = ATX_RE.match(line)
        if not m:
            continue
        body = CLOSING_HASHES_RE.sub("", m.group(1) or "")
        base = slugify(body)
        slug = base
        # Same scheme as github-slugger: first bare, then -1, -2, ...
        while slug in counts:
            counts[base] += 1
            slug = "{}-{}".format(base, counts[base])
        counts[slug] = 0
        anchors.add(slug)
    return anchors


def link_target(raw):
    """Return (path, fragment) for a link target, or None if not checked.

    path is "" for a same-file link such as #heading. fragment is None
    when the target has no #.
    """
    if raw.startswith("<") and raw.endswith(">"):
        raw = raw[1:-1]
    raw = raw.strip()
    if not raw or raw.startswith("/") or SCHEME_RE.match(raw):
        return None
    fragment = None
    if "#" in raw:
        raw, fragment = raw.split("#", 1)
    raw = raw.split("?", 1)[0]
    path = unquote(raw)
    if not path and fragment is None:
        return None
    return path, fragment


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

    anchor_cache = {}

    def anchors_for(path):
        key = os.path.realpath(path)
        if key not in anchor_cache:
            with open(key, encoding="utf-8", errors="replace") as fh:
                anchor_cache[key] = heading_anchors(fh.read())
        return anchor_cache[key]

    problems = []
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
                problems.append(
                    (
                        name,
                        num,
                        "wikilink [[{}]] not allowed, use a relative "
                        "Markdown link".format(m.group(1)),
                    )
                )
            for m in LINK_RE.finditer(line):
                parsed = link_target(m.group(1))
                if parsed is None:
                    continue
                target, fragment = parsed
                full = os.path.join(base, target) if target else path
                if not os.path.exists(full):
                    problems.append(
                        (name, num, "broken link: {}".format(m.group(1)))
                    )
                    continue
                if not fragment:
                    continue
                if not (os.path.isfile(full) and full.endswith(".md")):
                    continue
                if unquote(fragment).lower() not in anchors_for(full):
                    problems.append(
                        (name, num, "broken anchor: {}".format(m.group(1)))
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

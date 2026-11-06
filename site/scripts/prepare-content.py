#!/usr/bin/env python3
"""Prepare the cheat sheets for Hugo.

The sheets are plain Markdown with Obsidian-style [[wikilinks]] and no front
matter. Hugo cannot parse wikilinks, so this script writes transformed copies
of every sheet into a build directory that Hugo mounts as its content dir.

For each sheet it:
  * adds YAML front matter (title, description, and weight 1 for a section's
    lead sheet such as docker/docker.md) unless the file already has some;
  * turns [[wikilinks]] into normal relative Markdown links, leaving code
    fences, inline code, HTML comments and ![[embeds]] alone;
  * marks unresolved links with <span class="wikilink-missing"> and reports
    them.

Usage:
  prepare-content.py [--src DIR] [--out DIR] [--strict] [--watch]

  --src     Repository root to read sheets from (default: parent of site/).
  --out     Output content dir (default: site/.build/content). Must be
            inside site/.build/ because it is wiped on every run.
  --strict  Exit 1 if any link is unresolved or any basename is duplicated.
            Ignored in watch mode.
  --watch   After the first build, poll the sources every second and
            rebuild on change. Ctrl-C to stop.

Sources are every *.md under --src, except root-level files (README.md),
anything under a dot folder, the top-level site/ dir and node_modules/.
Python 3.9+, standard library only.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import posixpath
import re
import shutil
import signal
import sys
import tempfile
import time
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
SITE_DIR = SCRIPT_DIR.parent
REPO_ROOT = SITE_DIR.parent
BUILD_DIR = SITE_DIR / ".build"

DESC_MAX = 160
POLL_SECONDS = 1.0

# --- Regexes ---------------------------------------------------------------

# Optional blockquote markers, indentation and a list marker before a fence.
FENCE_PREFIX = r"^((?:[ \t]*>)*[ \t]*(?:(?:[-*+]|\d{1,9}[.)])[ \t]+)?)"
FENCE_OPEN_RE = re.compile(FENCE_PREFIX + r"(`{3,}|~{3,})(.*)$")
QUOTE_PREFIX_RE = re.compile(r"^(?:[ \t]*>)*[ \t]*")
WIKILINK_RE = re.compile(r"(?<!!)\[\[([^\[\]\n]+?)\]\]")
ALIAS_SPLIT_RE = re.compile(r"\\?\|")
INLINE_TOKEN_RE = re.compile(r"`+|<!--")
H1_RE = re.compile(r"^ {0,3}#[ \t]+(.+?)(?:[ \t]+#+)?[ \t]*$")
HEADING_RE = re.compile(r"^ {0,3}#{1,6}(?:[ \t]|$)")
LIST_RE = re.compile(r"^\s*(?:[-*+]|\d{1,9}[.)])(?:\s|$)")
HR_RE = re.compile(r"^\s*([-*_])(?:\s*\1){2,}\s*$")
TABLE_DELIM_RE = re.compile(
    r"^\s*\|?\s*:?-+:?\s*(?:\|\s*:?-+:?\s*)*\|?\s*$"
)
MD_LINK_RE = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
STRONG_RE = re.compile(r"(\*\*|__)(.+?)\1")
EM_RE = re.compile(r"(?<![\w*])([*_])(?!\s)(.+?)(?<!\s)\1(?![\w*])")
TAG_RE = re.compile(r"<[^>]+>")
SLUG_STRIP_RE = re.compile(r"[^\w\- ]", re.UNICODE)


# --- Data ------------------------------------------------------------------


@dataclass
class Sheet:
    """One source sheet and what was parsed from it."""

    rel: str  # posix path relative to --src, e.g. linux/awk.md
    path: Path
    front_matter: str = ""  # original front matter block, if any
    body: str = ""
    body_offset: int = 0  # source lines before the body
    title: str = ""
    description: str = ""

    @property
    def stem(self) -> str:
        return posixpath.splitext(posixpath.basename(self.rel))[0]

    @property
    def folder(self) -> str:
        return posixpath.dirname(self.rel)


@dataclass
class Stats:
    """Counters for the summary line."""

    sheets: int = 0
    converted: int = 0
    unresolved: int = 0
    duplicates: int = 0
    warnings: List[str] = field(default_factory=list)


# --- Discovery -------------------------------------------------------------


def discover(src: Path) -> List[Path]:
    """Return every source sheet under src, sorted by relative path."""
    found: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(src):
        rel_dir = Path(dirpath).relative_to(src)
        at_root = rel_dir == Path(".")
        keep = []
        for d in dirnames:
            if d.startswith(".") or d == "node_modules":
                continue
            if at_root and d == "site":
                continue
            keep.append(d)
        dirnames[:] = sorted(keep)
        if at_root:
            continue  # root-level *.md (README etc) are not sheets
        for name in filenames:
            path = Path(dirpath) / name
            # Skip symlinks so a link cannot pull files from outside the repo.
            if name.endswith(".md") and not name.startswith(".") and not path.is_symlink():
                found.append(path)
    return sorted(found, key=lambda p: p.relative_to(src).as_posix())


def snapshot(src: Path) -> Dict[str, Tuple[int, int]]:
    """Map each source's relative path to (mtime_ns, size)."""
    snap: Dict[str, Tuple[int, int]] = {}
    for p in discover(src):
        try:
            st = p.stat()
        except OSError:
            continue
        snap[p.relative_to(src).as_posix()] = (st.st_mtime_ns, st.st_size)
    return snap


# --- Markdown scanning -----------------------------------------------------


@dataclass
class ScanState:
    """Block state carried from line to line."""

    fence_char: str = ""
    fence_len: int = 0
    in_comment: bool = False

    @property
    def in_fence(self) -> bool:
        return self.fence_len > 0


def fence_step(line: str, state: ScanState) -> Optional[bool]:
    """Update fence state for one line.

    Returns True if the line is a fence line or inside a fence (code),
    None if the line is ordinary text.
    """
    if state.in_fence:
        rest = line[QUOTE_PREFIX_RE.match(line).end():]
        m = re.match(r"(`+|~+)\s*$", rest)
        if m and m.group(1)[0] == state.fence_char and len(m.group(1)) >= state.fence_len:
            state.fence_char, state.fence_len = "", 0
        return True
    if state.in_comment:
        return None
    m = FENCE_OPEN_RE.match(line)
    if m:
        run, info = m.group(2), m.group(3)
        if run[0] == "`" and "`" in info:
            return None  # inline code, not a fence
        state.fence_char, state.fence_len = run[0], len(run)
        return True
    return None


def split_inline(line: str, state: ScanState) -> List[Tuple[str, bool]]:
    """Split a non-fence line into (text, transformable) pieces.

    Inline code spans and HTML comments are not transformable. Comment
    state carries across lines.
    """
    pieces: List[Tuple[str, bool]] = []
    i, n = 0, len(line)
    while i < n:
        if state.in_comment:
            j = line.find("-->", i)
            if j < 0:
                pieces.append((line[i:], False))
                return pieces
            pieces.append((line[i:j + 3], False))
            state.in_comment = False
            i = j + 3
            continue
        m = INLINE_TOKEN_RE.search(line, i)
        if not m:
            pieces.append((line[i:], True))
            break
        start = m.start()
        # An escaped backtick is literal.
        if m.group(0)[0] == "`" and _escaped(line, start):
            pieces.append((line[i:start + 1], True))
            i = start + 1
            continue
        if start > i:
            pieces.append((line[i:start], True))
        token = m.group(0)
        if token == "<!--":
            state.in_comment = True
            pieces.append((token, False))
            i = m.end()
            continue
        closer = re.compile(r"(?<!`)`{%d}(?!`)" % len(token)).search(line, m.end())
        if closer:
            pieces.append((line[start:closer.end()], False))
            i = closer.end()
        else:
            pieces.append((token, False))  # unmatched run is literal
            i = m.end()
    return pieces


def _escaped(text: str, pos: int) -> bool:
    """True if the char at pos is preceded by an odd number of backslashes."""
    count = 0
    pos -= 1
    while pos >= 0 and text[pos] == "\\":
        count += 1
        pos -= 1
    return count % 2 == 1


def scan(lines: List[str]) -> Iterator[Tuple[int, str, Optional[List[Tuple[str, bool]]]]]:
    """Yield (index, line, pieces); pieces is None for fenced code lines."""
    state = ScanState()
    for idx, line in enumerate(lines):
        if fence_step(line, state):
            yield idx, line, None
        else:
            yield idx, line, split_inline(line, state)


# --- Text helpers ----------------------------------------------------------


def parse_wikilink(inner: str) -> Optional[Tuple[str, str, Optional[str]]]:
    """Split wikilink text into (target, heading, alias).

    Returns None when the text should be left alone (empty, or padded with
    whitespace like bash's [[ -f x ]]).
    """
    if not inner or inner != inner.strip():
        return None
    parts = ALIAS_SPLIT_RE.split(inner, maxsplit=1)
    ref = parts[0].strip()
    alias = parts[1].strip() if len(parts) > 1 else None
    if alias == "":
        alias = None
    target, _, heading = ref.partition("#")
    target, heading = target.strip(), heading.strip()
    if not target and not heading:
        return None
    return target, heading, alias


def plain_text(text: str) -> str:
    """Reduce inline Markdown to plain text."""

    def wl(m: "re.Match[str]") -> str:
        parsed = parse_wikilink(m.group(1))
        if not parsed:
            return m.group(0)
        target, heading, alias = parsed
        return alias or target or heading

    text = WIKILINK_RE.sub(wl, text)
    text = MD_LINK_RE.sub(r"\1", text)
    text = text.replace("`", "")
    text = STRONG_RE.sub(r"\2", text)
    text = EM_RE.sub(r"\2", text)
    text = TAG_RE.sub("", text)
    text = text.replace("\\|", "|")
    return re.sub(r"\s+", " ", text).strip()


def humanise(stem: str) -> str:
    """docker-compose -> Docker Compose."""
    return " ".join(w[:1].upper() + w[1:] for w in re.split(r"[-_\s]+", stem) if w)


def slugify(heading: str) -> str:
    """GitHub-style heading anchor."""
    s = SLUG_STRIP_RE.sub("", heading.strip().lower())
    return s.replace(" ", "-")


def truncate(text: str, limit: int = DESC_MAX) -> str:
    """Cut text on a word boundary, adding an ellipsis if shortened."""
    if len(text) <= limit:
        return text
    cut = text[:limit]
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip(" ,;:.-") + "\u2026"


def escape_label(label: str) -> str:
    """Escape characters that would break a Markdown link label."""
    for ch in ("\\", "[", "]", "|"):
        label = label.replace(ch, "\\" + ch)
    return label


def quote_path(path: str) -> str:
    """Percent-encode a relative link path."""
    return urllib.parse.quote(path, safe="/._-~")


# --- Parsing ---------------------------------------------------------------


def split_front_matter(text: str) -> Tuple[str, str, int]:
    """Return (front_matter, body, body_line_offset)."""
    if not text.startswith("---\n"):
        return "", text, 0
    lines = text.split("\n")
    for i in range(1, len(lines)):
        if lines[i].rstrip() in ("---", "..."):
            fm = "\n".join(lines[: i + 1]) + "\n"
            return fm, "\n".join(lines[i + 1:]), i + 1
    return "", text, 0


def front_matter_title(fm: str) -> str:
    """Best-effort read of a simple `title:` line from existing front matter."""
    m = re.search(r"^title:[ \t]*(.+?)[ \t]*$", fm, re.MULTILINE)
    if not m:
        return ""
    value = m.group(1)
    if value.startswith('"'):
        try:
            return str(json.loads(value))
        except ValueError:
            return value.strip('"')
    if value.startswith("'") and value.endswith("'") and len(value) > 1:
        return value[1:-1].replace("''", "'")
    return value


def find_title(lines: List[str]) -> Tuple[Optional[str], int]:
    """Return (H1 text, line index) for the first H1 before any fence."""
    state = ScanState()
    for idx, line in enumerate(lines):
        if fence_step(line, state):
            break
        m = H1_RE.match(line)
        if m:
            return m.group(1), idx
    return None, -1


def find_description(lines: List[str], start: int) -> Optional[str]:
    """Return the first prose paragraph from lines[start:]."""
    state = ScanState()
    block: List[str] = []

    def usable(b: List[str]) -> bool:
        if not b:
            return False
        joined = "\n".join(b)
        if "|" in joined and any(TABLE_DELIM_RE.match(x) for x in b):
            return False
        return True

    for line in lines[start:]:
        if fence_step(line, state):
            if usable(block):
                break
            block = []
            continue
        stripped = line.strip()
        structural = (
            not stripped
            or HEADING_RE.match(line)
            or LIST_RE.match(line)
            or HR_RE.match(line)
            or stripped.startswith((">", "<", "![", "|"))
            or line.startswith(("    ", "\t"))
        )
        if structural:
            if usable(block):
                break
            block = []
            continue
        block.append(stripped)
    if not usable(block):
        return None
    text = plain_text(" ".join(block))
    return text or None


def load_sheet(src: Path, path: Path) -> Sheet:
    """Read and parse one sheet."""
    raw = path.read_text(encoding="utf-8")
    raw = raw.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    fm, body, offset = split_front_matter(raw)
    sheet = Sheet(
        rel=path.relative_to(src).as_posix(),
        path=path,
        front_matter=fm,
        body=body,
        body_offset=offset,
    )
    lines = body.split("\n")
    h1, h1_idx = find_title(lines)
    sheet.title = (
        front_matter_title(fm) or (plain_text(h1) if h1 else "") or humanise(sheet.stem)
    )
    desc = find_description(lines, h1_idx + 1)
    sheet.description = truncate(desc) if desc else f"{sheet.title} cheat sheet"
    return sheet


# --- Link resolution -------------------------------------------------------


class Resolver:
    """Resolve wikilink targets to sheets."""

    def __init__(self, sheets: List[Sheet], stats: Stats) -> None:
        self.sheets = sheets
        self.by_stem: Dict[str, List[Sheet]] = {}
        for s in sheets:
            self.by_stem.setdefault(s.stem.lower(), []).append(s)
        for name, group in sorted(self.by_stem.items()):
            if len(group) > 1:
                stats.duplicates += 1
                paths = ", ".join(g.rel for g in group)
                warn(stats, f"WARN duplicate sheet name '{name}': {paths}")

    def resolve(self, target: str, origin: Sheet) -> Optional[Sheet]:
        key = target.strip().lower()
        if key.endswith(".md"):
            key = key[:-3]
        key = key.strip("/")
        if not key:
            return None
        if "/" in key:
            cands = [
                s for s in self.sheets
                if s.rel.lower()[:-3] == key or s.rel.lower()[:-3].endswith("/" + key)
            ]
        else:
            cands = self.by_stem.get(key, [])
        if not cands:
            return None
        for c in cands:
            if c.folder == origin.folder:
                return c
        return cands[0]


# --- Transform -------------------------------------------------------------


def warn(stats: Stats, message: str) -> None:
    """Print a warning to stderr and keep it."""
    stats.warnings.append(message)
    print(message, file=sys.stderr)


def gh_escape(value: str, prop: bool = False) -> str:
    """Escape a GitHub Actions workflow command value."""
    value = value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    if prop:
        value = value.replace(":", "%3A").replace(",", "%2C")
    return value


def report_unresolved(stats: Stats, rel: str, line: int, inner: str) -> None:
    """Report one unresolved wikilink."""
    stats.unresolved += 1
    msg = f"unresolved wikilink [[{inner}]]"
    warn(stats, f"WARN {rel}:{line}: {msg}")
    if os.environ.get("GITHUB_ACTIONS") == "true":
        print(
            f"::warning file={gh_escape(rel, True)},line={line}::{gh_escape(msg)}",
            flush=True,
        )


def render_link(
    m: "re.Match[str]", sheet: Sheet, resolver: Resolver, stats: Stats, lineno: int
) -> str:
    """Return the replacement for one wikilink match."""
    inner = m.group(1)
    parsed = parse_wikilink(inner)
    if parsed is None:
        return m.group(0)
    target, heading, alias = parsed
    if not target:  # [[#heading]] on the same page
        stats.converted += 1
        label = alias or heading
        return f"[{escape_label(label)}](#{slugify(heading)})"
    dest = resolver.resolve(target, sheet)
    if dest is None:
        shown = inner.replace("\\|", "|")
        report_unresolved(stats, sheet.rel, lineno, shown)
        label = alias or target
        title = html.escape(f"Unresolved link: [[{shown}]]").replace("|", "&#124;")
        text = html.escape(label).replace("|", "&#124;")
        return f'<span class="wikilink-missing" title="{title}">{text}</span>'
    stats.converted += 1
    href = quote_path(posixpath.relpath(dest.rel, sheet.folder or "."))
    if heading:
        href += "#" + slugify(heading)
    label = alias or (f"{dest.title} \u203a {heading}" if heading else dest.title)
    return f"[{escape_label(label)}]({href})"


def transform_body(sheet: Sheet, resolver: Resolver, stats: Stats) -> str:
    """Convert wikilinks in the body, skipping code and comments."""
    lines = sheet.body.split("\n")
    out: List[str] = []
    for idx, line, pieces in scan(lines):
        if pieces is None:
            out.append(line)
            continue
        lineno = sheet.body_offset + idx + 1
        buf = []
        for text, live in pieces:
            if live and "[[" in text:
                text = WIKILINK_RE.sub(
                    lambda m, ln=lineno: render_link(m, sheet, resolver, stats, ln), text
                )
            buf.append(text)
        out.append("".join(buf))
    return "\n".join(out)


def front_matter_for(sheet: Sheet) -> str:
    """Build YAML front matter for a sheet without any."""
    lines = [
        "---",
        f"title: {json.dumps(sheet.title, ensure_ascii=False)}",
        f"description: {json.dumps(sheet.description, ensure_ascii=False)}",
    ]
    if sheet.folder and sheet.stem == posixpath.basename(sheet.folder):
        lines.append("weight: 1")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def render_sheet(sheet: Sheet, resolver: Resolver, stats: Stats) -> str:
    """Return the full output text for one sheet."""
    body = transform_body(sheet, resolver, stats)
    if sheet.front_matter:
        text = sheet.front_matter + body
    else:
        text = front_matter_for(sheet) + body.lstrip("\n")
    return text.rstrip("\n") + "\n"


def build(src: Path) -> Tuple[Dict[str, str], Stats]:
    """Render every sheet. Returns ({rel: content}, stats)."""
    stats = Stats()
    sheets = [load_sheet(src, p) for p in discover(src)]
    stats.sheets = len(sheets)
    resolver = Resolver(sheets, stats)
    outputs = {s.rel: render_sheet(s, resolver, stats) for s in sheets}
    return outputs, stats


# --- Output ----------------------------------------------------------------


def check_out_dir(out: Path) -> Path:
    """Refuse any --out that is not strictly inside site/.build/."""
    resolved = out.resolve()
    build_dir = BUILD_DIR.resolve()
    if resolved == build_dir or build_dir not in resolved.parents:
        raise SystemExit(
            f"prepare-content: refusing to use --out {out}: "
            f"it must be inside {build_dir}"
        )
    return resolved


def clear_dir(out: Path) -> None:
    """Remove the contents of out, keeping out itself."""
    out.mkdir(parents=True, exist_ok=True)
    for child in out.iterdir():
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()


def write_if_changed(path: Path, content: str) -> bool:
    """Atomically write content unless the file already has it."""
    data = content.encode("utf-8")
    try:
        if path.read_bytes() == data:
            return False
    except OSError:
        pass
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".tmp-", suffix=".md")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    return True


def sync_outputs(out: Path, outputs: Dict[str, str]) -> int:
    """Write changed outputs, delete stale ones. Returns files written."""
    written = sum(write_if_changed(out / rel, text) for rel, text in outputs.items())
    wanted = {(out / rel) for rel in outputs}
    for dirpath, _dirs, files in os.walk(out, topdown=False):
        d = Path(dirpath)
        for name in files:
            p = d / name
            if p not in wanted:
                p.unlink()
        if d != out and not any(d.iterdir()):
            d.rmdir()
    return written


def summary(stats: Stats) -> str:
    return (
        f"prepare-content: {stats.sheets} sheets, {stats.converted} wikilinks "
        f"converted, {stats.unresolved} unresolved, {stats.duplicates} duplicate names"
    )


# --- Main ------------------------------------------------------------------


def watch(src: Path, out: Path) -> None:
    """Poll sources and rebuild on change until Ctrl-C."""
    last = snapshot(src)
    print(f"prepare-content: watching {src} (Ctrl-C to stop)", flush=True)
    while True:
        time.sleep(POLL_SECONDS)
        current = snapshot(src)
        if current == last:
            continue
        last = current
        try:
            outputs, stats = build(src)
            written = sync_outputs(out, outputs)
            print(f"{summary(stats)} ({written} written)", flush=True)
        except Exception as exc:  # keep watching after a bad read
            print(f"prepare-content: rebuild failed: {exc}", file=sys.stderr, flush=True)


def _raise_interrupt(_signum: int, _frame: object) -> None:
    """Treat SIGTERM like Ctrl-C so watch mode exits cleanly."""
    raise KeyboardInterrupt


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Copy cheat sheets into Hugo's content dir, "
        "converting [[wikilinks]] and adding front matter."
    )
    p.add_argument("--src", type=Path, default=REPO_ROOT, help="repo root (default: %(default)s)")
    p.add_argument(
        "--out", type=Path, default=BUILD_DIR / "content", help="output dir (default: %(default)s)"
    )
    p.add_argument(
        "--strict", action="store_true", help="exit 1 on unresolved links or duplicate names"
    )
    p.add_argument("--watch", action="store_true", help="rebuild on change")
    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    src = args.src.resolve()
    if not src.is_dir():
        print(f"prepare-content: --src {args.src} is not a directory", file=sys.stderr)
        return 2
    out = check_out_dir(args.out)
    outputs, stats = build(src)
    clear_dir(out)
    sync_outputs(out, outputs)
    print(summary(stats), flush=True)
    if args.watch:
        signal.signal(signal.SIGTERM, _raise_interrupt)
        try:
            watch(src, out)
        except KeyboardInterrupt:
            print("prepare-content: stopped", flush=True)
        return 0
    if args.strict and (stats.unresolved or stats.duplicates):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

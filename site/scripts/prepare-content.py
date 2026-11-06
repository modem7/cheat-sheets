#!/usr/bin/env python3
"""Prepare the cheat sheets for Hugo.

The sheets are plain Markdown with no front matter. This script writes a copy
of every sheet into a build directory that Hugo mounts as its content dir,
adding YAML front matter (title, description, and weight 1 for a section's
lead sheet such as docker/docker.md) unless the file already has some. The
body is copied unchanged.

Usage:
  prepare-content.py [--src DIR] [--out DIR] [--watch]

  --src     Repository root to read sheets from (default: parent of site/).
  --out     Output content dir (default: site/.build/content). Must be
            inside site/.build/ because it is wiped on every run.
  --watch   After the first build, poll the sources every second and
            rebuild on change. Ctrl-C to stop.

Sources are every *.md under --src, except root-level files (README.md),
anything under a dot folder, the top-level site/ dir and node_modules/.
Symlinked files are skipped. Python 3.9+, standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import posixpath
import re
import shutil
import signal
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

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


# --- Data ------------------------------------------------------------------


@dataclass
class Sheet:
    """One source sheet and what was parsed from it."""

    rel: str  # posix path relative to --src, e.g. linux/awk.md
    path: Path
    front_matter: str = ""  # original front matter block, if any
    body: str = ""
    title: str = ""
    description: str = ""

    @property
    def stem(self) -> str:
        return posixpath.splitext(posixpath.basename(self.rel))[0]

    @property
    def folder(self) -> str:
        return posixpath.dirname(self.rel)


# --- Discovery -------------------------------------------------------------


def discover(src: Path) -> list[Path]:
    """Return every source sheet under src, sorted by relative path."""
    found: list[Path] = []
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


def snapshot(src: Path) -> dict[str, tuple[int, int]]:
    """Map each source's relative path to (mtime_ns, size)."""
    snap: dict[str, tuple[int, int]] = {}
    for p in discover(src):
        try:
            st = p.stat()
        except OSError:
            continue
        snap[p.relative_to(src).as_posix()] = (st.st_mtime_ns, st.st_size)
    return snap


# --- Fence tracking --------------------------------------------------------


@dataclass
class FenceState:
    """Open code fence carried from line to line."""

    char: str = ""
    length: int = 0


def in_fence(line: str, state: FenceState) -> bool:
    """Update fence state for one line. True if the line is fence or code."""
    if state.length:
        rest = line[QUOTE_PREFIX_RE.match(line).end():]
        m = re.match(r"(`+|~+)\s*$", rest)
        if m and m.group(1)[0] == state.char and len(m.group(1)) >= state.length:
            state.char, state.length = "", 0
        return True
    m = FENCE_OPEN_RE.match(line)
    if m:
        run, info = m.group(2), m.group(3)
        if run[0] == "`" and "`" in info:
            return False  # inline code, not a fence
        state.char, state.length = run[0], len(run)
        return True
    return False


# --- Text helpers ----------------------------------------------------------


def plain_text(text: str) -> str:
    """Reduce inline Markdown to plain text."""
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


def truncate(text: str, limit: int = DESC_MAX) -> str:
    """Cut text on a word boundary, adding an ellipsis if shortened."""
    if len(text) <= limit:
        return text
    cut = text[:limit]
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip(" ,;:.-") + "…"


# --- Parsing ---------------------------------------------------------------


def split_front_matter(text: str) -> tuple[str, str]:
    """Return (front_matter, body)."""
    if not text.startswith("---\n"):
        return "", text
    lines = text.split("\n")
    for i in range(1, len(lines)):
        if lines[i].rstrip() in ("---", "..."):
            fm = "\n".join(lines[: i + 1]) + "\n"
            return fm, "\n".join(lines[i + 1:])
    return "", text


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


def find_title(lines: list[str]) -> tuple[str | None, int]:
    """Return (H1 text, line index) for the first H1 before any fence."""
    state = FenceState()
    for idx, line in enumerate(lines):
        if in_fence(line, state):
            break
        m = H1_RE.match(line)
        if m:
            return m.group(1), idx
    return None, -1


def find_description(lines: list[str], start: int) -> str | None:
    """Return the first prose paragraph from lines[start:]."""
    state = FenceState()
    block: list[str] = []

    def usable(b: list[str]) -> bool:
        if not b:
            return False
        # A Markdown table is not a description.
        joined = "\n".join(b)
        return not ("|" in joined and any(TABLE_DELIM_RE.match(x) for x in b))

    for line in lines[start:]:
        if in_fence(line, state):
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
    raw = raw.lstrip("﻿").replace("\r\n", "\n").replace("\r", "\n")
    fm, body = split_front_matter(raw)
    sheet = Sheet(rel=path.relative_to(src).as_posix(), path=path, front_matter=fm, body=body)
    lines = body.split("\n")
    h1, h1_idx = find_title(lines)
    sheet.title = (
        front_matter_title(fm) or (plain_text(h1) if h1 else "") or humanise(sheet.stem)
    )
    desc = find_description(lines, h1_idx + 1)
    sheet.description = truncate(desc) if desc else f"{sheet.title} cheat sheet"
    return sheet


# --- Render ----------------------------------------------------------------


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


def render_sheet(sheet: Sheet) -> str:
    """Return the full output text for one sheet."""
    if sheet.front_matter:
        text = sheet.front_matter + sheet.body
    else:
        text = front_matter_for(sheet) + sheet.body.lstrip("\n")
    return text.rstrip("\n") + "\n"


def build(src: Path) -> dict[str, str]:
    """Render every sheet. Returns {rel: content}."""
    sheets = [load_sheet(src, p) for p in discover(src)]
    return {s.rel: render_sheet(s) for s in sheets}


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


def sync_outputs(out: Path, outputs: dict[str, str]) -> int:
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


def summary(outputs: dict[str, str]) -> str:
    return f"prepare-content: {len(outputs)} sheets"


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
            outputs = build(src)
            written = sync_outputs(out, outputs)
            print(f"{summary(outputs)} ({written} written)", flush=True)
        except Exception as exc:  # noqa: BLE001 - keep watching after a bad read
            print(f"prepare-content: rebuild failed: {exc}", file=sys.stderr, flush=True)


def _raise_interrupt(_signum: int, _frame: object) -> None:
    """Treat SIGTERM like Ctrl-C so watch mode exits cleanly."""
    raise KeyboardInterrupt


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Copy cheat sheets into Hugo's content dir, "
        "adding front matter. The body is copied unchanged."
    )
    p.add_argument("--src", type=Path, default=REPO_ROOT, help="repo root (default: %(default)s)")
    p.add_argument(
        "--out", type=Path, default=BUILD_DIR / "content", help="output dir (default: %(default)s)"
    )
    p.add_argument("--watch", action="store_true", help="rebuild on change")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    src = args.src.resolve()
    if not src.is_dir():
        print(f"prepare-content: --src {args.src} is not a directory", file=sys.stderr)
        return 2
    out = check_out_dir(args.out)
    outputs = build(src)
    clear_dir(out)
    sync_outputs(out, outputs)
    print(summary(outputs), flush=True)
    if args.watch:
        signal.signal(signal.SIGTERM, _raise_interrupt)
        try:
            watch(src, out)
        except KeyboardInterrupt:
            print("prepare-content: stopped", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

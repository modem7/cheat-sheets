#!/usr/bin/env python3
"""Generate the sheet index in README.md from the Markdown files on disk.

Usage: python3 scripts/gen-index.py [--check] [ROOT]

The index lives between the markers

    <!-- index:start -->
    <!-- index:end -->

in README.md. Without --check the block is rewritten in place. With
--check nothing is written; the exit status is 1 if the block is out of
date (a sheet was added, renamed or retitled without regenerating), 0 if
it matches, 2 on a usage error.

Each sheet is listed under its folder using the text of its first H1 as
the link text. To add a new top-level folder, add it to SECTIONS below
(a folder missing from SECTIONS is an error, so it cannot be forgotten).
"""

import os
import re
import sys

START = "<!-- index:start -->"
END = "<!-- index:end -->"

# (folder, section title), in display order.
SECTIONS = [
    ("recipes", "Recipes"),
    ("linux", "Linux"),
    ("windows", "Windows"),
    ("macos", "macOS"),
    ("docker", "Docker"),
    ("distros", "Container Distros"),
    ("kubernetes", "Kubernetes"),
    ("proxmox", "Proxmox"),
    ("homelab", "Homelab"),
    ("infra", "Infrastructure"),
    ("cloud", "Cloud"),
    ("networking", "Networking"),
    ("unifi", "UniFi"),
    ("security", "Security"),
    ("backup", "Backup"),
    ("cicd", "CI/CD"),
    ("scripting", "Scripting"),
    ("ai", "AI"),
    ("databases", "Databases"),
    ("apps", "Apps"),
    ("tools", "Tools"),
    ("misc", "Misc"),
]

DOCS = [
    ("Contributing", "docs/CONTRIBUTING.md"),
    ("Sheet template", "docs/_template.md"),
]

H1_RE = re.compile(r"^#\s+(.+?)\s*#*\s*$")
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")


def title_of(path):
    """Return the first H1 of a Markdown file (outside fences), else the stem."""
    fence = None
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            m = FENCE_RE.match(line)
            if m:
                fence = None if fence == m.group(1)[0] else (fence or m.group(1)[0])
                continue
            if fence is None:
                h = H1_RE.match(line)
                if h:
                    return h.group(1).replace("|", "\\|")
    return os.path.basename(path)[:-3]


def sort_key(folder, path):
    stem = os.path.basename(path)[:-3]
    lead = stem == folder or stem.endswith(("overview", "index"))
    return (0 if lead else 1, os.path.dirname(path), stem)


def build(root):
    top = sorted(
        d for d in os.listdir(root)
        if os.path.isdir(os.path.join(root, d))
        and not d.startswith(".")
        and d not in {"node_modules", "docs", "scripts", "site"}
        and any(f.endswith(".md") for _, _, fs in os.walk(os.path.join(root, d)) for f in fs)
    )
    known = {f for f, _ in SECTIONS}
    missing = [d for d in top if d not in known]
    if missing:
        raise SystemExit(
            "error: folder(s) with sheets not listed in SECTIONS: " + ", ".join(missing)
        )

    out = ["## Index", ""]
    for folder, title in SECTIONS:
        base = os.path.join(root, folder)
        if not os.path.isdir(base):
            continue
        groups = {}
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
            for name in filenames:
                if name.endswith(".md"):
                    rel = os.path.relpath(os.path.join(dirpath, name), root).replace(os.sep, "/")
                    sub = os.path.dirname(rel)
                    groups.setdefault(sub, []).append(rel)
        if not groups:
            continue
        out.append("### " + title)
        out.append("")
        for sub in sorted(groups, key=lambda s: (s != folder, s)):
            items = sorted(groups[sub], key=lambda p: sort_key(folder, p))
            links = " · ".join(
                "[{}]({})".format(title_of(os.path.join(root, p)), p) for p in items
            )
            prefix = "" if sub == folder else "{}: ".format(sub[len(folder) + 1:].capitalize())
            out.append(prefix + links)
            out.append("")
    out.append("### Docs")
    out.append("")
    out.append(" · ".join("[{}]({})".format(t, p) for t, p in DOCS))
    out.append("")
    return "\n".join(out)


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    check = "--check" in args
    args = [a for a in args if a != "--check"]
    if len(args) > 1 or any(a.startswith("-") for a in args):
        print("usage: gen-index.py [--check] [ROOT]", file=sys.stderr)
        return 2
    root = os.path.abspath(
        args[0] if args else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    readme = os.path.join(root, "README.md")
    with open(readme, encoding="utf-8") as fh:
        text = fh.read()
    si, ei = text.find(START), text.find(END)
    if si == -1 or ei == -1 or ei < si:
        print("error: index markers not found in README.md", file=sys.stderr)
        return 2
    new = text[: si + len(START)] + "\n" + build(root) + text[ei:]
    if new == text:
        print("OK: README.md index is up to date")
        return 0
    if check:
        print("FAIL: README.md index is out of date; run: python3 scripts/gen-index.py")
        return 1
    with open(readme, "w", encoding="utf-8") as fh:
        fh.write(new)
    print("README.md index updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())

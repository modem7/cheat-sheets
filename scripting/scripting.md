# Scripting
Overview of the scripting and automation cheat sheets: shell, build tooling, Python and the checks that keep scripts correct. Start with [[bash]], keep [[bash-recipes]] open while writing, and lint everything before it ships.

SHEET | DESCRIPTION
---|---
[[bash]] | Strict mode, variables, quoting, arrays, parameter expansion, tests, loops, functions, `trap`, `getopts`, here-docs, redirection
[[bash-recipes]] | Argument parsing, logging, `flock` lockfiles, retry with backoff, safe temp files, idempotent checks, `xargs -P`
[[shellcheck-shfmt]] | Static analysis and formatting for shell, common SC codes, CI usage
[[make]] | Makefile syntax, phony targets, variables, pattern rules, self-documenting `help`
[[python-uv]] | `uv` projects, venvs, tools, inline script metadata, `pyproject.toml`
[[pre-commit]] | Run linters and secret scanning before every commit and in CI

## Related Sheets
SHEET | USE FOR
---|---
[[grep]] | Searching text
[[sed]] | Stream edits and substitution
[[awk]] | Column and field processing
[[jq]] | JSON in pipelines
[[curl]] | HTTP requests and API calls
[[linux]] | Everyday administration commands to script

## Choosing a Language
SITUATION | USE
---|---
Glue between commands, under about 100 lines | Bash
Needs arrays of structured data, JSON, HTTP, retries, tests | Python (a single file with `uv run` and inline metadata)
Repeatable project tasks (`up`, `lint`, `deploy`) | `make` calling small scripts
Must run on minimal images (Alpine, BusyBox) | POSIX `sh`, lint with `shellcheck -s sh`

## Script Hygiene Checklist
- Start with `#!/usr/bin/env bash` and `set -Eeuo pipefail`.
- Quote every variable expansion.
- Clean up with `trap ... EXIT`; use `mktemp` for temporary files.
- Make scripts safe to run twice (idempotent).
- Print errors to stderr and exit non-zero on failure.
- Run [[shellcheck-shfmt]] locally and via [[pre-commit]].

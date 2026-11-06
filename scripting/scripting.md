# Scripting
Overview of the scripting and automation cheat sheets: shell, build tooling, Python and the checks that keep scripts correct. Start with [Bash](bash.md), keep [Bash Recipes](bash-recipes.md) open while writing, and lint everything before it ships.

SHEET | DESCRIPTION
---|---
[Bash](bash.md) | Strict mode, variables, quoting, arrays, parameter expansion, tests, loops, functions, `trap`, `getopts`, here-docs, redirection
[Bash Recipes](bash-recipes.md) | Argument parsing, logging, `flock` lockfiles, retry with backoff, safe temp files, idempotent checks, `xargs -P`
[ShellCheck and shfmt](shellcheck-shfmt.md) | Static analysis and formatting for shell, common SC codes, CI usage
[Make](make.md) | Makefile syntax, phony targets, variables, pattern rules, self-documenting `help`
[Python and uv](python-uv.md) | `uv` projects, venvs, tools, inline script metadata, `pyproject.toml`
[pre-commit](pre-commit.md) | Run linters and secret scanning before every commit and in CI

## Related Sheets
SHEET | USE FOR
---|---
[Grep](../linux/grep.md) | Searching text
[SED Cheat-Sheet](../linux/sed.md) | Stream edits and substitution
[AWK](../linux/awk.md) | Column and field processing
[jq](../tools/jq.md) | JSON in pipelines
[curl](../tools/curl.md) | HTTP requests and API calls
[Linux](../linux/linux.md) | Everyday administration commands to script

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
- Run [ShellCheck and shfmt](shellcheck-shfmt.md) locally and via [pre-commit](pre-commit.md).

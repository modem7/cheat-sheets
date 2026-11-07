# Python and uv
`uv` is a fast Python package and project manager (written in Rust) that replaces `pip`, `venv`, `pip-tools`, `pipx` and most of `pyenv` with one tool. This sheet covers uv first, then the plain `venv` and `pip` basics it builds on. Use Python for scripts that outgrow [Bash](bash.md), especially anything that parses JSON ([jq](../tools/jq.md) covers the shell side) or calls HTTP APIs ([curl](../tools/curl.md) for quick tests).

Documentation: [uv docs](https://docs.astral.sh/uv/), [Python venv](https://docs.python.org/3/library/venv.html), [PEP 723 inline script metadata](https://packaging.python.org/en/latest/specifications/inline-script-metadata/)

## Install
COMMAND | DESCRIPTION
---|---
`curl -LsSf https://astral.sh/uv/install.sh \| sh` | Standalone installer (Linux and macOS)
`brew install uv` | Homebrew
`pipx install uv` | Via pipx
`uv self update` | Update uv (standalone install only)
`uv --version` | Verify
`uv generate-shell-completion bash` | Print shell completion script

## Projects
COMMAND | DESCRIPTION
---|---
`uv init <NAME>` | New project with `pyproject.toml`
`uv init` | Initialise the current directory
`uv init --app` / `--lib` | Application (default) or packaged library layout
`uv init --script <FILE.py>` | New standalone script with inline metadata
`uv add <PKG>` | Add a dependency (updates `pyproject.toml` and `uv.lock`)
`uv add '<PKG>>=2,<3'` | Add with a version constraint
`uv add --dev <PKG>` | Add a development dependency
`uv add -r requirements.txt` | Import from a requirements file
`uv remove <PKG>` | Remove a dependency
`uv sync` | Create `.venv` and install exactly what the lockfile says
`uv sync --frozen` | Install from the lockfile without updating it
`uv sync --locked` | Fail if the lockfile is out of date (CI)
`uv lock` | Update `uv.lock` only
`uv lock --upgrade` | Upgrade all locked versions
`uv lock --upgrade-package <PKG>` | Upgrade one package
`uv run <CMD>` | Run in the project environment (syncs first)
`uv run python -m pytest` | Run a tool from the environment
`uv tree` | Dependency tree
`uv export --format requirements-txt > requirements.txt` | Export for tools that need it
`uv build` | Build sdist and wheel
`uv publish` | Upload to PyPI

Commit `pyproject.toml` and `uv.lock`; do not commit `.venv/`.

## Python Versions
COMMAND | DESCRIPTION
---|---
`uv python list` | Available and installed versions
`uv python install 3.12` | Download and install a version
`uv python pin 3.12` | Write `.python-version` for the project
`uv venv --python 3.12` | Create a venv with a specific version
`uv run --python 3.13 script.py` | Run once with another version

## Virtual Environments and pip Interface
COMMAND | DESCRIPTION
---|---
`uv venv` | Create `.venv`
`uv venv <PATH>` | Create it elsewhere
`source .venv/bin/activate` | Activate (Linux and macOS)
`.venv\Scripts\Activate.ps1` | Activate (Windows PowerShell)
`deactivate` | Leave the environment
`uv pip install <PKG>` | Install into the active or `.venv` environment
`uv pip install -r requirements.txt` | Install from a file
`uv pip install -e .` | Editable install of the current project
`uv pip list`, `uv pip freeze` | What is installed
`uv pip uninstall <PKG>` | Remove
`uv pip compile requirements.in -o requirements.txt` | Pin to a lock-style file
`uv pip sync requirements.txt` | Make the environment match the file exactly

The `uv pip` interface is a drop-in for most `pip` commands; the `uv add` / `uv sync` project workflow is preferred for anything you keep.

## Scripts with Inline Metadata (PEP 723)
Dependencies live in a comment block at the top of a single file, so the script is self-contained.
```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests<3",
#   "rich",
# ]
# ///
import requests
from rich import print

r = requests.get("https://api.github.com/repos/astral-sh/uv", timeout=10)
print(r.json()["stargazers_count"])
```
COMMAND | DESCRIPTION
---|---
`uv run script.py` | Run; uv builds a cached throwaway environment from the metadata
`uv add --script script.py <PKG>` | Add a dependency to the block
`uv remove --script script.py <PKG>` | Remove one
`uv lock --script script.py` | Lock the script's dependencies
`chmod +x script.py && ./script.py` | Run directly via the shebang
`uv run --with <PKG> script.py` | One-off extra dependency without editing the file
`uv run --no-project script.py` | Ignore the surrounding project

## Tools (pipx replacement)
COMMAND | DESCRIPTION
---|---
`uvx <TOOL> [ARGS]` | Run a tool in a temporary environment (alias of `uv tool run`)
`uvx ruff check .` | Example: lint without installing
`uvx --from <PKG> <CMD>` | When the command name differs from the package name
`uvx <TOOL>@<VERSION>` | Run a specific version
`uv tool install <TOOL>` | Install into an isolated environment, put it on `PATH`
`uv tool list` | Installed tools
`uv tool upgrade <TOOL>` / `--all` | Upgrade
`uv tool uninstall <TOOL>` | Remove
`uv tool update-shell` | Add the tool bin directory to `PATH`

### uv vs pipx vs pip
NEED | uv | pipx | pip
---|---|---|---
Run a CLI once | `uvx <TOOL>` | `pipx run <TOOL>` | n/a
Install a CLI globally, isolated | `uv tool install` | `pipx install` | Pollutes the environment
Project dependencies and lockfile | `uv add`, `uv sync` | n/a | `pip install` plus manual pins
Manage Python versions | `uv python install` | n/a | n/a
Speed | Fast (parallel, cached) | Uses pip internally | Slowest

## pyproject.toml
```toml
[project]
name = "myapp"
version = "0.1.0"
description = "Homelab helper"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "requests>=2.31",
    "pyyaml",
]

[project.scripts]
myapp = "myapp.cli:main"

[dependency-groups]
dev = ["pytest", "ruff"]

[tool.ruff]
line-length = 100
```
`[project.scripts]` creates a `myapp` command when the project is installed (`uv tool install .` or `uv pip install -e .`).

## Plain venv and pip
COMMAND | DESCRIPTION
---|---
`python3 -m venv .venv` | Create a virtual environment
`source .venv/bin/activate` | Activate
`python -m pip install --upgrade pip` | Upgrade pip
`pip install <PKG>` | Install
`pip install -r requirements.txt` | Install from a file
`pip freeze > requirements.txt` | Pin everything currently installed
`pip list --outdated` | Show available upgrades
`pip show <PKG>` | Package details
`pip uninstall <PKG>` | Remove
`python3 -m pip --version` | Which pip and which Python
`which python` | Confirm you are using the venv one

On Debian and Ubuntu, `pip install` outside a venv fails with `externally-managed-environment` (PEP 668). Use a venv, `uv`, or `pipx` instead of `--break-system-packages`. If `python3 -m venv` complains, install `python3-venv`.

## Everyday One-Liners
COMMAND | DESCRIPTION
---|---
`python3 -m http.server 8000` | Serve the current directory over HTTP
`python3 -m json.tool < file.json` | Pretty-print JSON
`python3 -c 'import sys,json; print(json.load(sys.stdin)["key"])'` | Read a JSON field
`python3 -m venv --help` | Venv options
`python3 -m py_compile script.py` | Syntax check
`uv run python -m pdb script.py` | Debugger

## See Also
- [pip and pipx](pip-and-pipx.md)

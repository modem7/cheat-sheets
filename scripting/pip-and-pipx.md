# pip and pipx
`pip` installs Python packages into an environment; `pipx` installs Python command-line tools, each in its own isolated virtual environment, and puts the commands on your `PATH`. Use `pip` inside a virtual environment for project dependencies, and `pipx` for tools such as `ansible` or `yt-dlp`. For the faster all-in-one alternative see [Python and uv](python-uv.md).

Documentation: [pip](https://pip.pypa.io/en/stable/cli/) · [pipx](https://pipx.pypa.io/stable/)
Project: [pypa/pip](https://github.com/pypa/pip) · [pypa/pipx](https://github.com/pypa/pipx)

> **Verification:** options checked against `pip --help` for pip 24.0 and `pipx --help` for pipx 1.18.15 in a throwaway `python:3.11-slim` container. `pipx install`, `list`, `run`, `inject`, `runpip`, `upgrade` and `environment`, and `pip freeze`, `list --outdated`, `check`, `show`, `config list`, `download`, `hash` and `inspect` were run. Nothing was installed on the host. `pipx` flags change between releases (the newest ones are `--cooldown` and `--backend`); run `pipx <COMMAND> --help` for yours.

Related sheets: [Python and uv](python-uv.md), [pre-commit](pre-commit.md), [Ansible Cheat-Sheet](../tools/ansible.md), [yt-dlp](../tools/yt-dlp.md).

## Environments First
On Debian and Ubuntu the system Python is marked externally managed, so `pip install` outside a virtual environment is refused. Use a venv.

COMMAND | DESCRIPTION
---|---
`python3 -m venv .venv` | Create a virtual environment
`source .venv/bin/activate` | Activate it (`deactivate` to leave)
`python -m pip ...` | Run the pip belonging to that interpreter (safest form)
`sudo apt install python3-venv` | Needed on Debian and Ubuntu if `venv` is missing
`pip install --break-system-packages <PACKAGE>` | Override the external-management guard (avoid; can break OS tools)
`pip --require-virtualenv install <PACKAGE>` | Refuse to run outside a virtual environment
`PIP_REQUIRE_VIRTUALENV=true` | Same, as an environment variable

## Install and Remove
COMMAND | DESCRIPTION
---|---
`pip install <PACKAGE>` | Install the latest version
`pip install <PACKAGE>==<VERSION>` | Exact version
`pip install '<PACKAGE>>=1.2,<2'` | Version range (quote it)
`pip install '<PACKAGE>[<EXTRA>]'` | Install with an extra
`pip install -U <PACKAGE>` | Upgrade (`--upgrade`)
`pip install --force-reinstall <PACKAGE>` | Reinstall even if current
`pip install -r requirements.txt` | Install from a file
`pip install -c constraints.txt -r requirements.txt` | Apply version limits without adding packages
`pip install -e .` | Editable install of the current project
`pip install --no-deps <PACKAGE>` | Skip dependencies
`pip install --pre <PACKAGE>` | Allow pre-releases
`pip install --dry-run <PACKAGE>` | Show what would be installed
`pip install --only-binary :all: <PACKAGE>` | Refuse source builds (`--no-binary` forces them)
`pip install --user <PACKAGE>` | Install for the current user only
`pip install -t <DIR> <PACKAGE>` | Install into a target directory
`pip install --require-hashes -r requirements.txt` | Require a `--hash` for every entry; repeatable and tamper-evident
`pip install --report <FILE> <PACKAGE>` | Write a JSON install report (use `-` for stdout)
`pip uninstall <PACKAGE>` / `pip uninstall -y -r requirements.txt` | Remove, optionally without prompts

## Inspect
COMMAND | DESCRIPTION
---|---
`pip list` | Installed packages (`--outdated`, `--not-required`, `--format json`, `--local`)
`pip freeze` | Installed packages in requirements format (`--exclude-editable`, `--all`)
`pip freeze > requirements.txt` | Pin the current environment
`pip show <PACKAGE>` | Metadata (`-f` lists installed files)
`pip check` | Verify dependencies are consistent
`pip inspect` | JSON description of the environment
`pip debug` | Version, interpreter and compatible-tag details for bug reports
`pip --version` | pip version and location
`pip index versions <PACKAGE>` | List versions available on the index

`pip search` is still listed in `--help` but PyPI does not support it; search on pypi.org.

## Download and Build
COMMAND | DESCRIPTION
---|---
`pip download -d <DIR> -r requirements.txt` | Download distributions without installing (for offline installs)
`pip install --no-index --find-links <DIR> -r requirements.txt` | Install from that directory only
`pip wheel -w <DIR> -r requirements.txt` | Build wheels for your requirements
`pip hash <FILE>` | Print a `--hash=sha256:...` line for a downloaded file
`pip download --platform <TAG> --only-binary :all: --python-version <VER> <PACKAGE>` | Fetch wheels for another platform (see `pip download --help`)

## Indexes, Config and Cache
COMMAND | DESCRIPTION
---|---
`pip install -i <URL> <PACKAGE>` | Use another index (`--index-url`)
`pip install --extra-index-url <URL> <PACKAGE>` | Also search another index (a dependency-confusion risk; prefer a single index)
`pip install -f <DIR_OR_URL> <PACKAGE>` | Look in a directory or page of archives (`--find-links`)
`pip config list` | Show active configuration
`pip config debug` | Show config files and where each value comes from
`pip config set global.index-url <URL>` | Set an option in the user config
`pip config get global.index-url` | Read it
`pip config unset global.index-url` | Remove it
`pip config edit --editor <EDITOR>` | Edit the config file (`--user`, `--global`, `--site` pick the file)
`pip cache dir` / `pip cache info` | Show the cache location and size
`pip cache list` | List cached wheels
`pip cache remove '<PATTERN>'` / `pip cache purge` | Remove some or all cached wheels
`PIP_NO_CACHE_DIR=1` | Disable the cache (then `pip cache` commands fail)

Config lives in `pip.conf` (Linux) under the user or global config directory; `pip config debug` lists the exact paths.

## pipx: Install and Run Tools
COMMAND | DESCRIPTION
---|---
`sudo apt install pipx` | Install on Debian and Ubuntu (or `python3 -m pip install --user pipx`)
`pipx ensurepath` | Add pipx's bin directory to `PATH` (open a new shell afterwards)
`pipx install <PACKAGE>` | Install a tool in its own venv
`pipx install '<PACKAGE>==<VERSION>'` | Install a specific version
`pipx install --python <PYTHON> <PACKAGE>` | Use a particular interpreter
`pipx install --suffix <@SUFFIX> <PACKAGE>` | Install a second copy side by side
`pipx install --include-deps <PACKAGE>` | Also expose the dependencies' apps
`pipx install --pip-args '<ARGS>' <PACKAGE>` | Pass options through to pip (for example an index URL)
`pipx install --global <PACKAGE>` | System-wide install (`--global` works on most commands)
`pipx install git+https://example.com/<OWNER>/<REPO>.git` | Install from a Git URL
`pipx run <PACKAGE> <ARGS>` | Run once in a temporary environment, no install
`pipx run --spec '<PACKAGE>==<VERSION>' <COMMAND>` | Run a command from a specific package version
`pipx run --with <EXTRA_PACKAGE> <PACKAGE>` | Add extra packages to the temporary environment
`pipx run --no-cache <PACKAGE>` | Do not reuse a cached temporary environment
`pipx exec <APP>` | Run an app from an already installed environment

## pipx: Manage Tools
COMMAND | DESCRIPTION
---|---
`pipx list` | Installed tools and their apps (`--short`, `--json`, `--outdated`, `--include-injected`)
`pipx upgrade <PACKAGE>` | Upgrade one tool
`pipx upgrade-all` | Upgrade every tool
`pipx reinstall <PACKAGE>` / `pipx reinstall-all` | Rebuild after a Python upgrade
`pipx uninstall <PACKAGE>` / `pipx uninstall-all` | Remove
`pipx inject <TOOL> <EXTRA_PACKAGE>` | Add a package to a tool's venv (a plugin, for example)
`pipx uninject <TOOL> <EXTRA_PACKAGE>` | Remove it
`pipx runpip <TOOL> <PIP_ARGS>` | Run pip inside the tool's venv (`pipx runpip <TOOL> list`)
`pipx pin <PACKAGE>` / `pipx unpin <PACKAGE>` | Stop or resume upgrades for a tool
`pipx health` / `pipx repair` | Check, or fix, broken tool environments
`pipx interpreter list` | Python interpreters pipx manages
`pipx cache` | Manage cached `run` environments
`pipx environment` | Show the variables and paths pipx uses
`pipx completions` | Show how to enable shell completion

## pipx: Paths
VARIABLE | DESCRIPTION
---|---
`PIPX_HOME` | Where the tool venvs live
`PIPX_BIN_DIR` | Where the commands are linked (must be on `PATH`)
`PIPX_MAN_DIR` | Where man pages are linked
`PIPX_GLOBAL_HOME` / `PIPX_GLOBAL_BIN_DIR` | The same for `--global` installs

## Common Tasks
Reproducible dependencies for a project:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip freeze --exclude-editable > requirements.lock
python -m pip check
```

Offline install from a directory of downloads:

```bash
python -m pip download -d ./wheelhouse -r requirements.txt
python -m pip install --no-index --find-links ./wheelhouse -r requirements.txt
```

## Troubleshooting
SYMPTOM | FIX
---|---
`externally-managed-environment` error | Use a venv or `pipx`; avoid `--break-system-packages`
`pip: command not found` | Use `python3 -m pip`, or `sudo apt install python3-pip`
Tool installed with `pipx` is not found | Run `pipx ensurepath` and start a new shell
Tools break after a Python upgrade | `pipx reinstall-all`
Build fails for a package with C code | Install the compiler and headers (Debian: `build-essential python3-dev`), or use `--only-binary :all:`
Two tools need different versions of a library | Install each with `pipx`, not into one shared venv
`pip` installs into the wrong Python | Run `python -m pip`, and check with `pip --version`

## See Also
- [Python and uv](python-uv.md)
- [pre-commit](pre-commit.md)
- [Ansible Cheat-Sheet](../tools/ansible.md)

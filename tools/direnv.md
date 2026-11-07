# direnv
direnv loads and unloads environment variables when you `cd` into a directory, based on an `.envrc` file. Use it for per-project variables, tool versions on `PATH` and virtual environments, instead of exporting things by hand.

Documentation: [direnv documentation](https://direnv.net/) · [direnv-stdlib(1)](https://direnv.net/man/direnv-stdlib.1.html)
Project: [direnv on GitHub](https://github.com/direnv/direnv)

> **Verification:** commands and stdlib functions were checked against the `direnv` man page and `direnv stdlib` output in Ubuntu 24.04. Shell hook lines follow the direnv docs; the Fish and Nushell hooks were not run.

## Install and Hook
Install from your package manager (`sudo apt install direnv`, `brew install direnv`), then add the hook to your shell start-up file and restart the shell.

SHELL | LINE TO ADD
---|---
Bash (`~/.bashrc`) | `eval "$(direnv hook bash)"`
Zsh (`~/.zshrc`) | `eval "$(direnv hook zsh)"`
Fish (`~/.config/fish/config.fish`) | `direnv hook fish \| source`

See [Bash](../scripting/bash.md), [Zsh](../scripting/zsh.md) and [Fish](../scripting/fish.md) for start-up file details.

## Commands
COMMAND | DESCRIPTION
---|---
`direnv allow` | Trust the `.envrc` in the current directory
`direnv allow <PATH>` | Trust a given directory or file
`direnv deny` | Revoke trust
`direnv edit` | Edit `.envrc` in `$EDITOR` and allow it on save
`direnv reload` | Reload the environment now
`direnv status` | Which `.envrc` is loaded and whether it is allowed
`direnv exec <DIR> <COMMAND>` | Run a command with a directory's environment
`direnv prune` | Remove stale allow records
`direnv version` | Version

A changed `.envrc` is blocked until you run `direnv allow` again. That is the safety check against running code from a cloned repository.

## .envrc Examples
The file is Bash. Use the stdlib functions below rather than `export` where one exists.

```bash
# plain variables
export APP_ENV=development
export DATABASE_URL=postgres://user:PASSWORD@localhost:5432/app

# load a .env file
dotenv

# load .env only if it exists
dotenv_if_exists .env.local

# add a directory to PATH
PATH_add bin

# Python virtual environment (creates .direnv/python-<version> if needed)
layout python

# Node: use the version from .nvmrc (needs nvm)
use node

# watch extra files so changes trigger a reload
watch_file package.json
```

## Stdlib Functions
FUNCTION | DESCRIPTION
---|---
`PATH_add <DIR>` | Prepend a directory (relative to the `.envrc`) to `PATH`
`path_add <VAR> <DIR>` | Same for any path-like variable
`dotenv [FILE]` | Load a `.env` file (defaults to `.env`)
`dotenv_if_exists [FILE]` | As `dotenv`, silently skipped when missing
`source_env <FILE_OR_DIR>` | Load another `.envrc`
`source_env_if_exists <FILE>` | As above, skipped if missing
`source_up` | Load the `.envrc` from a parent directory
`layout python` | Per-project Python virtualenv under `.direnv/`
`layout node` | Add `node_modules/.bin` to `PATH`
`layout go` | Set `GOPATH` to `.direnv/go` and add its `bin` to `PATH`
`watch_file <FILE>` | Reload when the file changes
`use <TOOL> [VERSION]` | Call a `use_<TOOL>` function (for example `use node`, `use flake`)
`log_status <MESSAGE>` | Print a message when loading
`has <COMMAND>` | Test whether a command exists

List everything with `direnv stdlib`.

## Config File
`~/.config/direnv/direnv.toml` changes global behaviour:

```toml
[global]
warn_timeout = "30s"
```

Run `man direnv.toml` for all keys.

## Secrets
Never commit an `.envrc` that contains real secrets. Keep secrets in an untracked `.env` loaded with `dotenv`, or use a secrets manager: see [SOPS and age](../security/sops-age.md) and [Secret Scanning](../security/secret-scanning.md). Add `.envrc`, `.env` and `.direnv/` to `.gitignore` when they hold local values.

## Troubleshooting
SYMPTOM | FIX
---|---
`direnv: error .envrc is blocked` | Read it, then `direnv allow`
Nothing happens on `cd` | The hook is missing from your shell start-up file; restart the shell
Variables remain after leaving the directory | Only variables set through direnv are unloaded; check `direnv status`
Slow prompt | Avoid slow commands in `.envrc`; cache results or use `watch_file`
Editor or IDE does not see the variables | Start it from a shell inside the directory, or use its direnv extension

## See Also
- [Bash](../scripting/bash.md)
- [Zsh](../scripting/zsh.md)
- [Python and uv](../scripting/python-uv.md)
- [Modern CLI Tools](modern-cli-tools.md)
- [SOPS and age](../security/sops-age.md)

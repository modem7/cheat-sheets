# antidote
antidote is a fast Zsh plugin manager. It clones plugins from Git, then generates one static file that your `~/.zshrc` sources, so start-up stays quick. It can load [Oh My Zsh](oh-my-zsh.md) plugins without the full framework.

Project: [antidote](https://antidote.sh/)
Documentation: [antidote on GitHub](https://github.com/mattmc3/antidote)

Checked against antidote 2.3.0 using `antidote help` and its man pages.

## Install
```zsh
git clone --depth=1 https://github.com/mattmc3/antidote.git ${ZDOTDIR:-$HOME}/.antidote
```

Then in `~/.zshrc`:

```zsh
source ${ZDOTDIR:-$HOME}/.antidote/antidote.zsh
antidote load
```

`antidote load` reads `${ZDOTDIR:-$HOME}/.zsh_plugins.txt`, regenerates the static `.zsh_plugins.zsh` when needed and sources it.

## Commands
COMMAND | DESCRIPTION
---|---
`antidote load` | Statically source all bundles from the plugins file
`antidote bundle <FILE` | Clone bundles and print the static load script
`antidote install OWNER/REPO` | Clone a bundle and add it to the plugins file
`antidote update` | Update antidote and every cloned bundle
`antidote purge OWNER/REPO` | Remove one cloned bundle (`--all` removes every one)
`antidote list` | List cloned bundles (`-l` detail, `-d` dirs, `-u` URLs, `-j` JSON Lines)
`antidote path OWNER/REPO` | Print where a bundle is cloned
`antidote home` | Print the folder bundles are cloned into
`antidote init` | Set up dynamic bundling (see below)
`antidote snapshot save` / `list` / `restore` / `remove` / `home` | Manage point-in-time snapshots of bundle commits
`antidote help [COMMAND]` | Show the manual
`antidote --version`, `antidote --diagnostics` | Version and diagnostics

## The Plugins File
One bundle per line in `~/.zsh_plugins.txt`. `#` starts a comment. A bundle is `OWNER/REPO` (GitHub), a full Git URL, or a local file or folder.

```text
# plugins
zsh-users/zsh-completions kind:fpath path:src
zsh-users/zsh-autosuggestions
zsh-users/zsh-syntax-highlighting

# Oh My Zsh pieces
getantidote/use-omz
ohmyzsh/ohmyzsh path:lib
ohmyzsh/ohmyzsh path:plugins/git
ohmyzsh/ohmyzsh path:plugins/sudo

# theme
romkatv/powerlevel10k
```

Load `zsh-syntax-highlighting` near the end of the file; it must be loaded after other plugins that add widgets.

## Annotations
Written as `keyword:value` after the bundle.

ANNOTATION | EFFECT
---|---
`kind:zsh` | Source it as a plugin (the default)
`kind:fpath` | Only add it to `$fpath` (completions)
`kind:path` | Add it to `$PATH`
`kind:clone` | Only clone it
`kind:defer` | Load it after the prompt using `romkatv/zsh-defer`
`kind:autoload` | Autoload every file in the folder as a function
`path:SUBDIR` | Use a subfolder or file of the repo (e.g. `path:plugins/git`)
`branch:NAME` | Use a branch or tag instead of the default branch
`pin:SHA` | Lock to a full 40-character commit; skipped by `antidote update`
`conditional:FUNC` | Load only when the zero-argument function succeeds
`pre:FUNC`, `post:FUNC` | Run a function before / after the plugin loads
`autoload:DIR` | Also autoload a functions folder

Directives start a line and affect the lines after them:

```text
preset:ohmyzsh/ohmyzsh pin:FULL_40_CHAR_SHA

using:ohmyzsh/ohmyzsh path:plugins
git
sudo
extract
```

`using:` lets you list Oh My Zsh plugins as bare names. `preset:` sets default annotations for a bundle.

## Dynamic Bundling
No separate plugins file: bundles are listed in `~/.zshrc`.

```zsh
source ${ZDOTDIR:-$HOME}/.antidote/antidote.zsh
source <(antidote init)
antidote bundle zsh-users/zsh-autosuggestions
antidote bundle ohmyzsh/ohmyzsh path:plugins/git
```

Snapshots are only saved automatically after `antidote update` in static mode.

## Customisation
Set these with `zstyle` in `~/.zshrc` before `antidote load`:

ZSTYLE | EFFECT
---|---
`zstyle ':antidote:bundle' file PATH` | Use another plugins file
`zstyle ':antidote:static' file PATH` | Use another static file
`zstyle ':antidote:bundle:*' zcompile 'yes'` | Zsh-compile bundles
`zstyle ':antidote:bundle:*' min-age 7` | Hold bundles back by 7 days from upstream's newest commit
`zstyle ':antidote:snapshot' max 25` | Keep at most 25 snapshots
`ANTIDOTE_HOME=PATH` | Clone bundles somewhere else (default `~/.cache/antidote`)

## Regenerate Only When the File Changes
Avoids a rebuild on every shell start:

```zsh
zsh_plugins=${ZDOTDIR:-~}/.zsh_plugins
if [[ ! ${zsh_plugins}.zsh -nt ${zsh_plugins}.txt ]]; then
  antidote bundle <${zsh_plugins}.txt >${zsh_plugins}.zsh
fi
source ${zsh_plugins}.zsh
```

## Troubleshooting
SYMPTOM | FIX
---|---
New plugin not loaded | The static file is stale: `touch ~/.zsh_plugins.txt` or delete `~/.zsh_plugins.zsh`, then start a new shell
`antidote: command not found` | `~/.zshrc` must source `antidote.zsh` first
A plugin broke after an update | `antidote snapshot list`, then `antidote snapshot restore FILE`, or `pin:` the bundle
Pin or branch inconsistent | The same repo has different `pin:` / `branch:` on different lines: use `preset:` once
OMZ plugin cannot find helpers | Load `getantidote/use-omz` and `ohmyzsh/ohmyzsh path:lib` before OMZ plugins

## See Also
- [Zsh](zsh.md)
- [zshrc](zshrc.md)
- [Oh My Zsh](oh-my-zsh.md)
- [Powerlevel10k](powerlevel10k.md)
- [Zsh with antidote, Oh My Zsh and Powerlevel10k](../recipes/zsh-antidote-omz-p10k.md)

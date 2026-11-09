# Oh My Zsh
Oh My Zsh (OMZ) is a framework of Zsh plugins, themes and library files. You can use it on its own through its installer, or load only the parts you want through a plugin manager such as [antidote](antidote.md). For the underlying shell see [Zsh](zsh.md).

Project: [Oh My Zsh](https://ohmyz.sh/)
Documentation: [Oh My Zsh wiki](https://github.com/ohmyzsh/ohmyzsh/wiki)

The `omz` commands were read from the `omz` function in `lib/cli.zsh` of a current checkout. Plugin aliases were read from each plugin's README. The standalone installer was not run (`(unverified)`).

## Install and Update
COMMAND | DESCRIPTION
---|---
`sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"` | Standalone install into `~/.oh-my-zsh` (`(unverified)`; read the script first, it replaces `~/.zshrc` and keeps a backup)
`omz update` | Update Oh My Zsh
`omz version` | Show the version
`omz changelog` | Print the changelog
`omz reload` | Reload the current zsh session
`omz help` | List the commands
`omz pr test` / `omz pr clean` | Try a pull request / delete the pull request branches
`omz shellsaver` | Launch a Shellsaver (an aquarium by default); `omz shop` opens the shop

If you load OMZ through antidote there is no `~/.oh-my-zsh` and no `omz update`: update with `antidote update` instead.

## Plugins
COMMAND | DESCRIPTION
---|---
`omz plugin list` | List plugins
`omz plugin list --enabled` | List only the enabled plugins
`omz plugin info NAME` | Show a plugin's information
`omz plugin enable NAME` | Add a plugin to `plugins=(...)` in `~/.zshrc`
`omz plugin disable NAME` | Remove it
`omz plugin load NAME` | Load a plugin into the current shell only

In a standalone install, plugins live in `$ZSH/plugins` and your own in `$ZSH_CUSTOM/plugins`. Enable them in `~/.zshrc` **before** `source $ZSH/oh-my-zsh.sh`:

```zsh
plugins=(git sudo extract history)
```

## Themes
COMMAND | DESCRIPTION
---|---
`omz theme list` | List themes
`omz theme use NAME` | Load a theme in this shell only
`omz theme set NAME` | Write `ZSH_THEME` into `~/.zshrc`

The default theme is `robbyrussell`. For a faster, richer prompt see [Powerlevel10k](powerlevel10k.md), which replaces `ZSH_THEME` (set `ZSH_THEME=""` or `powerlevel10k/powerlevel10k` as its docs describe).

## Useful Plugins
PLUGIN | WHAT IT GIVES YOU
---|---
`git` | Dozens of aliases: `gst` (status), `ga` / `gaa` (add), `gcmsg` (commit message), `gcam` (commit all), `gco` / `gcb` (checkout / new branch), `gsw` (switch), `gl` / `gp` (pull / push), `gpf` (force with lease), `gfa` (fetch all, prune), `glog` (graph log), `gstp` (stash pop), `gwip` (wip commit)
`sudo` | Press `Esc` twice to prefix the current (or previous) command with `sudo`
`extract` | `extract FILE` unpacks most archive types
`history` | Aliases `h`, `hl` (less), `hs` (grep), `hsi` (case-insensitive grep); see [Shell History](shell-history.md)
`history-substring-search` | Up / down arrows search history by what you have typed
`per-directory-history` | History per directory with a global toggle
`z` | Jump to frequently used directories
`fzf` | Fuzzy finder key bindings and completion (needs `fzf` installed)
`command-not-found` | Suggest the package that provides a missing command
`systemd`, `ubuntu`, `ansible` | Aliases and completions for those tools

Check a plugin's README (`omz plugin info NAME` or its folder) before enabling it: several wrap commands you may not have installed.

## Useful Settings
Set in `~/.zshrc` before `source $ZSH/oh-my-zsh.sh`:

VARIABLE | EFFECT
---|---
`ZSH_THEME` | Theme name
`plugins=(...)` | Enabled plugins
`ZSH_CUSTOM` | Folder for your own plugins and themes
`DISABLE_AUTO_UPDATE`, `DISABLE_UPDATE_PROMPT` | Control the update behaviour (commented examples are in the template `zshrc`)

## Troubleshooting
SYMPTOM | FIX
---|---
`omz: command not found` | OMZ is not loaded as the framework (e.g. loaded through antidote `use-omz`); use your plugin manager instead
Plugin alias does nothing | The plugin is not in `plugins=(...)`, or is listed after `source $ZSH/oh-my-zsh.sh`
Slow start | Remove plugins you do not use, and see [Powerlevel10k](powerlevel10k.md) instant prompt
Theme icons show as boxes | Install a Nerd Font and select it in your terminal

## See Also
- [Zsh](zsh.md)
- [zshrc](zshrc.md)
- [antidote](antidote.md)
- [Powerlevel10k](powerlevel10k.md)
- [Shell History](shell-history.md)
- [Zsh with antidote, Oh My Zsh and Powerlevel10k](../recipes/zsh-antidote-omz-p10k.md)

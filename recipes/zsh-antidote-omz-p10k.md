# Zsh with antidote, Oh My Zsh and Powerlevel10k
Goal: a fast, reproducible Zsh set-up: antidote loads Oh My Zsh plugins, completions, autosuggestions and syntax highlighting, Powerlevel10k draws the prompt, and history is shared and deduplicated. The same three files rebuild it on any machine.

> **Verification:** antidote commands and annotations were checked against antidote 2.3.0 on Ubuntu, and the plugin list below is the one in use there. The Nerd Font step and a from-scratch run on a clean machine were not repeated for this recipe.

## Prerequisites
- Zsh 5.x and Git (`sudo apt install zsh git` on Debian or Ubuntu)
- A terminal using a [Nerd Font](https://www.nerdfonts.com/) (MesloLGS NF is the Powerlevel10k default)
- Zsh as your login shell: `chsh -s "$(command -v zsh)"`, then log out and in

## Steps
1. Back up what you have.

   ```bash
   cp ~/.zshrc ~/.zshrc.bak
   ```

2. Create the plugin list at `~/.zsh_plugins.txt`.

   ```text
   # Oh My Zsh core, loaded without the framework
   getantidote/use-omz
   ohmyzsh/ohmyzsh path:lib

   # Theme
   romkatv/powerlevel10k

   # Oh My Zsh plugins
   ohmyzsh/ohmyzsh path:plugins/git
   ohmyzsh/ohmyzsh path:plugins/sudo
   ohmyzsh/ohmyzsh path:plugins/extract
   ohmyzsh/ohmyzsh path:plugins/history

   # Completions, suggestions and highlighting (highlighting last)
   zsh-users/zsh-completions
   zsh-users/zsh-autosuggestions
   zsh-users/zsh-syntax-highlighting
   ```

3. Write `~/.zshrc` (see [zshrc](../scripting/zshrc.md) for the full annotated version).

   ```zsh
   if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
     source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
   fi

   typeset -U PATH path

   [[ -e ${ZDOTDIR:-~}/.antidote ]] ||
     git clone --depth=1 --quiet https://github.com/mattmc3/antidote.git ${ZDOTDIR:-~}/.antidote
   source ${ZDOTDIR:-~}/.antidote/antidote.zsh
   zsh_plugins=${ZDOTDIR:-~}/.zsh_plugins
   if [[ ! ${zsh_plugins}.zsh -nt ${zsh_plugins}.txt ]]; then
     antidote bundle <${zsh_plugins}.txt >${zsh_plugins}.zsh
   fi
   source ${zsh_plugins}.zsh

   HISTFILE=~/.zsh_history
   HISTSIZE=100000
   SAVEHIST=100000
   setopt EXTENDED_HISTORY SHARE_HISTORY HIST_IGNORE_ALL_DUPS HIST_IGNORE_SPACE HIST_VERIFY

   zstyle ':completion:*' menu select
   autoload -Uz compinit && compinit

   [[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh
   ```

4. Start a new shell. antidote clones itself and each plugin on first run, then the Powerlevel10k wizard starts. If it does not, run:

   ```bash
   exec zsh
   p10k configure
   ```

5. Add or remove plugins later by editing `~/.zsh_plugins.txt`. The static file rebuilds on the next shell start.

6. Update everything with `antidote update` (see [antidote](../scripting/antidote.md)).

## Verify
COMMAND | EXPECTED
---|---
`echo $ZSH_VERSION` | A 5.x version
`antidote list` | The cloned plugins from your list
`type gst` | `gst` is an alias for `git status` (from the OMZ git plugin)
`print -P '%F{green}ok%f'` | Green `ok`
`time zsh -i -c exit` | Well under a second after the first run
`p10k help segment` | Prints help (proves the theme loaded)

## Troubleshooting
SYMPTOM | FIX
---|---
No plugins load | `~/.zsh_plugins.zsh` empty or stale: delete it, start a new shell, read any error
Warning about output during start-up | Something prints before the prompt; move it above the instant prompt block or silence it
Icons are boxes | Select the Nerd Font in the terminal profile
OMZ plugin errors on a missing function | `getantidote/use-omz` and `ohmyzsh/ohmyzsh path:lib` must come before OMZ plugins in the list
Completions missing for a new tool | `rm -f ~/.zcompdump*; exec zsh`
History not shared | Check `SHARE_HISTORY` is set and `HISTFILE` points to the same file in both shells

## Rollback
```bash
cp ~/.zshrc.bak ~/.zshrc
rm -rf ~/.antidote ~/.cache/antidote ~/.zsh_plugins.zsh ~/.zsh_plugins.txt ~/.p10k.zsh
exec zsh
```

## Related Sheets
- [Zsh](../scripting/zsh.md)
- [zshrc](../scripting/zshrc.md)
- [antidote](../scripting/antidote.md)
- [Oh My Zsh](../scripting/oh-my-zsh.md)
- [Powerlevel10k](../scripting/powerlevel10k.md)
- [Shell History](../scripting/shell-history.md)

# zshrc
A commented layout for `~/.zshrc`, the file Zsh reads for every interactive shell. It ties together [antidote](antidote.md), [Oh My Zsh](oh-my-zsh.md) plugins, [Powerlevel10k](powerlevel10k.md), [history](shell-history.md) and completion. Language features are in [Zsh](zsh.md).

Documentation: [Zsh Startup Files](https://zsh.sourceforge.io/Doc/Release/Files.html)

The layout below is based on a working setup and was run under Zsh 5.9.

## Order Matters
ORDER | BLOCK | WHY
---|---|---
1 | Powerlevel10k instant prompt | Must be at the very top
2 | `PATH` and environment | Available to everything below
3 | Plugin manager and plugins | Loads the theme, completions and widgets
4 | History options | Independent of plugins
5 | Shell options (`AUTO_CD`, `CORRECT`) | Behaviour
6 | `zstyle` completion settings, then `compinit` | `compinit` after `fpath` is final
7 | Plugin settings (highlight colours, suggestion style) | After plugins are loaded
8 | Key bindings | After plugins, so they win
9 | Aliases and functions | Anywhere
10 | `source ~/.p10k.zsh` | After the theme is loaded

## Skeleton
```zsh
# 1. p10k instant prompt (top of file; copy verbatim)
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# 2. PATH without duplicates
typeset -U PATH path
path=("$HOME/bin" "$HOME/.local/bin" $path)

# 3. antidote: clone if missing, rebuild the static file only when the list changed
[[ -e ${ZDOTDIR:-~}/.antidote ]] ||
  git clone --depth=1 --quiet https://github.com/mattmc3/antidote.git ${ZDOTDIR:-~}/.antidote
source ${ZDOTDIR:-~}/.antidote/antidote.zsh
zsh_plugins=${ZDOTDIR:-~}/.zsh_plugins
if [[ ! ${zsh_plugins}.zsh -nt ${zsh_plugins}.txt ]]; then
  antidote bundle <${zsh_plugins}.txt >${zsh_plugins}.zsh
fi
source ${zsh_plugins}.zsh

# 4. history
HISTFILE=~/.zsh_history
HISTSIZE=100000
SAVEHIST=100000
setopt EXTENDED_HISTORY SHARE_HISTORY HIST_IGNORE_ALL_DUPS HIST_IGNORE_SPACE HIST_REDUCE_BLANKS HIST_VERIFY

# 5. behaviour
setopt AUTO_CD CORRECT

# 6. completion
zstyle ':completion:*' menu select
zstyle ':completion:*' list-colors ${(s.:.)LS_COLORS}
autoload -Uz compinit
if [[ -n ~/.zcompdump(#qN.mh+24) ]]; then compinit; else compinit -C; fi

# 9. aliases
alias ll='ls -alF'

# 10. prompt config
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh
```

Do not paste block 3 into a file that also loads Oh My Zsh through its own installer: use one or the other.

## Completion Cache
`compinit` builds `~/.zcompdump`, which is slow. The `(#qN.mh+24)` glob qualifier is true when the file is more than 24 hours old, so the full `compinit` runs once a day and `compinit -C` (skip the security check and reuse the cache) runs otherwise.

COMMAND | DESCRIPTION
---|---
`rm -f ~/.zcompdump*; exec zsh` | Rebuild completions after installing a tool or plugin
`compaudit` | List insecure completion directories
`compinit -C` | Start fast, trusting the cache

## Plugin Settings
SETTING | EFFECT
---|---
`ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE="fg=#4e4e4e"` | Colour of the grey suggestion text
`ZSH_HIGHLIGHT_HIGHLIGHTERS=(main brackets cursor)` | Which syntax-highlighting passes to run
`ZSH_HIGHLIGHT_STYLES[cursor]='bg=#4e4e4e'` | Style one highlight element

## Key Bindings
```zsh
typeset -g -A key
key[Home]="${terminfo[khome]}"
key[End]="${terminfo[kend]}"
key[Delete]="${terminfo[kdch1]}"
[[ -n "${key[Home]}"   ]] && bindkey -- "${key[Home]}"   beginning-of-line
[[ -n "${key[End]}"    ]] && bindkey -- "${key[End]}"    end-of-line
[[ -n "${key[Delete]}" ]] && bindkey -- "${key[Delete]}" delete-char
```

The `terminfo` values are only valid in application mode, so enable it while the line editor is active:

```zsh
if (( ${+terminfo[smkx]} && ${+terminfo[rmkx]} )); then
  autoload -Uz add-zle-hook-widget
  zle_application_mode_start() { echoti smkx }
  zle_application_mode_stop()  { echoti rmkx }
  add-zle-hook-widget -Uz zle-line-init   zle_application_mode_start
  add-zle-hook-widget -Uz zle-line-finish zle_application_mode_stop
fi
```

## Per-Machine Overrides
Keep machine-specific settings out of the shared file:

```zsh
[[ -f ~/.zshrc.local ]] && source ~/.zshrc.local
```

## Profiling a Slow Start
COMMAND | DESCRIPTION
---|---
`time zsh -i -c exit` | Time an interactive start
`zsh -f` | Start with no startup files, to compare
`zmodload zsh/zprof` then `zprof` | Add the first at the top of `~/.zshrc` and run `zprof` at the end: shows time per function
`zsh -xv` | Trace everything (very noisy)

## Troubleshooting
SYMPTOM | FIX
---|---
Plugin change has no effect | Static file is stale: `touch ~/.zsh_plugins.txt`, start a new shell
`compdef: command not found` | A plugin calls `compdef` before `compinit`: run `compinit` first or load that plugin later
Warning about console output at start | Something prints during start-up; see [Powerlevel10k](powerlevel10k.md) instant prompt
Home/End keys print `~` | Add the key bindings above
Changes in `~/.zshrc` not seen | `exec zsh` or `omz reload`

## See Also
- [Zsh](zsh.md)
- [antidote](antidote.md)
- [Oh My Zsh](oh-my-zsh.md)
- [Powerlevel10k](powerlevel10k.md)
- [Shell History](shell-history.md)
- [bashrc](bashrc.md)
- [Zsh with antidote, Oh My Zsh and Powerlevel10k](../recipes/zsh-antidote-omz-p10k.md)

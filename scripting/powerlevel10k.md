# Powerlevel10k
Powerlevel10k (p10k) is a fast, highly configurable Zsh prompt theme with a built-in configuration wizard and an "instant prompt" that shows the prompt before plugins finish loading. For a cross-shell alternative see [Starship Prompt](../tools/starship.md).

Project: [Powerlevel10k](https://github.com/romkatv/powerlevel10k)
Documentation: [Powerlevel10k README](https://github.com/romkatv/powerlevel10k#readme)

Commands and settings were read from the project README and checked against a working `~/.p10k.zsh`.

## Commands
COMMAND | DESCRIPTION
---|---
`p10k configure` | Run the wizard; writes `~/.p10k.zsh` and adds the loader line to `~/.zshrc`
`p10k reload` | Apply `POWERLEVEL9K_*` changes made in a running shell
`p10k help segment` | Reference for defining your own prompt segment
`p10k segment -t TEXT` | Print a segment from inside a custom segment function (see `p10k help segment`)

## Install
Pick one. With [antidote](antidote.md), add one line to `~/.zsh_plugins.txt`:

```text
romkatv/powerlevel10k
```

With [Oh My Zsh](oh-my-zsh.md) standalone, clone it into the custom themes folder and set the theme:

```zsh
git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k
```

```zsh
ZSH_THEME="powerlevel10k/powerlevel10k"
```

Restart the shell. The wizard starts by itself; run `p10k configure` if it does not.

## Fonts
Pick **MesloLGS NF** (recommended by the project) or another [Nerd Font](https://www.nerdfonts.com/), and select it in your terminal. iTerm2 and Termux can install the font from the wizard. Icons showing as boxes or question marks means the terminal font is wrong.

## `~/.zshrc` Layout
Keep the instant prompt block at the very top and the config source after the plugins:

```zsh
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# ... plugin manager and theme load here ...

[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh
```

Copy the instant prompt block verbatim. Anything that prompts for input (passwords, `[y/n]`) must go **above** it.

## Settings
Set in `~/.p10k.zsh` (the wizard writes them). Run `p10k reload` after editing a live shell.

SETTING | EFFECT
---|---
`POWERLEVEL9K_LEFT_PROMPT_ELEMENTS=(...)` | Segments on the left (e.g. `dir`, `vcs`, `prompt_char`)
`POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS=(...)` | Segments on the right (e.g. `status`, `command_execution_time`, `time`)
`POWERLEVEL9K_MODE` | Character set (e.g. `nerdfont-complete`); best left to `p10k configure`
`POWERLEVEL9K_INSTANT_PROMPT` | `verbose` (warn about output), `quiet`, or `off`
`POWERLEVEL9K_DISABLE_HOT_RELOAD=false` | Apply edits without `p10k reload`, at a small speed cost
`POWERLEVEL9K_TRANSIENT_PROMPT` | `off`, `always` or `same-dir`: trim the prompt of accepted command lines
`POWERLEVEL9K_DIR_MAX_LENGTH` / `POWERLEVEL9K_SHORTEN_STRATEGY` | How the directory is shortened

Add your own segment functions with the prefix `my_` (e.g. `prompt_my_temp`) and put `my_temp` in a prompt elements array.

## Troubleshooting
SYMPTOM | FIX
---|---
Wizard does not start | Run `p10k configure`; make sure the theme is loaded before `source ~/.p10k.zsh`
Boxes instead of icons | Install and select a Nerd Font, or choose ASCII in the wizard
"console output during zsh initialization" warning | Something prints during start-up: silence or move it above the instant prompt block, or set `POWERLEVEL9K_INSTANT_PROMPT=quiet`
Password prompt hangs at start | Move it above the instant prompt block
Prompt does not match config | Run `p10k reload`, or `exec zsh`
Theme gone after `antidote update` | Check the `romkatv/powerlevel10k` line is still in `~/.zsh_plugins.txt` and the static file is regenerated

## See Also
- [Zsh](zsh.md)
- [zshrc](zshrc.md)
- [antidote](antidote.md)
- [Oh My Zsh](oh-my-zsh.md)
- [Starship Prompt](../tools/starship.md)
- [Zsh with antidote, Oh My Zsh and Powerlevel10k](../recipes/zsh-antidote-omz-p10k.md)

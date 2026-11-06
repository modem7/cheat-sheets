# Starship Prompt
Starship is a minimal, blazing-fast, and infinitely customizable prompt for any shell. 

Project Homepage: [Starship: Cross-Shell Prompt](https://starship.rs/)
Documentation: [Configuration | Starship](https://starship.rs/config/)

A [Nerd Font](https://www.nerdfonts.com/) in your terminal is recommended for the icons.

## Installation

### Linux
1. Install the latest version for your system:
```
curl -sS https://starship.rs/install.sh | sh
```
2. Add the following to the end of `~/.bashrc` or `~/.zshrc`:
```
eval "$(starship init bash)"
# -- or --
eval "$(starship init zsh)"
```

### macOS
```
brew install starship
```

### Windows
```powershell
winget install --id Starship.Starship
```
Add to your PowerShell profile (`code $PROFILE`, see [PowerShell Cheat-Sheet](../windows/powershell.md)):
```powershell
Invoke-Expression (&starship init powershell)
```

## Configuration
Config lives in `~/.config/starship.toml`.

COMMAND | DESCRIPTION
---|---
`starship preset --list` | List built-in presets
`starship preset nerd-font-symbols -o ~/.config/starship.toml` | Apply a preset
`starship config` | Open the config in `$EDITOR`
`starship explain` | Explain each module shown in the current prompt
`starship timings` | Which modules are slow
`starship bug-report` | Gather details for an issue
`STARSHIP_CONFIG=~/alt.toml starship prompt` | Use a different config file

Example `starship.toml`:
```toml
add_newline = true
command_timeout = 500

[character]
success_symbol = "[➜](bold green)"
error_symbol = "[✗](bold red)"

[directory]
truncation_length = 3
truncate_to_repo = true

[git_branch]
symbol = " "

[kubernetes]
disabled = false
format = '[$symbol$context( \($namespace\))]($style) '

[docker_context]
disabled = true

[cmd_duration]
min_time = 2000
```

## Tips
- Disable modules you do not use, and set `command_timeout` to keep the prompt snappy in large repositories.
- Modules for [Kubectl](../kubernetes/kubectl.md) context, Python venv and cloud accounts are off or lightweight by default. Enable what you need.

# Windows Terminal
Modern tabbed terminal for Windows hosting PowerShell ([[powershell]]), Command Prompt and WSL ([[wsl]]).

## Install Windows Terminal
Windows Store: [Windows Terminal](https://aka.ms/terminal), or `winget install Microsoft.WindowsTerminal`

## Keyboard Shortcuts

### Application commands
SHORTCUT | ACTION
---|---
`Alt+F4` | Close window
`Ctrl+Shift+F` | Find
`Ctrl+Shift+Space` | Open dropdown
`Ctrl+,` | Open settings
`Ctrl+Shift+,` | Open settings.json
`Ctrl+Shift+P` | Command palette
`Alt+Enter` / `F11` | Toggle full screen

### Tab commands
SHORTCUT | ACTION
---|---
`Ctrl+Shift+D` | Duplicate tab
`Ctrl+Shift+T` | New tab
`Ctrl+Shift+1..9` | New tab from profile 1 to 9
`Ctrl+Tab` | Switch to next tab
`Ctrl+Shift+Tab` | Switch to previous tab
`Ctrl+Alt+1..9` | Switch to tab 1 to 9

### Pane commands
SHORTCUT | ACTION
---|---
`Alt+Shift+D` | Split pane automatically, same profile
`Alt+Shift+-` | Split pane horizontally
`Alt+Shift++` | Split pane vertically
`Alt+Shift+Arrows` | Resize pane
`Alt+Arrows` | Move pane focus
`Ctrl+Shift+W` | Close innermost pane, tab or window

### Clipboard, scrollback and zoom
SHORTCUT | ACTION
---|---
`Ctrl+Shift+C` / `Ctrl+Shift+V` | Copy / paste (plain `Ctrl+C` copies only when text is selected)
`Ctrl+Shift+Up` / `Down` | Scroll one line
`Ctrl+Shift+PgUp` / `PgDn` | Scroll one page
`Ctrl+=` / `Ctrl+-` / `Ctrl+0` | Increase / decrease / reset font size

## Command Line
```powershell
wt                                      # open Windows Terminal
wt -d C:\src                            # start in a folder
wt -p "Ubuntu"                          # open a profile
wt new-tab -p "PowerShell" ; split-pane -p "Ubuntu"   # tab with a split pane
```

## settings.json Tips
```json
{
  "defaultProfile": "{guid}",
  "profiles": {
    "defaults": { "font": { "face": "CaskaydiaCove Nerd Font", "size": 11 } }
  },
  "copyOnSelect": true
}
```
A Nerd Font is needed for Starship icons ([[starship]]).

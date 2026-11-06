# iTerm2
macOS terminal replacement. A good companion is a multiplexer such as [tmux](tmux.md), and a prompt such as [Starship Prompt](starship.md).

Install: `brew install --cask iterm2`

## Tabs and Windows
Shortcut | Description
---|---
`[⌘ Command] + [T]` | New Tab
`[⌘ Command] + [⟶ Right]` | Next Tab
`[⌘ Command] + [⟵ Left]` | Previous Tab
`[⌘ Command] + [W]` | Close Window or Tab
`[⇧ Shift] + [⌘ Command] + [⟶ Right]` | Move Tab right
`[⇧ Shift] + [⌘ Command] + [⟵ Left]` | Move Tab left
`[⌘ Command] + [1], [2], ...` | Go to Tab 1,2,...
`[⌘ Command] + [D]` | Split Window Vertically
`[⇧ Shift] + [⌘ Command] + [D]` | Split Window Horizontally
`[⌘ Command] + [⌥ Option] + [Arrows]` | Move between split panes
`[⇧ Shift] + [⌘ Command] + [↵ Enter]` | Maximize/restore the current pane
`[⌘ Command] + [↵ Enter]` | Toggle Fullscreen

## Cursor and selection
Shortcut | Description
---|---
`[˄ Control] + [B]` | Move back one character
`[˄ Control] + [F]` | Move forward one character
`[˄ Control] + [D]` | Delete current character
`[˄ Control] + [W]` | Delete previous word (in shell)
`[˄ Control] + [A]` | Move to the start of line
`[˄ Control] + [E]` | Move to the end of line
`[˄ Control] + [K]` | Delete to end of line
`[˄ Control] + [U]` | Delete to start of line
`[˄ Control] + [R]` | Reverse history search

## Search, Clipboard and Tools
Shortcut | Description
---|---
`[⌘ Command] + [F]` | Find
`[⌘ Command] + [;]` | Autocomplete from scrollback
`[⌘ Command] + [⇧ Shift] + [H]` | Paste history
`[⌘ Command] + [K]` | Clear buffer
`[˄ Control] + [L]` | Clear screen (shell)
`[⌘ Command] + [⇧ Shift] + [M]` | Set a mark, then `[⌘] + [⇧] + [↑]` jumps to previous mark
`[⌘ Command] + [⌥ Option] + [B]` | Instant Replay
`[⌘ Command] + [⇧ Shift] + [I]` | Broadcast input to all panes
`[⌘ Command] + [,]` | Preferences
Hold `[⌘ Command]` and click | Open a URL or file path under the cursor
Hold `[⌥ Option]` and drag | Rectangular selection

## Tips
- Enable **Profiles > Keys > Left Option key: Esc+** for word-jump shortcuts in shells.
- Shell integration: **iTerm2 > Install Shell Integration** gives command marks, `imgcat` and file download.
- `Profiles > Text > Font`: use a Nerd Font for prompt icons.

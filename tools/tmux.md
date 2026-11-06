# tmux
tmux is a terminal multiplexer: persistent sessions, split panes and windows that survive SSH disconnects ([OpenSSH Cheat-Sheet](openssh.md)).

Default prefix is `Ctrl+b`. In the tables, "prefix" means press `Ctrl+b`, release, then the key.

## Sessions
COMMAND | DESCRIPTION
---|---
`tmux` | New session
`tmux new -s <NAME>` | New named session
`tmux ls` | List sessions
`tmux attach -t <NAME>` / `tmux a` | Attach (most recent with `a`)
`tmux new -A -s <NAME>` | Attach, or create if missing
`tmux kill-session -t <NAME>` | Kill a session
`tmux kill-server` | Kill everything
`prefix d` | Detach
`prefix $` | Rename session
`prefix s` | Switch session
`prefix (` / `)` | Previous / next session

## Windows (tabs)
KEYS | DESCRIPTION
---|---
`prefix c` | New window
`prefix ,` | Rename window
`prefix n` / `p` | Next / previous window
`prefix 0-9` | Go to window number
`prefix w` | Window list
`prefix &` | Close window

## Panes
KEYS | DESCRIPTION
---|---
`prefix %` | Split left/right
`prefix "` | Split top/bottom
`prefix arrow` | Move between panes
`prefix o` | Next pane
`prefix z` | Zoom pane toggle
`prefix x` | Close pane
`prefix {` / `}` | Swap pane
`prefix Space` | Cycle layouts
`prefix Ctrl+arrow` | Resize (hold Ctrl)
`prefix q` | Show pane numbers
`prefix !` | Break pane into its own window

## Copy Mode and Scrolling
KEYS | DESCRIPTION
---|---
`prefix [` | Enter copy mode (scroll with arrows or PgUp)
`q` | Leave copy mode
`/` or `?` | Search forward / backward (in copy mode)
`Space`, `Enter` | Start selection, copy (default emacs keys)
`prefix ]` | Paste

## Useful ~/.tmux.conf
```tmux
set -g mouse on
set -g history-limit 50000
set -g base-index 1
setw -g pane-base-index 1
set -g renumber-windows on
set -sg escape-time 10
set -g default-terminal "tmux-256color"
setw -g mode-keys vi

bind | split-window -h -c "#{pane_current_path}"
bind - split-window -v -c "#{pane_current_path}"
bind r source-file ~/.tmux.conf \; display "Reloaded"
```
Reload without restarting: `tmux source-file ~/.tmux.conf`.

## Scripting
COMMAND | DESCRIPTION
---|---
`tmux send-keys -t <NAME> "<CMD>" Enter` | Type a command into a session
`tmux capture-pane -t <NAME> -p` | Print the pane contents
`tmux new -d -s <NAME> "<CMD>"` | Run a command in a detached session
`tmux split-window -h "<CMD>"` | Split and run a command

## Plugins
Install TPM: `git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm`, then in `.tmux.conf`:
```tmux
set -g @plugin 'tmux-plugins/tpm'
set -g @plugin 'tmux-plugins/tmux-resurrect'
run '~/.tmux/plugins/tpm/tpm'
```
Install with `prefix I`.

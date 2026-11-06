# Modern CLI Tools
Faster, friendlier replacements and add-ons for classic Unix commands. Package names are for Ubuntu 24.04 unless noted. Use [[homebrew]] on macOS (and Linux), or `cargo install` for the Rust ones. See [[linuxbasics]] for classic commands.

TOOL | REPLACES | INSTALL (APT)
---|---|---
`ripgrep` (`rg`) | `grep -r` | `sudo apt install ripgrep`
`fd` | `find` | `sudo apt install fd-find` (binary is `fdfind`)
`fzf` | interactive filter | `sudo apt install fzf`
`bat` | `cat` | `sudo apt install bat` (binary is `batcat`)
`eza` | `ls` | `sudo apt install eza`
`zoxide` | `cd` | `sudo apt install zoxide`
`btop` | `top` / `htop` | `sudo apt install btop`
`ncdu` | `du` | `sudo apt install ncdu`
`tldr` | `man` summaries | `sudo apt install tldr`
`httpie` (`http`) | `curl` for APIs | `sudo apt install httpie`
`lazygit` | git TUI | `brew install lazygit`, or the release binary
`delta` | `git diff` pager | `brew install git-delta`
`dust` | `du` (visual tree) | `cargo install du-dust`, or `brew install dust`
`hyperfine` | `time` (benchmarking) | `sudo apt install hyperfine`

Some of these may be missing from older releases. Fall back to `cargo install` or a release binary. Aliases for Debian-renamed binaries:
```bash
alias fd=fdfind
alias bat=batcat
```

## ripgrep
COMMAND | DESCRIPTION
---|---
`rg "text"` | Search recursively, respecting `.gitignore`
`rg -i "text"` | Ignore case
`rg -F "a.b"` | Fixed string, no regex
`rg -l "text"` | File names only
`rg -c "text"` | Count per file
`rg -t py "def "` | Only Python files (`rg --type-list`)
`rg -g '*.md' "text"` | Glob filter (`-g '!dist'` excludes)
`rg -C 3 "text"` | Context lines
`rg --hidden "text"` | Include hidden files
`rg -n -e "a" -e "b"` | Multiple patterns
`rg "foo" -r "bar"` | Show replacements (does not edit files)
`rg -w "word"` | Whole-word match
`rg -v "text"` | Invert: lines that do not match
`rg -o "[0-9.]+"` | Print only the matching part
`rg -U "start.*\n.*end"` | Multiline match
`rg --files` | List files that would be searched (like `fd` with ignore rules)
`rg --files -g '*.yml'` | List files matching a glob
`rg -z "text" file.gz` | Search inside compressed files
`rg --stats "text"` | Match and file counts
`rg --json "text"` | JSON output for scripts ([[jq]])
`rg -uuu "text"` | Search everything: no ignore rules, hidden and binary files
`rg -A 2 -B 1 "text"` | Lines after and before

For classic tools see [[grep]], [[sed]] and [[awk]]. Put defaults in a file and point `RIPGREP_CONFIG_PATH` at it (one flag per line, for example `--smart-case`).

## fd
COMMAND | DESCRIPTION
---|---
`fd name` | Find by regex in file names
`fd -e md` | By extension
`fd -t d` | Directories only (`-t f` files)
`fd -H -I name` | Include hidden and ignored files
`fd -e log -x gzip {}` | Run a command on each match
`fd -e tmp -X rm` | One command with all matches
`fd -g '*.conf' /etc` | Glob instead of regex, in a given directory
`fd -d 2 name` | Limit search depth
`fd --changed-within 1d` | Modified in the last day (`--changed-before` too)
`fd -S +100M` | Larger than 100 MB (`-S -1k` for smaller)
`fd -E node_modules -E .git name` | Exclude paths
`fd -p 'src/.*test'` | Match against the full path
`fd -0 -e jpg \| xargs -0 ls -l` | NUL-separated output for safe piping

## fzf
COMMAND | DESCRIPTION
---|---
`fzf` | Pick a file interactively
`Ctrl`+`R` | Fuzzy search shell history (after the shell integration is enabled)
`Ctrl`+`T` | Paste a file path
`Alt`+`C` | `cd` into a directory
`git branch \| fzf \| xargs git checkout` | Pick a branch ([[git]])
`kubectl get pods -o name \| fzf` | Pick a resource ([[kubectl]])
`fzf --preview 'bat --color=always {}'` | File preview
`fzf -m` | Multi-select with `Tab`
`fzf --height 40% --reverse` | Compact inline layout
`fzf -e` / `fzf '^start'` | Exact match / anchor to start (`'word` for exact term, `!word` to exclude)
`fzf --bind 'enter:become(vim {})'` | Replace fzf with an editor on Enter

Enable key bindings in bash or zsh: `eval "$(fzf --bash)"` or `source <(fzf --zsh)` (fzf 0.48 and later; older packages ship a `key-bindings.bash` file instead).

Useful environment variables for your shell profile:
```bash
export FZF_DEFAULT_COMMAND='fd --type f --hidden --exclude .git'
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
export FZF_DEFAULT_OPTS='--height 40% --layout=reverse --border'
export FZF_CTRL_T_OPTS="--preview 'bat -n --color=always {}'"
```

### fzf Combos
COMMAND | DESCRIPTION
---|---
`git switch "$(git branch --all \| sed 's/^[* ]*//' \| fzf)"` | Pick and switch branch ([[git]])
`git log --oneline \| fzf --preview 'git show --color=always {1}'` | Browse commits with a diff preview
`git diff --name-only \| fzf -m \| xargs git add` | Stage chosen changed files
`docker ps -a --format '{{.Names}}' \| fzf \| xargs docker logs -f` | Follow logs of a chosen container ([[docker]])
`docker exec -it "$(docker ps --format '{{.Names}}' \| fzf)" sh` | Shell into a chosen container
`kubectl get pods -o name \| fzf \| xargs kubectl logs -f` | Logs of a chosen pod ([[kubectl]])
`kubectl config get-contexts -o name \| fzf \| xargs kubectl config use-context` | Switch cluster context
`kill -9 $(ps -ef \| sed 1d \| fzf -m \| awk '{print $2}')` | Pick processes to kill
`rg --line-number . \| fzf --delimiter : --preview 'bat --color=always --highlight-line {2} {1}'` | Search file contents interactively
`rg -l "text" \| fzf --preview 'bat --color=always {}'` | Files containing text, with preview
`fd -t d \| fzf` | Pick a directory
`cd "$(fd -t d \| fzf)"` | `cd` into a chosen directory
`ssh "$(grep '^Host ' ~/.ssh/config \| cut -d' ' -f2 \| fzf)"` | Pick an SSH host ([[openssh]])
`systemctl list-units --type=service --no-legend \| fzf` | Browse services

## bat, eza, zoxide
COMMAND | DESCRIPTION
---|---
`bat file` | Show with syntax highlighting and line numbers
`bat -p file` | Plain output (no decorations), good for piping
`eza -lah --git` | Long list with git status
`eza --tree --level=2` | Tree view
`eval "$(zoxide init bash)"` | Enable `z` in your shell (`zsh` for zsh)
`z proj` | Jump to the most frequent matching directory
`zi` | Pick a directory interactively
`bat -r 10:20 file` | Show only lines 10 to 20
`bat -l yaml` | Force a language (useful when piping)
`bat --list-themes` | Available themes (set with `BAT_THEME` or `--theme`)
`bat -A file` | Show non-printable characters
`bat cache --build` | Rebuild the syntax cache after adding syntaxes
`eza -l --sort=modified` | Sort by modification time (`--sort=size`, `--reverse`)
`eza -T -L 2 --git-ignore` | Tree that respects `.gitignore`
`eza -la --icons --group-directories-first` | Icons (needs a Nerd Font) and directories first
`eza -D` | Directories only
`zoxide add <DIR>` | Add a directory to the database manually
`zoxide query -l` | List the database with scores
`zoxide remove <DIR>` | Drop a directory

Handy aliases:
```bash
alias ls='eza --group-directories-first'
alias ll='eza -lah --git --group-directories-first'
alias cat='bat -pp'    # plain, no pager; use `command cat` for the real one
export MANPAGER="sh -c 'col -bx | bat -l man -p'"    # coloured man pages
```
`eval "$(zoxide init bash --cmd cd)"` replaces `cd` itself with the zoxide-aware version.

## delta
A syntax-highlighting pager for `git diff`, `git log -p` and `git show` ([[git]]). Install with `brew install git-delta`, `winget install dandavison.delta`, or the `.deb` from its releases page. Add to `~/.gitconfig`:
```ini
[core]
    pager = delta
[interactive]
    diffFilter = delta --color-only
[delta]
    navigate = true     # n / N jump between files
    line-numbers = true
    side-by-side = false
[merge]
    conflictStyle = zdiff3
```
COMMAND | DESCRIPTION
---|---
`git diff` | Now rendered with delta
`git -c delta.side-by-side=true diff` | Side-by-side for one command
`delta file1 file2` | Diff two files without git
`git log -p` | Highlighted history with patches
`delta --show-config` | Print the active configuration

## ncdu and dust
Both find what is using disk space. `ncdu` is interactive; `dust` prints a tree with bars.

COMMAND | DESCRIPTION
---|---
`ncdu /var` | Scan a directory, browse with arrows, `d` deletes, `q` quits
`ncdu -x /` | Stay on one filesystem (skip mounts)
`ncdu -o scan.json /srv && ncdu -f scan.json` | Scan once, browse later (also over SSH)
`ncdu --exclude node_modules .` | Skip a pattern
`sudo ncdu -x /` | Include directories you cannot read as your user
`dust` | Tree of the current directory
`dust -d 2` | Limit depth
`dust -n 20` | Show 20 entries
`dust -r` | Reverse order (biggest at the bottom)
`dust -X .git` | Ignore a directory
`dust -e '\.log$'` | Only count names matching a regex
`dust -b` | Do not show percent bars
`du -sh * \| sort -h` | Classic fallback ([[linuxbasics]])

## btop
COMMAND | DESCRIPTION
---|---
`btop` | Resource monitor for CPU, memory, disks, network and processes
`btop --utf-force` | Force UTF-8 symbols on a limited terminal
`btop --low-color` | 16-colour mode (for example over a plain SSH session)
`Esc` | Open the menu and options
`f` | Filter processes
`t` / `k` | Toggle tree view / kill the selected process

Config lives in `~/.config/btop/btop.conf`. For per-container usage see [[docker]] (`docker stats`).

## hyperfine
Command-line benchmarking: runs a command many times and reports mean, spread and min/max.

COMMAND | DESCRIPTION
---|---
`hyperfine 'sleep 0.3'` | Benchmark one command
`hyperfine 'fd -e md' 'find . -name "*.md"'` | Compare commands
`hyperfine -w 3 '<CMD>'` | Three warm-up runs first
`hyperfine -r 50 '<CMD>'` | Exactly 50 runs
`hyperfine -p 'sync' '<CMD>'` | Run a prepare command before each timing
`hyperfine -L tool rg,grep '{tool} -r foo .'` | Parameter scan over a list
`hyperfine --export-markdown bench.md '<CMD>'` | Export results (also `--export-json`)
`hyperfine -i '<CMD>'` | Ignore non-zero exit codes
`hyperfine -N 'ls'` | No shell wrapper, for very fast commands

## Combos
COMMAND | DESCRIPTION
---|---
`rg -l "TODO" \| xargs bat` | View every file containing a string
`rg --files \| fzf --preview 'bat --color=always {}'` | Fuzzy open with preview
`fd -e log -x gzip` | Compress every log under the current directory
`fd -e jpg -x convert {} {.}.png` | Convert in bulk, `{.}` is the name without extension
`fd -t f -S +100M -x ls -lh` | List files bigger than 100 MB
`fd -H '^\.env$' -X rg -l "PASSWORD"` | Hunt for plaintext secrets in env files
`rg "ERROR" /var/log -g '*.log' --no-filename -o \| sort \| uniq -c \| sort -rn` | Count error lines by text
`fd -e md \| fzf -m \| xargs -o vim` | Pick Markdown files to edit
`dust -d 1 /var/lib/docker` | See what Docker is using ([[docker]])

## Others Worth Knowing
- `jq` for JSON ([[jq]]), `yq` for YAML.
- `tmux` ([[tmux]]) and `starship` prompt ([[starship]]).
- `curl` ([[curl]]) and `nmap` ([[nmap]]).
- `direnv` loads environment per directory; `just` and `make` run project tasks.
- `gh`, `glab`, `tea` for Git hosts: [[github-cli]], [[gitlab]], [[gitea]].

## Not Verified
Package names and availability vary by distro release and were not checked on a live system.

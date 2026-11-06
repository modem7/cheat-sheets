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

For classic tools see [[grep]], [[sed]] and [[awk]].

## fd
COMMAND | DESCRIPTION
---|---
`fd name` | Find by regex in file names
`fd -e md` | By extension
`fd -t d` | Directories only (`-t f` files)
`fd -H -I name` | Include hidden and ignored files
`fd -e log -x gzip {}` | Run a command on each match
`fd -e tmp -X rm` | One command with all matches

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

Enable key bindings in bash or zsh: `eval "$(fzf --bash)"` or `source <(fzf --zsh)` (fzf 0.48 and later; older packages ship a `key-bindings.bash` file instead).

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

## Others Worth Knowing
- `jq` for JSON ([[jq]]), `yq` for YAML.
- `tmux` ([[tmux]]) and `starship` prompt ([[starship]]).
- `curl` ([[curl]]) and `nmap` ([[nmap]]).
- `direnv` loads environment per directory; `just` and `make` run project tasks.
- `gh`, `glab`, `tea` for Git hosts: [[github-cli]], [[gitlab]], [[gitea]].

## Not Verified
Package names and availability vary by distro release and were not checked on a live system.

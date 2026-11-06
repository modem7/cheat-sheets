# Homebrew
Homebrew is the package manager for macOS (and Linux). It installs command line tools ("formulae") and GUI apps ("casks"). On Windows use [Chocolatey](../windows/chocolatey.md); on Debian and Ubuntu use `apt`.

Homepage and docs: [brew.sh](https://brew.sh), [Homebrew Docs](https://docs.brew.sh)

---
## Install
Copy the one-line install command from [brew.sh](https://brew.sh) (read the script first if you prefer). On Apple Silicon, Homebrew lives in `/opt/homebrew`; add it to your shell:
```zsh
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```
Intel Macs use `/usr/local`, and Linux uses `/home/linuxbrew/.linuxbrew`. Run `brew doctor` after installing. See [Docker on macOS Silicon](docker-on-macos-silicon.md) for Apple Silicon notes.

## Everyday Commands
COMMAND | DESCRIPTION
---|---
`brew install <FORMULA>` | Install a CLI tool
`brew install --cask <APP>` | Install a GUI app
`brew search <TEXT>` | Search
`brew info <NAME>` | Details and caveats
`brew list` / `brew list --cask` | Installed formulae / casks
`brew uninstall <NAME>` | Remove
`brew uninstall --zap --cask <APP>` | Remove an app and its leftovers
`brew update` | Update Homebrew and the package list
`brew outdated` | Show what can be upgraded
`brew upgrade` | Upgrade everything (or `brew upgrade <NAME>`)
`brew cleanup` | Remove old versions and caches
`brew doctor` | Diagnose problems
`brew deps --tree <NAME>` | Dependency tree
`brew pin <NAME>` | Hold a formula at its current version

## Services
COMMAND | DESCRIPTION
---|---
`brew services list` | Background services
`brew services start <NAME>` | Start now and at login
`brew services restart <NAME>` | Restart
`brew services stop <NAME>` | Stop

## Taps
COMMAND | DESCRIPTION
---|---
`brew tap <USER/REPO>` | Add a third-party repository
`brew tap` | List taps
`brew untap <USER/REPO>` | Remove one

## Brewfile (Reproducible Setup)
```bash
brew bundle dump --file=~/Brewfile --force
brew bundle --file=~/Brewfile
```
`brew bundle dump` writes everything installed into a `Brewfile`. Commit it to a [Git](../tools/git.md) repository to rebuild a machine in one command. A Brewfile contains lines such as `brew "jq"`, `cask "iterm2"` and `tap "homebrew/cask-fonts"`.

## Tools Covered Here
`kubernetes-cli` ([Kubectl](../kubernetes/kubectl.md)), `k9s` ([K9s](../kubernetes/k9s.md)), `kind` ([Kind](../kubernetes/kind.md)), `helm` ([Helm Cheat-Sheet](../tools/helm.md)), `jq` ([jq](../tools/jq.md)), `tmux` ([tmux](../tools/tmux.md)), `starship` ([Starship Prompt](../tools/starship.md)), `gh` ([GitHub and the gh CLI](../tools/github-cli.md)), `azure-cli` ([Azure CLI (az)](../tools/azure-cli.md)), `awscli` ([AWS CLI](../tools/aws-cli.md)), `iterm2` ([iTerm2](../tools/iterm2.md)).

## Not Verified
Written from knowledge of Homebrew and not run here.

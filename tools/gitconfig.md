# gitconfig
The Git configuration files and the settings worth setting. Everyday Git commands are in [Git](git.md); signing and credentials are covered further in [GitHub and the gh CLI](github-cli.md) and [GPG](../security/gpg.md).

Documentation: [git-config](https://git-scm.com/docs/git-config)

Setting names were checked against the `git-config` man page of Git 2.53.

## Files and Scopes
SCOPE | FILE | FLAG
---|---|---
System | `/etc/gitconfig` | `--system`
Global (you) | `~/.gitconfig` or `~/.config/git/config` | `--global`
Local (one repo) | `.git/config` | `--local` (default when writing)
Worktree | `.git/config.worktree` | `--worktree`

Later scopes override earlier ones: local beats global beats system.

## Commands
COMMAND | DESCRIPTION
---|---
`git config --global KEY VALUE` | Set a value
`git config --global --unset KEY` | Remove it
`git config --global --get KEY` | Read one value
`git config --list --show-origin` | Every effective setting and the file it came from
`git config --global --edit` | Open the global file in your editor
`git config --global --add KEY VALUE` | Add another value to a multi-valued key
`git config --global --get-all KEY` | Read all values of a multi-valued key
`git config --global --replace-all KEY VALUE` | Replace every value of a key
`git config --global --remove-section SECTION` | Delete a whole section

## A Sensible Starter
```ini
[user]
	name = YOUR_NAME
	email = you@example.com
[init]
	defaultBranch = main
[core]
	editor = nano
[pull]
	rebase = false
[push]
	autoSetupRemote = true
[fetch]
	prune = true
[merge]
	conflictStyle = zdiff3
[rebase]
	autoStash = true
	autoSquash = true
[rerere]
	enabled = true
[commit]
	verbose = true
[diff]
	algorithm = histogram
[alias]
	st = status -sb
	lg = log --oneline --graph --decorate
```

## Useful Settings
KEY | EFFECT
---|---
`user.name`, `user.email` | Author on every commit
`user.useConfigOnly = true` | Refuse to guess an identity; forces you to set one per repo
`init.defaultBranch` | Name of the first branch in new repos
`core.editor` | Editor for commit messages and rebases
`core.pager` | Pager for long output (`less -FRX` is common)
`core.autocrlf` | `input` on Linux and macOS, `true` on Windows
`pull.rebase` | `true` rebases on pull, `false` merges
`pull.ff = only` | Refuse a pull that is not a fast-forward
`push.default` | Which branch `git push` sends (default `simple`)
`push.autoSetupRemote` | First push of a new branch sets its upstream automatically
`fetch.prune` | Delete remote-tracking branches that no longer exist
`merge.conflictStyle = zdiff3` | Show the common ancestor in conflict markers
`rebase.autoStash` | Stash and reapply local changes around a rebase
`rebase.autoSquash` | Order `fixup!` and `squash!` commits automatically
`rerere.enabled` | Remember how you resolved a conflict and reuse it
`commit.verbose` | Show the diff in the commit message editor
`diff.algorithm` | `histogram` or `patience` for clearer diffs
`diff.colorMoved` | Colour moved lines differently from added or removed
`status.short` | Short `git status` by default
`tag.sort`, `branch.sort` | Sort order for `git tag` / `git branch` (e.g. `-committerdate`)
`transfer.fsckObjects` | Check object integrity on fetch and push
`log.date` | Date format in `git log`

## Aliases
```ini
[alias]
	st = status -sb
	co = checkout
	sw = switch
	br = branch
	lg = log --oneline --graph --decorate --all
	last = log -1 HEAD --stat
	unstage = restore --staged
	amend = commit --amend --no-edit
	wip = !git add -A && git commit -m wip --no-verify
```

An alias starting with `!` runs as a shell command. Create one from the command line with `git config --global alias.st "status -sb"`.

## Conditional Includes
Use a different identity per folder:

```ini
[includeIf "gitdir:~/work/"]
	path = ~/.gitconfig-work
```

`~/.gitconfig-work` then holds `[user]` with the work name and email. `gitdir:` matches repos whose `.git` is under that path (a trailing `/` matches everything below it); `gitdir/i:` ignores case. `include.path` includes a file unconditionally.

## Credentials
KEY | EFFECT
---|---
`credential.helper = cache --timeout=3600` | Keep credentials in memory for an hour
`credential.helper = store` | Save them in plain text in `~/.git-credentials` (avoid)
`credential.https://github.com.helper = !gh auth git-credential` | Use the GitHub CLI as the helper for GitHub
`url."git@github.com:".insteadOf = https://github.com/` | Always use SSH for GitHub URLs

When a helper list needs resetting, set an empty `helper =` first, then the helper you want (that is why `gh auth setup-git` writes an empty line before its helper).

## Signing
```bash
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
git config --global commit.gpgsign true
```

## Safe Directory
Git refuses repos owned by another user. Trust one explicitly:

```bash
git config --global --add safe.directory /srv/REPO_PATH
```

## Troubleshooting
SYMPTOM | FIX
---|---
Wrong author on commits | `git config --show-origin user.email` shows which file wins; set it locally in that repo
`detected dubious ownership` | Add the path with `safe.directory`
Settings seem ignored | `git config --list --show-origin`; a later scope or an `includeIf` is overriding
`includeIf` does nothing | The path needs a trailing `/`, and the repo must be inside it (check with `git rev-parse --git-dir`)
Asked for a password every push | Configure a credential helper or use SSH

## See Also
- [Git](git.md)
- [Git Recipes](git-recipes.md)
- [Git Troubleshooting](git-troubleshooting.md)
- [GitHub and the gh CLI](github-cli.md)
- [GPG](../security/gpg.md)
- [OpenSSH Cheat-Sheet](openssh.md)

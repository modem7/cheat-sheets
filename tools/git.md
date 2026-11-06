# Git

Git is an open source version control system, which supports your development tasks,
especially in distributed code projects.

## Installation

Git can be easily installed on Linux systems with the available package managers.
E.g. for Debian based systems by `apt install git`.

For other systems, see the download page of Git [here](https://git-scm.com/downloads).

## Configuration

Git can be configured by the CLI using the `git config` command. For first configuration
it is necessary to configure at least the parameters `user.name` and `user.email`. This
can be done by the following commands:

```bash
git config --global user.name "Your Name"
```

```bash
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
git config --global pull.rebase false     # or true to rebase on pull
git config --global core.autocrlf input   # Windows: true, Linux/macOS: input
git config --list --show-origin
```
Hosting and CLIs: [GitHub and the gh CLI](github-cli.md), [GitLab and the glab CLI](gitlab.md), [Gitea (and Forgejo)](gitea.md). Repository SSH keys: [OpenSSH Cheat-Sheet](openssh.md). Faster tooling: [Modern CLI Tools](modern-cli-tools.md).

## Using Git

The following commands can be helpful for working with `git`.

| git command                        | Comment                                                                                                                                        |
| ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `git init`                         | Initialize a directory as git managed repository                                                                                               |
| `git clone <repo_url>`             | Clone a remote repository to your local client                                                                                                 |
| `git status`                       | Shows uncommitted changes, new files etc.                                                                                                       |
| `git add <wildcard_or_filename>`   | Stage an updated / new file to the next commit                                                                                                 |
| `git rm <wildcard_or_filename>`    | Remove a file and stage the removal for the next commit                                                                                        |
| `git commit -m "<commit message>"` | Commit staged changes under a new commit                                                                                                       |
| `git commit`                       | Will open an editor to write more descriptive commit messages.<br> See [here](https://cbea.ms/git-commit/) for a guide on good commit messages |
| `git switch <branch_name>`         | Switch to another branch (`git checkout` still works)                                                                                                                       |
| `git branch`                       | Shows a list of existing branches                                                                                                              |
| `git branch <branch_name>`         | Creates a new branch (from the currently checked out branch)                                                                                   |
| `git merge <branch_name>`          | Merge changes from `branch_name` to the currently checked out branch                                                                           |
| `git push`                         | Push committed changes to the remote repository                                                                                                 |
| `git pull`                         | Pull current state from the remote repository to your local repo                                                                               |

### More Commands
COMMAND | DESCRIPTION
---|---
`git diff` / `git diff --staged` | Unstaged / staged changes
`git log --oneline --graph --decorate --all` | Compact history graph
`git log -p -- <file>` | History of one file with patches
`git blame <file>` | Who last changed each line
`git show <commit>` | Show one commit
`git switch -c <branch>` | Create and switch to a branch
`git branch -d <branch>` | Delete a merged branch (`-D` to force)
`git push -u origin <branch>` | Push a new branch and set upstream
`git push origin --delete <branch>` | Delete a remote branch
`git fetch --all --prune` | Update remote refs and drop deleted ones
`git pull --rebase` | Pull and replay local commits on top
`git rebase -i HEAD~3` | Edit, squash or reorder the last three commits
`git restore <file>` | Discard unstaged changes in a file
`git restore --staged <file>` | Unstage a file
`git reset --soft HEAD~1` | Undo the last commit, keep the changes staged
`git reset --hard HEAD~1` | Undo the last commit and **discard** the changes
`git revert <commit>` | Add a commit that undoes another (safe for shared history)
`git commit --amend` | Change the last commit (do not do this after pushing to a shared branch)
`git stash` / `git stash pop` | Shelve and restore uncommitted work
`git stash list` | List stashes
`git cherry-pick <commit>` | Apply one commit to the current branch
`git tag -a v1.0.0 -m "msg"` | Annotated tag (`git push --tags` to publish)
`git remote -v` | Show remotes
`git remote add origin <url>` | Add a remote
`git remote set-url origin <url>` | Change a remote URL
`git clean -fdn` | Preview untracked files that `-fd` would delete
`git reflog` | Recover lost commits after a bad reset or rebase
`git bisect start` | Binary search for the commit that broke something
`git worktree add ../dir <branch>` | Check out another branch in a second folder
`git submodule update --init --recursive` | Fetch submodules
`git config --global alias.st status` | Create an alias (`git st`)
`git push --force-with-lease` | Safer force push, refuses if the remote moved

### Ignoring Files
Put patterns in `.gitignore` (per repository) or the global file `~/.config/git/ignore`. Files already tracked stay tracked until `git rm --cached <file>`.

### SSH and Signed Commits
```bash
ssh-keygen -t ed25519 -C "you@example.com"
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
git config --global commit.gpgsign true
```
Upload the public key to your Git host as both an authentication and a signing key. See [OpenSSH Cheat-Sheet](openssh.md).

### Working with git-flow

Git-flow assists you by combining multiple steps of `git` commands to one `git-flow` command
which will do a workflow of steps. Although `git-flow` makes life easier in some cases,
it makes it also more complex sometimes and you need to execute some steps before or after using
a `git-flow` command as regular `git` command. (See below)

As an example, here is the comparison between the regular `git` commands and the appropriate
`git-flow` command for creating a release.

| git-flow command                                    | git command                                           |
| --------------------------------------------------- | ----------------------------------------------------- |
| `git-flow feature start <feature_name>`             | `git checkout -b feature/<feature_name> develop`      |
| `git-flow feature finish <feature_name> [--squash]` | `git checkout develop`                                |
|                                                     | `git merge [--squash] --no-ff feature/<feature_name>` |
|                                                     | `git branch -d feature/<feature_name>`                |

Another `git-flow` cheat sheet can be found [here](https://danielkummer.github.io/git-flow-cheatsheet/).

## Using git-crypt

Having secret or sensitive information in your git repository is never a good choice. But
sometimes it's necessary. Never push unencrypted data to your remote repository.

Git-crypt is a transparent encryption tool that works seamless with your Git repository. All sensitive
information is encrypted before pushed to the remote repository. Once you've unlocked the
repository locally, all data will be decrypted automatically when pulling from the remote
repo. This makes development with encrypted data effortless.

To install git-crypt, you can use your package manager of choice (e.g. `apt`):

```bash
sudo apt install git-crypt
```

To initialize a new repository with git-crypt, you can use `git-crypt init` when located in the
repository directory. An already encrypted git repository can be unlocked by `git-crypt unlock`.
This requires you to have either the repository encryption key in your GPG keychain, or that
your private GPG key has been added to the allowed keys in the repository. For more details,
see the links below.

For more information, check out the official Github repository [here](https://github.com/AGWA/git-crypt).
A tutorial on git-crypt can be found [here](https://thedatabaseme.de/2022/04/13/lets-keep-this-our-secret-transparent-git-encryption-using-git-crypt/).
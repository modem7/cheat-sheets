# Git Recipes
Task-oriented Git recipes: "I did X by mistake, how do I get back?" and "how do I find Y?". Basics (init, add, commit, branches, remotes) live in [Git](git.md), GitHub from the terminal in [GitHub and the gh CLI](github-cli.md), and error-message-led fixes in [Git Troubleshooting](git-troubleshooting.md). Commands here were checked against current Git (2.5x). Lines marked **rewrites history** change commit IDs, so only do them on commits you have not shared, or coordinate and use `--force-with-lease`.

Documentation: [Git reference](https://git-scm.com/docs), [Pro Git book](https://git-scm.com/book), [git-filter-repo](https://github.com/newren/git-filter-repo)

## Undo and Fix Commits
COMMAND | DESCRIPTION
---|---
`git reset --soft HEAD~1` | Undo the last commit, keep changes **staged**
`git reset HEAD~1` | Undo the last commit, keep changes **unstaged** (`--mixed`, the default)
`git reset --hard HEAD~1` | Undo the last commit and **discard** the changes
`git reset --hard origin/<BRANCH>` | Throw away all local commits and changes, match the remote
`git commit --amend` | Edit the message and include staged changes in the last commit
`git commit --amend --no-edit` | Add staged changes to the last commit, keep the message
`git commit --amend --reset-author` | Reset author to the current `user.name` / `user.email`
`git restore <FILE>` | Discard unstaged changes in a file
`git restore --staged <FILE>` | Unstage a file, keep the edits
`git restore --source=<COMMIT> -- <FILE>` | Bring one file back from another commit
`git restore -p <FILE>` | Discard changes hunk by hunk
`git revert <COMMIT>` | New commit that undoes a commit (safe on shared branches)
`git revert <OLD>..<NEW>` | Revert a range, one revert per commit (`-n` to combine into one)
`git revert -m 1 <MERGE_COMMIT>` | Undo a merge, keeping parent 1 (the branch you merged into)

After pushing, prefer `revert`. If you amend or reset a pushed commit on your own branch:
```bash
git push --force-with-lease
```
`--force-with-lease` refuses if someone else pushed in the meantime, unlike `--force`.

Reverting a merge: Git then thinks the branch's changes are already merged, so merging that branch again brings nothing in. To re-merge later, first revert the revert (`git revert <REVERT_COMMIT>`), then merge.

## Committed on the Wrong Branch
Not pushed yet, work is on `main` but belongs on a new branch:
```bash
git branch feature            # new branch at the current commit
git reset --hard origin/main  # put main back (drops the commits from main only)
git switch feature
```

Last commit belongs on an existing branch:
```bash
git switch <TARGET>
git cherry-pick main          # copy the commit
git switch main
git reset --hard HEAD~1       # remove it from main
```

Uncommitted work on the wrong branch: `git stash`, `git switch <RIGHT_BRANCH>`, `git stash pop`. Git also carries uncommitted changes across `git switch` if they do not conflict.

## Interactive Rebase, Squash, Fixup
COMMAND | DESCRIPTION
---|---
`git rebase -i HEAD~4` | Edit the last four commits
`git rebase -i --root` | Edit from the very first commit
`git rebase -i <BASE>` | Edit everything after `<BASE>` (for a branch: `git rebase -i main`)
`git rebase --continue` / `--abort` / `--skip` | Resolve and carry on, cancel, or drop the current commit
`git commit --fixup <COMMIT>` | Create a `fixup!` commit aimed at an older commit
`git commit --squash <COMMIT>` | Same, but lets you edit the message at squash time
`git rebase -i --autosquash <BASE>` | Reorder and mark `fixup!` / `squash!` commits automatically
`git config --global rebase.autoSquash true` | Make `--autosquash` the default for interactive rebases
`git config --global rebase.autoStash true` | Stash and restore dirty changes around a rebase
`git rebase --onto <NEW_BASE> <OLD_BASE> <BRANCH>` | Move a branch to a new base (for example after its parent was squash-merged)
`git rebase main --exec '<TEST_CMD>'` | Run a command after each commit during the rebase
`git merge --squash <BRANCH>` | Stage the branch's net change as one commit (you then `git commit`)

Commands in the todo list:
KEYWORD | EFFECT
---|---
`pick` | Keep the commit
`reword` | Keep, edit the message
`edit` | Stop to amend the commit, then `git rebase --continue`
`squash` | Meld into the previous commit and combine messages
`fixup` | Meld into the previous commit and discard this message
`drop` | Delete the commit
`exec <CMD>` | Run a shell command at this point

Typical flow to tidy a branch before a PR:
```bash
git commit --fixup <COMMIT_TO_FIX>
git rebase -i --autosquash origin/main
git push --force-with-lease
```
Reorder the lines to reorder the commits. To split a commit, mark it `edit`, then `git reset HEAD~1`, commit the pieces separately, and `git rebase --continue`.

Merge conflicts mid-rebase: fix the files, `git add <FILE>`, `git rebase --continue`. To use "ours" and "theirs" correctly note that during a rebase they are swapped: `--ours` is the branch you are rebasing **onto**, `--theirs` is your commit being replayed.

## Recover with the Reflog
The reflog records where `HEAD` and branches pointed, locally, for about 90 days (30 for unreachable entries by default). Almost nothing is lost after a bad `reset --hard`, rebase or deleted branch if it was ever committed.

COMMAND | DESCRIPTION
---|---
`git reflog` | History of where `HEAD` has been
`git reflog show <BRANCH>` | Reflog for one branch
`git reset --hard HEAD@{1}` | Go back to where `HEAD` was one move ago
`git reset --hard <BRANCH>@{2.hours.ago}` | Go back in time
`git branch rescue <SHA>` | Make a branch from a lost commit, the safest way to recover it
`git switch -c <BRANCH> <SHA>` | Same and switch
`git fsck --lost-found` | Dangling commits and blobs not in any reflog
`git fsck --no-reflogs --unreachable \| grep commit` | Find a dropped stash or an orphaned commit

Recover a deleted branch: find its last commit in `git reflog`, then `git branch <NAME> <SHA>`. Uncommitted changes that were never staged or stashed cannot be recovered by Git.

## Cherry-pick and Patches
COMMAND | DESCRIPTION
---|---
`git cherry-pick <COMMIT>` | Apply one commit here
`git cherry-pick <A> <B>` | Several commits
`git cherry-pick <A>^..<B>` | Inclusive range A to B
`git cherry-pick -x <COMMIT>` | Append "(cherry picked from commit ...)" to the message
`git cherry-pick -n <COMMIT>` | Apply to the working tree without committing
`git cherry-pick -m 1 <MERGE>` | Pick a merge commit relative to parent 1
`git cherry-pick --continue` / `--abort` | After conflicts / cancel
`git format-patch -3` | Write the last three commits as `.patch` files
`git am < 0001-fix.patch` | Apply patches as commits
`git apply --check <FILE.diff>` | Test whether a diff applies

## Bisect
Binary search for the commit that introduced a bug.
```bash
git bisect start
git bisect bad                 # current commit is broken
git bisect good v1.4.0         # last known good tag or commit
# Git checks out the midpoint: test it, then answer
git bisect good                # or: git bisect bad
git bisect reset               # finish and return to where you started
```

Automate with a script (exit `0` = good, `1`-`127` except `125` = bad, `125` = cannot test, skip):
```bash
git bisect start HEAD v1.4.0
git bisect run ./test.sh
# or inline
git bisect run sh -c 'make && ./check'
git bisect reset
```
`git bisect log` shows the steps, `git bisect skip` skips an untestable commit.

## Stash Recipes
COMMAND | DESCRIPTION
---|---
`git stash push -m "<MESSAGE>"` | Stash tracked changes with a name
`git stash push -u` | Include untracked files (`-a` for ignored files too)
`git stash push -p` | Choose hunks interactively
`git stash push -- <PATH>` | Stash only certain paths
`git stash push --keep-index` | Stash but leave staged changes in place (test the staged state)
`git stash list` | List stashes
`git stash show -p stash@{1}` | Show a stash as a diff
`git stash apply stash@{1}` | Apply and keep the stash
`git stash pop` | Apply the latest and drop it
`git stash drop stash@{1}` | Delete one
`git stash clear` | Delete all (recoverable only with `git fsck`)
`git stash branch <BRANCH> stash@{0}` | Create a branch from the stash's base commit and apply it, good for stashes that now conflict
`git checkout stash@{0} -- <FILE>` | Take one file from a stash
`git stash push -m "wip" && git pull --rebase && git stash pop` | Update a dirty tree

`git stash pop` leaves the stash in the list if applying it conflicts, so you do not lose it.

## Worktrees
Check out several branches at once in separate folders sharing one repository (no second clone, no stashing to switch).

COMMAND | DESCRIPTION
---|---
`git worktree add ../<DIR> <BRANCH>` | New folder with an existing branch
`git worktree add -b <NEW_BRANCH> ../<DIR> origin/main` | New folder with a new branch off `origin/main`
`git worktree add --detach ../<DIR> <TAG>` | Detached HEAD, e.g. to test a release
`git worktree list` | List worktrees
`git worktree remove ../<DIR>` | Delete a clean worktree (`--force` if dirty)
`git worktree prune` | Forget worktrees whose folder was deleted by hand
`git worktree lock ../<DIR>` | Protect one on removable storage

A branch can be checked out in only one worktree at a time. After a PR merges: `git worktree remove ../<DIR>` and `git branch -d <BRANCH>`.

## Sparse and Shallow Clones
COMMAND | DESCRIPTION
---|---
`git clone --depth 1 <URL>` | Latest commit only, much smaller (`--branch <TAG>` for a release)
`git clone --depth 1 --single-branch -b <BRANCH> <URL>` | One branch, shallow
`git fetch --deepen 50` | Fetch 50 more commits of history
`git fetch --unshallow` | Convert to a full clone
`git clone --filter=blob:none <URL>` | Partial clone: full history, file contents fetched on demand
`git clone --filter=blob:none --sparse <URL>` | Partial and only the top-level files checked out
`git sparse-checkout set <DIR1> <DIR2>` | Check out only these folders (cone mode)
`git sparse-checkout add <DIR>` | Add another folder
`git sparse-checkout list` | Show the selection
`git sparse-checkout disable` | Check out everything again

Shallow clones limit `git log`, `blame`, `bisect` and some CI versioning (such as `git describe`). In GitHub Actions use `fetch-depth: 0` for full history. A blob-less partial clone usually works better than `--depth` when you need history.

## Rewrite Author or Email
COMMAND | DESCRIPTION
---|---
`git commit --amend --reset-author --no-edit` | Fix the last commit
`git rebase -r --root --exec 'git commit --amend --no-edit --reset-author'` | Reset author on every commit (set `user.name` / `user.email` first). **Rewrites history**
`git rebase -r <BASE> --exec '...'` | Same, only commits after `<BASE>`
`git filter-repo --mailmap <FILE>` | Bulk rewrite across the whole repo from a mailmap file
`.mailmap` file | Fix names in `git log` and `shortlog` output without rewriting anything

`.mailmap` and `filter-repo --mailmap` use this format:
```text
Correct Name <correct@example.com> <old@example.com>
```
`git filter-branch` still exists but its own docs recommend `git filter-repo` instead. For a rebase-based rewrite of only your own commits on a branch, force-push afterwards with `--force-with-lease`.

## Remove a Committed Secret
**Step 0: rotate the secret.** Treat anything that was ever pushed to a remote as compromised, because clones, forks, CI logs and caches may already hold it. Rewriting history is clean-up, not a substitute for revoking the credential.

Not pushed yet: `git commit --amend` or interactive rebase (drop or `edit` the commit), then check with `git log -p -S'<SECRET>'`.

Already pushed (needs [git-filter-repo](https://github.com/newren/git-filter-repo), `apt install git-filter-repo` or `pip install git-filter-repo`), run on a **fresh clone** (filter-repo refuses non-fresh clones unless you pass `--force`):
```bash
git clone <URL> repo-clean && cd repo-clean

# remove a whole file from all history
git filter-repo --invert-paths --path <PATH/TO/SECRET_FILE>

# or replace a string everywhere (one rule per line in the file)
printf '%s\n' '<SECRET>==>***REMOVED***' > replacements.txt
git filter-repo --replace-text replacements.txt

# filter-repo drops the remote as a safety measure, so re-add it
git remote add origin <URL>
git push --force --all
git push --force --tags
```
Then:
- **Everyone** with a clone must re-clone (or hard-reset and prune). Old clones would otherwise push the secret back.
- Forks and open pull requests keep the old commits. On GitHub, pull request refs (`refs/pull/*`) and cached commit URLs can stay reachable after a force-push, so for sensitive data contact GitHub Support to remove cached views and run garbage collection. See GitHub's "Removing sensitive data from a repository" guide.
- Remove it from build caches, CI logs, release artifacts and container images too.
- Add the file to `.gitignore`, and add a pre-commit scanner such as `gitleaks` or `trufflehog`, and enable GitHub secret scanning and push protection.
- To keep a secret in the repo safely, encrypt it (git-crypt in [Git](git.md), SOPS, [Bitwarden Cheat-Sheet](bitwarden.md)).

## Clean Untracked Files
COMMAND | DESCRIPTION
---|---
`git clean -n -d` | Dry run: list untracked files and folders that would go
`git clean -f -d` | Delete untracked files and folders
`git clean -f -d -x` | Also delete ignored files (build output, `.env`)
`git clean -f -d -X` | Delete **only** ignored files
`git clean -i` | Interactive
`git clean -f -d -e '<PATTERN>'` | Keep files matching a pattern
`git restore . && git clean -fd` | Reset the working tree to HEAD (tracked and untracked), irreversible

Always run the dry run (`-n`) first. `git clean` cannot be undone.

## Find Who or What Changed a Line
COMMAND | DESCRIPTION
---|---
`git blame <FILE>` | Last commit per line
`git blame -L 40,60 <FILE>` | Only lines 40 to 60
`git blame -w -C -C -C <FILE>` | Ignore whitespace and detect lines moved or copied between files
`git blame --ignore-rev <COMMIT> <FILE>` | Skip a formatting-only commit
`git config blame.ignoreRevsFile .git-blame-ignore-revs` | Skip every commit listed in that file by default (GitHub honours this file name too)
`git log -p --follow -- <FILE>` | History of a file including renames
`git log -L 40,60:<FILE>` | History of a line range
`git log -L :<FUNCTION>:<FILE>` | History of one function
`git log -S'<STRING>' --oneline` | Commits where the **number of occurrences** of a string changed (pickaxe)
`git log -G'<REGEX>' --oneline` | Commits whose diff has a line matching a regex
`git log -S'<STRING>' -p --all` | Same, across all branches, with patches
`git log --diff-filter=D --summary -- <PATH>` | Which commit deleted a file
`git log --all -- <PATH>` | History of a path even if deleted
`git log --author='<NAME>' --since='2 weeks ago'` | Filter by person and date
`git log --grep='<TEXT>' -i` | Search commit messages
`git show <COMMIT>:<PATH>` | A file as of an old commit
`git describe --tags <COMMIT>` | Nearest tag
`git branch --contains <COMMIT>` / `git tag --contains <COMMIT>` | Which branches or tags include it

`-S` finds when a string was added or removed, `-G` finds changes to lines that match a pattern (useful when the count is unchanged). See [Regex](../misc/regex.md) for the pattern syntax.

## Compare Branches
COMMAND | DESCRIPTION
---|---
`git log main..feature --oneline` | Commits on `feature` not on `main`
`git log --left-right --oneline main...feature` | Commits unique to each side (`<` main, `>` feature)
`git diff main...feature` | Changes on `feature` since it branched (merge base), which is what a PR shows
`git diff main..feature` | Direct difference between the two tips
`git diff --stat main...feature` | Summary of files changed
`git diff --name-only main...feature` | Changed file names only
`git range-diff main old-feature new-feature` | Compare two versions of a rebased series
`git cherry -v main feature` | Which commits are already upstream by patch (`+` not yet, `-` yes)
`git branch --merged main` / `--no-merged main` | Branches fully merged into `main` or not
`git merge-base main feature` | Common ancestor
`git diff <A> <B> -- <PATH>` | One file between two commits or branches

Delete merged local branches:
```bash
git branch --merged main | grep -vE '^\*|main|master' | xargs -r git branch -d
git fetch --prune
```
Squash-merged branches do not count as merged to Git, so `git branch -d` refuses; check with `gh pr list --head <BRANCH> --state all` and then use `-D`.

## Tags and Releases
COMMAND | DESCRIPTION
---|---
`git tag -a v1.2.0 -m "Release 1.2.0"` | Annotated tag (use these for releases)
`git tag -s v1.2.0 -m "Release 1.2.0"` | Signed tag
`git tag v1.2.0 <COMMIT>` | Tag an older commit
`git push origin v1.2.0` | Publish one tag
`git push --follow-tags` | Push commits plus the annotated tags that point at them
`git push origin --delete v1.2.0` | Delete a remote tag
`git tag -d v1.2.0` | Delete a local tag
`git tag -l 'v1.*' --sort=-v:refname` | List by version, newest first
`git describe --tags --abbrev=0` | Latest tag reachable from here
`git fetch --tags --force` | Update tags that moved on the remote
`git log v1.1.0..v1.2.0 --oneline` | Changelog between two tags
`gh release create v1.2.0 --generate-notes` | GitHub release with auto notes (see [GitHub and the gh CLI](github-cli.md))
`gh release create v1.2.0 --notes-file CHANGELOG.md ./dist/*` | Release with notes and assets
`gh release create v1.2.0 --target <BRANCH>` | Create the tag from a branch if it does not exist yet

Avoid moving published tags. If you must: `git tag -f v1.2.0 <COMMIT>` then `git push --force origin v1.2.0`.

## Submodules
COMMAND | DESCRIPTION
---|---
`git submodule add <URL> <PATH>` | Add a submodule (commit `.gitmodules` and the new path)
`git clone --recurse-submodules <URL>` | Clone with submodules
`git submodule update --init --recursive` | Fetch submodules in an existing clone
`git submodule update --remote --merge <PATH>` | Move a submodule to the latest of its tracked branch
`git submodule status` | Show checked-out commits (`+` out of date, `-` not initialised)
`git submodule foreach 'git pull origin main'` | Run a command in each
`git config --global submodule.recurse true` | Make `pull`, `checkout` and similar recurse into submodules
`git diff --submodule` | Show submodule changes as commit lists

Remove one:
```bash
git submodule deinit -f <PATH>
git rm -f <PATH>
rm -rf .git/modules/<PATH>
git commit -m "Remove submodule <PATH>"
```
The parent repo records a commit SHA for each submodule, so after `git pull` run `git submodule update --init --recursive` (or set `submodule.recurse`).

## Quality-of-life Config
Set once with `git config --global <KEY> <VALUE>`; they live in `~/.gitconfig`.

SETTING | EFFECT
---|---
`push.autoSetupRemote true` | `git push` on a new branch sets upstream automatically (Git 2.37+)
`pull.ff only` | `git pull` refuses to create merge commits (or use `pull.rebase true`)
`fetch.prune true` | Drop deleted remote branches on every fetch
`rebase.autoSquash true` | Honour `fixup!` commits in `rebase -i`
`rebase.autoStash true` | Stash dirty changes around a rebase
`rerere.enabled true` | Remember conflict resolutions and replay them
`merge.conflictStyle zdiff3` | Show the base version in conflict markers (Git 2.35+)
`diff.algorithm histogram` | Better diffs for moved code
`branch.sort -committerdate` | Most recent branches first in `git branch`
`tag.sort -version:refname` | Tags in version order
`column.ui auto` | Columns in `git branch` and `git tag` output
`help.autocorrect prompt` | Suggest and ask when you mistype a command (Git 2.46+)
`init.defaultBranch main` | Name for new repos
`core.editor "code --wait"` | Editor for commit messages and rebases

Aliases:
```ini
[alias]
    st = status -sb
    co = switch
    br = branch -vv
    lg = log --oneline --graph --decorate --all
    last = log -1 --stat
    unstage = restore --staged
    amend = commit --amend --no-edit
    undo = reset --soft HEAD~1
    wip = !git add -A && git commit -m 'wip'
    fp = push --force-with-lease
    gone = !git branch -vv | awk '/: gone]/{print $1}'
```
Alias with `!` runs in the shell. Create one on the command line: `git config --global alias.lg "log --oneline --graph --decorate --all"`.

## Sign Commits with an SSH Key
Needs Git 2.34 or newer. Reuse your existing SSH key (see [OpenSSH Cheat-Sheet](openssh.md)).
```bash
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
git config --global commit.gpgsign true
git config --global tag.gpgsign true

# local verification: list who is allowed to sign
echo "$(git config user.email) $(cut -d' ' -f1,2 ~/.ssh/id_ed25519.pub)" >> ~/.config/git/allowed_signers
git config --global gpg.ssh.allowedSignersFile ~/.config/git/allowed_signers
```
COMMAND | DESCRIPTION
---|---
`git commit -S -m "msg"` | Sign one commit explicitly
`git log --show-signature -1` | Show signature status
`git log --format='%h %G? %an'` | `G` good, `B` bad, `N` unsigned, `E` cannot check
`git verify-commit <COMMIT>` | Verify one commit
`git config user.signingkey "key::ssh-ed25519 AAAA..."` | Inline key, or use `ssh-agent` with a key file path
`git rebase --exec 'git commit --amend --no-edit -n -S' -i <BASE>` | Sign existing commits (**rewrites history**)

For the "Verified" badge on GitHub, add the same public key under **Settings > SSH and GPG keys** with the key type **Signing Key** (authentication and signing are separate entries even for one key). Same on GitLab and Gitea ([GitLab and the glab CLI](gitlab.md), [Gitea (and Forgejo)](gitea.md)). The `allowed_signers` file is only for local verification.

## Forks and Upstream
```bash
gh repo fork <OWNER>/<REPO> --clone          # fork and clone, sets origin (fork) and upstream
cd <REPO>
git remote -v                                # check; add by hand if missing:
git remote add upstream https://github.com/<OWNER>/<REPO>.git
```

Keep a fork up to date:
```bash
git fetch upstream
git switch main
git merge --ff-only upstream/main            # or: git rebase upstream/main
git push origin main
```
Or in one go on GitHub: `gh repo sync <YOUR_USER>/<REPO>` (branch of the fork; `--force` to overwrite a diverged branch).

Contribute:
```bash
git fetch upstream
git switch -c fix-typo upstream/main         # branch off the latest upstream
# ...commit...
git push -u origin fix-typo
gh pr create --repo <OWNER>/<REPO> --fill    # PR from your fork to the upstream repo
```
COMMAND | DESCRIPTION
---|---
`gh pr checkout <NUMBER>` | Check out a PR (including from a fork) locally
`gh pr checkout <NUMBER> -b <LOCAL_BRANCH>` | Under a name of your choice
`git fetch origin pull/<NUMBER>/head:pr-<NUMBER>` | Same without `gh`
`gh pr create --repo <OWNER>/<REPO> --head <USER>:<BRANCH>` | PR from an explicit fork branch
`git branch -u upstream/main main` | Track upstream with local `main`
`git remote rename origin fork` | Rename a remote
`gh repo set-default <OWNER>/<REPO>` | Pick which repo `gh` commands target
`gh pr merge <NUMBER> --squash --delete-branch` | Merge from the CLI (see [GitHub and the gh CLI](github-cli.md))

After a squash merge, update your branch base with `git fetch upstream && git rebase --onto upstream/main <OLD_BASE> <BRANCH>` or just delete the branch and start fresh.

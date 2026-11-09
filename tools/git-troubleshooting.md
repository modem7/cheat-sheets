# Git Troubleshooting
Symptom-led fixes for "I did something wrong in Git, how do I get out?". Find the error or situation, run the fix. Deeper versions of most fixes are in [Git Recipes](git-recipes.md), and the basics are in [Git](git.md). Inspired by [Oh Shit, Git!?!](https://ohshitgit.com/) by Katie Sylor-Miller.

Documentation: [Git reference](https://git-scm.com/docs), [Pro Git book](https://git-scm.com/book)

## First Aid
Before trying anything risky, make the situation recoverable.

COMMAND | DESCRIPTION
---|---
`git status` | What state the repo is in, and what Git suggests doing next
`git log --oneline --graph --all -20` | Where every branch points
`git reflog` | Everything `HEAD` has done, newest first. Shows commits that no branch points to any more
`git branch backup/<NAME>` | Bookmark the current commit so a later `reset` cannot lose it
`git stash push -u` | Park uncommitted and untracked work (`git stash pop` brings it back)
`git rebase --abort` / `git merge --abort` / `git cherry-pick --abort` | Cancel a half-finished operation and return to how things were

Committed work is almost never lost, as the reflog keeps it for weeks. Uncommitted changes that were never staged or stashed **are** lost after `reset --hard` or `git clean`.

## Time Machine (Reflog)
Undo almost anything that was committed: a bad reset, rebase, merge or deleted branch.

```bash
git reflog
# find the entry from before it went wrong, e.g. HEAD@{3}
git reset --hard HEAD@{3}
```

`--hard` discards uncommitted changes in tracked files. To keep the old state alongside the current one, make a branch instead: `git branch rescue HEAD@{3}`. More in [Recover with the Reflog](git-recipes.md#recover-with-the-reflog).

## Fix the Last Commit
SITUATION | FIX
---|---
Forgot a file or need one small change | Make the change, `git add <FILE>`, then `git commit --amend --no-edit`
Typo in the last commit message | `git commit --amend` (or `git commit --amend -m "<MESSAGE>"`)
Committed with the wrong author or email | `git commit --amend --reset-author`
Want the commit undone but keep the work | `git reset --soft HEAD~1` (changes stay staged) or `git reset HEAD~1` (unstaged)
Want the commit and the work gone | `git reset --hard HEAD~1` (**destroys** the changes)
Need to undo a commit from several commits ago | `git log --oneline`, then `git revert <COMMIT>` (adds a new commit that undoes it)

`--amend`, `reset` and rebase **rewrite history**. Only use them on commits you have not pushed to a shared branch. After pushing, prefer `git revert`. If you rewrote a pushed commit on your own branch, use `git push --force-with-lease`, which refuses if someone else pushed in the meantime (plain `--force` does not).

## Wrong Branch
SITUATION | FIX
---|---
Committed to `main`, meant a new branch (not pushed) | See below
Committed to the wrong existing branch | `git switch <RIGHT_BRANCH>`, `git cherry-pick <COMMIT>`, then remove it from the wrong branch with `git switch <WRONG_BRANCH>` and `git reset --hard HEAD~1`
Edited files on the wrong branch (uncommitted) | `git stash`, `git switch <RIGHT_BRANCH>`, `git stash pop`

Commit on `main` that belongs on a new branch:
```bash
git branch feature            # new branch at the current commit
git reset --hard origin/main  # put main back (drops the commit from main only)
git switch feature
```

This does not work once the commit is pushed to a shared branch. If you already tried other things first, check `git reflog` for the right commit to reset to instead of `origin/main`. More in [Committed on the Wrong Branch](git-recipes.md#committed-on-the-wrong-branch).

## Undo Changes to Files
COMMAND | DESCRIPTION
---|---
`git restore <FILE>` | Discard unstaged edits to a file (**cannot be undone**)
`git restore --staged <FILE>` | Unstage a file, keep the edits
`git restore --source=<COMMIT> -- <FILE>` | Put the file back as it was in an older commit (unstaged edit)
`git restore --source=<COMMIT> --staged --worktree -- <FILE>` | Same, and stage it ready to commit
`git checkout <COMMIT> -- <FILE>` | Older equivalent of the above, stages the old version
`git rm --cached <FILE>` | Stop tracking a file but keep it on disk
`git clean -n -d` | Dry run: list untracked files that `git clean -f -d` would delete

## Nothing Happened
SYMPTOM | CAUSE AND FIX
---|---
`git diff` shows nothing but files changed | The changes are already staged. Use `git diff --staged` (also `--cached`)
`git diff` shows nothing for a new file | Untracked files are not diffed. `git add -N <FILE>` (intent to add) makes them appear
Edited `.gitignore` but a file is still tracked | Ignoring only affects untracked files. `git rm --cached <FILE>` (or `git rm -r --cached <DIR>`), then commit
`git status` shows a file that is in `.gitignore` | Same cause. Check what matches with `git check-ignore -v <FILE>`
Renamed a file by case only and Git did not notice (macOS, Windows) | `git mv <old> <new>` (on a case-insensitive disk, go via a temporary name)
Whole file shows as changed | Line endings changed. Check `git config core.autocrlf` and use a `.gitattributes` file such as `* text=auto`
File mode changes everywhere | `git config core.fileMode false` (common on shared Windows or WSL mounts)
Commit works but the author is wrong | Set `git config user.name "<NAME>"` and `git config user.email "<EMAIL>"` for the repo, then amend

## Detached HEAD
`HEAD` points at a commit, not a branch, so new commits are not on any branch and are easy to lose. This happens after `git checkout <COMMIT>`, `<TAG>` or `origin/<BRANCH>`.

SITUATION | FIX
---|---
Just looking around | `git switch -` returns you to the previous branch
Made commits you want to keep | `git switch -c <NEW_BRANCH>` right now, they come with you
Already switched away and lost them | `git reflog`, find the commit, `git branch rescue <SHA>`
Rebase is stuck in a detached state | `git rebase --abort`, or fix the conflict and `git rebase --continue`

## Push and Pull Errors
ERROR | FIX
---|---
`! [rejected] ... (non-fast-forward)` or `fetch first` | The remote has commits you do not. `git pull --rebase` (or `git pull`), then push again
Push rejected after you amended or rebased | You rewrote history. If the branch is yours: `git push --force-with-lease`. Never force-push a shared branch
`fatal: The current branch <BRANCH> has no upstream branch` | `git push -u origin <BRANCH>` (or `git push --set-upstream origin HEAD`)
`fatal: refusing to merge unrelated histories` | The two histories share no commit. Only if that is intended: `git pull --allow-unrelated-histories`
`fatal: Need to specify how to reconcile divergent branches` | Pick once: `git config --global pull.rebase true` (or `pull.ff only`, or `false` to merge)
`error: Your local changes ... would be overwritten by merge/checkout` | Commit or `git stash` first, then retry, then `git stash pop`
`remote: error: File ... is larger than ...` or `pre-receive hook declined` | A large file is in a commit. Remove it from history before pushing: `git rm --cached <FILE>` and `git commit --amend` if it is the last commit, otherwise see [Remove a Committed Secret](git-recipes.md#remove-a-committed-secret) (same `git filter-repo` approach)
`remote: Permission denied` / `Authentication failed` | Wrong credentials or token expired. Check `git remote -v`, then see [SSH](#ssh-and-authentication)
Pushed to the wrong remote or URL | `git remote set-url origin <URL>`, then `git remote -v` to check
`remote rejected ... protected branch` | The server forbids direct or force pushes to that branch. Open a PR with a new commit that reverts instead

## Merge and Rebase Trouble
SITUATION | FIX
---|---
Merge conflict | `git status` lists the files. Edit out the `<<<<<<<`, `=======` and `>>>>>>>` markers, `git add <FILE>`, then `git commit` (merge) or `git rebase --continue` (rebase)
Take one side for a whole file | `git checkout --ours -- <FILE>` or `git checkout --theirs -- <FILE>`, then `git add <FILE>`. In a **rebase** the meaning swaps: `--ours` is the branch you are rebasing onto, `--theirs` is your own commit
Merge went wrong, not committed yet | `git merge --abort`
Merge went wrong and is already committed (not pushed) | `git reset --hard ORIG_HEAD`, or pick a point from `git reflog`
Merge already pushed | `git revert -m 1 <MERGE_COMMIT>` (see the warning on re-merging in [Undo and Fix Commits](git-recipes.md#undo-and-fix-commits))
Same conflict again and again during a rebase | `git config --global rerere.enabled true` records and replays your resolutions
Rebase went wrong and is finished | `git reflog`, find the entry before `rebase (start)`, `git reset --hard <ENTRY>`
Lost track of which files conflict | `git diff --name-only --diff-filter=U`

## Stash Trouble
SITUATION | FIX
---|---
`git stash pop` had conflicts | The stash is kept, not dropped. Resolve the conflicts, then `git stash drop`
Dropped a stash by accident | `git fsck --no-reflogs --unreachable \| grep commit`, then `git stash apply <SHA>` or `git branch rescue <SHA>`
Forgot what is stashed | `git stash list`, then `git stash show -p stash@{0}`

## Reset to Match the Remote
Last resort when a local branch is beyond repair and you do not need its local work. These steps are **destructive and unrecoverable** for anything uncommitted or untracked.

```bash
git fetch origin
git switch main
git branch backup/main-before-reset   # safety net: keeps your old commits reachable
git reset --hard origin/main
git clean -n -d                       # dry run first
git clean -f -d                       # delete untracked files and folders
```

Repeat for each broken branch. If it is still a mess, clone a fresh copy next to the old one and copy over only the files you need, rather than deleting the old directory straight away.

## SSH and Authentication
COMMAND | DESCRIPTION
---|---
`ssh -T git@github.com` | Test SSH access to GitHub (replace the host for other servers)
`ssh -vT git@github.com` | Same, verbose, to see which key is offered
`git remote -v` | Check whether the remote uses HTTPS or SSH
`git remote set-url origin git@github.com:<OWNER>/<REPO>.git` | Switch a remote from HTTPS to SSH
`gh auth status` / `gh auth login` | Check or redo GitHub CLI authentication, see [GitHub and the gh CLI](github-cli.md)
`GIT_TRACE=1 GIT_CURL_VERBOSE=1 git <COMMAND>` | Show what Git is doing (**may print tokens, redact before sharing**)

More in [OpenSSH Cheat-Sheet](openssh.md).

## Repository Damage
SYMPTOM | FIX
---|---
`fatal: not a git repository` | You are outside a repo, or `.git` was removed. Check with `git rev-parse --show-toplevel`
`fatal: bad object` / `error: object file ... is empty` | Corrupt object. Run `git fsck`. If the remote has the data, the safest fix is a fresh `git clone` and copy over unpushed work
`fatal: Unable to create '.git/index.lock': File exists` | A Git process crashed. Make sure no Git is running, then delete the lock: `rm .git/index.lock`
`warning: refname 'X' is ambiguous` | A branch and a tag share a name. Delete or rename one
Repo is huge or slow | `git count-objects -vH`, `git gc`. See [Sparse and Shallow Clones](git-recipes.md#sparse-and-shallow-clones)

## See Also
- [Git](git.md)
- [Git Recipes](git-recipes.md)
- [GitHub and the gh CLI](github-cli.md)
- [OpenSSH Cheat-Sheet](openssh.md)

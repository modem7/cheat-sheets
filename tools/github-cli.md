# GitHub and the gh CLI
`gh` is GitHub's official command line tool for repositories, pull requests, issues, Actions and the API. For plain Git commands see [[git]]. For other Git hosts see [[gitlab]] and [[gitea]].

Documentation: [GitHub CLI manual](https://cli.github.com/manual/)

---
## Install and Log In
PLATFORM | COMMAND
---|---
Debian / Ubuntu | add the official apt repo from the manual, then `sudo apt install gh`
macOS | `brew install gh` ([[homebrew]])
Windows | `choco install gh` ([[chocolatey]]) or `winget install GitHub.cli`

COMMAND | DESCRIPTION
---|---
`gh auth login` | Log in (browser or token, choose SSH or HTTPS)
`gh auth status` | Show the logged-in account and scopes
`gh auth setup-git` | Use gh as the Git credential helper
`gh auth refresh -s workflow` | Add a token scope
`ssh -T git@github.com` | Test SSH access

For scripts set `GH_TOKEN` (and `GH_HOST`/`GH_ENTERPRISE_TOKEN` for Enterprise). Use `--repo OWNER/REPO` (or `-R`) to run a command against another repository without cloning it.

## Repositories
COMMAND | DESCRIPTION
---|---
`gh repo clone OWNER/REPO` | Clone
`gh repo create NAME --private --source=. --push` | Create from the current folder and push
`gh repo fork --clone` | Fork and clone
`gh repo view --web` | Open in the browser
`gh repo list OWNER --limit 50` | List repositories
`gh repo edit --visibility private --accept-visibility-change-consequences` | Change settings
`gh repo delete OWNER/REPO` | Delete (needs the `delete_repo` scope)

## Pull Requests
COMMAND | DESCRIPTION
---|---
`gh pr create --fill` | Open a PR from the branch using the commit messages
`gh pr create --title "T" --body-file body.md --draft` | Open a draft with a body from a file
`gh pr list --state all` | List PRs
`gh pr view 15 --comments` | Show a PR
`gh pr checkout 15` | Check out a PR branch
`gh pr diff 15` | Show the diff
`gh pr checks 15 --watch` | Watch CI
`gh pr review 15 --approve` | Review (`--request-changes`, `--comment`)
`gh pr merge 15 --squash --delete-branch` | Merge
`gh pr edit 15 --title "T" --body-file body.md` | Edit title or description
`gh pr ready 15` | Mark a draft as ready

## Issues
COMMAND | DESCRIPTION
---|---
`gh issue create --title "T" --body "B" --label bug` | Create
`gh issue list --assignee @me` | List yours
`gh issue view 12` | Show
`gh issue close 12 --comment "Done"` | Close
`gh issue comment 12 --body "text"` | Comment

## Actions and Workflows
COMMAND | DESCRIPTION
---|---
`gh run list --limit 10` | Recent runs
`gh run view <ID> --log-failed` | Logs of failed steps
`gh run watch <ID>` | Follow a run
`gh run rerun <ID> --failed` | Re-run failed jobs
`gh workflow list` | List workflows
`gh workflow run NAME.yml -f key=value` | Trigger a `workflow_dispatch` workflow
`gh secret set NAME --body "value"` | Set a repository secret
`gh variable set NAME --body "value"` | Set an Actions variable

## Releases, API and Extras
COMMAND | DESCRIPTION
---|---
`gh release create v1.0.0 --generate-notes ./file` | Create a release with assets
`gh release list` | List releases
`gh api repos/OWNER/REPO` | Call the REST API
`gh api graphql -f query='{ viewer { login } }'` | GraphQL
`gh api repos/OWNER/REPO/pulls --jq '.[].title'` | Filter output with a jq expression ([[jq]])
`gh alias set co 'pr checkout'` | Create an alias
`gh extension install OWNER/gh-NAME` | Install an extension
`gh search repos "topic:homelab" --limit 10` | Search

## Useful GitHub Features
- **Actions**: workflows live in `.github/workflows/*.yml`. This repo uses one to auto-assign issues.
- **Renovate or Dependabot**: automated dependency PRs (`renovate.json` here).
- **Repository settings as code**: the Probot Settings app reads `.github/settings.yml`.
- **SSH keys and signing**: add keys at https://github.com/settings/keys. See [[openssh]].
- **Pages**, **Releases**, **Packages (ghcr.io)** and **Codespaces** are built in.

## Not Verified
Commands were written from knowledge of current `gh` and not run here. Check `gh <command> --help` for flags in your version.

# Claude Code
Anthropic's terminal coding agent. It reads and edits files, runs commands and talks to MCP servers, under a permission system you control. Pairs with [MCP](mcp.md) and the [Claude API](claude-api.md).

Documentation: [Claude Code docs](https://docs.claude.com/en/docs/claude-code/overview) · [CLI reference](https://docs.claude.com/en/docs/claude-code/cli-reference) · [Settings](https://docs.claude.com/en/docs/claude-code/settings) · [Hooks](https://docs.claude.com/en/docs/claude-code/hooks)

> **Verification:** CLI flags and subcommands were checked against `claude --help` (version 2.1.220). Slash commands, keyboard shortcuts, settings keys and file layouts are from the official docs and not executed here; those not confirmed are marked `(unverified)`.

## Start and Resume
COMMAND | DESCRIPTION
---|---
`claude` | Start an interactive session in the current directory
`claude "PROMPT"` | Start interactive with an initial prompt
`claude -p "PROMPT"` | Print mode: answer and exit (headless)
`claude -c` | Continue the most recent conversation in this directory
`claude -r [ID_OR_SEARCH]` | Resume by session ID, or pick from a list
`claude -n NAME` | Name the session
`claude -w [NAME]` | Work in a new git worktree
`claude --from-pr [PR]` | Resume a session linked to a pull request
`claude --add-dir DIR` | Allow tool access to an extra directory
`claude update` | Check for and install updates
`claude doctor` | Check installation health
`claude auth login` / `claude auth status` / `claude auth logout` | Manage authentication
`claude setup-token` | Create a long-lived token for scripts and CI

## Common Flags
FLAG | DESCRIPTION
---|---
`--model MODEL` | Alias (`sonnet`, `opus`) or full model name
`--effort LEVEL` | `low`, `medium`, `high`, `xhigh` or `max`
`--permission-mode MODE` | `acceptEdits`, `auto`, `bypassPermissions`, `manual`, `dontAsk` or `plan`
`--allowedTools "Bash(git *)" Edit` | Tools allowed without prompting
`--disallowedTools TOOL` | Tools denied
`--tools TOOL...` | Restrict the set of available tools
`--append-system-prompt TEXT` | Add to the default system prompt
`--system-prompt TEXT` | Replace the system prompt
`--settings FILE_OR_JSON` | Load extra settings
`--setting-sources user,project,local` | Choose which settings sources load
`--mcp-config FILE...` | Load MCP servers from JSON
`--strict-mcp-config` | Use only servers from `--mcp-config`
`--agents JSON` | Define subagents inline
`--plugin-dir PATH` | Load a plugin from a directory
`--debug [FILTER]` / `--debug-file PATH` | Debug logging
`--safe-mode` | Start with all customisations disabled
`--dangerously-skip-permissions` | Skip every permission check. Only in a sandbox with no sensitive access

## Headless Mode (`-p`)
Options below only apply with `-p`.

COMMAND | DESCRIPTION
---|---
`claude -p "PROMPT" --output-format json` | One JSON result object
`claude -p "PROMPT" --output-format stream-json` | Streaming JSON events (add `--verbose` if the CLI asks for it)
`claude -p "PROMPT" --json-schema SCHEMA_JSON` | Validate output against a JSON Schema
`claude -p "PROMPT" --max-budget-usd 2` | Stop at a spend limit
`claude -p "PROMPT" --fallback-model sonnet` | Fall back if the model is overloaded
`claude -p "PROMPT" --no-session-persistence` | Do not save the session
`cat FILE \| claude -p "Summarise this"` | Pipe input

```bash
git diff main... | claude -p "Review this diff for bugs" --output-format text
```

## Slash Commands
Type `/` in a session to list what is available (`/help`). Custom commands and skills appear in the same list.

COMMAND | DESCRIPTION
---|---
`/help` | Show help and commands
`/clear` | Start a fresh conversation
`/compact [FOCUS]` | Summarise history to free context
`/resume` | Pick a previous session
`/model` | Change model
`/config` | Open settings
`/permissions` | View or edit permission rules
`/memory` | Edit memory files (CLAUDE.md)
`/init` | Create a CLAUDE.md for the repo
`/mcp` | Manage MCP servers
`/agents` | Manage subagents
`/hooks` | View hook configuration
`/doctor` | Diagnose the install
`/cost` | Show token use and cost `(unverified)`
`/status` | Show version, model and account `(unverified)`
`/login` / `/logout` | Switch account
`/exit` | Quit

## Keyboard Shortcuts
Shortcuts are `(unverified)`; use `/help` for the list on your version.

KEY | ACTION
---|---
`Esc` | Interrupt the current turn
`Esc Esc` | Rewind or edit an earlier message
`Shift+Tab` | Cycle permission modes
`Ctrl+C` | Cancel input or interrupt
`Ctrl+D` | Exit
`Ctrl+R` | Search prompt history
`@PATH` | Mention a file
`!COMMAND` | Run a shell command from the prompt

## Settings and Permissions
Settings merge from user (`~/.claude/settings.json`), project (`.claude/settings.json`, shared) and local (`.claude/settings.local.json`, not committed). Managed policy overrides all.

```json
{
  "model": "sonnet",
  "permissions": {
    "allow": ["Bash(git status)", "Bash(git diff *)", "Read"],
    "ask": ["Bash(git push *)"],
    "deny": ["Read(./.env)", "Read(./secrets/**)"]
  },
  "env": { "EXAMPLE_VAR": "value" }
}
```

RULE FORM | MEANING
---|---
`Tool` | The whole tool (for example `Read`, `Edit`, `WebFetch`)
`Bash(PATTERN)` | Shell commands matching a pattern (`Bash(npm run test *)`)
`Read(PATH_GLOB)` / `Edit(PATH_GLOB)` | File access by path
`mcp__SERVER__TOOL` | A tool from an MCP server

Deny rules win over allow. Never rely on prompt text to protect secrets; deny the file read.

## CLAUDE.md and Memory
FILE | SCOPE
---|---
`~/.claude/CLAUDE.md` | Personal, all projects
`./CLAUDE.md` | Project, committed to git
`./CLAUDE.local.md` | Personal project notes, not committed `(unverified)`
`@path/to/file.md` inside CLAUDE.md | Import another file

Keep CLAUDE.md short and concrete: build and test commands, conventions, things not obvious from code. See [Prompting and Context Engineering](prompting-patterns.md).

## Hooks
Hooks run your commands at lifecycle events. Configure in settings under `hooks`.

EVENT | FIRES
---|---
`PreToolUse` | Before a tool runs; can block it
`PostToolUse` | After a tool succeeds
`UserPromptSubmit` | When you submit a prompt
`Stop` / `SubagentStop` | When the agent or a subagent finishes
`SessionStart` / `SessionEnd` | Session boundaries
`Notification` | When Claude needs attention
`PreCompact` | Before context compaction

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{ "type": "command", "command": "/path/to/check-command.sh" }]
      }
    ]
  }
}
```

The hook receives event JSON on stdin. Exit code `2` blocks the action and feeds stderr back to Claude; `0` continues.

## Skills and Subagents
WHAT | WHERE
---|---
Skill | `.claude/skills/NAME/SKILL.md` (or `~/.claude/skills/NAME/`)
Subagent | `.claude/agents/NAME.md` (or `~/.claude/agents/`)
Plugin | `claude plugin install PLUGIN@MARKETPLACE`; also `enable`, `disable`, `details`

```markdown
---
name: log-triage
description: Use when asked to find the cause of an error in logs.
---
Steps and instructions for the skill go here.
```

```markdown
---
name: reviewer
description: Reviews diffs for bugs. Use after code changes.
tools: Read, Grep, Glob
model: sonnet
---
You review diffs and report problems with file and line.
```

## MCP Servers
COMMAND | DESCRIPTION
---|---
`claude mcp add --transport http NAME URL` | Add a remote HTTP server
`claude mcp add NAME -e KEY=VALUE -- COMMAND ARGS` | Add a local stdio server
`claude mcp add-json NAME 'JSON'` | Add from a JSON string
`claude mcp list` | List servers and health
`claude mcp get NAME` | Show one server
`claude mcp remove NAME` | Remove a server
`claude mcp login NAME` / `claude mcp logout NAME` | OAuth for a server
`claude mcp add -s user ...` | Scope: `local` (default), `user` or `project`
`claude mcp serve` | Run Claude Code itself as an MCP server

Project-scoped servers live in `.mcp.json` and need approval on first use. More in [MCP](mcp.md).

## Environment Variables
VARIABLE | USE
---|---
`ANTHROPIC_API_KEY` | API key authentication instead of an account login
`ANTHROPIC_MODEL` | Default model `(unverified)`
`MAX_THINKING_TOKENS` | Extended thinking budget `(unverified)`
`CLAUDE_CODE_SIMPLE=1` | Same as `--bare` (set by that flag)

## See Also
- [Claude API and SDKs](claude-api.md)
- [Model Context Protocol (MCP)](mcp.md)
- [Prompting and Context Engineering](prompting-patterns.md)
- [AI](ai.md)

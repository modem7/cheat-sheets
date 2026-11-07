# Codex, Gemini and Copilot CLIs
Terminal coding agents from OpenAI, Google and GitHub, comparable to [Claude Code](claude-code.md). Each reads a project instruction file, edits files and runs commands with an approval model.

Documentation: [Codex CLI](https://github.com/openai/codex) · [Gemini CLI](https://github.com/google-gemini/gemini-cli) · [GitHub Copilot CLI](https://docs.github.com/en/copilot/concepts/agents/about-copilot-cli)

> **Verification:** none of these CLIs is installed here and nothing was executed. Every row is from vendor docs as remembered and is `(unverified)`. These tools change quickly: run `TOOL --help` before relying on any flag.

## Codex CLI (OpenAI) `(unverified)`
COMMAND | DESCRIPTION
---|---
`npm install -g @openai/codex` | Install
`codex` | Interactive session
`codex "PROMPT"` | Start with a prompt
`codex exec "PROMPT"` | Non-interactive run
`codex login` | Sign in with ChatGPT account or an API key
`~/.codex/config.toml` | User configuration
`AGENTS.md` | Project instructions it reads

## Gemini CLI (Google) `(unverified)`
COMMAND | DESCRIPTION
---|---
`npm install -g @google/gemini-cli` | Install
`gemini` | Interactive session
`gemini -p "PROMPT"` | Non-interactive prompt
`gemini -m MODEL` | Choose a model
`GEMINI_API_KEY` | Environment variable for API key auth
`GEMINI.md` | Project instructions it reads
`~/.gemini/settings.json` | User settings, including MCP servers

## GitHub Copilot CLI `(unverified)`
COMMAND | DESCRIPTION
---|---
`npm install -g @github/copilot` | Install
`copilot` | Interactive session
`copilot -p "PROMPT"` | Non-interactive prompt
`/login` | Sign in from within the session

Requires a Copilot subscription. The older `gh copilot` extension is a different, narrower tool `(unverified)`.

## Comparison
TOOL | PROJECT FILE | MCP
---|---|---
[Claude Code](claude-code.md) | `CLAUDE.md` | Yes, see [MCP](mcp.md)
Codex CLI | `AGENTS.md` | Yes `(unverified)`
Gemini CLI | `GEMINI.md` | Yes `(unverified)`
Copilot CLI | `.github/copilot-instructions.md` `(unverified)` | Yes `(unverified)`

## Safe Use
- Run agents in a repo or container you can discard; commit before a long run.
- Keep permissions narrow and avoid any "skip all approvals" mode outside a sandbox.
- Never put API keys in the project instruction file. See [Secret Scanning](../security/secret-scanning.md).

## See Also
- [Aider](aider.md)
- [OpenAI API](openai-api.md)
- [AI](ai.md)
